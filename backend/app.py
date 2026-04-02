"""
AI Content Localization Platform - Flask Application

Integrated Flask server that orchestrates all backend modules:
- Context analyzer (language detection, sentiment)
- Localization engine (AI translation)
- Cultural adaptation (idioms and expressions)
- Quality validation (grammar and fluency)
- SQLite database (persistent storage)

Run with:
    python app.py

The server will start on http://localhost:5000
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# IMPORT MODULES
# ============================================================================
# These imports are organized to avoid circular dependencies
# Each module is self-contained and imported only once

try:
    # Context Analysis Modules
    from app.services.context_analyzer import (
        detect_language,
        analyze_sentiment,
        get_text_characteristics
    )
    
    # Localization Engine
    from app.services.localization_engine_class import LocalizationEngine
    
    # Cultural Adaptation
    from app.services.cultural_adapter import CulturalAdapterEngine
    
    # Quality Validation
    from app.services.quality_validation import check_grammar
    
    # Database Models
    from app.models import (
        Base,
        User,
        LocalizationHistory,
        CulturalAdaptation,
        Feedback,
        Analytics,
    )
    
    # Logging
    from app.core.logger import get_logger
    
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    raise

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Application configuration"""
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./localization.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # API
    API_TITLE = "AI Content Localization Platform"
    API_VERSION = "1.0.0"
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Environment
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENV = os.getenv("ENVIRONMENT", "development")


# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__)
app.config.from_object(Config)

# CORS configuration - allow frontend to call backend
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
})

logger = get_logger(__name__)

# ============================================================================
# DATABASE SETUP
# ============================================================================

def create_db_engine(database_url: str) -> Any:
    """
    Create SQLAlchemy database engine.
    
    Args:
        database_url: Database connection string
        
    Returns:
        SQLAlchemy Engine
    """
    if "sqlite" in database_url:
        # SQLite configuration
        from sqlalchemy.pool import StaticPool
        engine = create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=Config.DEBUG,
        )
        
        # Enable foreign key support in SQLite
        from sqlalchemy import event, Engine
        
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        # PostgreSQL or other database
        engine = create_engine(
            database_url,
            pool_size=20,
            max_overflow=40,
            echo=Config.DEBUG,
            pool_pre_ping=True,  # Verify connections before using
            future=True,
        )
    
    return engine


# Initialize database
db_engine = create_db_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def init_database():
    """Initialize database schema (create tables if they don't exist)."""
    try:
        Base.metadata.create_all(bind=db_engine)
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# ERROR HANDLING
# ============================================================================

class LocalizationError(Exception):
    """Base exception for localization errors."""
    pass


class LanguageDetectionError(LocalizationError):
    """Raised when language detection fails."""
    pass


class LocalizationEngineError(LocalizationError):
    """Raised when localization engine fails."""
    pass


class CulturalAdaptationError(LocalizationError):
    """Raised when cultural adaptation fails."""
    pass


class ValidationError(LocalizationError):
    """Raised when validation fails."""
    pass


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        "success": False,
        "error": "Bad request",
        "details": str(error),
    }), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        "success": False,
        "error": "Not found",
        "details": str(error),
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "details": "An unexpected error occurred",
    }), 500


@app.errorhandler(LocalizationError)
def handle_localization_error(error):
    """Handle localization-specific errors."""
    logger.error(f"Localization error: {error}")
    return jsonify({
        "success": False,
        "error": type(error).__name__,
        "details": str(error),
    }), 400


# ============================================================================
# DECORATORS
# ============================================================================

def require_json(f):
    """Decorator to require JSON content type."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type must be application/json",
            }), 400
        return f(*args, **kwargs)
    return decorated_function


def handle_errors(f):
    """Decorator to handle and log errors."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except LocalizationError as e:
            logger.warning(f"Localization error: {e}")
            return jsonify({
                "success": False,
                "error": type(e).__name__,
                "details": str(e),
            }), 400
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            return jsonify({
                "success": False,
                "error": "Database error",
                "details": "Failed to save data to database",
            }), 500
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "details": str(e) if Config.DEBUG else "An unexpected error occurred",
            }), 500
    return decorated_function


# ============================================================================
# SERVICE LAYER - LOCALIZATION PIPELINE
# ============================================================================

