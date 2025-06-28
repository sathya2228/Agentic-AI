# Agentic AI Lesson & Quiz Platform

An intelligent educational platform that dynamically generates lesson plans, quizzes, and personalized feedback for students.  
Built with Python (Flask),  LangGraph,  Gemini Generative AI, and  MongoDB.  
Includes automatic email delivery, feedback analysis, and factual validation using RAG (Retrieval-Augmented Generation).

---

##  Features

-  **Dynamic Lesson Generation**: Create custom lesson plans by subject, grade, topic, and duration.
-  **Personalized Quizzes**: Auto-generate quizzes tailored to the lesson.
-  **Feedback & Scoring**: Evaluate student answers, compute scores, and provide improvement suggestions.
-  **Email Delivery**: Send quiz links directly to student emails.
-  **RAG Validation**: Ensure factual accuracy by cross-checking with your knowledge base.
-  **Agentic AI Flow**: Modular LangGraph pipeline: content, quiz, tone adaptation, RAG, analysis.
-  **MongoDB Storage**: Store student quiz results, answers, emails, and scores.

---

##  Tech Stack

| Layer           | Technology                                                   |
|-----------------|--------------------------------------------------------------|
| Backend         | Python, Flask                                                |
|Framework        | LangGraph, LangChain                                         |
| LLM             | Google Gemini API (Generative + Embeddings)                  |
| RAG             | FAISS vector store,embedding-001                             |
| Database        | MongoDB Atlas                                                |
| Frontend        | HTML, CSS                                                    |


---

##  Setup Instructions

```bash
# Clone the repository
git clone https://github.com/sathya2228/agentic-ai.git
cd agentic-ai

# (Recommended) Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables or configure your Gemini API key in:
# backend/agents/langgraph_agent_flow.py and backend/agents/rag_agent.py
# (Replace GEMINI_API_KEY)

# Start the Flask app
python app.py

