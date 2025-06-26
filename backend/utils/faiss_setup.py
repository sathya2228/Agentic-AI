from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def load_faiss_index():
    embedding = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )
    loader = TextLoader("C:/Users/HP/Downloads/AgenticAI/AgenticAI/backend/textbook.txt", encoding="utf-8")
    docs = loader.load()
    db = FAISS.from_documents(docs, embedding)
    return db.as_retriever()
