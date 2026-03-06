def process_pdfs(pdf_files):
    text_chunks = []
    for pdf in pdf_files:
        # Extrair texto do PDF
        text = extract_text_from_pdf(pdf)
        # Dividir em chunks menores (ex: 500 caracteres com overlap)
        chunks = split_text(text, chunk_size=500, overlap=50)
        text_chunks.extend(chunks)
    return text_chunks