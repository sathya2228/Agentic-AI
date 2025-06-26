from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key="AIzaSyAOuG6ZCzHe8BwNwJIk_KH5VCRGIvbhYWU"
)

def generate_report(quiz, answers):
    prompt = f"""
    Here is a student's quiz and their responses.

    Quiz:
    {quiz}

    Student's Answers:
    {answers}

    Please analyze and give:
    - Score out of 5
    - Strengths and weaknesses
    - Learning suggestions
    """
    return llm.invoke(prompt).content
