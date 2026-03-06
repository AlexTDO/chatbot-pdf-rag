def ask_question(question, vector_store, k=3):
    # Buscar chunks mais relevantes
    relevant_docs = vector_store.similarity_search(question, k=k)
    
    # Criar prompt com contexto
    context = "\n".join([doc.page_content for doc in relevant_docs])
    prompt = f"""
    Baseado no seguinte contexto, responda a pergunta:
    
    Contexto: {context}
    
    Pergunta: {question}
    
    Resposta:
    """
    
    # Gerar resposta com LLM
    response = llm.generate(prompt)
    return response