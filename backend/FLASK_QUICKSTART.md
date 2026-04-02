# Flask Application - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Navigate to backend directory
cd backend

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

### Step 2: Configure Environment

Create a `.env` file in the `backend` directory:

```bash
# .env
OPENAI_API_KEY=sk-your_actual_key_here
DATABASE_URL=sqlite:///./localization.db
OPENAI_MODEL=gpt-4o-mini
DEBUG=True
ENVIRONMENT=development
```

**Get OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy and paste in `.env`

### Step 3: Start the Server

```bash
python app.py
```

**Expected Output:**
```
======================================================================
Starting AI Content Localization Platform
Version: 1.0.0
Environment: development
Database: sqlite:///./localization.db
======================================================================
✓ Database initialized successfully
✓ Application initialized successfully
 * Running on http://0.0.0.0:5000
```

### Step 4: Test the API

Open another terminal and test:

```bash
# Health check
curl http://localhost:5000/health

# Localize English to Spanish
curl -X POST http://localhost:5000/api/localize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_language": "es",
    "tone": "casual"
  }'
```

✅ You're done! The server is running.

---

## 📊 API Endpoints

### 1. POST /api/localize - Main Translation Endpoint

```bash
curl -X POST http://localhost:5000/api/localize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Once in a blue moon",
    "target_language": "fr",
    "tone": "formal",
    "user_id": "user_123"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original_text": "Once in a blue moon",
    "detected_language": "en",
    "sentiment": "neutral",
    "localized_text": "De temps en temps",
    "explanation": "Idiom translation...",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "quality_score": 94.5,
    "tone": "formal",
    "target_language": "fr"
  }
}
```

**Parameters:**
- `text` (required) - Text to translate
- `target_language` (required) - Language code: es, fr, de, it, pt, hi, ja, zh, kr, ar, ru
- `tone` (optional) - formal, casual, marketing, technical, neutral
- `user_id` (optional) - User ID for tracking

---

### 2. POST /api/feedback - Submit Feedback

```bash
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "rating": 5,
    "comment": "Perfect translation!",
    "user_id": "user_123"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": "uuid-feedback-123"
}
```

---

### 3. GET /api/history - Get Translation History

```bash
# Get user's history
curl http://localhost:5000/api/history?user_id=user_123&limit=10

# Get history for specific language
curl http://localhost:5000/api/history?target_language=es&limit=20
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "request_id": "uuid-1",
      "user_id": "user_123",
      "source_text": "Hello world",
      "localized_text": "Hola mundo",
      "source_language": "en",
      "target_language": "es",
      "sentiment": "neutral",
      "tone": "casual",
      "quality_score": 95.5,
      "created_at": "2026-03-15T10:30:45"
    }
  ],
  "pagination": {
    "total": 42,
    "limit": 10,
    "offset": 0
  }
}
```

---

### 4. GET /health - Health Check

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-15T10:30:45.123456"
}
```

---

## 🧪 Complete Example Workflow

### Step 1: Translate Text

```bash
# Save response to file
curl -X POST http://localhost:5000/api/localize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The ball is in your court",
    "target_language": "de",
    "tone": "casual"
  }' > response.json

# Extract request_id
cat response.json | grep -o '"request_id":"[^"]*"' | cut -d'"' -f4
# Output: 550e8400-e29b-41d4-a716-446655440000
```

### Step 2: Submit Feedback

```bash
REQUEST_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d "{
    \"request_id\": \"$REQUEST_ID\",
    \"rating\": 5,
    \"comment\": \"Excellent translation!\"
  }"
```

### Step 3: View History

```bash
curl http://localhost:5000/api/history?limit=5
```

---

## 🐍 Python Client Example

Create `client.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000"

class LocalizationClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def localize(self, text, target_language, tone="neutral", user_id=None):
        """Translate text to target language"""
        payload = {
            "text": text,
            "target_language": target_language,
            "tone": tone,
            "user_id": user_id
        }
        
        response = requests.post(
            f"{self.base_url}/api/localize",
            json=payload
        )
        
        return response.json()
    
    def feedback(self, request_id, rating, comment="", user_id=None):
        """Submit feedback on translation"""
        payload = {
            "request_id": request_id,
            "rating": rating,
            "comment": comment,
            "user_id": user_id
        }
        
        response = requests.post(
            f"{self.base_url}/api/feedback",
            json=payload
        )
        
        return response.json()
    
    def history(self, user_id=None, limit=20, offset=0):
        """Get translation history"""
        params = {
            "limit": limit,
            "offset": offset
        }
        if user_id:
            params["user_id"] = user_id
        
        response = requests.get(
            f"{self.base_url}/api/history",
            params=params
        )
        
        return response.json()


