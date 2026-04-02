"""
SQLAlchemy ORM Models for AI Localization Platform

Database schema definition with comprehensive models:
- User: Platform users and authentication
- LocalizationHistory: Request history and results
- Feedback: User ratings and comments on translations
- Analytics: Aggregated metrics and usage statistics
- CulturalAdaptation: Tracked cultural replacement details

All models include:
- Proper relationships and foreign keys
- Indexing for query performance
- Validation constraints
- Timestamp tracking (created_at, updated_at)
- Comprehensive docstrings
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, 
    Boolean, ForeignKey, Enum, Index, UniqueConstraint,
    JSON, Numeric
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class LocaleLanguage(str, enum.Enum):
    """Supported target languages"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    HINDI = "hi"
    GERMAN = "de"
    PORTUGUESE = "pt"
    JAPANESE = "ja"
    CHINESE = "zh"
    ARABIC = "ar"
    RUSSIAN = "ru"
    KOREAN = "ko"
    ITALIAN = "it"


class ToneType(str, enum.Enum):
    """Supported tone variations"""
    FORMAL = "formal"
    CASUAL = "casual"
    MARKETING = "marketing"
    TECHNICAL = "technical"
    NEUTRAL = "neutral"


class SentimentType(str, enum.Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class IdiomCategoryType(str, enum.Enum):
    """Cultural idiom category"""
    METAPHOR = "metaphor"
    SIMILE = "simile"
    IDIOM = "idiom"
    COLLOQUIALISM = "colloquialism"
    PROVERB = "proverb"
    SLANG = "slang"
    CULTURAL_REFERENCE = "cultural_reference"


# ============================================================================
# USER MANAGEMENT
# ============================================================================

class User(Base):
    """
    User account model for authentication and profile management.
    
    Fields:
    - user_id: Unique identifier (UUID auto-generated)
    - email: User email (unique)
    - username: Display name (optional)
    - api_key: API key for programmatic access
    - subscription_tier: free, pro, enterprise
    - is_active: Account status
    - created_at: Account creation timestamp
    - updated_at: Last update timestamp
    
    Relationships:
    - localizations: List of all user's localization requests
    - feedbacks: Feedback records created by user
    """
    
    __tablename__ = "users"
    
    # Primary Key
    user_id = Column(String(36), primary_key=True, index=True)
    
    # User Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True, index=True)
    api_key = Column(String(255), unique=True, nullable=True, index=True)
    
    # Subscription & Status
    subscription_tier = Column(String(20), default="free", nullable=False)  # free, pro, enterprise
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    localizations = relationship(
        "LocalizationHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    feedbacks = relationship(
        "Feedback",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_api_key", "api_key"),
        Index("idx_user_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<User(user_id='{self.user_id}', email='{self.email}', tier='{self.subscription_tier}')>"


# ============================================================================
# LOCALIZATION HISTORY
# ============================================================================

class LocalizationHistory(Base):
    """
    Localization request history with full request/response data.
    
    Fields:
    - request_id: Unique request identifier
    - user_id: Foreign key to User
    - source_text: Original text (English)
    - target_language: Target language code
    - source_language: Source language (default: English)
    - tone: Selected tone for output
    - localized_text: Generated localization
    - explanation: Human-readable explanation of changes
    - detected_sentiment: Sentiment of source text
    - quality_score: Quality metric 0-100
    - character_count: Length of source text
    - execution_time_ms: Processing time in milliseconds
    - model_used: Which AI model was used (gpt-4o-mini, gemini-pro, etc.)
    - created_at: Request timestamp
    
    Relationships:
    - user: Reference to User
    - cultural_adaptations: List of idiom/metaphor replacements
    - feedback: Optional user feedback on this localization
    """
    
    __tablename__ = "localization_history"
    
    # Primary & Foreign Keys
    request_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Input Parameters
    source_text = Column(Text, nullable=False)
    source_language = Column(String(10), default="en", nullable=False)
    target_language = Column(String(10), nullable=False, index=True)
    tone = Column(String(20), nullable=False, index=True)
    
    # Output Data
    localized_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    
    # Analysis Metrics
    detected_sentiment = Column(String(20), nullable=True)
    quality_score = Column(Float, nullable=False, index=True)
    character_count = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    execution_time_ms = Column(Integer, nullable=False)
    
    # Model Information
    model_used = Column(String(50), nullable=False)
    
    # Cultural Adaptation Tracking
    idioms_detected = Column(Integer, default=0, nullable=False)
    idioms_replaced = Column(Integer, default=0, nullable=False)
    cultural_adaptations_applied = Column(JSON, nullable=True)  # Array of adaptations
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="localizations")
    cultural_adaptations = relationship(
        "CulturalAdaptation",
        back_populates="localization",
        cascade="all, delete-orphan",
        lazy="select"
    )
    feedback = relationship(
        "Feedback",
        back_populates="localization",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_localization_user_id", "user_id"),
        Index("idx_localization_target_lang", "target_language"),
        Index("idx_localization_tone", "tone"),
        Index("idx_localization_quality_score", "quality_score"),
        Index("idx_localization_created_at", "created_at"),
        Index("idx_localization_composite", "user_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<LocalizationHistory(request_id='{self.request_id}', target_lang='{self.target_language}', quality={self.quality_score})>"


# ============================================================================
# CULTURAL ADAPTATION DETAILS
# ============================================================================

class CulturalAdaptation(Base):
    """
    Detailed tracking of cultural replacements (idioms, metaphors, etc).
    
    Fields:
    - adaptation_id: Unique identifier
    - request_id: Foreign key to LocalizationHistory
    - source_idiom: Original idiom/phrase
    - target_idiom: Replacement in target language
    - category: Type of cultural element (idiom, metaphor, etc.)
    - equivalence_type: direct, partial, conceptual, none
    - semantic_preservation: 0-1 score of meaning preservation
    - explanation: Why this replacement was made
    - created_at: Tracking timestamp
    
    Relationships:
    - localization: Reference to parent LocalizationHistory
    """
    
    __tablename__ = "cultural_adaptations"
    
    # Primary & Foreign Keys
    adaptation_id = Column(String(36), primary_key=True, index=True)
    request_id = Column(String(36), ForeignKey("localization_history.request_id"), nullable=False, index=True)
    
    # Adaptation Details
    source_idiom = Column(String(255), nullable=False)
    target_idiom = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    equivalence_type = Column(String(20), nullable=False)  # direct, partial, conceptual, none
    
    # Quality Metrics
    semantic_preservation = Column(Float, nullable=False)  # 0-1
    confidence_score = Column(Float, nullable=False)
    
    # Documentation
    explanation = Column(Text, nullable=True)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    localization = relationship("LocalizationHistory", back_populates="cultural_adaptations")
    
    # Indexes
    __table_args__ = (
        Index("idx_adaptation_request_id", "request_id"),
        Index("idx_adaptation_category", "category"),
        Index("idx_adaptation_equivalence", "equivalence_type"),
    )
    
    def __repr__(self) -> str:
        return f"<CulturalAdaptation('{self.source_idiom}' → '{self.target_idiom}', equivalence={self.equivalence_type})>"


# ============================================================================
# FEEDBACK SYSTEM
# ============================================================================

class Feedback(Base):
    """
    User feedback on localization quality.
    
    Fields:
    - feedback_id: Unique identifier
    - request_id: Foreign key to LocalizationHistory
    - user_id: Foreign key to User
    - rating: 1-5 star rating
    - comment: Optional detailed feedback text
    - aspects: JSON object with feedback on specific aspects
      {
        "accuracy": 1-5,
        "tone_preserved": boolean,
        "cultural_fit": 1-5,
        "readability": 1-5,
        "idiom_handling": 1-5
      }
    - helpful: Was this translation helpful? (boolean)
    - created_at: Feedback timestamp
    
    Relationships:
    - user: Reference to User who gave feedback
    - localization: Reference to localization being reviewed
    """
    
    __tablename__ = "feedback"
    
    # Primary & Foreign Keys
    feedback_id = Column(String(36), primary_key=True, index=True)
    request_id = Column(String(36), ForeignKey("localization_history.request_id"), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Rating & Content
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    
    # Detailed Feedback Aspects (JSON)
    aspects = Column(JSON, nullable=True)
    # Example structure:
    # {
    #   "accuracy": 5,
    #   "tone_preserved": true,
    #   "cultural_fit": 4,
    #   "readability": 5,
    #   "idiom_handling": 4
    # }
    
    # Overall Usefulness
    helpful = Column(Boolean, nullable=True)  # True/False/Null for "unsure"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")
    localization = relationship("LocalizationHistory", back_populates="feedback")
    
    # Indexes & Constraints
    __table_args__ = (
        Index("idx_feedback_request_id", "request_id"),
        Index("idx_feedback_user_id", "user_id"),
        Index("idx_feedback_rating", "rating"),
        Index("idx_feedback_created_at", "created_at"),
        UniqueConstraint("request_id", "user_id", name="uq_one_feedback_per_request"),
    )
    
    def __repr__(self) -> str:
        return f"<Feedback(feedback_id='{self.feedback_id}', rating={self.rating}, helpful={self.helpful})>"


# ============================================================================
# ANALYTICS & AGGREGATES
# ============================================================================

class Analytics(Base):
    """
    Aggregated analytics and usage statistics.
    
    Fields:
    - metric_id: Unique identifier
    - user_id: Foreign key to User (optional - null for platform-wide metrics)
    - metric_date: Date for daily rollup
    - total_requests: Number of requests
    - total_characters: Total characters processed
    - total_words: Total words processed
    - avg_quality_score: Average quality score
    - avg_execution_time_ms: Average processing time
    - languages_used: JSON array of languages used that day
    - top_tone: Most used tone setting
    - top_language: Most localized target language
    - feedback_count: Number of feedbacks received
    - avg_rating: Average rating from feedback
    - cultural_adaptations_applied: Total idiom replacements
    - error_count: Number of errors/failures
    - created_at: Record timestamp
    
    Structure:
    - Daily rollup by user_id (or NULL for platform-wide)
    - Query-optimized for dashboard and reporting
    """
    
    __tablename__ = "analytics"
    
    # Primary & Foreign Keys
    metric_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True, index=True)
    
    # Time Period
    metric_date = Column(DateTime, nullable=False, index=True)
    
    # Volume Metrics
    total_requests = Column(Integer, default=0, nullable=False)
    total_characters = Column(Integer, default=0, nullable=False)
    total_words = Column(Integer, default=0, nullable=False)
    
    # Quality Metrics
    avg_quality_score = Column(Float, nullable=False)  # 0-100
    avg_execution_time_ms = Column(Float, nullable=False)
    
    # Usage Patterns (JSON)
    languages_used = Column(JSON, nullable=True)  # ["es", "hi", "fr", ...]
    tones_used = Column(JSON, nullable=True)  # {"formal": 5, "casual": 3, ...}
    
    # Top Categories
    top_language = Column(String(10), nullable=True)
    top_tone = Column(String(20), nullable=True)
    
    # Feedback Metrics
    feedback_count = Column(Integer, default=0, nullable=False)
    avg_rating = Column(Float, nullable=True)  # 1-5
    
    # Cultural Adaptation Metrics
    cultural_adaptations_applied = Column(Integer, default=0, nullable=False)
    idioms_detected_avg = Column(Float, default=0.0, nullable=False)
    
    # Error Tracking
    error_count = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, nullable=False)  # 0-1
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_analytics_user_id", "user_id"),
        Index("idx_analytics_metric_date", "metric_date"),
        Index("idx_analytics_composite", "user_id", "metric_date"),
    )
    
    def __repr__(self) -> str:
        return f"<Analytics(metric_id='{self.metric_id}', requests={self.total_requests}, quality={self.avg_quality_score})>"


# ============================================================================
# LANGUAGE SUPPORT & METADATA
# ============================================================================

class LanguageMetadata(Base):
    """
    Metadata about supported languages and locale-specific rules.
    
    Fields:
    - lang_code: ISO 639-1 language code (e.g., "es")
    - language_name: Full language name (e.g., "Spanish")
    - native_name: Name in native language (e.g., "Español")
    - region_code: ISO 3166-1 alpha-2 region code (e.g., "ES")
    - is_active: Whether language is currently supported
    - native_speakers: Approximate number of native speakers
    - linguistic_family: Language family (Romance, Indo-Aryan, etc.)
    - complexity_score: Difficulty for NLP (1-10)
    - supported_idioms: Approximate count of idioms in database
    - created_at: Metadata timestamp
    """
    
    __tablename__ = "language_metadata"
    
    # Primary Key
    lang_code = Column(String(10), primary_key=True, index=True)
    
    # Language Information
    language_name = Column(String(100), nullable=False)
    native_name = Column(String(100), nullable=False)
    region_code = Column(String(10), nullable=True)
    
    # Support Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Linguistic Data
    native_speakers = Column(Integer, nullable=True)  # in millions
    linguistic_family = Column(String(50), nullable=True)
    complexity_score = Column(Integer, nullable=False)  # 1-10, NLP difficulty
    
    # Database Statistics
    supported_idioms = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<LanguageMetadata(lang_code='{self.lang_code}', language='{self.language_name}')>"


# ============================================================================
# TONE PROFILES & PRESETS
# ============================================================================

class ToneProfile(Base):
    """
    Predefined tone profiles with linguistic characteristics.
    
    Fields:
    - tone_id: Unique identifier
    - tone_name: Tone type (formal, casual, etc.)
    - description: Human-readable description
    - characteristics: JSON with linguistic features
      {
        "vocabulary_level": "high|medium|low",
        "sentence_length": "long|medium|short",
        "punctuation_density": 0-1,
        "use_contractions": boolean,
        "use_slang": boolean,
        "politeness_level": "high|medium|low"
      }
    - system_prompt: Base prompt for this tone
    - example_output: Sample of this tone's output
    - is_active: Whether tone is available
    """
    
    __tablename__ = "tone_profiles"
    
    # Primary Key
    tone_id = Column(String(36), primary_key=True, index=True)
    
    # Tone Information
    tone_name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Linguistic Characteristics (JSON)
    characteristics = Column(JSON, nullable=True)
    
    # Prompting
    system_prompt = Column(Text, nullable=False)
    example_output = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<ToneProfile(tone_name='{self.tone_name}')>"


# ============================================================================
# USAGE QUOTA TRACKING
# ============================================================================

class UsageQuota(Base):
    """
    Track usage quotas per subscription tier.
    
    Fields:
    - user_id: Foreign key to User
    - requests_this_month: Count of requests in current month
    - characters_this_month: Characters processed this month
    - quota_limit_requests: Max requests allowed (tier-dependent)
    - quota_limit_characters: Max characters allowed (tier-dependent)
    - reset_date: When quota resets
    - last_updated: Last quota update
    """
    
    __tablename__ = "usage_quotas"
    
    # Primary & Foreign Key
    user_id = Column(String(36), ForeignKey("users.user_id"), primary_key=True, index=True)
    
    # Current Month Usage
    requests_this_month = Column(Integer, default=0, nullable=False)
    characters_this_month = Column(Integer, default=0, nullable=False)
    
    # Quota Limits
    quota_limit_requests = Column(Integer, nullable=False)  # Tier-dependent
    quota_limit_characters = Column(Integer, nullable=False)  # Tier-dependent
    
    # Reset Schedule
    reset_date = Column(DateTime, nullable=False)
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        quota_pct = (self.requests_this_month / self.quota_limit_requests * 100) if self.quota_limit_requests > 0 else 0
        return f"<UsageQuota(user_id='{self.user_id}', usage={quota_pct:.0f}%)>"


# ============================================================================
# API CALL LOGS
# ============================================================================

class APILog(Base):
    """
    Detailed logging of API calls for debugging and analytics.
    
    Fields:
    - log_id: Unique identifier
    - user_id: Foreign key to User (optional)
    - endpoint: API endpoint called
    - method: HTTP method (GET, POST, etc.)
    - status_code: HTTP response status
    - response_time_ms: Time taken
    - error_message: Error details if applicable
    - created_at: Log timestamp
    """
    
    __tablename__ = "api_logs"
    
    # Primary Key
    log_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True, index=True)
    
    # Request Details
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    
    # Response Details
    status_code = Column(Integer, nullable=False, index=True)
    response_time_ms = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_api_log_user_id", "user_id"),
        Index("idx_api_log_endpoint", "endpoint"),
        Index("idx_api_log_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<APILog(endpoint='{self.endpoint}', status={self.status_code}, time={self.response_time_ms}ms)>"
