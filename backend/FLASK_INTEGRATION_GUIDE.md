# Flask Application Integration Guide

## Overview

This guide explains how all backend modules are integrated into a working Flask application that performs semantic localization with cultural awareness.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Integration](#module-integration)
3. [Localization Pipeline](#localization-pipeline)
4. [API Endpoints](#api-endpoints)
5. [Error Handling](#error-handling)
6. [Running the Server](#running-the-server)
7. [Example Requests](#example-requests)
8. [Module Interactions](#module-interactions)

---

## Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Flask Web Application                     │
│                        (app.py)                             │
├─────────────────────────────────────────────────────────────┤
│  API Layer: Routes & Request Handling                       │
│  - POST /api/localize                                       │
│  - POST /api/feedback                                       │
│  - GET /api/history                                         │
│  - GET /health                                              │
├─────────────────────────────────────────────────────────────┤
│  Service Layer: Business Logic (LocalizationService)        │
│  - Pipeline orchestration                                   │
│  - Error handling                                           │
│  - Database operations                                      │
├─────────────────────────────────────────────────────────────┤
│  Module Layer: Feature Implementation                       │
│  1. Context Analyzer       - Language & sentiment detection │
│  2. Localization Engine    - AI translation                 │
│  3. Cultural Adapter       - Idiom adaptation               │
│  4. Quality Validator      - Grammar checking               │
├─────────────────────────────────────────────────────────────┤
│  Data Layer: Database (SQLite)                              │
│  - Models: User, LocalizationHistory, Feedback, etc.        │
│  - ORM: SQLAlchemy                                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **Flask App** | `app.py` | Main application, routes, pipeline orchestration |
| **Context Analyzer** | `app/services/context_analyzer.py` | Language detection, sentiment analysis |
| **Localization Engine** | `app/services/localization_engine.py` | AI-powered translation |
| **Cultural Adapter** | `app/services/cultural_adapter.py` | Idiom and expression adaptation |
| **Quality Validator** | `app/services/quality_validation.py` | Grammar and fluency checking |
| **Database Models** | `app/models.py` | SQLAlchemy ORM models |
| **Database Engine** | `app/database.py` | Connection pooling and session management |
| **Logger** | `app/core/logger.py` | Centralized logging |

---

## Module Integration

### No Circular Imports

The application is structured to avoid circular dependencies:

```
app.py (imports)
├── context_analyzer.py (standalone - only imports logger)
├── localization_engine.py (standalone - only imports config, logger)
├── cultural_adapter.py (standalone - no dependencies)
├── quality_validation.py (standalone - no dependencies)
├── models.py (standalone - pure SQLAlchemy)
└── database.py (standalone - creates engine, imports models)
```

### Why This Works

1. **Context Analyzer** - Pure NLP functions, no framework dependencies
2. **Localization Engine** - Calls external APIs (OpenAI), no circular refs
3. **Cultural Adapter** - Static idiom database, no frame work dependencies
4. **Quality Validator** - Grammar tool, no framework dependencies
5. **Models** - Pure SQLAlchemy declarative models
6. **app.py** - Imports all above (top-level only), no cross-imports

### Import Structure in app.py

```python
# Stage 1: Context Analysis (pure functions)
from app.services.context_analyzer import (
    detect_language,
    analyze_sentiment,
    get_text_characteristics
)

# Stage 2: Localization Engine (API integration)
from app.services.localization_engine import LocalizationEngine

# Stage 3: Cultural Adaptation (static data)
from app.services.cultural_adapter import CulturalAdapterEngine

# Stage 4: Quality Validation (tool integration)
from app.services.quality_validation import check_grammar

# Stage 5: Database Models (ORM)
from app.models import (
    Base, User, LocalizationHistory,
    CulturalAdaptation, Feedback, Analytics
)

# Stage 6: Utilities
from app.core.logger import get_logger
```

---

## Localization Pipeline

### Complete Pipeline (9 Stages)

```
User Request (text, target_lang, tone)
         ↓
    [VALIDATION]
         ↓
[1. LANGUAGE DETECTION] → detect_language(text)
         ↓
[2. SENTIMENT ANALYSIS] → analyze_sentiment(text)
         ↓
[3. TEXT CHARACTERISTICS] → get_text_characteristics(text)
         ↓
[4. TRANSLATION] → LocalizationEngine.localize(...)
         ↓
[5. CULTURAL ADAPTATION] → CulturalAdapterEngine.adapt(...)
         ↓
[6. QUALITY VALIDATION] → check_grammar(text, language)
         ↓
[7. QUALITY SCORING] → Calculate composite score
         ↓
[8. DATABASE SAVE] → Save localization + adaptations
         ↓
[9. RESPONSE] → Return to user
```

### Stage Details

#### Stage 1: Language Detection
```python
detected_language = detect_language(text)
# Input: "Bonjour le monde"
# Output: "fr"
# Supports: en, es, fr, de, hi, pt, ja, zh, ar, ru, ko, it
```

#### Stage 2: Sentiment Analysis
```python
sentiment = analyze_sentiment(text)
# Input: "I love this product!"
# Output: "positive"
# Returns: positive, negative, neutral
```

#### Stage 3: Text Characteristics
```python
characteristics = get_text_characteristics(text)
# Output: {
#   "word_count": 42,
#   "char_count": 250,
#   "is_question": False,
#   "has_urls": False,
#   "is_technical": False
# }
```

#### Stage 4: Translation with AI
```python
result = LocalizationEngine.localize(
    text="Once in a blue moon",
    source_language="en",
    target_language="es",
    tone="casual",
    sentiment_hint="neutral"
)
# Output: {
#   "localized_text": "De vez en cuando",
#   "explanation": "...",
#   "quality_score": 92
# }
```

#### Stage 5: Cultural Adaptation
```python
adaptations = CulturalAdapterEngine.adapt(
    text="De vez en cuando",
    source_language="en",
    target_language="es"
)
# Output: [
#   {
#     "source_idiom": "once in a blue moon",
#     "target_idiom": "de vez en cuando",
#     "equivalence_type": "direct",
#     "semantic_preservation": 0.95
#   }
# ]
```

#### Stage 6: Grammar Validation
```python
validation = check_grammar("De vez en cuando", lang="es")
# Output: {
#   "is_fluent": True,
#   "issue_count": 0,
#   "issues": []
# }
```

#### Stage 7: Quality Score Calculation
```
Quality Score = (Translation Quality × 0.7) + (Grammar Score × 0.3)
              = (92 × 0.7) + (100 × 0.3)
              = 64.4 + 30
              = 94.4 (out of 100)
```

#### Stage 8: Database Save
```python
# LocalizationHistory record saved with:
LocalizationHistory(
    request_id=uuid,
    user_id=user_id,
    source_text="Once in a blue moon",
    localized_text="De vez en cuando",
    source_language="en",
    target_language="es",
    quality_score=94.4,
)

# CulturalAdaptation records also saved
```

#### Stage 9: Return Response
```json
{
  "success": true,
  "data": {
    "original_text": "Once in a blue moon",
    "detected_language": "en",
    "sentiment": "neutral",
    "localized_text": "De vez en cuando",
    "explanation": "Idiom translation...",
    "request_id": "uuid-1234",
    "quality_score": 94.4,
    "tone": "casual",
    "target_language": "es"
  }
}
```

---

## API Endpoints

### 1. Health Check

```
GET /health

Response:
{
  "status": "healthy",
  "database": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-15T10:30:45.123456"
}
```

### 2. Root Endpoint

```
GET /

Response:
{
  "app": "AI Content Localization Platform",
  "version": "1.0.0",
  "environment": "development",
  "endpoints": {
    "health": "GET /health",
    "localize": "POST /api/localize",
    "feedback": "POST /api/feedback",
    "history": "GET /api/history"
  }
}
```

### 3. Localization (Main Endpoint)

```
POST /api/localize

Request:
{
  "text": "Hello world",
  "target_language": "es",
  "tone": "casual",
  "user_id": "user123" (optional)
}

Response (Success):
{
  "success": true,
  "data": {
    "original_text": "Hello world",
    "detected_language": "en",
    "sentiment": "neutral",
    "localized_text": "Hola mundo",
    "explanation": "...",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "quality_score": 95.5,
    "tone": "casual",
    "target_language": "es",
    "adaptations": [...]
  }
}

Response (Error):
{
  "success": false,
  "error": "ValidationError",
  "details": "Text cannot be empty"
}
```

### 4. Feedback

```
POST /api/feedback

Request:
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "rating": 5,
  "comment": "Excellent translation!",
  "user_id": "user123" (optional),
  "aspects": {
    "accuracy": 5,
    "tone_preserved": true,
    "cultural_fit": 5,
    "readability": 5
  }
}

Response:
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": "uuid-5678"
}
```

### 5. History

```
GET /api/history?user_id=user123&limit=20&offset=0

Response:
{
  "success": true,
  "data": [
    {
      "request_id": "uuid-1",
      "user_id": "user123",
      "source_text": "Hello world",
      "localized_text": "Hola mundo",
      "source_language": "en",
      "target_language": "es",
      "sentiment": "neutral",
      "tone": "casual",
      "quality_score": 95.5,
      "created_at": "2026-03-15T10:30:45",
      "feedback": {
        "feedback_id": "uuid-5678",
        "rating": 5,
        "comment": "Excellent!",
        "created_at": "2026-03-15T10:31:00"
      }
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0
  }
}
```

---

## Error Handling

### Error Flow

```
User Request
    ↓
Validation (400 Bad Request)
    ↓
Module Processing
    ├─ LanguageDetectionError → 400
    ├─ LocalizationEngineError → 400
    ├─ CulturalAdaptationError → 400
    ├─ ValidationError → 400
    └─ Unexpected Exception → 500
    ↓
Database Error → 500
    ↓
Error Response to User
```

### Error Response Format

```json
{
  "success": false,
  "error": "ErrorTypeName",
  "details": "Human-readable error message"
}
```

### Common Errors

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| ValidationError | 400 | Empty text or invalid language | Provide non-empty text and valid 2-letter language |
| LanguageDetectionError | 400 | Cannot detect language | Use text in a supported language |
| LocalizationEngineError | 400 | Translation failed | Check OpenAI API key and quota |
| CulturalAdaptationError | 400 | Adaptation failed | Non-critical; continues pipeline |
| ValidationError (grammar) | 400 | Invalid tone | Use: formal, casual, marketing, neutral |
| SQLAlchemyError | 500 | Database error | Check database connection |

---

## Running the Server

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Create .env file with:
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./localization.db
OPENAI_MODEL=gpt-4o-mini
DEBUG=False
ENVIRONMENT=development
```

### Start Server

```bash
# From project root
python app.py

# Output:
# ======================================================================
# Starting AI Content Localization Platform
# Version: 1.0.0
# Environment: development
# Database: sqlite:///./localization.db
# ======================================================================
# ✓ Database initialized successfully
# ✓ Application initialized successfully
# * Running on http://0.0.0.0:5000
```

### Access Points

- **API Base**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **API Docs**: See examples below

---

## Example Requests

### Using cURL

```bash
# 1. Localize English to Spanish
curl -X POST http://localhost:5000/api/localize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The ball is in your court",
    "target_language": "es",
    "tone": "formal",
    "user_id": "user123"
  }'

# 2. Submit feedback
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "rating": 5,
    "comment": "Perfect translation!",
    "user_id": "user123"
  }'

# 3. Get history
curl http://localhost:5000/api/history?user_id=user123&limit=10

# 4. Health check
curl http://localhost:5000/health
```

### Using Python Requests

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# 1. Localize
payload = {
    "text": "It's raining cats and dogs",
    "target_language": "fr",
    "tone": "casual",
    "user_id": "user123"
}

response = requests.post(
    f"{BASE_URL}/api/localize",
    json=payload,
    headers={"Content-Type": "application/json"}
)

result = response.json()
print(f"Status: {result['success']}")
print(f"Localized: {result['data']['localized_text']}")
request_id = result['data']['request_id']

# 2. Submit feedback
feedback = {
    "request_id": request_id,
    "rating": 5,
    "comment": "Excellent!",
    "user_id": "user123"
}

response = requests.post(
    f"{BASE_URL}/api/feedback",
    json=feedback
)

print(response.json())

# 3. Get history
response = requests.get(
    f"{BASE_URL}/api/history",
    params={"user_id": "user123", "limit": 20}
)

history = response.json()
print(f"Total records: {history['pagination']['total']}")
for record in history['data']:
    print(f"- {record['source_text']} → {record['localized_text']}")
```

### Using JavaScript Fetch

```javascript
const BASE_URL = "http://localhost:5000";

// 1. Localize
async function localize() {
  const payload = {
    text: "Once in a blue moon",
    target_language: "de",
    tone: "formal",
    user_id: "user123"
  };

  const response = await fetch(`${BASE_URL}/api/localize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  console.log(result.data.localized_text);
  return result.data.request_id;
}

// 2. Submit feedback
async function submitFeedback(requestId) {
  const feedback = {
    request_id: requestId,
    rating: 5,
    comment: "Great translation!",
    user_id: "user123"
  };

  const response = await fetch(`${BASE_URL}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(feedback)
  });

  const result = await response.json();
  console.log(result.message);
}

// 3. Get history
async function getHistory() {
  const response = await fetch(
    `${BASE_URL}/api/history?user_id=user123&limit=10`
  );

  const result = await response.json();
  result.data.forEach(item => {
    console.log(`${item.source_text} → ${item.localized_text}`);
  });
}

// Usage
localize()
  .then(requestId => submitFeedback(requestId))
  .then(() => getHistory());
```

---

## Module Interactions

### LocalizationService Class

The `LocalizationService` class orchestrates all modules:

```python
class LocalizationService:
    """
    Coordinates the complete localization pipeline.
    Interactions with all modules happen here.
    """
    
    def __init__(self, db_session):
        # Initialize module engines
        self.localization_engine = LocalizationEngine()
        self.cultural_adapter = CulturalAdapterEngine()
        self.db = db_session
    
    def localize(self, text, target_language, tone, user_id):
        # Stage 1: Call context_analyzer module
        detected_language = self._detect_language(text)
        sentiment = self._analyze_sentiment(text)
        characteristics = self._get_characteristics(text)
        
        # Stage 2: Call localization engine module
        localized = self._translate(
            text, detected_language, target_language, tone, sentiment
        )
        
        # Stage 3: Call cultural adapter module
        adaptations = self._apply_cultural_adaptation(
            localized["text"], detected_language, target_language
        )
        
        # Stage 4: Call quality validator module
        validation = self._validate_quality(localized["text"], target_language)
        
        # Stage 5: Save to database (models)
        self._save_localization(...)
        
        # Stage 6: Return unified response
        return {
            "original_text": text,
            "detected_language": detected_language,
            "sentiment": sentiment,
            "localized_text": localized["text"],
            ...
        }
```

### Inter-Module Communication

```
Context Analyzer → LocalizationService
├─ detect_language(text) → language code
├─ analyze_sentiment(text) → sentiment label
└─ get_text_characteristics(text) → metadata dict

LocalizationEngine → LocalizationService
├─ localize(...) → {
│    "localized_text": str,
│    "explanation": str,
│    "quality_score": float
│  }

CulturalAdapterEngine → LocalizationService
├─ adapt(...) → [
│    {
│      "source_idiom": str,
│      "target_idiom": str,
│      "equivalence_type": str,
│      "semantic_preservation": float
│    }
│  ]

QualityValidator → LocalizationService
├─ check_grammar(text, lang) → {
│    "is_fluent": bool,
│    "issue_count": int,
│    "issues": list
│  }

Database Models → LocalizationService
├─ LocalizationHistory.add()
├─ CulturalAdaptation.add()
├─ Feedback.add()
└─ User.query()
```

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    User Request                              │
│  {text, target_language, tone, user_id}                      │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
            ┌──────────────────────┐
            │ LocalizationService  │ (Orchestration)
            └──────────────────────┘
         ┌─────────┬────────┬────────┬─────────┐
         ↓         ↓        ↓        ↓         ↓
    [Analyzer] [Engine] [Adapter] [Validator] [DB]
         ↓         ↓        ↓        ↓         ↓
    lang, sent  localized cultural quality   saved
    ↓ ↓ ↓
    └─────┬─────┘
          ↓
    ┌──────────────────┐
    │ Response Dict    │
    └────────┬─────────┘
             ↓
    ┌──────────────────┐
    │ JSON to Frontend │
    └──────────────────┘
```

---

## Deployment Considerations

### Development

```bash
python app.py
# Runs on localhost:5000
# SQLite database file: localization.db
```

### Production

```bash
# Use production WSGI server (Gunicorn)
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Or with environment variables
ENVIRONMENT=production DEBUG=False DATABASE_URL=postgresql://... \
  gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Database Migration

```bash
# Development: SQLite
DATABASE_URL=sqlite:///./localization.db

# Production: PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/database

# All code works the same - just change DATABASE_URL!
```

---

## Testing

### Unit Test Example

```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_localize(client):
    payload = {
        "text": "Hello world",
        "target_language": "es"
    }
    response = client.post('/api/localize', json=payload)
    assert response.status_code == 200
    assert response.json['success'] == True
    assert 'localized_text' in response.json['data']

def test_feedback(client):
    # First localize
    payload = {
        "text": "Hello world",
        "target_language": "es"
    }
    loc_response = client.post('/api/localize', json=payload)
    request_id = loc_response.json['data']['request_id']
    
    # Then submit feedback
    feedback = {
        "request_id": request_id,
        "rating": 5,
        "comment": "Great!"
    }
    response = client.post('/api/feedback', json=feedback)
    assert response.status_code == 201
    assert response.json['success'] == True
```

### Run Tests

```bash
pytest tests/ -v
pytest tests/test_api.py::test_localize -v
```

---

## Monitoring & Logging

### Log Levels

```python
# In app/core/logger.py
logger.debug("Detailed diagnostic info")    # Development
logger.info("General information")          # Status updates
logger.warning("Warning messages")          # Non-critical issues
logger.error("Error messages")              # Failures
```

### Example Log Output

```
2026-03-15 10:30:45.123 INFO Starting AI Content Localization Platform
2026-03-15 10:30:45.234 INFO Version: 1.0.0
2026-03-15 10:30:45.345 INFO Database: sqlite:///./localization.db
2026-03-15 10:30:45.456 DEBUG Starting localization pipeline (ID: 550e8400...)
2026-03-15 10:30:45.567 INFO Detected language: en
2026-03-15 10:30:45.678 INFO Detected sentiment: neutral
2026-03-15 10:30:45.789 DEBUG Text characteristics: {'word_count': 3, ...}
2026-03-15 10:30:46.123 INFO Translation completed
2026-03-15 10:30:46.234 INFO Applied 1 cultural adaptations
2026-03-15 10:30:46.345 INFO Quality validation completed (score: 94.4)
2026-03-15 10:30:46.456 INFO ✓ Pipeline completed successfully (ID: ...)
```

---

## Troubleshooting

### Q: "ModuleNotFoundError: No module named 'app'"
**A:** Make sure you're running from the project root directory:
```bash
cd /path/to/mini\ projecttt/backend
python app.py
```

### Q: "OPENAI_API_KEY not set"
**A:** Create `.env` file in backend directory:
```
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./localization.db
```

### Q: "Database is locked"
**A:** This happens with SQLite under concurrent load. Use PostgreSQL for production:
```bash
DATABASE_URL=postgresql://user:pass@localhost/db python app.py
```

### Q: "Module 'app.services.cultural_adapter' has no attribute 'CulturalAdapterEngine'"
**A:** Check that `cultural_adapter.py` exports the class correctly. It should have:
```python
class CulturalAdapterEngine:
    def adapt(self, text, source_language, target_language):
        ...
```

---

## Summary

This Flask application successfully integrates all backend modules:

✅ **Context Analyzer** - Detects language & sentiment  
✅ **Localization Engine** - AI-powered translation  
✅ **Cultural Adapter** - Idiom and expression adaptation  
✅ **Quality Validator** - Grammar and fluency checking  
✅ **Database Models** - Persistent storage with SQLAlchemy  
✅ **Error Handling** - Comprehensive exception management  
✅ **API Endpoints** - RESTful routes for frontend integration  
✅ **No Circular Imports** - Clean dependency structure  
✅ **Production Ready** - Logging, security, performance  
✅ **Easy Deployment** - Single command: `python app.py`  

All modules work together in a seamless pipeline to provide intelligent, culturally-aware text localization.
