# Flask Application - Code Guide

This guide explains the key sections of `app.py` and how to modify or extend the application.

## File Structure

`app.py` is organized into the following sections:

```python
# 1. Module Docstring & Top-level Imports
# 2. Configuration Class (Config)
# 3. Flask App Initialization
# 4. Database Setup Functions
# 5. Error Classes & Handlers
# 6. Decorator Functions
# 7. LocalizationService Class (Main Orchestrator)
# 8. API Endpoint Decorators
# 9. Endpoint Functions (4 total)
# 10. Application Startup & Main
```

---

## Section 1: Module Setup

### Imports Organization

The imports are carefully ordered to **avoid circular dependencies**:

```python
# STAGE 1: Core Framework
from flask import Flask, request, jsonify
from flask_cors import CORS

# STAGE 2: Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# NOT IMPORTED: Don't import app.py modules at top level!
# These are imported inside LocalizationService.__init__()
```

### Why This Matters

```python
# ✅ GOOD: Staged imports to avoid circular references
from app.services.context_analyzer import detect_language
from app.models import LocalizationHistory

# ❌ BAD: Would cause circular import if context_analyzer imports app
# from app import app  # Don't do this in services!
```

---

## Section 2: Configuration Class

### How to Modify Settings

```python
class Config:
    """Application configuration"""
    
    # To add a new setting:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    MY_NEW_SETTING = os.getenv("MY_NEW_SETTING", "default_value")
    
    # To change defaults:
    # Production: DEBUG = False
    # Development: DEBUG = True
```

### Common Configuration Changes

```python
# Enable/disable debug mode
DEBUG=True python app.py

# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://user:pass@localhost/db python app.py

# Change OpenAI model
OPENAI_MODEL=gpt-4-turbo python app.py
```

---

## Section 3: Flask App Initialization

### How CORS Works

```python
CORS(app, resources={
    r"/api/*": {  # Applies to all /api/* routes
        "origins": ["*"],  # Allow all origins (change for production!)
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
})
```

### To Restrict CORS (Production)

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://yourdomain.com",
            "https://app.yourdomain.com"
        ],  # Only allow your frontend
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"],
    }
})
```

---

## Section 4: Database Functions

### `create_db_engine()` - Creates Database Connection

```python
def create_db_engine(database_url: str) -> Any:
    """
    Creates SQLAlchemy engine based on database type.
    Automatically detects SQLite vs PostgreSQL.
    """
    
    if "sqlite" in database_url:
        # SQLite configuration for development
        # - Single connection pool (StaticPool)
        # - Check same thread disabled for Flask
        # - Enable foreign keys
        engine = create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=Config.DEBUG,  # Logs all SQL if DEBUG=True
        )
    else:
        # PostgreSQL configuration for production
        # - Connection pooling (20 connections, overflow 40)
        # - Pre-ping checks connections are alive
        engine = create_engine(
            database_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,  # Important!
        )
    
    return engine
```

### `init_database()` - Creates All Tables

```python
def init_database():
    """
    Called on app startup.
    Creates all tables defined in models.py if they don't exist.
    
    Uses: Base.metadata.create_all()
    """
    Base.metadata.create_all(bind=db_engine)
    logger.info("✓ Database initialized successfully")
```

### How to Add a New Table

```python
# 1. Define model in app/models.py
class MyNewTable(Base):
    __tablename__ = "my_new_table"
    # ... columns ...

# 2. Import in app.py
from app.models import MyNewTable

# 3. Restart app - init_database() creates it automatically!
```

---

## Section 5: Error Classes & Handlers

### Custom Exception Hierarchy

```python
class LocalizationError(Exception):      # Base
    pass

class LanguageDetectionError(LocalizationError):    # Specific
    pass

class LocalizationEngineError(LocalizationError):   # Specific
    pass

# Usage:
if not detected_language:
    raise LanguageDetectionError("Failed to detect language")
```

### Error Handlers

```python
@app.errorhandler(LocalizationError)
def handle_localization_error(error):
    """
    Catches all LocalizationError subclasses.
    Returns 400 with error details.
    """
    return jsonify({
        "success": False,
        "error": type(error).__name__,
        "details": str(error),
    }), 400
```

### Adding a New Error Type

```python
# 1. Define exception class
class MyCustomError(LocalizationError):
    pass

# 2. Define handler (or use existing LocalizationError handler)
@app.errorhandler(MyCustomError)
def handle_my_error(error):
    return jsonify({"error": str(error)}), 400

# 3. Raise in code
raise MyCustomError("Something went wrong")
```

---

## Section 6: Decorators

### `@require_json` Decorator

```python
@require_json
def localize():
    """
    Decorator ensures Content-Type: application/json
    and request.get_json() is not None
    """
    pass

# Equivalent to:
def localize():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400
    # ... endpoint code ...
```

### `@handle_errors` Decorator

```python
@handle_errors
def localize():
    """
    Catches all exceptions in endpoint.
    Provides unified error response format.
    Logs errors automatically.
    """
    pass

