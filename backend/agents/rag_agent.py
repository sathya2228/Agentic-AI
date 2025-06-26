import os
import shutil
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 🔐 Gemini API Key
GEMINI_API_KEY = "AIzaSyAOuG6ZCzHe8BwNwJIk_KH5VCRGIvbhYWU"

# 📁 Paths
INDEX_DIR = "D:/Sathya/June/26-6-2025/Agentic-AI/backend/vectorstore/faiss_index"
PDF_PATH = "D:/Sathya/June/26-6-2025/Agentic-AI/backend/documents/knowledge.pdf"


# ✅ Load or build FAISS retriever
def load_or_build_retriever():
    embedding = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )

    faiss_index_file = os.path.join(INDEX_DIR, "index.faiss")

    # 🔄 If FAISS index exists, load it
    if os.path.exists(faiss_index_file):
        return FAISS.load_local(
            INDEX_DIR,
            embeddings=embedding,
            allow_dangerous_deserialization=True
        ).as_retriever()

    # 🧹 Cleanup if index folder exists but invalid
    if os.path.exists(INDEX_DIR) and not os.path.isdir(INDEX_DIR):
        os.remove(INDEX_DIR)
    os.makedirs(INDEX_DIR, exist_ok=True)

    # 📄 Load and split PDF
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # 🧠 Embed and store in FAISS
    vectorstore = FAISS.from_documents(chunks, embedding)
    vectorstore.save_local(INDEX_DIR)

    return vectorstore.as_retriever()


# ✅ Generate response and print retrieved data always
def rag_response(query: str):
    retriever = load_or_build_retriever()

    # ✅ Display retrieved documents in terminal (always)
    print("\n🔍 Retrieved Documents Matching the Query:\n")
    retrieved_docs = retriever.get_relevant_documents(query)
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"--- Document {i} ---")
        print("📄 Metadata:", doc.metadata)
        print("📘 Content:\n", doc.page_content[:500])  # Limit output for readability
        print("––––––––––––––––––––––––––––––––––––––––––––––––––––\n")

    # 🤖 LLM + QA Chain
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY
    )

    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa.invoke({"query": query})
