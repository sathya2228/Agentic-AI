from agents.rag_agent import rag_response

query = "What is an acid?"
response = rag_response(query)
print("AI Answer:\n", response)
