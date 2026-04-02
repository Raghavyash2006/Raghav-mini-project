# Backend Architecture Guide

## Overview

The AI Content Localization Platform backend is built with **FastAPI**, providing REST APIs for content localization with AI-powered cultural adaptation.

### Core Features

- ✅ **Language Detection**: Automatically detects source language
- ✅ **Sentiment Analysis**: Analyzes emotional tone
- ✅ **AI Localization**: Uses OpenAI API for culturally-aware translation
- ✅ **Quality Tracking**: Stores ratings and feedback
- ✅ **History Management**: Full audit trail of localizations
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **Database Persistence**: SQLite/PostgreSQL support

---

## Module Breakdown

### 1. **Input Processing** (`input_processing.py`)

**Purpose**: Cleans and normalizes input text before processing.

**Key Functions**:
- `clean_input(text: str)` - Removes special characters, normalizes whitespace, fixes encoding issues
- `normalize_text(text: str)` - Standardizes quotes, spacing, and encoding

**Why This Matters**:
- Ensures consistent processing
- Fixes encoding issues from different sources
- Prevents injection attacks

**Example**:
```python
from app.services import input_processing

dirty_text = "  Hello  "world"  "
clean_text = input_processing.clean_input(dirty_text)
# Result: 'Hello "world"'
```

---

### 2. **Context Analyzer** (`context_analyzer.py`)

**Purpose**: Extracts linguistic and contextual information from text.

**Key Functions**:

#### `detect_language(text: str) -> str`
Uses `langdetect` library to identify language.
- Returns ISO 639-1 codes: 'en', 'fr', 'es', 'de', etc.
- Defaults to 'en' if detection fails

```python
lang = context_analyzer.detect_language("Bonjour le monde")
# Returns: 'fr'
```

#### `analyze_sentiment(text: str) -> str`
Uses `TextBlob` for sentiment classification.
- Returns: 'positive', 'negative', or 'neutral'
- Based on polarity score (-1 to 1)

```python
sentiment = context_analyzer.analyze_sentiment("I love this!")
# Returns: 'positive'
```

#### `get_text_characteristics(text: str) -> Dict`
Extracts contextual metadata:
- `word_count`: Number of words
- `is_question`: Whether text ends with '?'
- `has_urls`: If text contains links
- `is_technical`: If contains technical terms

```python
chars = context_analyzer.get_text_characteristics("What is an API?")
# Returns: {'word_count': 4, 'is_question': True, 'has_urls': False, ...}
```

#### `analyze_context(text: str) -> Dict`
**Main orchestrator function** - combines all analysis into single output.

```python
context = context_analyzer.analyze_context("Great product!")
# Returns:
# {
#     'language': 'en',
#     'sentiment': 'positive',
#     'characteristics': {...}
# }
```

---

### 3. **Localization Engine** (`localization_engine.py`)

**Purpose**: Core AI-powered localization using OpenAI API.

**Key Functions**:

#### `generate_localization(...) -> Dict`
**Main function** - generates localized content with cultural adaptation.

**Parameters**:
- `text`: Original text
- `source_language`: Source language code
- `target_language`: Target language code  
- `tone`: 'formal', 'casual', 'marketing', 'neutral'
- `sentiment`: Detected sentiment
- `characteristics`: Text metadata

**Returns**:
```python
{
    "localized_text": "Hola a todos!",
    "explanation": "Casual Spanish greeting adapted for enthusiasm",
    "tone_applied": "casual",
    "cultural_adaptations": ["greeting_style", "punctuation"],
    "quality_score": 92.5
}
```

**Example Usage**:
```python
result = localization_engine.generate_localization(
    text="Hello everyone!",
    source_language="en",
    target_language="es",
    tone="casual",
    sentiment="positive",
    characteristics={"word_count": 2, "is_question": False}
)
```

**How It Works**:
1. Builds a detailed prompt with cultural context
2. Sends to OpenAI Chat API (gpt-4o-mini by default)
3. Receives JSON response with localization
4. Validates response structure
5. Returns result with quality score

**Prompt Structure**:
```
You are an expert localization specialist...
Original text: "Break a leg!"
Target language: Spanish
Requirements:
- Preserve tone and sentiment
- Adapt cultural references
- Consider technical content...
```

---

### 4. **Database Layer** (`db/`)

#### **Models** (`models.py`)

Two main tables:

**LocalizationRequest**
```python
- id: int (Primary Key)
- original_text: str - Input text
- source_language: str - Detected language code
- target_language: str - Target language code
- localized_text: str - AI output
- tone: str - Applied tone
- sentiment: str - Detected sentiment
- explanation: str - Why this localization
- quality_score: float - 0-100 rating
- created_at: datetime
- updated_at: datetime
```

**Feedback**
```python
- id: int (Primary Key)
- request_id: int (Foreign Key)
- rating: int - 1-5 stars
- comment: str - User feedback
- helpful: bool
- created_at: datetime
```