# Usage
if __name__ == "__main__":
    client = LocalizationClient()
    
    # Translate
    result = client.localize(
        text="The early bird catches the worm",
        target_language="es",
        tone="formal",
        user_id="user_001"
    )
    
    print("Translation:")
    print(f"  Original: {result['data']['original_text']}")
    print(f"  Localized: {result['data']['localized_text']}")
    print(f"  Quality: {result['data']['quality_score']}/100")
    
    request_id = result['data']['request_id']
    
    # Submit feedback
    feedback_result = client.feedback(
        request_id=request_id,
        rating=5,
        comment="Perfect idiom translation!",
        user_id="user_001"
    )
    print(f"\n✓ {feedback_result['message']}")
    
    # Get history
    history = client.history(user_id="user_001", limit=5)
    print(f"\nTranslation history ({history['pagination']['total']} total):")
    for item in history['data']:
        print(f"  - {item['source_text']} → {item['localized_text']}")
```

Run it:
```bash
python client.py
```

---

## 🎯 Supported Languages

| Code | Language |
|------|----------|
| en | English |
| es | Spanish |
| fr | French |
| de | German |
| it | Italian |
| pt | Portuguese |
| hi | Hindi |
| ja | Japanese |
| zh | Chinese |
| ar | Arabic |
| ru | Russian |
| ko | Korean |

---

## 📋 Complete Pipeline Diagram

```
User Input
    ↓
[1] Detect Language
    ↓
[2] Analyze Sentiment
    ↓
[3] Get Text Characteristics
    ↓
[4] AI Translation (OpenAI)
    ↓
[5] Cultural Adaptation (Idioms)
    ↓
[6] Grammar Validation
    ↓
[7] Quality Scoring
    ↓
[8] Save to Database
    ↓
Response with metadata and quality score
    ↓
[Optional] User submits feedback
    ↓
Feedback saved for model improvement
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app'"

**Solution:** Make sure you're in the backend directory:
```bash
cd backend
python app.py
```

### Error: "OPENAI_API_KEY not set"

**Solution:** Create `.env` file with:
```
OPENAI_API_KEY=sk-...
```

### Error: "Database is locked"

**Solution:** Only one process should access SQLite at a time. If running tests, close the server first:
```bash
# In test environment, use in-memory database
export DATABASE_URL=sqlite:///:memory:
```

### Error: "Connection refused" when calling API

**Solution:** Make sure server is running:
```bash
python app.py  # In separate terminal
```

### Error: "All inputs rejected" from OpenAI

**Solution:** Check API key and rate limits:
```bash
# Verify API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 🔧 Development Tips

### Enable Debug Mode

In `.env`:
```
DEBUG=True
```

This will:
- Show detailed error messages
- Reload server on file changes
- Log all SQL queries

### Access SQLite Database Directly

```bash
# Interactive sqlite shell
sqlite3 localization.db

# View tables
.tables

# Query history
SELECT source_text, localized_text, quality_score FROM localization_history LIMIT 5;

# Count records
SELECT COUNT(*) FROM localization_history;
```

### View Server Logs

```bash
# All logs
tail -f server.log

# Only errors
grep ERROR server.log

# Real-time processing
python app.py 2>&1 | tee server.log
```

---

## 📦 Project Structure

```
backend/
├── app.py                          # Main Flask application
├── requirements.txt                # Dependencies
├── .env                            # Configuration (git-ignored)
├── localization.db                 # SQLite database (auto-created)
│
├── app/
│   ├── __init__.py
│   ├── models.py                   # Database models
│   ├── database.py                 # Database configuration
│   │
│   ├── services/
│   │   ├── context_analyzer.py     # Language detection, sentiment
│   │   ├── localization_engine.py  # AI translation
│   │   ├── cultural_adapter.py     # Idiom adaptation
│   │   └── quality_validation.py   # Grammar checking
│   │
│   └── core/
│       └── logger.py               # Logging configuration
│
└── tests/
    ├── test_api.py                 # API endpoint tests
    └── test_services.py            # Service unit tests
```

---

## 🚀 Next Steps

1. **Integrate with Frontend** - Update frontend API calls to use endpoints above
2. **Add Authentication** - Implement user login/API key validation
3. **Deploy to Production** - Use Gunicorn + PostgreSQL
4. **Monitor Performance** - Set up logging and metrics
5. **Optimize LLM Prompts** - Fine-tune translation quality
6. **Add More Languages** - Extend supported language list

---

## 📚 Full Documentation

For detailed information, see:

- [FLASK_INTEGRATION_GUIDE.md](FLASK_INTEGRATION_GUIDE.md) - Complete architecture and module interaction
- [DATABASE_QUICK_REFERENCE.md](DATABASE_QUICK_REFERENCE.md) - Database schema reference
- [DATABASE_DESIGN.md](DATABASE_DESIGN.md) - Complete database design
- [CULTURAL_ADAPTATION_ALGORITHM.md](CULTURAL_ADAPTATION_ALGORITHM.md) - Idiom adaptation logic

---

## 📞 Support

For issues or questions:

1. Check [FLASK_INTEGRATION_GUIDE.md](FLASK_INTEGRATION_GUIDE.md) > Troubleshooting section
2. Review error logs: `tail -f server.log`
3. Test with [client.py](#python-client-example) example
4. Check database: `sqlite3 localization.db`

---

**Happy localizing! 🌍**
