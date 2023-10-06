from langchain.document_loaders import DataFrameLoader
from langchain.vectorstores import Chroma
import pandas as pd

from client import persistent_client, embeddings
from concurrent.futures import ThreadPoolExecutor

def clearCollection():
    try:
        persistent_client.delete_collection(name="abstract")
    except:
        print('no abstract collection')
    
    try:
        persistent_client.delete_collection(name="title")
    except:
        print('no title collection')

def uploadSingleDoc(collection, id, doc):
    return collection.add_documents(ids=[id], documents=[doc])

def excelUpload(excelFile):
    clearCollection()
    
    df = pd.read_excel(excelFile).dropna(how='all')
    df.columns = df.columns.str.lower()
    df.fillna('')

    persistent_client.get_or_create_collection(name="abstract", embedding_function=embeddings)
    persistent_client.get_or_create_collection(name="title", embedding_function=embeddings)

    langchain_chroma_abstract = Chroma(
        client=persistent_client,
        collection_name="abstract",
        embedding_function=embeddings,
    )
    langchain_chroma_title = Chroma(
        client=persistent_client,
        collection_name="title",
        embedding_function=embeddings,
    )

    loader = DataFrameLoader(df, page_content_column='abstract')
    abstractDocs = loader.load()

    loader = DataFrameLoader(df, page_content_column='title')
    titleDocs = loader.load()

    executor = ThreadPoolExecutor(max_workers=5)
    abstractFutures = [executor.submit(uploadSingleDoc, langchain_chroma_abstract, str(id), doc) for doc, id in zip(abstractDocs, range(len(abstractDocs)))]
    titleFutures = [executor.submit(uploadSingleDoc, langchain_chroma_title, str(id), doc) for doc, id in zip(titleDocs, range(len(titleDocs)))]
    
    futures = abstractFutures + titleFutures
    return (executor, futures)

# executor, futures = excelUpload('data/combined.xlsx')

# from concurrent.futures import as_completed
# from tqdm import tqdm
# Below is for testing in debug mode
# with tqdm(total=len(futures)) as pbar:
#     for future in as_completed(futures):
#         result = future.result()
#         pbar.update(1)