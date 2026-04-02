"""
FastAPI routers for localization endpoints.

Provides three main APIs:
- POST /localize: Generate localization for input text
- GET /history: Retrieve localization history
- POST /feedback: Submit user feedback
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from datetime import datetime

from app.api.v1 import schemas
from app.db import crud
from app.db.models import LocalizationRequest, Feedback
from app.db.session import get_session
from app.services import context_analyzer, localization_engine, input_processing
from app.core.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/v1", tags=["localization"])


@router.post(
    "/localize",
    response_model=schemas.LocalizeResponse,
    responses={
        400: {"model": schemas.ErrorResponse},
        500: {"model": schemas.ErrorResponse},
    }
)
def localize(
    payload: schemas.LocalizeRequest,
    session: Session = Depends(get_session)
):
    """
    Generate AI-powered localization for input text.
    
    This endpoint:
    1. Validates and cleans input text
    2. Detects source language and sentiment
    3. Calls generative AI to create localization
    4. Stores result in database
    5. Returns localized output with metadata
    
    Args:
        payload: LocalizeRequest containing text, target_language, and tone
        session: Database session
        
    Returns:
        LocalizeResponse with localized_text, detected_language, explanation, etc.
        
    Raises:
        HTTPException 400: Invalid input
        HTTPException 500: Localization generation failed
        
    Example:
        POST /v1/localize
        {
            "text": "Hello everyone!",
            "target_language": "es",
            "tone": "casual"
        }
        
        Response:
        {
            "request_id": 1,
            "original_text": "Hello everyone!",
            "detected_language": "en",
            "localized_text": "¡Hola a todos!",
            "tone": "casual",
            "sentiment": "positive",
            "explanation": "Casual Spanish greeting with enthusiasm",
            "quality_score": 94.5
        }
    """
    try:
        # Step 1: Clean and validate input
        cleaned_text = input_processing.clean_input(payload.text)
        
        # Step 2: Analyze context (language, sentiment)
        try:
            context = context_analyzer.analyze_context(cleaned_text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        source_language = context['language']
        sentiment = context['sentiment']
        characteristics = context.get('characteristics', {})
        
        logger.info(
            f"Processing localization: {source_language}→{payload.target_language}, "
            f"sentiment={sentiment}, tone={payload.tone}"
        )
        
        # Step 3: Call generative localization engine
        try:
            localization_result = localization_engine.generate_localization(
                text=cleaned_text,
                source_language=source_language,
                target_language=payload.target_language,
                tone=payload.tone,
                sentiment=sentiment,
                characteristics=characteristics,
            )
        except RuntimeError as e:
            logger.error(f"Localization engine failed: {e}")
            raise HTTPException(status_code=500, detail="Localization generation failed") from e
        except ValueError as e:
            logger.error(f"Invalid localization response: {e}")
            raise HTTPException(status_code=500, detail="Invalid AI response format") from e
        
        # Step 4: Store in database
        request_model = LocalizationRequest(
            original_text=payload.text,
            source_language=source_language,
            target_language=payload.target_language,
            localized_text=localization_result['localized_text'],
            tone=payload.tone,
            sentiment=sentiment,
            explanation=localization_result.get('explanation', ''),
            quality_score=localization_result.get('quality_score', None),
        )
        
        try:
            db_request = crud.create_localization_request(session, request_model)
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Failed to store result") from e
        
        # Step 5: Format and return response
        return schemas.LocalizeResponse(
            request_id=db_request.id,
            original_text=payload.text,
            detected_language=source_language,
            localized_text=localization_result['localized_text'],
            tone=payload.tone,
            sentiment=sentiment,
            explanation=localization_result.get('explanation', ''),
            quality_score=localization_result.get('quality_score'),
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.exception(f"Unexpected error in /localize: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get(
    "/history",
    response_model=schemas.HistoryResponse,
    responses={
        400: {"model": schemas.ErrorResponse},
    }
)
def get_history(
    target_language: str = Query(None, description="Filter by target language"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    session: Session = Depends(get_session)
):
    """
    Retrieve paginated localization history.
    
    Returns previous localization requests with their results.
    
    Args:
        target_language: Optional filter by target language code
        page: Page number (1-indexed)
        limit: Records per page (max 100)
        session: Database session
        
    Returns:
        HistoryResponse with paginated list of localizations
        
    Example:
        GET /v1/history?page=1&limit=20&target_language=es
        
        Returns:
        {
            "items": [...],
            "total": 150,
            "page": 1,
            "page_size": 20
        }
    """
    try:
        # Calculate pagination offset
        skip = (page - 1) * limit
        
        # Get total count (simplified: would need separate count query in production)
        all_results = crud.get_localization_history(
            session,
            skip=0,
            limit=999999,
            target_language=target_language
        )
        total = len(all_results)
        
        # Get paginated results
        results = crud.get_localization_history(
            session,
            skip=skip,
            limit=limit,
            target_language=target_language
        )
        
        # Convert to response items
        items = [
            schemas.HistoryItem(
                request_id=r.id,
                original_text=r.original_text,
                detected_language=r.source_language,
                target_language=r.target_language,
                localized_text=r.localized_text,
                tone=r.tone,
                sentiment=r.sentiment,
                quality_score=r.quality_score,
                created_at=r.created_at.isoformat(),
            )
            for r in results
        ]
        
        logger.info(f"Retrieved history: page={page}, limit={limit}, total={total}")
        
        return schemas.HistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=limit,
        )
        
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history") from e


@router.post(
    "/feedback",
    response_model=schemas.FeedbackResponse,
    responses={
        404: {"model": schemas.ErrorResponse},
        400: {"model": schemas.ErrorResponse},
    }
)
def submit_feedback(
    payload: schemas.FeedbackRequest,
    session: Session = Depends(get_session)
):
    """
    Submit user feedback for a localization result.
    
    Stores rating and comments for quality improvement.
    
    Args:
        payload: FeedbackRequest with request_id, rating, and optional comment
        session: Database session
        
    Returns:
        FeedbackResponse with feedback ID and confirmation
        
    Raises:
        HTTPException 404: Request ID not found
        HTTPException 400: Invalid feedback
        
    Example:
        POST /v1/feedback
        {
            "request_id": 1,
            "rating": 5,
            "comment": "Excellent localization!"
        }
        
        Response:
        {
            "id": 42,
            "request_id": 1,
            "rating": 5,
            "comment": "Excellent localization!",
            "helpful": true
        }
    """
    try:
        # Verify the localization request exists
        request_record = crud.get_localization_request(session, payload.request_id)
        if not request_record:
            raise HTTPException(
                status_code=404,
                detail=f"Localization request {payload.request_id} not found"
            )
        
        # Create feedback record
        feedback_model = Feedback(
            request_id=payload.request_id,
            rating=payload.rating,
            comment=payload.comment,
            helpful=True,
        )
        
        db_feedback = crud.create_feedback(session, feedback_model)
        
        # Log feedback for analytics
        logger.info(
            f"Feedback recorded: request_id={payload.request_id}, "
            f"rating={payload.rating}, comment_length={len(payload.comment or '')}"
        )
        
        return schemas.FeedbackResponse(
            id=db_feedback.id,
            request_id=db_feedback.request_id,
            rating=db_feedback.rating,
            comment=db_feedback.comment,
            helpful=True,
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail="Failed to store feedback") from e


@router.get("/health", tags=["health"])
def health_check():
    """
    Simple health check endpoint.
    
    Returns:
        dict with status
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