# Catches:
# - LocalizationError
# - SQLAlchemyError (database errors)
# - Generic Exception (logs with traceback)
```

### How to Add a Decorator

```python
def my_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Code before function
        print("Before endpoint")
        
        result = f(*args, **kwargs)
        
        # Code after function
        print("After endpoint")
        return result
    return decorated_function

@app.route("/api/myendpoint")
@my_decorator
def myendpoint():
    return jsonify({"message": "works"})
```

---

## Section 7: LocalizationService Class

### Main Orchestration Class

```python
class LocalizationService:
    def __init__(self, db_session: Session):
        """
        Initialize with database session and module engines.
        Called for each API request with fresh session.
        """
        self.db = db_session  # Database connection
        self.localization_engine = LocalizationEngine()  # AI module
        self.cultural_adapter = CulturalAdapterEngine()  # Idiom module
        self.logger = get_logger(__name__)
    
    def localize(self, text, target_language, tone, user_id) -> Dict:
        """
        Main pipeline: 9 stages from input to output.
        Each stage has error handling.
        Returns unified response dict.
        """
        # Stages 1-9 implemented here
        pass
```

### Understanding the Pipeline

```python
def localize(self, ...):
    # STAGE 1: Validation
    if not text:
        raise ValidationError("...")
    
    # STAGE 2: Language Detection
    lang = self._detect_language(text)
    
    # STAGE 3: Sentiment Analysis
    sentiment = self._analyze_sentiment(text)
    
    # ... More stages ...
    
    # STAGE 9: Save & Return
    return {
        "original_text": text,
        "localized_text": result,
        # ... More fields ...
    }
```

### How to Add a Pipeline Stage

```python
def localize(self, ...):
    # ... existing stages ...
    
    # NEW STAGE: X
    my_result = self._new_processor(some_data)
    
    # ... more stages ...

def _new_processor(self, data):
    """Process data and return result"""
    try:
        # Call external module or service
        result = some_module.process(data)
        return result
    except Exception as e:
        self.logger.error(f"Processing failed: {e}")
        raise MyCustomError(str(e))
```

### Database Save Methods

```python
def _save_localization(self, ...):
    """Save LocalizationHistory record"""
    record = LocalizationHistory(
        request_id=request_id,
        user_id=user_id,
        # ... all fields ...
    )
    self.db.add(record)
    self.db.commit()  # Important!
    return record

def _save_cultural_adaptation(self, ...):
    """Save CulturalAdaptation record"""
    adaptation = CulturalAdaptation(...)
    self.db.add(adaptation)
    self.db.commit()
