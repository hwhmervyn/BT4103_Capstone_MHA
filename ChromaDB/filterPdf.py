from langchain.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from client import persistent_client, embeddings

query ="cultural adaptations of pyschological first aid in various countries"

def uploadSmallChunk(collection, doc):
    return collection.add_documents(documents=[doc])
    

def smallChunkCollection():
    langchain_chroma_pdf = Chroma(
        client=persistent_client,
        collection_name="pdf",
        embedding_function=embeddings,
    )

    try:
        persistent_client.delete_collection(name="pdf_child")
    except:
        print('no pdf collection')
    
    persistent_client.get_or_create_collection(name="pdf_child", embedding_function=embeddings)


    smaller_chunk_pdf = Chroma(
        client=persistent_client,
        collection_name="pdf_child",
        embedding_function=embeddings,
    )



    child_splitter = RecursiveCharacterTextSplitter(chunk_size=250,chunk_overlap=10)

    large_docs = langchain_chroma_pdf.get()

    # ['ids', 'embeddings', 'metadatas', 'documents']
    # print(large_docs['documents'][0])


    small_chunks = []
    for large_doc_index in range(0,len(large_docs['ids'])):
        chunks = child_splitter.create_documents([large_docs['documents'][large_doc_index]], metadatas=[{'fileName':large_docs['metadatas'][large_doc_index]['fileName'],'parentID':large_docs['ids'][large_doc_index]}] * 1)
        small_chunks.extend(chunks)


    for i in range(0,len(small_chunks)):
        print(f"Small Chunk: {i}")
        smaller_chunk_pdf.add_documents(documents=[small_chunks[i]])

    ''' 
    executor = ThreadPoolExecutor(max_workers=5)
    pdfFutures = [executor.submit(uploadSmallChunk, smaller_chunk_pdf, doc) for doc in small_chunks]
    
    return (executor, pdfFutures)
    '''

def filter_relevant_pdfs(query):    
    langchain_chroma_pdf = Chroma(
        client=persistent_client,
        collection_name="pdf",
        embedding_function=embeddings,
    )
    smaller_chunk_pdf = Chroma(
        client=persistent_client,
        collection_name="pdf_child",
        embedding_function=embeddings,
    )
    small_len = persistent_client.get_or_create_collection(name="pdf_child", embedding_function=embeddings).count()
    filtered_docs = smaller_chunk_pdf.similarity_search_with_score(query,small_len)

    threshold = 1
    filtered_docs = list(filter(lambda x: x[1] < threshold, filtered_docs))

    print(f"Child Chunks Num: {len(filtered_docs)}")

    papers = []
    parentIDs = []
    for doc in filtered_docs:
        papers.append(doc[0].metadata['fileName'])
        parentIDs.append(doc[0].metadata['parentID'])
    

    filtered_docs.sort(key = lambda x: x[1] )
    papers = list(dict.fromkeys(papers))
    parentIDs = list(dict.fromkeys(parentIDs))



    relevant_chunks = langchain_chroma_pdf.get(ids=parentIDs)
    print(f"Parent Chunks Num: {len(relevant_chunks['ids'])}")

    try:
        persistent_client.delete_collection(name="pdf_relevant")
    except:
        print('no pdf collection')


    relevant_chunks_collection = persistent_client.get_or_create_collection(name="pdf_relevant")
    relevant_chunks_collection.add(ids = relevant_chunks['ids'],
                                metadatas = relevant_chunks['metadatas'],
                                documents = relevant_chunks['documents'],
                                embeddings = relevant_chunks['embeddings'])


    return papers




# Query from chromaDB
smallChunkCollection()
relevant_papers = filter_relevant_pdfs(query)

relevant_chunks_collection = persistent_client.get_collection(name="pdf_relevant")
print(relevant_chunks_collection.get(
    where={"fileName": "Psychological First Aid_ Objectives, Practicing, Vulnerable Groups and Ethical Rules to Follow.pdf"}
))
 
print("Done")