import chromaUtils
from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor
from langchain.docstore.document import Document

import sys, os
workingDirectory = os.getcwd()
preProcessingDirectory = os.path.join(workingDirectory, "data_preprocessing")
chromaDirectory = os.path.join(workingDirectory, "ChromaDB")
dirs = [workingDirectory, preProcessingDirectory, chromaDirectory]
for d in dirs:
    if d not in sys.path:
        sys.path.append(d)

from pdfMain import pdfMain
from ChromaDB import chrom

def uploadSmallChunk(collection, doc):
    return collection.add_documents(documents=[doc])
    
def uploadSingleDoc(collection, id, doc):
    return collection.add_documents(ids=[id], documents=[doc])

# reads in a list of pdf file paths, processes the pdfs, and schedules futures to upload them in front-end
def schedulePdfUpload(listOfPDFfilepaths, collectionName):
    sectionsByFile = []
    issues = []

    # iterate through each pdf file path and passes into pdfMain function that processes it to produce a list of sections
    for path in listOfPDFfilepaths:
        try:
            sectionsByFile.append((pdfMain(path),path))
        except Exception as e:
            issues.append((e, path))
            print(f"Skipped file: {path} when creating Collection")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1250,
        chunk_overlap  = 10,
        length_function = lambda x: len(x.split(" ")),
        add_start_index = True,
    ) #create text splitter

    sectionChunks = []
    for sections,fileName in sectionsByFile: #chunk the sections using the text splitter
        sections= list(filter(lambda x: len(x[0].split(" ")) > 100, sections))
        for section in sections:
            chunks = text_splitter.create_documents([section[0]], metadatas=[{'fileName':fileName.split("\\")[-1],'pageNum':f"{section[1][0]} to {section[1][1]}"}]*1)
            sectionChunks.extend(chunks)

    chromaUtils.createCollection(collectionName) #creates a new collection
    langchain_chroma_pdf = chromaUtils.getCollection(collectionName) #retrieves the newly created collection

    executor = ThreadPoolExecutor(max_workers=5) #instantiate an executor
    pdfFutures = [executor.submit(uploadSingleDoc, langchain_chroma_pdf, str(id), doc) for doc, id in zip(sectionChunks, range(len(sectionChunks)))] #schedule all the upload tasks
    
    return (issues, executor, pdfFutures) #return a list of pdf file names for the pdfs with issues, the executor used to schedule and run the upload tasks and the list of pdf upload futures that can be iterated through in the front-end

# copies the relevant file chunks generated from pdf filtering into a new collection
def copyCollection(input_collection_name, output_collection_name, rel_file_names):
    input_collection = chromaUtils.getCollection(input_collection_name)
    # retrieves the relevant file chunks
    docs_dict=input_collection.get(
        where={"fileName": {"$in": rel_file_names}},
        include=['metadatas', 'documents']
    )
    try:
        # create the output collection
        chromaUtils.createCollection(output_collection_name)
        output_collection = chromaUtils.getCollection(output_collection_name)
        doc_ids, doc_objs= [], []
        #schedule chunk uploads
        for i in range(len(docs_dict['ids'])):
            doc_str = docs_dict['documents'][i]
            doc_metadata = docs_dict['metadatas'][i]
            doc_ids.append(docs_dict['ids'][i])
            doc_objs.append(Document(page_content=doc_str,metadata=doc_metadata))
        
        executor = ThreadPoolExecutor(max_workers=5)
        pdfFutures = [executor.submit(uploadSingleDoc, output_collection, id, doc) for doc, id in zip(doc_objs, doc_ids)]
        return (executor, pdfFutures)
    except Exception as e: # abort the process if error
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
