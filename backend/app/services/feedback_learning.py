from app.db.models import Feedback


def summarize_feedback(rating: int, comment: str):
    # In a real production loop, this would train models.
    return {
        "rating": rating,
        "comment": comment,
        "improvement_suggestion": "Collect more detailed comments and generate prompt tuning examples.",
    }


def process_feedback(feedback: Feedback):
    return summarize_feedback(feedback.rating, feedback.comment or "")