#### **CRUD Operations** (`crud.py`)

```python
# Create localization
request = crud.create_localization_request(session, request_model)

# Retrieve
request = crud.get_localization_request(session, request_id)

# Get history with filtering
requests = crud.get_localization_history(
    session, 
    skip=0, 
    limit=20,
    target_language='es'
)

# Store feedback
feedback = crud.create_feedback(session, feedback_model)

# Get feedback for request
feedback_list = crud.get_feedback_for_request(session, request_id)

# Average rating
avg = crud.get_average_rating(session, request_id)
```

---

### 5. **API Schemas** (`api/v1/schemas.py`)

Pydantic models defining exact API contracts.

#### Request/Response Examples

**POST /localize**
```json
Request:
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
  "explanation": "Casual Spanish greeting",
  "quality_score": 94.5
}
```

**GET /history**
```json
Response:
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

**POST /feedback**
```json
Request:
{
  "request_id": 1,
  "rating": 5,
  "comment": "Perfect translation!"
}

Response:
{
  "id": 42,
  "request_id": 1,
  "rating": 5,
  "comment": "Perfect translation!",
  "helpful": true
}
```

---

### 6. **API Routes** (`api/v1/routers.py`)

Three main endpoints:

#### **POST /v1/localize**
- **Input**: Text, target language, tone
- **Process**: Detect language → Analyze sentiment → Call AI → Store result
- **Output**: Localized text with explanation
- **Error Codes**: 400 (validation), 500 (AI error)

#### **GET /v1/history**
- **Query Params**: `page`, `limit`, `target_language` (optional filter)
- **Output**: Paginated history with total count
- **Error Codes**: 500 (database error)

#### **POST /v1/feedback**
- **Input**: Request ID, rating (1-5), comment
- **Process**: Validate request exists → Store feedback
- **Output**: Feedback confirmation
- **Error Codes**: 404 (request not found), 500 (storage error)

#### **GET /v1/health**
- Simple health check
- Returns: `{"status": "ok", "timestamp": "..."}`

---

### 7. **Configuration** (`core/config.py`)

Uses Pydantic Settings to manage environment variables:

```python
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./localization.db
OPENAI_MODEL=gpt-4o-mini
DEBUG=True
```

---

### 8. **Logging** (`core/logger.py`)

Centralized logging setup:

```python
logger = get_logger(__name__)
logger.info("User submitted localization request")
logger.warning("Language detection failed")
logger.error("Database connection error")
```

---

## Data Flow Diagram

```
User Request (JSON)
        ↓
  /v1/localize
        ↓
1. Input Processing (clean_input)
        ↓
2. Context Analysis (detect_language, sentiment)
        ↓
3. Generative Localization (OpenAI API call)
        ↓
4. Database Storage (LocalizationRequest table)
        ↓
JSON Response (LocalizeResponse schema)
        ↓
Frontend Display
        ↓
User Feedback
        ↓
/v1/feedback
        ↓
Store in Feedback table
```

---

## Error Handling Strategy

### Validation Errors (400)
```python
# Text empty
{"error": "VALIDATION_ERROR", "message": "Text cannot be empty"}

# Target language missing
{"error": "VALIDATION_ERROR", "message": "target_language is required"}
```

### Runtime Errors (500)
```python
# OpenAI API fails
{"error": "LOCALIZATION_ERROR", "message": "Localization generation failed"}

# Database error
{"error": "DATABASE_ERROR", "message": "Failed to store result"}
```

---

## Environment Setup

### .env file
```
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=sqlite:///./localization.db
OPENAI_MODEL=gpt-4o-mini
DEBUG=True
```

### Installation
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Running
```bash
uvicorn app.main:app --reload --port 8000
```

---

## Testing the Backend

### Test 1: Simple Localization
```bash
curl -X POST http://localhost:8000/v1/localize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world!",
    "target_language": "fr",
    "tone": "casual"
  }'
```

### Test 2: Get History
```bash
curl http://localhost:8000/v1/history?page=1&limit=10
```

### Test 3: Submit Feedback
```bash
curl -X POST http://localhost:8000/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": 1,
    "rating": 5,
    "comment": "Great translation!"
  }'
```

### Test 4: Health Check
```bash
curl http://localhost:8000/v1/health
```

---

## Key Design Decisions

| Decision | Why |
|----------|-----|
| **FastAPI** | Fast, auto-docs, async support, easy to deploy |
| **SQLModel** | SQLAlchemy + Pydantic = type safety + ORM |
| **TextBlob** | Pure Python sentiment, no C++ compilation |
| **langdetect** | Lightweight language detection |
| **OpenAI API** | State-of-the-art localization quality |
| **SQLite/PostgreSQL** | Flexible: SQLite for dev, Postgres for prod |

---

## Next Steps

1. ✅ Backend API complete
2. 📝 Add pytest unit tests
3. 📝 Integrate with Frontend React app
4. 📝 Deploy to Render
5. 📝 Setup CI/CD with GitHub Actions