```

---

## Section 8: API Endpoints

### Health Check Endpoint

```python
@app.route("/health", methods=["GET"])
def health():
    """
    Minimal health check - no auth required.
    Tests database connection.
    Returns:
    - 200 if healthy
    - 503 if database unavailable
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")  # Simple query
        db.close()
        return jsonify({"status": "healthy"}), 200
    except:
        return jsonify({"status": "unhealthy"}), 503
```

### Main Localization Endpoint

```python
@app.route("/api/localize", methods=["POST"])
@require_json
@handle_errors
def localize():
    """
    Main endpoint: POST /api/localize
    
    Request must include:
    - text: string (required)
    - target_language: string (required)
    - tone: string (optional)
    - user_id: string (optional)
    
    Response is JSON with all translation metadata.
    """
    
    # 1. Parse request
    data = request.get_json()
    text = data.get("text", "").strip()
    target_language = data.get("target_language", "").lower()
    tone = data.get("tone", "neutral").lower()
    
    # 2. Validate
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    if tone not in ["formal", "casual", "marketing", "neutral"]:
        return jsonify({"error": "Invalid tone"}), 400
    
    # 3. Process
    db = SessionLocal()
    try:
        service = LocalizationService(db)  # Fresh service per request
        result = service.localize(text, target_language, tone, user_id)
        
        return jsonify({
            "success": True,
            "data": result,
        }), 200
    finally:
        db.close()  # Always close
```

### Adding a New Endpoint

```python
@app.route("/api/mynewendpoint", methods=["GET", "POST"])
@require_json  # If POST
@handle_errors
def mynewendpoint():
    """Document here"""
    
    if request.method == "GET":
        param = request.args.get("param")
    else:
        data = request.get_json()
        param = data.get("param")
    
    # Process
    result = do_something(param)
    
    return jsonify({
        "success": True,
        "data": result,
    }), 200
```

---

## Section 9: Endpoint Details

### POST /api/localize

**What it does:**
1. Receives text and target language
2. Runs complete localization pipeline
3. Saves to database
4. Returns structured response

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/localize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "target_language": "es"
  }'
```

**Response Fields:**
- `original_text` - What user provided
- `detected_language` - Auto-detected language
- `sentiment` - Emotional tone
- `localized_text` - Translated output
- `quality_score` - 0-100 score
- `request_id` - Unique ID for tracking
- `adaptations` - Idiom replacements made
- `validation` - Grammar check results

---

### POST /api/feedback

**What it does:**
1. Validates request_id exists
2. Saves feedback to database
3. Returns feedback_id

**Modifications for Extended Feedback:**
```python
# In feedback() endpoint, add:
aspects = data.get("aspects", {})  # Get aspects dict

# Store in database (requires model change):
feedback = Feedback(
    aspects_json=json.dumps(aspects),  # Store as JSON
)
```

---

### GET /api/history

**Query Parameters:**
- `user_id` - Filter by user
- `target_language` - Filter by language
- `limit` - Records per page (default 20, max 100)
- `offset` - Pagination offset (default 0)

**To Sort Differently:**
```python
# Current: Most recent first
records = query.order_by(LocalizationHistory.created_at.desc())

# Alternative: By quality score
records = query.order_by(LocalizationHistory.quality_score.desc())

# Alternative: Oldest first
records = query.order_by(LocalizationHistory.created_at.asc())
```

---

## Section 10: Application Startup

### Startup Flow

```python
if __name__ == "__main__":
    init_database()  # Create tables
    
    app.run(
        host="0.0.0.0",       # Listen on all interfaces
        port=5000,            # Default port
        debug=Config.DEBUG,   # Reload on code changes
    )
```

### Startup Process

```
python app.py
    ↓
Load .env variables
    ↓
Initialize Flask app
    ↓
Set up CORS middleware
    ↓
Create database engine
    ↓
Create session factory
    ↓
Define all routes
    ↓
Define error handlers
    ↓
Call init_database()
    ↓
Start server on port 5000
    ↓
Ready to accept requests!
```

---

## Common Modifications

### Change Database

```python
# In .env
# Development (SQLite):
DATABASE_URL=sqlite:///./localization.db

# Production (PostgreSQL):
DATABASE_URL=postgresql://user:password@localhost:5432/db
```

### Change Port

```bash
# Modify app.run()
app.run(port=8000)

# Or set environment variable
PORT=8000 python app.py
```

### Add Logging to File

```python
# After app initialization:
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

### Increase Request Timeout

```python
# Flask default is 30 seconds
from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.timeout = 60  # 60 seconds
```

### Add Authentication

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/api/localize", methods=["POST"])
@require_api_key
def localize():
    # Protected endpoint
    pass
```

---

## Debugging Tips

### Enable SQL Query Logging

```python
# In Config class:
DEBUG=True  # In .env

# Or programmatically:
app.config['SQLALCHEMY_ECHO'] = True
```

### Add Debug Prints

```python
def localize():
    print(f"DEBUG: Received text: {text}")
    print(f"DEBUG: Target language: {target_language}")
    
    result = service.localize(...)
    
    print(f"DEBUG: Result: {result}")
    return jsonify({"success": True, "data": result})
```

### Check Database State

```python
# From Python shell:
from app.models import LocalizationHistory
from app.database import SessionLocal

db = SessionLocal()
count = db.query(LocalizationHistory).count()
print(f"Total records: {count}")

recent = db.query(LocalizationHistory).order_by(
    LocalizationHistory.created_at.desc()
).first()
print(f"Most recent: {recent.localized_text}")
```

### Monitor Requests

```python
@app.before_request
def log_request():
    print(f"→ {request.method} {request.path}")

@app.after_request
def log_response(response):
    print(f"← {response.status_code}")
    return response
```

---

## Performance Optimization

### Database Connection Pooling

```python
# Already configured in create_db_engine():
# SQLite: StaticPool (single connection)
# PostgreSQL: pool_size=20, max_overflow=40

# To adjust for more concurrent users:
engine = create_engine(
    database_url,
    pool_size=50,        # Increase base pool
    max_overflow=100,    # Increase overflow
    pool_pre_ping=True,  # Verify connections
)
```

### Cache Repeated Queries

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_language_features(lang_code):
    """Cache language features to avoid repeated lookups"""
    return database_lookup(lang_code)
```

### Batch Database Operations

```python
# Instead of multiple single saves:
# ❌ SLOWER
for item in items:
    db.add(item)
    db.commit()

# ✅ FASTER  
for item in items:
    db.add(item)
db.commit()  # Single commit
```

---

## Security Checklist

- ✅ Input validation on all endpoints
- ✅ SQL injection prevention (using ORM)
- ✅ Error messages don't expose secrets
- ✅ API key in environment, not code
- ✅ CORS restricted in production
- ✅ Content-Type validation on POST
- ✅ Database connection pooling
- ✅ Logging for audit trail

---

## Summary

This `app.py` file is your complete Flask application. It:

1. **Orchestrates all modules** through LocalizationService
2. **Implements 9-stage pipeline** for localization
3. **Provides 4 REST endpoints** for frontend integration
4. **Handles all errors** gracefully
5. **Persists data** to SQLite database
6. **Is production-ready** with logging and monitoring

**To use:** `python app.py`

**To extend:** Follow patterns shown above for adding stages, endpoints, or error types.

---

**Happy hacking! 🚀**
