# backend/utils/faiss_setup.py

import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
INDEX_DIR = "D:\Sathya\June\26-6-2025\Agentic-AI\backend\vectorstore\faiss_index"
PDF_PATH = "D:\Sathya\June\26-6-2025\Agentic-AI\backend\documents\knowledge.pdf"

def build_faiss_index():
    # ✅ Load PDF
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    # ✅ Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    # ✅ Embed with Gemini
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )

    # ✅ Store in FAISS
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_DIR)
    print("✅ FAISS index built and saved.")

def load_faiss_index():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )
    return FAISS.load_local(INDEX_DIR, embeddings).as_retriever()
