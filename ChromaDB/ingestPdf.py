import chromaUtils
from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor

import sys, os
workingDirectory = os.getcwd()
preProcessingDirectory = os.path.join(workingDirectory, "data_preprocessing")
sys.path.append(workingDirectory)
sys.path.append(preProcessingDirectory)

from pdfMain import pdfMain

def uploadSmallChunk(collection, doc):
    return collection.add_documents(documents=[doc])
    
def uploadSingleDoc(collection, id, doc):
    return collection.add_documents(ids=[id], documents=[doc])

def schedulePdfUpload(listOfPDFfilepaths):
    chromaUtils.clearCollection(['pdf'])
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
            print(fileName.split("\\")[-1])
            chunks = text_splitter.create_documents([section[0]], metadatas=[{'fileName':fileName.split("\\")[-1],'pageNum':f"{section[1][0]} to {section[1][1]}"}]*1)
            sectionChunks.extend(chunks)

    chromaUtils.createCollection("pdf")
    langchain_chroma_pdf = chromaUtils.getCollection("pdf")

    executor = ThreadPoolExecutor(max_workers=5)
    pdfFutures = [executor.submit(uploadSingleDoc, langchain_chroma_pdf, str(id), doc) for doc, id in zip(sectionChunks, range(len(sectionChunks)))]
    
    return (issues, executor, pdfFutures)

# _, futures = schedulePdfUpload(pdf_files)
# # Below is for testing in debug mode
# from tqdm import tqdm
# from concurrent.futures import ThreadPoolExecutor, as_completed
# with tqdm(total=len(futures)) as pbar:
#     for future in as_completed(futures):
#         result = future.result()
#         pbar.update(1)