class LocalizationService:
    """
    Orchestrates the complete localization pipeline.
    
    Pipeline stages:
    1. Detect source language
    2. Analyze sentiment and tone
    3. Translate using AI
    4. Apply cultural adaptation
    5. Validate grammar and fluency
    6. Save to database
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize localization service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.localization_engine = LocalizationEngine()
        self.cultural_adapter = CulturalAdapterEngine()
        self.logger = get_logger(__name__)
    
    def localize(
        self,
        text: str,
        target_language: str,
        tone: str = "neutral",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute complete localization pipeline.
        
        Pipeline:
        1. Validate input
        2. Detect source language
        3. Analyze sentiment
        4. Get text characteristics
        5. Translate with AI
        6. Apply cultural adaptations
        7. Validate grammar
        8. Save to database
        9. Return result
        
        Args:
            text: Text to localize
            target_language: Target language code (e.g., 'es', 'fr')
            tone: Tone for localization (formal, casual, marketing, neutral)
            user_id: User ID for tracking
            
        Returns:
            Dictionary with localization result including:
            - original_text: Input text
            - detected_language: Detected source language
            - sentiment: Detected sentiment
            - localized_text: Translated and adapted text
            - explanation: Details about the localization
            - request_id: Unique request ID
            
        Raises:
            LocalizationError: If any pipeline stage fails
        """
        request_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Starting localization pipeline (ID: {request_id})")
            
            # ================================================================
            # STAGE 1: INPUT VALIDATION
            # ================================================================
            if not text or not text.strip():
                raise ValidationError("Text cannot be empty")
            
            if len(text) > 50000:
                raise ValidationError("Text exceeds maximum length of 50,000 characters")
            
            if not target_language or len(target_language) != 2:
                raise ValidationError("Invalid target language code (use 2-letter code)")
            
            text = text.strip()
            self.logger.debug(f"Input validated: {len(text)} chars")
            
            # ================================================================
            # STAGE 2: LANGUAGE DETECTION
            # ================================================================
            detected_language = self._detect_language(text)
            self.logger.info(f"Detected language: {detected_language}")
            
            # ================================================================
            # STAGE 3: SENTIMENT ANALYSIS
            # ================================================================
            sentiment = self._analyze_sentiment(text)
            self.logger.info(f"Detected sentiment: {sentiment}")
            
            # ================================================================
            # STAGE 4: GET TEXT CHARACTERISTICS
            # ================================================================
            characteristics = self._get_characteristics(text)
            self.logger.debug(f"Text characteristics: {characteristics}")
            
            # ================================================================
            # STAGE 5: AI TRANSLATION & LOCALIZATION
            # ================================================================
            localized = self._translate(
                text=text,
                source_language=detected_language,
                target_language=target_language,
                tone=tone,
                sentiment=sentiment,
            )
            self.logger.info(f"Translation completed")
            
            # ================================================================
            # STAGE 6: CULTURAL ADAPTATION
            # ================================================================
            adaptations = self._apply_cultural_adaptation(
                localized_text=localized["text"],
                source_language=detected_language,
                target_language=target_language,
            )
            self.logger.info(f"Applied {len(adaptations)} cultural adaptations")
            
            # ================================================================
            # STAGE 7: GRAMMAR & FLUENCY VALIDATION
            # ================================================================
            validation = self._validate_quality(
                text=localized["text"],
                language=target_language,
            )
            quality_score = self._calculate_quality_score(
                validation,
                localized.get("quality_score", 85),
            )
            self.logger.info(f"Quality validation completed (score: {quality_score})")
            
            # ================================================================
            # STAGE 8: SAVE TO DATABASE
            # ================================================================
            localization_record = self._save_localization(
                request_id=request_id,
                user_id=user_id,
                source_text=text,
                localized_text=localized["text"],
                source_language=detected_language,
                target_language=target_language,
                sentiment=sentiment,
                tone=tone,
                quality_score=quality_score,
                explanation=localized.get("explanation", ""),
            )
            
            # Save cultural adaptations
            for adaptation in adaptations:
                self._save_cultural_adaptation(
                    request_id=request_id,
                    source_idiom=adaptation.get("source_idiom"),
                    target_idiom=adaptation.get("target_idiom"),
                    equivalence_type=adaptation.get("equivalence_type"),
                    semantic_preservation=adaptation.get("semantic_preservation", 0.8),
                )
            
            self.logger.info(f"Saved to database: {localization_record.request_id}")
            
            # ================================================================
            # STAGE 9: BUILD RESPONSE
            # ================================================================
            result = {
                "original_text": text,
                "detected_language": detected_language,
                "sentiment": sentiment,
                "localized_text": localized["text"],
                "explanation": localized.get("explanation", ""),
                "request_id": request_id,
                "quality_score": quality_score,
                "tone": tone,
                "target_language": target_language,
                "adaptations": adaptations,
                "validation": {
                    "is_fluent": validation.get("is_fluent", True),
                    "issue_count": validation.get("issue_count", 0),
                },
            }
            
            self.logger.info(f"✓ Pipeline completed successfully (ID: {request_id})")
            return result
            
        except Exception as e:
            self.logger.error(f"✗ Pipeline failed: {e}", exc_info=True)
            raise
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text."""
        try:
            lang = detect_language(text)
            if lang not in ["en", "es", "fr", "de", "hi", "pt", "ja", "zh", "ar", "ru", "ko", "it"]:
                # For unsupported languages, default to English
                self.logger.warning(f"Detected language '{lang}' not fully supported, using 'en'")
                lang = "en"
            return lang
        except Exception as e:
            raise LanguageDetectionError(f"Failed to detect language: {e}")
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text."""
        try:
            sentiment = analyze_sentiment(text)
            return sentiment
        except Exception as e:
            self.logger.warning(f"Sentiment analysis failed: {e}, defaulting to 'neutral'")
            return "neutral"
    
    def _get_characteristics(self, text: str) -> Dict[str, Any]:
        """Get text characteristics."""
        try:
            chars = get_text_characteristics(text)
            return chars
        except Exception as e:
            self.logger.warning(f"Failed to get characteristics: {e}")
            return {
                "word_count": len(text.split()),
                "char_count": len(text),
            }
    
    def _translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        tone: str,
        sentiment: str,
    ) -> Dict[str, Any]:
        """
        Translate text using localization engine.
        
        Returns:
            Dictionary with:
            - text: Translated text
            - explanation: Translation explanation
            - quality_score: Translation quality 0-100
        """
        try:
            result = self.localization_engine.localize(
                text=text,
                source_language=source_language,
                target_language=target_language,
                tone=tone,
                sentiment_hint=sentiment,
            )

            if isinstance(result, str):
                result = {"localized_text": result}
            elif not hasattr(result, "get"):
                result = {"localized_text": str(result)}

            return {
                "text": result.get("localized_text", ""),
                "explanation": result.get("explanation", ""),
                "quality_score": result.get("quality_score", 85),
            }
        except Exception as e:
            raise LocalizationEngineError(f"Translation failed: {e}")
    
    def _apply_cultural_adaptation(
        self,
        localized_text: str,
        source_language: str,
        target_language: str,
    ) -> List[Dict[str, Any]]:
        """
        Apply cultural adaptations (idiom replacements).
        
        Returns:
            List of applied adaptations
        """
        try:
            adapted_text = self.cultural_adapter.adapt_cultural_references(
                text=localized_text,
                source_lang=source_language,
                target_lang=target_language,
            )

            if adapted_text == localized_text:
                return []

            return [
                {
                    "source_text": localized_text,
                    "adapted_text": adapted_text,
                    "source_language": source_language,
                    "target_language": target_language,
                }
            ]
        except Exception as e:
            self.logger.warning(f"Cultural adaptation failed: {e}")
            return []
    
    def _validate_quality(
        self,
        text: str,
        language: str,
    ) -> Dict[str, Any]:
        """
        Validate grammar and fluency.
        
        Returns:
            Validation result with issues and fluency score
        """
        try:
            # Map language code to language-tool language
            lang_map = {
                "en": "en",
                "es": "es",
                "fr": "fr",
                "de": "de",
                "pt": "pt",
            }
            
            validation_lang = lang_map.get(language, "en")
            result = check_grammar(text, validation_lang)
            return result
        except Exception as e:
            self.logger.warning(f"Grammar validation failed: {e}")
            return {
                "is_fluent": True,
                "issue_count": 0,
                "issues": [],
            }
    
    def _calculate_quality_score(
        self,
        validation: Dict[str, Any],
        translation_quality: float,
    ) -> float:
        """
        Calculate overall quality score (0-100).
        
        Factors:
        - Translation quality (70% weight)
        - Grammar validation (30% weight)
        """
        grammar_issues = validation.get("issue_count", 0)
        grammar_score = max(0, 100 - (grammar_issues * 5))  # 5 points per issue
        
        quality_score = (translation_quality * 0.7) + (grammar_score * 0.3)
        return round(min(100, max(0, quality_score)), 2)
    
    def _save_localization(
        self,
        request_id: str,
        user_id: Optional[str],
        source_text: str,
        localized_text: str,
        source_language: str,
        target_language: str,
        sentiment: str,
        tone: str,
        quality_score: float,
        explanation: str,
    ) -> "LocalizationHistory":
        """Save localization to database."""
        try:
            # Get or create user
            if user_id:
                user = self.db.query(User).filter_by(user_id=user_id).first()
            else:
                user = None
            
            record = LocalizationHistory(
                request_id=request_id,
                user_id=user.user_id if user else None,
                source_text=source_text,
                localized_text=localized_text,
                source_language=source_language,
                target_language=target_language,
                sentiment=sentiment,
                tone=tone,
                quality_score=quality_score,
                explanation=explanation,
                created_at=datetime.now(),
            )
            
            self.db.add(record)
            self.db.commit()
            
            return record
        except Exception as e:
            self.db.rollback()
            raise
    
    def _save_cultural_adaptation(
        self,
        request_id: str,
        source_idiom: str,
        target_idiom: str,
        equivalence_type: str,
        semantic_preservation: float,
    ) -> None:
        """Save cultural adaptation to database."""
        try:
            adaptation = CulturalAdaptation(
                request_id=request_id,
                source_idiom=source_idiom,
                target_idiom=target_idiom,
                equivalence_type=equivalence_type,
                semantic_preservation=semantic_preservation,
                created_at=datetime.now(),
            )
            
            self.db.add(adaptation)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save cultural adaptation: {e}")
            # Don't raise - cultural adaptation is not critical


