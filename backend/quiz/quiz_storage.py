import uuid

# In-memory quiz database
quiz_db = {}

def save_quiz(quiz_questions, email, responses=None, score=None, feedback=None):
    """
    Save a new quiz or update an existing one based on questions and email.

    Parameters:
    - quiz_questions (list): List of questions (each is a dict with 'text', 'options', 'answer')
    - email (str): Email of the user
    - responses (list or None): Student's answers
    - score (int or None): Quiz score
    - feedback (str or None): Feedback report

    Returns:
    - quiz_id (str): Unique quiz ID
    """

    # Check if quiz already exists (same questions + email)
    for quiz_id, data in quiz_db.items():
        if data.get("quiz") == quiz_questions and data.get("email") == email:
            # Update the existing quiz entry
            data["responses"] = responses or data.get("responses", [])
            data["score"] = score if score is not None else data.get("score")
            data["feedback_report"] = feedback if feedback is not None else data.get("feedback_report")
            return quiz_id

    # Create a new quiz entry
    quiz_id = str(uuid.uuid4())
    quiz_db[quiz_id] = {
        "email": email,
        "quiz": quiz_questions,
        "responses": responses or [],
        "score": score,
        "feedback_report": feedback
    }
    return quiz_id


def get_quiz(quiz_id):
    """
    Retrieve a quiz by its ID.

    Parameters:
    - quiz_id (str): Unique quiz ID

    Returns:
    - dict or None: Quiz data if found, else None
    """
    return quiz_db.get(quiz_id)
