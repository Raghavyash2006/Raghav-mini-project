# Backend Setup & Run Guide

This guide will walk you through setting up and running the AI Content Localization Backend.

---

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Windows PowerShell or Linux/Mac terminal
- OpenAI API Key (create at https://platform.openai.com/api-keys)

---

## Step 1: Create API Key

Before running the backend, you need an OpenAI API key:

1. Visit https://platform.openai.com/api-keys
2. Sign up or log in with your account
3. Click "Create new secret key"
4. Copy the key
5. **Store it safely** - you'll need it in step 3

---

## Step 2: Navigate to Backend Directory

```bash
cd "c:\Users\vansh\Downloads\OneDrive\Desktop\mini projecttt\backend"
```

Verify you see:
- `app/` folder
- `requirements.txt`
- `.env` file

---

## Step 3: Configure Environment Variables

Edit the `.env` file:

```bash
# Open the file (Windows)
notepad .env

# Or use any text editor and add/update:
OPENAI_API_KEY=sk-your-actual-key-here
DATABASE_URL=sqlite:///./localization.db
OPENAI_MODEL=gpt-4o-mini
DEBUG=True
```

**Important**: Replace `sk-your-actual-key-here` with your actual OpenAI API key.

---

## Step 4: Create Python Virtual Environment

A virtual environment isolates project dependencies from your system Python.

### On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### On Mac/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Verify activation** - your terminal prompt should show `(.venv)` prefix.

---

## Step 5: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

This installs:
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sqlmodel** - Database ORM
- **langdetect** - Language detection
- **textblob** - Sentiment analysis
- **openai** - OpenAI API client
- Other utilities

**Installation time**: ~2-3 minutes

**Expected output**:
```
Successfully installed fastapi-0.112.1 uvicorn-0.24.0 sqlmodel-0.0.8 ... [many packages]
```

---

## Step 6: Verify Installation

```bash
# Check Python version
python --version

# Check if packages installed correctly
pip list

# Test importing key packages
python -c "import fastapi; import sqlmodel; import openai; print('All imports successful!')"
```

Expected output:
```
All imports successful!
```

---

## Step 7: Run the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Will watch for changes in these directories: ['C:\...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Application startup complete
```

The `--reload` flag watches for code changes and auto-restarts the server during development.

---

## Step 8: Test the Backend

Open another terminal window (keep server running) and test endpoints:

### Test 1: Health Check
```bash
curl http://localhost:8000/v1/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2024-03-15T..."}
```

### Test 2: Simple Localization
```bash
curl -X POST http://localhost:8000/v1/localize ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Hello world!\", \"target_language\": \"es\", \"tone\": \"casual\"}"
```

Expected response:
```json
{
  "request_id": 1,
  "original_text": "Hello world!",
  "detected_language": "en",
  "localized_text": "¡Hola mundo!",
  "tone": "casual",
  "sentiment": "neutral",
  "explanation": "...",
  "quality_score": 95.0
}
```

### Test 3: Get History
```bash
curl http://localhost:8000/v1/history?page=1&limit=10
```

### Test 4: Submit Feedback
```bash
curl -X POST http://localhost:8000/v1/feedback ^
  -H "Content-Type: application/json" ^
  -d "{\"request_id\": 1, \"rating\": 5, \"comment\": \"Great!\"}"
```

---

## Step 9: Explore Interactive Docs

FastAPI automatically generates interactive API documentation:

1. **Swagger UI** (Recommended):
   - Open: http://localhost:8000/v1/docs
   - Interactive API explorer with "Try it out" button

2. **ReDoc** (Alternative):
   - Open: http://localhost:8000/v1/redoc
   - Clean, readable API documentation

3. **OpenAPI JSON**:
   - View: http://localhost:8000/v1/openapi.json
   - Raw API schema

---

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routers.py      ← Main API endpoints
│   │       └── schemas.py      ← Request/Response schemas
│   ├── core/
│   │   ├── config.py           ← Settings & environment
│   │   └── logger.py           ← Logging setup
│   ├── db/
│   │   ├── models.py           ← Database models
│   │   ├── crud.py             ← Database operations
│   │   └── session.py          ← Database connection
│   ├── services/
│   │   ├── input_processing.py ← Text cleaning
│   │   ├── context_analyzer.py ← Language & sentiment
│   │   └── localization_engine.py ← AI localization
│   └── main.py                 ← FastAPI app initialization
├── requirements.txt            ← Python dependencies
├── .env                        ← Environment variables
└── localization.db            ← SQLite database (created on first run)
```

---

## Common Issues & Solutions

### Issue 1: "Module not found" or "No module named"
**Cause**: Virtual environment not activated or packages not installed

**Solution**:
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements.txt
```

### Issue 2: OpenAI API Error - "Invalid API key"
**Cause**: `OPENAI_API_KEY` not set or incorrect

**Solution**:
1. Check `.env` file has valid key
2. Key should start with `sk-`
3. Verify key in https://platform.openai.com/api-keys
4. Restart server after updating `.env`

### Issue 3: "Address already in use" (Port 8000)
**Cause**: Another process using port 8000

**Solution**:
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill existing process (Windows PowerShell):
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

### Issue 4: Database locked error
**Cause**: Multiple processes accessing SQLite simultaneously

**Solution**:
1. Only run one server instance
2. For production, use PostgreSQL instead of SQLite

### Issue 5: SSL Certificate Error with OpenAI
**Cause**: Certificate validation issue

**Solution**:
```bash
# This is usually fine - OpenAI API is secure
# If issues persist, update certificates:
pip install --upgrade certifi
```

---

## Database Management

### Inspect Database
```bash
# Install sqlite3 if needed
pip install sqlite3

# View tables
sqlite3 localization.db ".tables"

# View schema
sqlite3 localization.db ".schema localizationrequest"

# Query data
sqlite3 localization.db "SELECT * FROM localizationrequest LIMIT 5;"
```

### Reset Database
```bash
# Delete old database
rm localization.db

# Restart server - new database will be created
uvicorn app.main:app --reload --port 8000
```

---

## Upgrade to PostgreSQL (Production)

To use PostgreSQL instead of SQLite:

1. Install PostgreSQL from https://www.postgresql.org/download/
2. Create database:
   ```sql
   CREATE DATABASE localization_db;
   ```
3. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/localization_db
   ```
4. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```
5. Restart server

---

## Production Deployment

### Using Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### Using Docker
```bash
docker build -t localization-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... localization-backend
```

### Deployment Platforms
- **Render.com**: `render.yaml` configuration in repo
- **Heroku**: `Procfile` needed
- **AWS**: Deploy container to ECS/EKS
- **Digital Ocean**: App Platform

---

## Development Commands

### Run Tests
```bash
pytest -v
```

### Format Code
```bash
black app/
```

### Check Code Quality
```bash
flake8 app/
```

### View Logs
```bash
# Server output shows logs
# Clean logs with Ctrl+C and restart
```

---

## Next Steps

1. ✅ Backend running successfully
2. 📝 Connect frontend (React) to this API
3. 📝 Test end-to-end flow
4. 📝 Deploy to Render

---

## Support

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **OpenAI Docs**: https://platform.openai.com/docs
- **SQLModel Docs**: https://sqlmodel.tiangolo.com
- **Issues**: Check GitHub issues or create detailed problem description with logs

