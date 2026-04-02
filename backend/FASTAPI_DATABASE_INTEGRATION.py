"""
FastAPI Integration Examples - Database Usage

Practical examples showing how to use the ORM models and database
connection in FastAPI route handlers and services.

Includes:
- Route handlers with database operations
- Error handling patterns
- Pagination and filtering
- Transaction management
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from app.database import get_db, init_db, startup_db, shutdown_db
from app.models import (
    User, LocalizationHistory, Feedback, CulturalAdaptation,
    Analytics, LocaleLanguage, ToneType
)


# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="AI Content Localization Platform",
    description="Enterprise-grade localization with AI and NLP",
    version="1.0.0"
)


# Database lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    await startup_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup database connections on shutdown"""
    from app.database import engine
    engine.dispose()


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/users/register")
def register_user(
    email: str,
    username: str,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        email: User email address
        username: Display name
        db: Database session (injected)
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if email exists
    existing_user = db.query(User).filter_by(email=email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Create new user
    user = User(
        user_id=str(uuid.uuid4()),
        email=email,
        username=username,
        api_key=str(uuid.uuid4()),
        subscription_tier="free",
        is_active=True
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return {
            "user_id": user.user_id,
            "email": user.email,
            "username": user.username,
            "api_key": user.api_key,
            "subscription_tier": user.subscription_tier
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}")
def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user profile by ID.
    
    Args:
        user_id: User identifier
        db: Database session
        
    Returns:
        User profile object
        
    Raises:
        HTTPException 404: If user not found
    """
    user = db.query(User).filter_by(user_id=user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "username": user.username,
        "subscription_tier": user.subscription_tier,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "total_requests": len(user.localizations)
    }


# ============================================================================
# LOCALIZATION ENDPOINTS
# ============================================================================

@app.post("/localizations")
def create_localization(
    user_id: str,
    source_text: str,
    target_language: str,
    tone: str,
    localized_text: str,
    quality_score: float,
    model_used: str = "gpt-4o-mini",
    db: Session = Depends(get_db)
):
    """
    Create a new localization record.
    
    Args:
        user_id: Owner of the request
        source_text: Original text
        target_language: Target language code (es, hi, fr, etc.)
        tone: Tone type (formal, casual, marketing, technical, neutral)
        localized_text: Generated localization
        quality_score: Quality metric 0-100
        model_used: Which model generated this
        db: Database session
        
    Returns:
        Created localization object
    """
    # Verify user exists
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create localization record
    localization = LocalizationHistory(
        request_id=str(uuid.uuid4()),
        user_id=user_id,
        source_text=source_text,
        source_language="en",
        target_language=target_language,
        tone=tone,
        localized_text=localized_text,
        quality_score=quality_score,
        character_count=len(source_text),
        word_count=len(source_text.split()),
        execution_time_ms=100,  # Would come from actual execution
        model_used=model_used,
        idioms_detected=0,
        idioms_replaced=0
    )
    
    try:
        db.add(localization)
        db.commit()
        db.refresh(localization)
        
        return {
            "request_id": localization.request_id,
            "localized_text": localization.localized_text,
            "quality_score": localization.quality_score,
            "created_at": localization.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/localizations/history/{user_id}")
def get_localization_history(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    target_language: Optional[str] = None,
    min_quality: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get user's localization history with pagination and filtering.
    
    Args:
        user_id: User identifier
        page: Page number (1-indexed)
        page_size: Items per page (1-100)
        target_language: Optional filter by language
        min_quality: Optional filter by minimum quality score
        db: Database session
        
    Returns:
        Paginated list of localizations
    """
    # Verify user
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query
    query = db.query(LocalizationHistory).filter_by(user_id=user_id)
    
    # Apply filters
    if target_language:
        query = query.filter_by(target_language=target_language)
    if min_quality is not None:
        query = query.filter(LocalizationHistory.quality_score >= min_quality)
    
    # Count total
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    items = query.order_by(
        LocalizationHistory.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    return {
        "items": [
            {
                "request_id": item.request_id,
                "source_text": item.source_text,
                "localized_text": item.localized_text,
                "target_language": item.target_language,
                "tone": item.tone,
                "quality_score": item.quality_score,
                "created_at": item.created_at
            }
            for item in items
        ],
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
            "has_next": page < (total + page_size - 1) // page_size
        }
    }


@app.get("/localizations/{request_id}")
def get_localization(
    request_id: str,
    db: Session = Depends(get_db)
):
    """
    Get specific localization with all details.
    
    Args:
        request_id: Request identifier
        db: Database session
        
    Returns:
        Localization with cultural adaptations and feedback
    """
    localization = db.query(LocalizationHistory).filter_by(
        request_id=request_id
    ).first()
    
    if not localization:
        raise HTTPException(status_code=404, detail="Localization not found")
    
    return {
        "request_id": localization.request_id,
        "source_text": localization.source_text,
        "localized_text": localization.localized_text,
        "quality_score": localization.quality_score,
        "cultural_adaptations": [
            {
                "source_idiom": ca.source_idiom,
                "target_idiom": ca.target_idiom,
                "category": ca.category,
                "equivalence_type": ca.equivalence_type,
                "semantic_preservation": ca.semantic_preservation
            }
            for ca in localization.cultural_adaptations
        ] if localization.cultural_adaptations else [],
        "feedback": {
            "rating": localization.feedback.rating,
            "comment": localization.feedback.comment,
            "aspects": localization.feedback.aspects
        } if localization.feedback else None,
        "created_at": localization.created_at
    }


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@app.post("/feedback")
def create_feedback(
    request_id: str,
    user_id: str,
    rating: int,
    comment: Optional[str] = None,
    aspects: Optional[dict] = None,
    helpful: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Submit feedback on a localization.
    
    Args:
        request_id: Localization to review
        user_id: User submitting feedback
        rating: Star rating 1-5
        comment: Optional feedback text
        aspects: JSON with detailed ratings
            {
                "accuracy": 1-5,
                "tone_preserved": boolean,
                "cultural_fit": 1-5,
                "readability": 1-5,
                "idiom_handling": 1-5
            }
        helpful: Was it helpful?
        db: Database session
        
    Returns:
        Created feedback object
    """
    # Validate rating
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    
    # Verify localization exists
    localization = db.query(LocalizationHistory).filter_by(
        request_id=request_id
    ).first()
    if not localization:
        raise HTTPException(status_code=404, detail="Localization not found")
    
    # Check if feedback already exists
    existing = db.query(Feedback).filter_by(request_id=request_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Feedback already submitted")
    
    # Create feedback
    feedback = Feedback(
        feedback_id=str(uuid.uuid4()),
        request_id=request_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
        aspects=aspects,
        helpful=helpful
    )
    
    try:
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return {
            "feedback_id": feedback.feedback_id,
            "rating": feedback.rating,
            "created_at": feedback.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/user/{user_id}")
def get_user_feedback(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all feedback submitted by a user"""
    feedbacks = db.query(Feedback).filter_by(user_id=user_id).all()
    
    return {
        "average_rating": sum(f.rating for f in feedbacks) / len(feedbacks) if feedbacks else 0,
        "feedback_count": len(feedbacks),
        "feedback": [
            {
                "feedback_id": f.feedback_id,
                "request_id": f.request_id,
                "rating": f.rating,
                "created_at": f.created_at
            }
            for f in feedbacks
        ]
    }


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/analytics/user/{user_id}")
def get_user_analytics(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get user analytics summary.
    
    Args:
        user_id: User identifier
        days: Number of days to look back
        db: Database session
        
    Returns:
        Analytics summary
    """
    # Verify user
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get localizations
    since = datetime.utcnow() - timedelta(days=days)
    localizations = db.query(LocalizationHistory).filter(
        LocalizationHistory.user_id == user_id,
        LocalizationHistory.created_at >= since
    ).all()
    
    if not localizations:
        return {
            "total_requests": 0,
            "total_characters": 0,
            "avg_quality": 0,
            "languages_used": [],
            "avg_rating": 0
        }
    
    # Calculate metrics
    total_requests = len(localizations)
    total_characters = sum(loc.character_count for loc in localizations)
    avg_quality = sum(loc.quality_score for loc in localizations) / total_requests
    
    # Languages used
    languages_used = list(set(loc.target_language for loc in localizations))
    
    # Feedback metrics
    feedbacks = [loc.feedback for loc in localizations if loc.feedback]
    avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks) if feedbacks else 0
    
    return {
        "time_period_days": days,
        "total_requests": total_requests,
        "total_characters": total_characters,
        "avg_quality_score": round(avg_quality, 2),
        "languages_used": languages_used,
        "avg_rating": round(avg_rating, 2),
        "feedback_count": len(feedbacks)
    }


@app.get("/analytics/platform")
def get_platform_analytics(
    db: Session = Depends(get_db)
):
    """
    Get platform-wide analytics.
    
    Returns:
        Platform statistics
    """
    # Total metrics
    total_requests = db.query(func.count(LocalizationHistory.request_id)).scalar() or 0
    total_characters = db.query(func.sum(LocalizationHistory.character_count)).scalar() or 0
    avg_quality = db.query(func.avg(LocalizationHistory.quality_score)).scalar() or 0
    
    # Language distribution
    lang_stats = db.query(
        LocalizationHistory.target_language,
        func.count(LocalizationHistory.request_id).label("count"),
        func.avg(LocalizationHistory.quality_score).label("avg_quality")
    ).group_by(LocalizationHistory.target_language).all()
    
    # User count
    total_users = db.query(func.count(User.user_id)).scalar() or 0
    
    # Feedback metrics
    total_feedback = db.query(func.count(Feedback.feedback_id)).scalar() or 0
    avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 0
    
    return {
        "total_requests": total_requests,
        "total_characters": total_characters,
        "avg_quality_score": round(float(avg_quality), 2),
        "total_users": total_users,
        "total_feedback": total_feedback,
        "avg_user_rating": round(float(avg_rating), 2),
        "language_distribution": [
            {
                "language": stat.target_language,
                "requests": stat.count,
                "avg_quality": round(float(stat.avg_quality), 2) if stat.avg_quality else 0
            }
            for stat in lang_stats
        ]
    }


@app.get("/analytics/languages")
def get_language_analytics(
    db: Session = Depends(get_db)
):
    """
    Get detailed language-specific metrics.
    
    Returns:
        Analytics by language
    """
    stats = db.query(
        LocalizationHistory.target_language,
        func.count(LocalizationHistory.request_id).label("request_count"),
        func.avg(LocalizationHistory.quality_score).label("avg_quality"),
        func.sum(LocalizationHistory.character_count).label("total_chars"),
        func.count(func.distinct(LocalizationHistory.user_id)).label("unique_users")
    ).group_by(LocalizationHistory.target_language).order_by(
        func.count(LocalizationHistory.request_id).desc()
    ).all()
    
    return {
        "language_statistics": [
            {
                "language": s.target_language,
                "requests": s.request_count,
                "avg_quality": round(float(s.avg_quality), 2),
                "total_characters": s.total_chars,
                "unique_users": s.unique_users
            }
            for s in stats
        ]
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check with database verification.
    
    Returns:
        Health status
    """
    try:
        # Verify database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
