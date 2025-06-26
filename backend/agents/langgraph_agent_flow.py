from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from typing import TypedDict
from backend.agents.rag_agent import rag_response
import re
import json

# ✅ Gemini API Setup
GEMINI_API_KEY = "AIzaSyAOuG6ZCzHe8BwNwJIk_KH5VCRGIvbhYWU"  # Replace with a valid API key
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY
)

# ✅ Define the State type
class LessonState(TypedDict):
    subject: str
    grade: str
    topic: str
    duration: str
    num_questions: int
    lesson: str
    quiz: list
    tone_adjusted: str
    analysis: str
    rag_facts: str
    student_answers: list
    score: int
    feedback_report: str

# ✅ Agent 1: Generate Lesson Plan
def content_generator_agent(state: LessonState) -> LessonState:
    if state.get("student_answers"):
        print("ℹ️ Skipping content generation (feedback mode).")
        return state

    query = f"Provide factual information about the topic '{state['topic']}' for grade {state['grade']} {state['subject']}."
    facts = rag_response(query)

    prompt = f"""
Use the following verified facts to create a structured lesson plan.

Facts:
{facts}

Create a lesson for:
- Subject: {state['subject']}
- Grade: {state['grade']}
- Topic: {state['topic']}
- Duration: {state['duration']}

Include objectives, core ideas, activities, examples, and a summary.
"""
    response = llm.invoke(prompt)
    state["lesson"] = response.content
    state["rag_facts"] = facts
    return state

# ✅ Agent 2: Quiz Generator
def quiz_generator_agent(state: LessonState) -> LessonState:
    if state.get("student_answers") or state.get("quiz"):
        print("ℹ️ Skipping quiz generation (feedback mode or pre-existing quiz).")
        return state

    if not state['lesson'].strip():
        raise ValueError("Lesson content is empty. Cannot generate quiz.")

    prompt = f"""
Based on this lesson content, create {state['num_questions']} multiple-choice quiz questions.

Format:
Question X: <question>
a) ...
b) ...
c) ...
d) ...
Answer: <correct option letter>

Lesson:
{state['lesson']}
"""
    response = llm.invoke(prompt)
    raw_quiz = response.content

    questions = []
    blocks = re.findall(
        r"(Question\s*\d+:.*?)(?=\nQuestion\s*\d+:|\Z)", raw_quiz.strip(), re.DOTALL
    )

    for block in blocks:
        lines = block.strip().split("\n")
        question_line = next((line for line in lines if line.lower().startswith("question")), "")
        options = [line.strip() for line in lines if re.match(r"^[a-dA-D]\)", line.strip())]
        answer_line = next((line for line in lines if "Answer" in line), "")
        match = re.search(r"([a-dA-D])", answer_line)
        correct_letter = match.group(1).lower() if match else "a"

        clean_options = [re.sub(r"^[a-dA-D]\)\s*", "", opt) for opt in options]

        if question_line and clean_options and len(clean_options) >= 4:
            questions.append({
                "text": question_line.strip(),
                "options": clean_options,
                "answer": correct_letter
            })

    if not questions:
        raise ValueError("Quiz parsing failed. No questions found.")

    state["quiz"] = questions
    return state

# ✅ Agent 3: Tone Adapter
def tone_adapter_agent(state: LessonState) -> LessonState:
    if state.get("student_answers"):
        print("ℹ️ Skipping tone adaptation (feedback mode).")
        return state

    prompt = f"Rewrite the following content for a Grade {state['grade']} student:\n\n{state['lesson']}"
    response = llm.invoke(prompt)
    state["tone_adjusted"] = response.content
    return state

# ✅ Agent 4: RAG Validation
def rag_agent(state: LessonState) -> LessonState:
    if state.get("student_answers"):
        print("ℹ️ Skipping RAG validation (feedback mode).")
        return state

    query = f"Verify this lesson content for factual accuracy:\n\n{state['lesson']}"
    result = rag_response(query)
    verified_info = result.get("result", "") if isinstance(result, dict) else result
    state["rag_facts"] = verified_info
    return state

# ✅ Agent 5: Feedback and Scoring (Updated)
def feedback_analysis_agent(state: LessonState) -> LessonState:
    student_answers = state.get("student_answers", [])

    if not state.get("quiz"):
        state["score"] = 0
        state["feedback_report"] = "⚠️ No quiz data available for scoring."
        return state

    if not isinstance(student_answers, list) or not any(student_answers):
        state["score"] = 0
        state["feedback_report"] = "⚠️ No student answers submitted."
        return state

    correct_answers = [q["answer"].strip().lower() for q in state["quiz"]]
    score = 0
    mistakes = []

    for i, (q, student_ans) in enumerate(zip(state["quiz"], student_answers)):
        student_clean = student_ans.strip().lower()
        correct_letter = correct_answers[i]

        options = q.get("options", [])
        matched_letter = None

        if len(student_clean) == 1 and student_clean in ['a', 'b', 'c', 'd']:
            matched_letter = student_clean
        elif student_clean in [opt.lower() for opt in options]:
            matched_letter = chr(ord('a') + [opt.lower() for opt in options].index(student_clean))

        if matched_letter == correct_letter:
            score += 1
        else:
            student_display = (
                f"{matched_letter.upper()}) {options[ord(matched_letter) - ord('a')]}"
                if matched_letter and ord(matched_letter) - ord('a') < len(options)
                else student_ans
            )
            mistakes.append({
                "question": q["text"],
                "correct": f"{correct_letter.upper()}) {options[ord(correct_letter) - ord('a')]}",
                "student": student_display
            })

    state["score"] = score

    feedback_prompt = f"""
The student attempted a quiz of {len(correct_answers)} questions and scored {score}.

Here are the mistakes:
{json.dumps(mistakes, indent=2)}

Write a short feedback report with strengths, areas for improvement, and suggestions to prepare better.
"""
    feedback = llm.invoke(feedback_prompt).content
    state["analysis"] = feedback
    state["feedback_report"] = feedback
    return state

# ✅ Build LangGraph
builder = StateGraph(LessonState)

builder.add_node("ContentGenerator", content_generator_agent)
builder.add_node("QuizGenerator", quiz_generator_agent)
builder.add_node("ToneAdapter", tone_adapter_agent)
builder.add_node("RAGAgent", rag_agent)
builder.add_node("AnalysisAgent", feedback_analysis_agent)

builder.set_entry_point("ContentGenerator")
builder.add_edge("ContentGenerator", "QuizGenerator")
builder.add_edge("QuizGenerator", "ToneAdapter")
builder.add_edge("ToneAdapter", "RAGAgent")
builder.add_edge("RAGAgent", "AnalysisAgent")
builder.add_edge("AnalysisAgent", END)

graph = builder.compile()

# ✅ Entry Function
def run_lesson_flow(subject: str, grade: str, topic: str, duration: str, num_questions: int,
                    student_answers: list = [], existing_quiz: list = []):
    initial_state = {
        "subject": subject,
        "grade": grade,
        "topic": topic,
        "duration": duration,
        "num_questions": num_questions,
        "lesson": "",
        "quiz": existing_quiz,
        "tone_adjusted": "",
        "analysis": "",
        "rag_facts": "",
        "student_answers": student_answers,
        "score": 0,
        "feedback_report": ""
    }
    return graph.invoke(initial_state)
