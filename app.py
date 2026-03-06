import streamlit as st
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import ollama
import os
import tempfile
import time
from datetime import datetime
import hashlib

# Configuração da página
st.set_page_config(
    page_title="📚 Chatbot PDF com Ollama",
    page_icon="🤖",
    layout="wide"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .stChat {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
    }
    .assistant-message {
        background-color: #28a745;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
    }
    .sidebar-info {
        padding: 10px;
        background-color: #e9ecef;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização das variáveis de sessão
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None

if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()

if 'config' not in st.session_state:
    st.session_state.config = {
        'chunk_size': 512,                    # ✅ Otimizado: 83 chunks em média
        'chunk_overlap': 100,                  # ✅ Otimizado: 20% de overlap
        'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',  # ✅ Otimizado: 0.199s, dim 384
        'ollama_model': 'mistral',              # ✅ Otimizado: 2.25s médio, melhor português
        'k_retrieval': 5,                       # ✅ Otimizado: Mais rápido e mais contexto
        'temperature': 0.7
    }

# Título principal
st.title("🤖 Chatbot Inteligente para PDFs")
st.markdown("---")

# ===== FUNÇÕES DEFINIDAS ANTES DE SEREM USADAS =====

def process_pdfs(uploaded_files):
    """Processa os PDFs enviados e cria o vector store"""
    all_texts = []
    
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.processed_files:
            # Salvar temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                # Extrair texto
                with open(tmp_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                
                # Dividir em chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=st.session_state.config['chunk_size'],
                    chunk_overlap=st.session_state.config['chunk_overlap'],
                    separators=["\n\n", "\n", ".", " ", ""]
                )
                chunks = text_splitter.split_text(text)
                all_texts.extend(chunks)
                
                st.session_state.processed_files.add(uploaded_file.name)
                st.success(f"✅ {uploaded_file.name} processado!")
                
            except Exception as e:
                st.error(f"❌ Erro ao processar {uploaded_file.name}: {str(e)}")
            finally:
                # Limpar arquivo temporário
                os.unlink(tmp_path)
    
    if all_texts:
        # Criar embeddings e vector store
        with st.spinner("Criando embeddings..."):
            embeddings = HuggingFaceEmbeddings(
                model_name=st.session_state.config['embedding_model']
            )
            
            # Criar ID único para esta sessão
            session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
            
            st.session_state.vectorstore = Chroma.from_texts(
                texts=all_texts,
                embedding=embeddings,
                persist_directory=f"./chroma_{session_id}"
            )
        
        st.success(f"🎉 Total de {len(all_texts)} chunks processados!")

def generate_response(prompt, context_docs):
    """Gera resposta usando Ollama baseada no contexto"""
    
    # Preparar contexto
    context = "\n\n".join(context_docs)
    
    # Criar prompt estruturado - Otimizado para o mistral
    system_prompt = """Você é um assistente especializado em responder perguntas baseado exclusivamente no contexto fornecido.
Use apenas as informações do contexto para responder. Se a informação não estiver no contexto, diga que não encontrou.
Seja conciso, direto e responda SEMPRE em português."""
    
    full_prompt = f"""{system_prompt}

Contexto:
{context}

Pergunta: {prompt}

Resposta (em português):"""
    
    try:
        # Chamar Ollama
        response = ollama.chat(
            model=st.session_state.config['ollama_model'],
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': full_prompt}
            ],
            options={
                'temperature': st.session_state.config['temperature']
            }
        )
        
        return response['message']['content']
    
    except Exception as e:
        return f"❌ Erro ao gerar resposta: {str(e)}"

# ===== SIDEBAR - CONFIGURAÇÕES =====
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Mostrar badge de configurações otimizadas
    st.markdown("""
    <div style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
        ⚡ Configurações otimizadas via experimentos!
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📄 Modelos", expanded=True):
        # Modelo Ollama
        available_models = ["llama2", "mistral", "gemma:2b", "phi", "neural-chat"]
        st.session_state.config['ollama_model'] = st.selectbox(
            "Modelo Ollama:",
            available_models,
            index=1  # Índice 1 = mistral (padrão otimizado)
        )
        
        # Modelo de Embedding
        embedding_options = [
            'sentence-transformers/all-MiniLM-L6-v2',
            'sentence-transformers/all-mpnet-base-v2',
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        ]
        st.session_state.config['embedding_model'] = st.selectbox(
            "Modelo Embedding:",
            embedding_options,
            index=0  # Índice 0 = all-MiniLM-L6-v2 (padrão otimizado)
        )
    
    with st.expander("🔧 Parâmetros"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.config['chunk_size'] = st.slider(
                "Tamanho do chunk:",
                min_value=256,
                max_value=2048,
                value=st.session_state.config['chunk_size'],
                step=128
            )
            st.session_state.config['k_retrieval'] = st.slider(
                "K (documentos):",
                min_value=1,
                max_value=10,
                value=st.session_state.config['k_retrieval']
            )
        with col2:
            st.session_state.config['chunk_overlap'] = st.slider(
                "Overlap:",
                min_value=0,
                max_value=500,
                value=st.session_state.config['chunk_overlap'],
                step=50
            )
            st.session_state.config['temperature'] = st.slider(
                "Temperatura:",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.config['temperature'],
                step=0.1
            )
    
    st.markdown("---")
    
    # Upload de PDFs
    st.header("📁 Upload de PDFs")
    uploaded_files = st.file_uploader(
        "Escolha seus PDFs:",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("🔄 Processar PDFs", type="primary"):
            with st.spinner("Processando documentos..."):
                process_pdfs(uploaded_files)
    
    st.markdown("---")
    
    # Estatísticas
    st.header("📊 Estatísticas")
    if st.session_state.vectorstore:
        st.info(f"📄 Documentos processados: {len(st.session_state.processed_files)}")
        st.info(f"💬 Mensagens na conversa: {len(st.session_state.messages)}")
        
        # Mostrar configuração atual
        with st.expander("⚙️ Configuração atual"):
            st.json(st.session_state.config)
    
    # Botão limpar chat
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

# ===== ÁREA PRINCIPAL - CHAT =====
st.header("💬 Chat com seus Documentos")

# Exibir mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Mostrar fontes se disponíveis (apenas para assistente)
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📚 Ver fontes"):
                for i, source in enumerate(message["sources"], 1):
                    st.text(f"Fonte {i}: {source[:200]}...")

# Input do usuário
if prompt := st.chat_input("Digite sua pergunta sobre os documentos..."):
    # Adicionar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Verificar se há documentos processados
    if st.session_state.vectorstore is None:
        with st.chat_message("assistant"):
            st.error("⚠️ Por favor, faça upload de alguns PDFs primeiro!")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "⚠️ Por favor, faça upload de alguns PDFs primeiro!"
            })
    else:
        # Buscar documentos relevantes
        with st.spinner("🔍 Buscando informações relevantes..."):
            relevant_docs = st.session_state.vectorstore.similarity_search(
                prompt, 
                k=st.session_state.config['k_retrieval']
            )
            context_docs = [doc.page_content for doc in relevant_docs]
        
        # Gerar resposta
        with st.spinner("🤔 Pensando..."):
            start_time = time.time()
            response = generate_response(prompt, context_docs)
            elapsed_time = time.time() - start_time
        
        # Exibir resposta
        with st.chat_message("assistant"):
            st.markdown(response)
            
            # Mostrar tempo de resposta
            st.caption(f"⏱️ Resposta gerada em {elapsed_time:.2f} segundos")
            
            # Mostrar fontes
            with st.expander("📚 Ver trechos utilizados"):
                for i, doc in enumerate(context_docs, 1):
                    st.text_area(f"Fonte {i}", doc, height=100)
        
        # Salvar no histórico
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": context_docs
        })

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 10px;'>
    Desenvolvido com ❤️ usando Streamlit, LangChain e Ollama<br>
    <small>Configurações otimizadas via experimentos: chunk_size=512, k=5, modelo=mistral</small>
</div>
""", unsafe_allow_html=True)