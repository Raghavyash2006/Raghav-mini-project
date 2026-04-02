from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import desc
from app.db.models import LocalizationRequest, Feedback


def create_localization_request(session: Session, request: LocalizationRequest) -> LocalizationRequest:
    """
    Create and store a new localization request.
    
    Args:
        session: Database session
        request: LocalizationRequest model instance
        
    Returns:
        Created LocalizationRequest with ID
    """
    session.add(request)
    session.commit()
    session.refresh(request)
    return request


def get_localization_request(session: Session, request_id: int) -> Optional[LocalizationRequest]:
    """
    Retrieve a specific localization request by ID.
    
    Args:
        session: Database session
        request_id: Request ID to retrieve
        
    Returns:
        LocalizationRequest or None if not found
    """
    return session.get(LocalizationRequest, request_id)


def get_localization_history(
    session: Session,
    skip: int = 0,
    limit: int = 20,
    target_language: Optional[str] = None
) -> List[LocalizationRequest]:
    """
    Retrieve localization history with optional filtering.
    
    Args:
        session: Database session
        skip: Pagination offset
        limit: Max records to return
        target_language: Optional filter by target language
        
    Returns:
        List of LocalizationRequest records
    """
    query = select(LocalizationRequest).order_by(desc(LocalizationRequest.created_at))
    
    if target_language:
        query = query.where(LocalizationRequest.target_language == target_language)
    
    return session.exec(query.offset(skip).limit(limit)).all()


def create_feedback(session: Session, feedback: Feedback) -> Feedback:
    """
    Store user feedback for a localization result.
    
    Args:
        session: Database session
        feedback: Feedback model instance
        
    Returns:
        Created Feedback record with ID
    """
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


def get_feedback_for_request(session: Session, request_id: int) -> List[Feedback]:
    """
    Get all feedback for a specific localization request.
    
    Args:
        session: Database session
        request_id: Parent request ID
        
    Returns:
        List of Feedback records
    """
    return session.exec(
        select(Feedback).where(Feedback.request_id == request_id)
    ).all()


def get_average_rating(session: Session, request_id: int) -> Optional[float]:
    """
    Calculate average rating for a request.
    
    Args:
        session: Database session
        request_id: Parent request ID
        
    Returns:
        Average rating or None if no feedback
    """
    feedback_list = get_feedback_for_request(session, request_id)
    if not feedback_list:
        return None
    return sum(f.rating for f in feedback_list) / len(feedback_list)
