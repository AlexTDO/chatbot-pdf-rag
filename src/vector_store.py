def create_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = Chroma.from_texts(
        texts=chunks, 
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    return vector_store