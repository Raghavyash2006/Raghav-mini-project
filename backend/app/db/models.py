from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class LocalizationRequest(SQLModel, table=True):
    """
    Stores localization history with full context.
    
    Attributes:
        id: Unique request identifier
        original_text: Input text from user
        source_language: Detected language code (e.g., 'en', 'fr')
        target_language: Target language code
        localized_text: AI-generated localized output
        tone: Requested tone (formal, casual, marketing)
        sentiment: Detected sentiment (positive, negative, neutral)
        explanation: AI reasoning behind localization choices
        quality_score: Automatic quality rating (0-100)
        created_at: Timestamp
        updated_at: Last update timestamp
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    original_text: str = Field(index=True)
    source_language: str
    target_language: str
    localized_text: str
    tone: str
    sentiment: str
    explanation: Optional[str] = None
    quality_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    feedback_items: list["Feedback"] = Relationship(back_populates="request")


class Feedback(SQLModel, table=True):
    """
    User feedback on localization quality.
    
    Attributes:
        id: Unique feedback ID
        request_id: Foreign key to LocalizationRequest
        rating: User rating (1-5 stars)
        comment: Optional user comment
        helpful: Whether user found it helpful
        created_at: Timestamp
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="localizationrequest.id", index=True)
    rating: int = Field(ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    comment: Optional[str] = None
    helpful: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    request: Optional[LocalizationRequest] = Relationship(back_populates="feedback_items")