# ============================================================================
# API ENDPOINTS
# ============================================================================

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        # Try database connection
        db = SessionLocal()
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except:
            db_status = "unhealthy"
        finally:
            db.close()
        
        return jsonify({
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
        }), 503


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information."""
    return jsonify({
        "app": Config.API_TITLE,
        "version": Config.API_VERSION,
        "environment": Config.ENV,
        "endpoints": {
            "health": "GET /health",
            "localize": "POST /api/localize",
            "feedback": "POST /api/feedback",
            "history": "GET /api/history",
        },
        "docs": "See README.md for documentation",
    }), 200


# ============================================================================
# MAIN ENDPOINT: LOCALIZATION
# ============================================================================

@app.route("/api/localize", methods=["POST"])
@require_json
@handle_errors
def localize():
    """
    POST /api/localize
    
    Localize text with full pipeline:
    1. Detect language
    2. Analyze sentiment
    3. Translate
    4. Apply cultural adaptation
    5. Validate quality
    6. Save to database
    
    Request body:
    {
        "text": "string (required) - Text to localize",
        "target_language": "string (required) - Target language code (es, fr, de, etc.)",
        "tone": "string (optional) - Tone: formal, casual, marketing, neutral (default: neutral)",
        "user_id": "string (optional) - User ID for tracking"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "original_text": "string",
            "detected_language": "string",
            "sentiment": "string",
            "localized_text": "string",
            "explanation": "string",
            "request_id": "uuid",
            "quality_score": number,
            "adaptations": [...]
        }
    }
    """
    # Get request parameters
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is required",
        }), 400
    
    text = data.get("text", "").strip()
    target_language = data.get("target_language", "").lower()
    tone = data.get("tone", "neutral").lower()
    user_id = data.get("user_id")
    
    # Validate tone
    valid_tones = ["formal", "casual", "marketing", "neutral", "technical"]
    if tone not in valid_tones:
        return jsonify({
            "success": False,
            "error": f"Invalid tone. Must be one of: {', '.join(valid_tones)}",
        }), 400
    
    # Create localization service and process
    db = SessionLocal()
    try:
        service = LocalizationService(db)
        result = service.localize(
            text=text,
            target_language=target_language,
            tone=tone,
            user_id=user_id,
        )
        
        return jsonify({
            "success": True,
            "data": result,
        }), 200
    finally:
        db.close()


# ============================================================================
# FEEDBACK ENDPOINT
# ============================================================================

@app.route("/api/feedback", methods=["POST"])
@require_json
@handle_errors
def submit_feedback():
    """
    POST /api/feedback
    
    Submit feedback on a localization result.
    
    Request body:
    {
        "request_id": "string (required) - Request ID from localization response",
        "user_id": "string (optional) - User ID",
        "rating": number (required) - Rating 1-5",
        "comment": "string (optional) - User comment",
        "aspects": {
            "accuracy": number,
            "tone_preserved": boolean,
            "cultural_fit": number,
            "readability": number
        }
    }
    
    Response:
    {
        "success": true,
        "message": "Feedback submitted successfully",
        "feedback_id": "uuid"
    }
    """
    data = request.get_json()
    
    # Validate required fields
    request_id = data.get("request_id")
    if not request_id:
        return jsonify({
            "success": False,
            "error": "request_id is required",
        }), 400
    
    rating = data.get("rating")
    if not rating or rating < 1 or rating > 5:
        return jsonify({
            "success": False,
            "error": "rating must be between 1 and 5",
        }), 400
    
    # Create feedback record
    db = SessionLocal()
    try:
        # Verify request exists
        localization = db.query(LocalizationHistory).filter_by(
            request_id=request_id
        ).first()
        
        if not localization:
            return jsonify({
                "success": False,
                "error": f"Request ID not found: {request_id}",
            }), 404
        
        feedback_id = str(uuid.uuid4())
        feedback = Feedback(
            feedback_id=feedback_id,
            request_id=request_id,
            user_id=data.get("user_id"),
            rating=int(rating),
            comment=data.get("comment", ""),
            created_at=datetime.now(),
        )
        
        db.add(feedback)
        db.commit()
        
        logger.info(f"Feedback submitted: {feedback_id}")
        
        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id,
        }), 201
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to submit feedback: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to submit feedback",
            "details": str(e) if Config.DEBUG else None,
        }), 500
    finally:
        db.close()


# ============================================================================
# HISTORY ENDPOINT
# ============================================================================

@app.route("/api/history", methods=["GET"])
@handle_errors
def get_history():
    """
    GET /api/history
    
    Get localization history for a user or all records.
    
    Query parameters:
    - user_id: string (optional) - Filter by user ID
    - limit: integer (optional, default: 20) - Number of records to return
    - offset: integer (optional, default: 0) - Pagination offset
    - language: string (optional) - Filter by target language
    - start_date: string (optional) - ISO format start date
    - end_date: string (optional) - ISO format end date
    
    Response:
    {
        "success": true,
        "data": [
            {
                "request_id": "uuid",
                "user_id": "string",
                "source_text": "string",
                "localized_text": "string",
                "source_language": "string",
                "target_language": "string",
                "sentiment": "string",
                "tone": "string",
                "quality_score": number,
                "created_at": "ISO timestamp",
                "feedback": {...} (if available)
            }
        ],
        "total": number,
        "limit": number,
        "offset": number
    }
    """
    # Get query parameters
    user_id = request.args.get("user_id")
    language = request.args.get("language")
    limit = min(int(request.args.get("limit", 20)), 100)  # Max 100
    offset = max(0, int(request.args.get("offset", 0)))
    
    db = SessionLocal()
    try:
        # Build query
        query = db.query(LocalizationHistory)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if language:
            query = query.filter_by(target_language=language)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        records = query.order_by(
            LocalizationHistory.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Format response
        data = []
        for record in records:
            # Get associated feedback if exists
            feedback = db.query(Feedback).filter_by(
                request_id=record.request_id
            ).first()
            
            item = {
                "request_id": record.request_id,
                "user_id": record.user_id,
                "source_text": record.source_text,
                "localized_text": record.localized_text,
                "source_language": record.source_language,
                "target_language": record.target_language,
                "sentiment": record.sentiment,
                "tone": record.tone,
                "quality_score": record.quality_score,
                "explanation": record.explanation,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            }
            
            if feedback:
                item["feedback"] = {
                    "feedback_id": feedback.feedback_id,
                    "rating": feedback.rating,
                    "comment": feedback.comment,
                    "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
                }
            
            data.append(item)
        
        return jsonify({
            "success": True,
            "data": data,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
            },
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to retrieve history: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve history",
            "details": str(e) if Config.DEBUG else None,
        }), 500
    finally:
        db.close()


# ============================================================================
# APPLICATION STARTUP
# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def startup():
    """Initialize on first request."""
    logger.info("=" * 70)
    logger.info(f"Starting {Config.API_TITLE}")
    logger.info(f"Version: {Config.API_VERSION}")
    logger.info(f"Environment: {Config.ENV}")
    logger.info(f"Database: {Config.DATABASE_URL}")
    logger.info("=" * 70)
    
    # Initialize database
    init_database()
    
    logger.info("✓ Application initialized successfully")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    """
    Run Flask application.
    
    Usage:
        python app.py
    
    The server will start on http://localhost:5000
    """
    init_database()
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=Config.DEBUG,
        use_reloader=Config.DEBUG,
    )
