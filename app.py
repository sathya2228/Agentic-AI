from flask import Flask, render_template, request, url_for
from backend.agents.langgraph_agent_flow import run_lesson_flow
from backend.quiz.mango_storage import save_quiz, get_quiz    # ✅ single correct import
from backend.quiz.email_sender import send_quiz_email
import markdown

app = Flask(__name__, template_folder='frontend', static_folder='static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send_quiz', methods=['POST'])
def send_quiz():
    subject = request.form.get('subject', '').strip()
    grade = request.form.get('grade', '').strip()
    topic = request.form.get('topic', '').strip()
    duration = request.form.get('duration', '').strip()
    email = request.form.get('email', '').strip()
    num_questions = int(request.form.get('num_questions', 5))

    result = run_lesson_flow(subject, grade, topic, duration, num_questions)

    if not result or not isinstance(result.get("quiz"), list) or len(result["quiz"]) == 0:
        return render_template("error.html", message="❌ Failed to generate quiz. Please try again.")

    quiz_id = save_quiz(result['quiz'], email)
    quiz_link = url_for('take_quiz', quiz_id=quiz_id, _external=True)
    send_quiz_email(email, quiz_link)

    for key in ['lesson', 'rag_facts', 'tone_adjusted', 'analysis']:
        if isinstance(result.get(key), str):
            result[key] = markdown.markdown(result[key])

    return render_template("result.html", result=result, link=quiz_link)


def enrich_question(q, user_ans):
    options = q.get('options', [])
    correct_letter = q.get('answer', '').strip().lower()
    correct_index = ord(correct_letter) - ord('a')
    q['correct_text'] = (
        f"{correct_letter.upper()}) {options[correct_index]}"
        if 0 <= correct_index < len(options)
        else "Invalid correct answer"
    )

    user_ans_clean = user_ans.strip().lower()
    if len(user_ans_clean) == 1 and 'a' <= user_ans_clean <= chr(ord('a') + len(options) - 1):
        user_index = ord(user_ans_clean) - ord('a')
        q['user_text'] = f"{user_ans_clean.upper()}) {options[user_index]}"
    elif user_ans_clean in [opt.lower() for opt in options]:
        user_index = [opt.lower() for opt in options].index(user_ans_clean)
        q['user_text'] = f"{chr(ord('A') + user_index)}) {options[user_index]}"
    else:
        q['user_text'] = f"{user_ans}) Invalid option"


@app.route('/take_quiz/<quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    quiz_data = get_quiz(quiz_id)
    if not quiz_data:
        return render_template("error.html", message="❌ Invalid or expired quiz link.")

    quiz = quiz_data["quiz"]

    # ✅ Case A: Already submitted
    if quiz_data.get("responses"):
        responses = quiz_data["responses"]
        for q, user_ans in zip(quiz, responses):
            enrich_question(q, user_ans)

        feedback_html = markdown.markdown(quiz_data.get("feedback_report", "No feedback available."))
        return render_template(
            "quiz_report.html",
            responses=responses,
            quiz=quiz,
            score=quiz_data.get("score", "N/A"),
            feedback=feedback_html
        )

    # 🟡 Case B: First-time submission
    if request.method == 'POST':
        responses = [request.form.get(f'q{i+1}', '').strip().lower() for i in range(len(quiz))]

        feedback_result = run_lesson_flow(
            subject="",
            grade="",
            topic="",
            duration="",
            num_questions=len(quiz),
            student_answers=responses,
            existing_quiz=quiz
        )

        for q, user_ans in zip(quiz, responses):
            enrich_question(q, user_ans)

        score = feedback_result.get("score", 0)
        feedback_text = feedback_result.get("feedback_report", "No feedback available.")

        # ✅ Save results to MongoDB
        save_quiz(
            quiz_questions=quiz,
            email=quiz_data["email"],
            responses=responses,
            score=score,
            feedback=feedback_text
        )

        feedback_html = markdown.markdown(feedback_text)
        return render_template(
            "quiz_report.html",
            responses=responses,
            quiz=quiz,
            score=score,
            feedback=feedback_html
        )

    # 🆓 Case C: Load quiz form
    return render_template("quiz_form.html", quiz=quiz, quiz_id=quiz_id)


if __name__ == '__main__':
    app.run(debug=True)
