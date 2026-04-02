# API Specification

## Base URL
```
http://localhost:8000/v1
```

## Authentication
Currently, all endpoints are public. JWT authentication can be added for production.

---

## Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/localize` | Generate localization |
| GET | `/history` | Retrieve history |
| POST | `/feedback` | Submit feedback |
| GET | `/health` | Health check |

---

## 1. POST /localize

Generate AI-powered localized content.

### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "text": "string (1-5000 chars, required)",
  "target_language": "string (ISO 639-1, required)",
  "tone": "string (formal|casual|marketing|neutral, default: neutral)"
}
```

### Response (200 OK)

```json
{
  "request_id": 1,
  "original_text": "Hello everyone!",
  "detected_language": "en",
  "localized_text": "¡Hola a todos!",
  "tone": "casual",
  "sentiment": "positive",
  "explanation": "Adapted informal Spanish greeting",
  "quality_score": 94.5
}
```

### Error Responses

**400 Bad Request** - Invalid input:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Text cannot be empty",
  "details": null
}
```

**500 Internal Server Error** - Processing failed:
```json
{
  "error": "LOCALIZATION_ERROR",
  "message": "Localization generation failed",
  "details": "OpenAI API error"
}
```

### Example Requests

#### cURL
```bash
curl -X POST http://localhost:8000/v1/localize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Break a leg!",
    "target_language": "es",
    "tone": "casual"
  }'
```

#### Python (requests)
```python
import requests

url = "http://localhost:8000/v1/localize"
payload = {
    "text": "Hello there!",
    "target_language": "fr",
    "tone": "formal"
}
response = requests.post(url, json=payload)
result = response.json()
print(result["localized_text"])
```

#### JavaScript (fetch)
```javascript
const response = await fetch('http://localhost:8000/v1/localize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hello everyone!',
    target_language: 'de',
    tone: 'casual'
  })
});
const result = await response.json();
console.log(result.localized_text);
```

---

## 2. GET /history

Retrieve paginated localization history.

### Request

**Query Parameters**:
```
page: integer (≥1, default: 1)
  - Page number (1-indexed)

limit: integer (1-100, default: 20)
  - Records per page

target_language: string (optional)
  - Filter by target language (e.g., 'es', 'fr')
```

### Response (200 OK)

```json
{
  "items": [
    {
      "request_id": 3,
      "original_text": "Good morning!",
      "detected_language": "en",
      "target_language": "es",
      "localized_text": "¡Buenos días!",
      "tone": "casual",
      "sentiment": "positive",
      "quality_score": 96.2,
      "created_at": "2024-03-15T10:30:00"
    },
    {
      "request_id": 2,
      "original_text": "Hello world",
      "detected_language": "en",
      "target_language": "fr",
      "localized_text": "Bonjour le monde",
      "tone": "neutral",
      "sentiment": "neutral",
      "quality_score": 98.1,
      "created_at": "2024-03-15T10:25:00"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

### Example Requests

#### Get First 20 Records
```bash
curl http://localhost:8000/v1/history?page=1&limit=20
```

#### Get Only Spanish Localizations
```bash
curl http://localhost:8000/v1/history?target_language=es&page=1
```

#### Get Second Page (Records 21-40)
```bash
curl http://localhost:8000/v1/history?page=2&limit=20
```

#### Python
```python
import requests

response = requests.get('http://localhost:8000/v1/history', params={
    'page': 1,
    'limit': 20,
    'target_language': 'es'
})
history = response.json()
for item in history['items']:
    print(f"{item['original_text']} → {item['localized_text']}")
```

---

## 3. POST /feedback

Submit user feedback for a localization result.

### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "request_id": integer (required, >0),
  "rating": integer (required, 1-5),
  "comment": "string (optional, max 500 chars)"
}
```

### Response (200 OK)

```json
{
  "id": 42,
  "request_id": 1,
  "rating": 5,
  "comment": "This translation is perfect!",
  "helpful": true
}
```

### Error Responses

**404 Not Found** - Request ID doesn't exist:
```json
{
  "error": "NOT_FOUND",
  "message": "Localization request 999 not found",
  "details": null
}
```

**400 Bad Request** - Invalid rating:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Rating must be between 1 and 5",
  "details": null
}
```

### Example Requests

#### cURL
```bash
curl -X POST http://localhost:8000/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": 1,
    "rating": 5,
    "comment": "Excellent work!"
  }'
```

#### Python
```python
import requests

url = "http://localhost:8000/v1/feedback"
payload = {
    "request_id": 1,
    "rating": 4,
    "comment": "Good, but slightly awkward phrasing"
}
response = requests.post(url, json=payload)
feedback = response.json()
print(f"Feedback ID: {feedback['id']}")
```

#### JavaScript
```javascript
const response = await fetch('http://localhost:8000/v1/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    request_id: 1,
    rating: 5,
    comment: 'Perfect translation!'
  })
});
const result = await response.json();
console.log(`Feedback ID: ${result.id}`);
```

---

## 4. GET /health

Simple health check endpoint (no auth required).

### Request
```
GET /health
```

### Response (200 OK)

```json
{
  "status": "ok",
  "timestamp": "2024-03-15T15:30:45.123456"
}
```

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Request successful |
| 400 | Bad request (validation error) |
| 404 | Resource not found |
| 422 | Unprocessable entity (schema error) |
| 500 | Internal server error |

---

## Input Validation Rules

### Text Field (in /localize)
- Minimum: 1 character
- Maximum: 5000 characters
- Cannot be empty or whitespace-only
- Special characters are allowed

### Target Language
- ISO 639-1 format (2-5 characters)
- Examples: 'en', 'es', 'fr', 'de', 'zh', 'ja'
- Case-insensitive

### Tone
- Must be one of: `formal`, `casual`, `marketing`, `neutral`
- Default: `neutral`
- Case-insensitive

### Rating (in /feedback)
- Integer from 1 to 5
- 1 = Poor
- 2 = Fair
- 3 = Good
- 4 = Very Good
- 5 = Excellent

---

## Common Use Cases

### Use Case 1: Localize Marketing Copy

```python
def localize_marketing_text(text, target_lang):
    response = requests.post(
        'http://localhost:8000/v1/localize',
        json={
            'text': text,
            'target_language': target_lang,
            'tone': 'marketing'
        }
    )
    return response.json()

result = localize_marketing_text(
    "Unlock your potential today!",
    "es"
)
print(result['localized_text'])
# Output: ¡Desbloquea tu potencial hoy!
```

### Use Case 2: Get Recent Spanish Translations

```python
response = requests.get(
    'http://localhost:8000/v1/history',
    params={'target_language': 'es', 'page': 1}
)
history = response.json()
print(f"Found {history['total']} Spanish translations")
```

### Use Case 3: Rate a Translation

```python
requests.post(
    'http://localhost:8000/v1/feedback',
    json={
        'request_id': 42,
        'rating': 5,
        'comment': 'Natural and culturally appropriate!'
    }
)
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:
- Implement per-IP rate limiting (e.g., 100 req/min)
- Implement per-user rate limiting with API keys
- Use `slowapi` library with FastAPI

---

## CORS Policy

**Current**: Allows all origins (`*`)
**Production**: Should specify exact frontend origins

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

---

## OpenAPI Documentation

Interactive API docs available at:
- **Swagger UI**: `http://localhost:8000/v1/docs`
- **ReDoc**: `http://localhost:8000/v1/redoc`
- **OpenAPI JSON**: `http://localhost:8000/v1/openapi.json`

