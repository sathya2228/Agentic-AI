def generate_feedback_report(quiz, responses):
    correct_count = 0
    total = len(quiz)
    detailed = []

    for i, q in enumerate(quiz):
        correct = q["answer"]
        user_ans = responses[i] if i < len(responses) else "No response"
        correct_flag = user_ans.strip() == correct.strip()
        if correct_flag:
            correct_count += 1
        detailed.append({
            "question": q["text"],
            "your_answer": user_ans,
            "correct_answer": correct,
            "status": "✅ Correct" if correct_flag else "❌ Incorrect"
        })

    score = f"{correct_count} / {total}"
    percentage = (correct_count / total) * 100

    feedback = {
        "score": score,
        "percentage": percentage,
        "remarks": "Excellent! 🎉" if percentage >= 80 else (
            "Good! Review your mistakes." if percentage >= 50 else "Needs Improvement."),
        "details": detailed
    }

    return feedback
