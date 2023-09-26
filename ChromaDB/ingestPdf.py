from langchain.vectorstores import Chroma
from client import persistent_client, embeddings
from pdfMain import pdfMain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor

def clearCollection():
    try:
        persistent_client.delete_collection(name="pdf")
    except:
        print('no pdf collection')

def uploadSingleDoc(collection, id, doc):
    return collection.add_documents(ids=[id], documents=[doc])

def pdfUpload(listOfPdfs):
    clearCollection()

    sectionsByFile = [] #[(pdfMain(file),file.name) for file in listOfPdfs]
    issues = []
    for file in listOfPdfs:
        try:
            sectionsByFile.append((pdfMain(file, file.name),file.name))
        except Exception as e:
            issues.append((e, file.name))
    text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size = 1250,
    chunk_overlap  = 10,
    length_function = lambda x: len(x.split(" ")),
    add_start_index = True,
    )

    sectionChunks = []
    for sections,fileName in sectionsByFile:
        sections = list(filter(lambda x: len(x.split(" ")) > 100, sections))
        chunks = text_splitter.create_documents(sections, metadatas=[{'fileName':fileName}]*len(sections))
        sectionChunks.extend(chunks)

    persistent_client.get_or_create_collection(name="pdf", embedding_function=embeddings)

    langchain_chroma_pdf = Chroma(
        client=persistent_client,
        collection_name="pdf",
        embedding_function=embeddings,
    )

    executor = ThreadPoolExecutor(max_workers=5)
    pdfFutures = [executor.submit(uploadSingleDoc, langchain_chroma_pdf, str(id), doc) for doc, id in zip(sectionChunks, range(len(sectionChunks)))]
    
    return (issues, executor, pdfFutures)


# # Below is for testing in debug mode
# from tqdm import tqdm
# from concurrent.futures import ThreadPoolExecutor, as_completed
# with tqdm(total=len(futures)) as pbar:
#     for future in as_completed(futures):
#         result = future.result()
#         pbar.update(1)