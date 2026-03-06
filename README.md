# 📚 Chatbot Inteligente para PDFs - Assistente de TCC

## 🎯 Visão Geral
Este projeto implementa um chatbot interativo que responde perguntas baseado exclusivamente no conteúdo de arquivos PDF. Desenvolvido para auxiliar estudantes e pesquisadores na análise de múltiplos documentos científicos.

## 🏗️ Arquitetura
[Incluir diagrama do fluxo]

## 🚀 Como Executar
1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Coloque seus PDFs na pasta `inputs/`
4. Execute: `streamlit run app.py`

## 📊 Resultados
![Chatbot Demo](assets/print-app.png)
![Experimentos](assets/print-experimentos.png)

## 💡 Insights Obtidos
- A importância do "chunking" adequado para qualidade das respostas
- Como diferentes modelos de embedding afetam a precisão
- Trade-offs entre usar modelos locais vs APIs

## 🔮 Possibilidades Futuras
- Implementar cache de respostas frequentes
- Adicionar suporte a múltiplos idiomas
- Criar API REST para integração com outros sistemas