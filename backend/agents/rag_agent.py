import os
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.utils.faiss_setup import load_faiss_index
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def rag_response(query):
    retriever = load_faiss_index()
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY
    )
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    result = qa_chain.invoke({"query": query})
    return result
