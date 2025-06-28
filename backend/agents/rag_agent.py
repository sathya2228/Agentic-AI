import os
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 🔐 Gemini API Key
GEMINI_API_KEY = "AIzaSyDNRLCtqbaiLXEzRr0QPwEq-PejPUtCa94"

# 📁 Paths
INDEX_DIR = "D:/Sathya/June/26-6-2025/Agentic-AI/backend/vectorstore/faiss_index"
PDF_PATH = "D:/Sathya/June/26-6-2025/Agentic-AI/backend/documents/knowledge.pdf"

# ✅ Load or build FAISS retriever
def load_or_build_vectorstore():
    embedding = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )

    faiss_index_file = os.path.join(INDEX_DIR, "index.faiss")

    if os.path.exists(faiss_index_file):
        return FAISS.load_local(
            INDEX_DIR,
            embeddings=embedding,
            allow_dangerous_deserialization=True
        )
    else:
        if os.path.exists(INDEX_DIR) and not os.path.isdir(INDEX_DIR):
            os.remove(INDEX_DIR)
        os.makedirs(INDEX_DIR, exist_ok=True)

        loader = PyPDFLoader(PDF_PATH)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(chunks, embedding)
        vectorstore.save_local(INDEX_DIR)
        return vectorstore

# ✅ Generate response using RAG
def rag_response(query: str, debug: bool = True):
    vectorstore = load_or_build_vectorstore()

    # Get top 5 relevant documents with scores
    try:
        scored_docs = vectorstore.similarity_search_with_score(query, k=5)
        score_threshold = 0.3
        filtered_docs = [doc for doc, score in scored_docs if score >= score_threshold]
    except Exception as e:
        return f"❌ Error retrieving documents: {str(e)}"

    if not filtered_docs:
        if debug:
            print("⚠️ No relevant documents found.\n")
        return "❌ No relevant information found in the knowledge base for your query."

    # Debugging Output
    if debug:
        print("\n🔍 Retrieved Documents Matching the Query:\n")
        for i, doc in enumerate(filtered_docs, 1):
            print(f"--- Document {i} ---")
            print("📄 Metadata:", doc.metadata)
            print("📘 Content:\n", doc.page_content[:500])
            print("––––––––––––––––––––––––––––––––––––––––––––––––––––\n")

    # Compile context
    context = "\n\n".join([doc.page_content for doc in filtered_docs])

    # Prompt
    prompt = f"""You are a helpful assistant. Use ONLY the context below to answer the question.
If the answer is not found in the context, reply: '❌ No relevant information found in the knowledge base.'

Context:
{context}

Question: {query}
Answer:"""

    # 🔗 LLM call
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY
    )

    response = llm.invoke(prompt)

    # ✅ Normalize response
    if isinstance(response, str):
        return response.strip()
    elif hasattr(response, "text") and callable(response.text):
        return response.text().strip()
    elif hasattr(response, "text"):
        return str(response.text).strip()
    else:
        return "⚠️ Unexpected response format from LLM."
