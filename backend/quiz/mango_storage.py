from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb+srv://sathyasihub:jCWPhwGYF64FzGAR@cluster0.wu7hypd.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["student"]         # Database name
collection = db["Mark"]       # Collection name

def save_quiz(quiz_questions, email, responses=None, score=None, feedback=None):
    """
    Save quiz data to MongoDB.
    """
    quiz_data = {
        "email": email,
        "quiz": quiz_questions,
        "responses": responses or [],
        "score": score if score is not None else 0,
        "feedback_report": feedback or "",
    }
    result = collection.insert_one(quiz_data)
    print(f"✅ Quiz data saved with ID: {result.inserted_id}")
    return str(result.inserted_id)

def get_quiz(quiz_id):
    """
    Retrieve quiz data by MongoDB _id.
    """
    from bson import ObjectId
    try:
        return collection.find_one({"_id": ObjectId(quiz_id)})
    except Exception as e:
        print(f"❌ Failed to load quiz: {e}")
        return None
