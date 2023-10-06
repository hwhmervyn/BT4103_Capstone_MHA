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