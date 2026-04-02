"""
API Request/Response schemas using Pydantic.

Defines exact input/output contracts for all endpoints.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class LocalizeRequest(BaseModel):
    """
    POST /localize request schema.
    
    Attributes:
        text: The text content to localize (1-5000 characters)
        target_language: ISO 639-1 language code (e.g., 'es', 'fr', 'de')
        tone: Optional tone specification (formal, casual, marketing)
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text content to localize"
    )
    target_language: str = Field(
        ...,
        min_length=2,
        max_length=5,
        description="ISO 639-1 target language code (e.g., 'es', 'fr')"
    )
    tone: str = Field(
        default="neutral",
        description="Tone: formal, casual, marketing, or neutral"
    )
    
    @validator('tone')
    def validate_tone(cls, v):
        valid_tones = ['formal', 'casual', 'marketing', 'neutral']
        if v.lower() not in valid_tones:
            raise ValueError(f"Tone must be one of {valid_tones}")
        return v.lower()


class LocalizeResponse(BaseModel):
    """
    POST /localize response schema.
    
    Attributes:
        request_id: Unique identifier for this localization request
        original_text: The input text
        detected_language: ISO 639-1 code of detected source language
        localized_text: The localized output
        tone: The tone applied
        explanation: Reasoning behind localization choices
        quality_score: Automatic quality rating (0-100)
    """
    request_id: int = Field(..., description="Unique request ID for feedback/history")
    original_text: str = Field(..., description="Original input text")
    detected_language: str = Field(..., description="Auto-detected source language code")
    localized_text: str = Field(..., description="Localized output text")
    tone: str = Field(..., description="Tone that was applied")
    sentiment: str = Field(..., description="Detected sentiment (positive/negative/neutral)")
    explanation: str = Field(..., description="Explanation of localization decisions")
    quality_score: Optional[float] = Field(None, description="Quality rating 0-100")
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": 1,
                "original_text": "Hi there! Let's grab coffee.",
                "detected_language": "en",
                "localized_text": "¡Hola! Vamos a tomar un café.",
                "tone": "casual",
                "sentiment": "positive",
                "explanation": "Adapted greeting and coffee reference to Spanish casual context",
                "quality_score": 92.5
            }
        }


class FeedbackRequest(BaseModel):
    """
    POST /feedback request schema.
    
    Attributes:
        request_id: ID of the localization request being rated
        rating: User rating from 1 (poor) to 5 (excellent)
        comment: Optional detailed feedback
    """
    request_id: int = Field(..., gt=0, description="ID of localization request")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    comment: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional feedback comment"
    )


class FeedbackResponse(BaseModel):
    """
    POST /feedback response schema.
    
    Attributes:
        id: Feedback record ID
        request_id: Associated request ID
        rating: The submitted rating
        comment: The submitted comment
        helpful: Whether feedback was recorded successfully
    """
    id: int
    request_id: int
    rating: int
    comment: Optional[str] = None
    helpful: bool = Field(default=True, description="Whether feedback improved the system")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 5,
                "request_id": 1,
                "rating": 5,
                "comment": "Perfect! Very natural translation.",
                "helpful": True
            }
        }


class HistoryItem(BaseModel):
    """Single item in localization history."""
    request_id: int
    original_text: str
    detected_language: str
    target_language: str
    localized_text: str
    tone: str
    sentiment: str
    quality_score: Optional[float]
    created_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": 1,
                "original_text": "Hello",
                "detected_language": "en",
                "target_language": "es",
                "localized_text": "Hola",
                "tone": "casual",
                "sentiment": "neutral",
                "quality_score": 95.0,
                "created_at": "2024-03-15T10:30:00"
            }
        }


class HistoryResponse(BaseModel):
    """
    GET /history response schema.
    
    Returns paginated localization history.
    """
    items: List[HistoryItem]
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Records per page")
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "request_id": 1,
                        "original_text": "Hello",
                        "detected_language": "en",
                        "target_language": "es",
                        "localized_text": "Hola",
                        "tone": "casual",
                        "sentiment": "neutral",
                        "quality_score": 95.0,
                        "created_at": "2024-03-15T10:30:00"
                    }
                ],
                "total": 150,
                "page": 1,
                "page_size": 20
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response returned by all endpoints.
    
    Attributes:
        error: Error type/code
        message: Human-readable error message
        details: Optional additional details
    """
    error: str
    message: str
    details: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Invalid input parameters",
                "details": "target_language is required"
            }
        }

