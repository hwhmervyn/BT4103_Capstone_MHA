from langchain.vectorstores import Chroma
from client import persistent_client, embeddings
from data_preprocessing.pdfMain import pdfMain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor

import sys, os
workingDirectory = os.getcwd()
sys.path.append(workingDirectory)

def clearCollection():
    try:
        persistent_client.delete_collection(name="pdf")
    except:
        print('no pdf collection')

    try:
        persistent_client.delete_collection(name="pdf_child")
    except:
        print('no pdf_child collection')

def uploadSmallChunk(collection, doc):
    return collection.add_documents(documents=[doc])
    
def uploadSingleDoc(collection, id, doc):
    return collection.add_documents(ids=[id], documents=[doc])

def pdfUpload(listOfPDFfilepaths):
    clearCollection()

    sectionsByFile = []
    issues = []
    for path in listOfPDFfilepaths:
        try:
            sectionsByFile.append((pdfMain(path),path))
        except Exception as e:
            issues.append((e, path))

    text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size = 1250,
    chunk_overlap  = 10,
    length_function = lambda x: len(x.split(" ")),
    add_start_index = True,
    )

    sectionChunks = []
    for sections,fileName in sectionsByFile:
        sections= list(filter(lambda x: len(x[0].split(" ")) > 100, sections))
        for section in sections:
            chunks = text_splitter.create_documents([section[0]], metadatas=[{'fileName':fileName,'pageNum':f"{section[1][0]} to {section[1][1]}"}]*1)
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

def uploadSmallChunk(collection, doc):
    return collection.add_documents(documents=[doc])
    

def smallChunkCollection():
    persistent_client.get_or_create_collection(name="pdf_child", embedding_function=embeddings)
    
    langchain_chroma_pdf = Chroma(
        client=persistent_client,
        collection_name="pdf",
        embedding_function=embeddings,
    )

    langchain_chroma_child_pdf  = Chroma(
        client=persistent_client,
        collection_name="pdf_child",
        embedding_function=embeddings,
    )

    child_splitter = RecursiveCharacterTextSplitter(chunk_size=250,chunk_overlap=10)

    large_docs = langchain_chroma_pdf.get()

    small_chunks = []
    for large_doc_index in range(0,len(large_docs['ids'])):
        chunks = child_splitter.create_documents([large_docs['documents'][large_doc_index]], metadatas=[{'fileName':large_docs['metadatas'][large_doc_index]['fileName'],'parentID':large_docs['ids'][large_doc_index]}] * 1)
        small_chunks.extend(chunks)

    executor = ThreadPoolExecutor(max_workers=5)
    pdfFutures = [executor.submit(uploadSmallChunk, langchain_chroma_child_pdf, doc) for doc in small_chunks]
    
    return (executor, pdfFutures)

# _, futures = pdfUpload(pdf_files)
# # Below is for testing in debug mode
# from tqdm import tqdm
# from concurrent.futures import ThreadPoolExecutor, as_completed
# with tqdm(total=len(futures)) as pbar:
#     for future in as_completed(futures):
#         result = future.result()
#         pbar.update(1)