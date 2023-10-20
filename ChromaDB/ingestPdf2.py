import chromaUtils
from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor
from langchain.docstore.document import Document

import sys, os
workingDirectory = os.getcwd()
preProcessingDirectory = os.path.join(workingDirectory, "data_preprocessing")
chromaDirectory = os.path.join(workingDirectory, "ChromaDB")
sys.path.append(workingDirectory)
sys.path.append(preProcessingDirectory)
sys.path.append(chromaDirectory)

from pdfMain import pdfMain
from ChromaDB import chromaUtils

def uploadSmallChunk(collection, doc):
    return collection.add_documents(documents=[doc])
    
def uploadSingleDoc(collection, id, doc):
    return collection.add_documents(ids=[id], documents=[doc])

def schedulePdfUpload(listOfPDFfilepaths, collectionName):
    sectionsByFile = []
    issues = []

    for path in listOfPDFfilepaths:
        try:
            sectionsByFile.append((pdfMain(path),path))
        except Exception as e:
            issues.append((e, path))
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1250,
        chunk_overlap  = 10,
        length_function = lambda x: len(x.split(" ")),
        add_start_index = True,
    )

    sectionChunks = []
    for sections,fileName in sectionsByFile:
        sections= list(filter(lambda x: len(x[0].split(" ")) > 100, sections))
        for section in sections:
            chunks = text_splitter.create_documents([section[0]], metadatas=[{'fileName':fileName.split("\\")[-1],'pageNum':f"{section[1][0]} to {section[1][1]}"}]*1)
            sectionChunks.extend(chunks)

    chromaUtils.createCollection(collectionName)
    langchain_chroma_pdf = chromaUtils.getCollection(collectionName)

    executor = ThreadPoolExecutor(max_workers=5)
    pdfFutures = [executor.submit(uploadSingleDoc, langchain_chroma_pdf, str(id), doc) for doc, id in zip(sectionChunks, range(len(sectionChunks)))]
    
    return (issues, executor, pdfFutures)

def copyCollection(input_collection_name, output_collection_name, rel_file_names):
    input_collection = chromaUtils.getCollection(input_collection_name)
    docs_dict=input_collection.get(
        where={"fileName": {"$in": rel_file_names}},
        include=['metadatas', 'documents']
    )
    try:
        chromaUtils.createCollection(output_collection_name)
        output_collection = chromaUtils.getCollection(output_collection_name)
        doc_ids, doc_objs= [], []
        for i in range(len(docs_dict['ids'])):
            doc_str = docs_dict['documents'][i]
            doc_metadata = docs_dict['metadatas'][i]
            doc_ids.append(docs_dict['ids'][i])
            doc_objs.append(Document(page_content=doc_str,metadata=doc_metadata))
        
        executor = ThreadPoolExecutor(max_workers=5)
        pdfFutures = [executor.submit(uploadSingleDoc, output_collection, id, doc) for doc, id in zip(doc_objs, doc_ids)]
        return (executor, pdfFutures)
    except Exception as e:
        print(e)
        chromaUtils.clearCollection([output_collection_name])
        print("copy collection aborted")

# _, futures = schedulePdfUpload(pdf_files)
# # Below is for testing in debug mode
# from tqdm import tqdm
# from concurrent.futures import ThreadPoolExecutor, as_completed
# with tqdm(total=len(futures)) as pbar:
#     for future in as_completed(futures):
#         result = future.result()
#         pbar.update(1)
