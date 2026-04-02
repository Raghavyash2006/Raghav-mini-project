# AI-Powered Content Localization Platform

A full-stack application that uses AI to localize content with cultural awareness, tone preservation, and sentiment analysis.

## 🎯 Key Features

- **AI-Powered Translation**: Uses OpenAI GPT-4o-mini for intelligent localization
- **Language Detection**: Automatically detects source language
- **Sentiment Preservation**: Maintains emotional tone across languages
- **Cultural Adaptation**: Adapts idioms, metaphors, and references appropriately
- **Tone Control**: Formal, casual, or marketing tone options
- **Quality Tracking**: Automatic quality scoring and user feedback system
- **API-First**: Clean REST API with interactive documentation
- **Database Persistence**: Full history of localizations and feedback
- **Production-Ready**: Error handling, validation, logging

## 📋 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database + Pydantic validation
- **OpenAI API** - GPT-4o-mini for localization
- **langdetect** - Language detection
- **TextBlob** - Sentiment analysis
- **uvicorn** - ASGI server
- **SQLite/PostgreSQL** - Database

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Vite** - Build tool and dev server

### Deployment
- **Docker** - Containerization
- **Render** - Cloud deployment (optional)
- **GitHub** - Source control

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API key (get at https://platform.openai.com/api-keys)

### Backend Setup

1. **Navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   source .venv/bin/activate     # Mac/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (edit `.env`):
   ```
   OPENAI_API_KEY=sk-your-key-here
   DATABASE_URL=sqlite:///./localization.db
   OPENAI_MODEL=gpt-4o-mini
   DEBUG=True
   ```

5. **Run backend**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   Backend should be running at: http://localhost:8000/v1/docs

### Frontend Setup

1. **Navigate to frontend** (new terminal):
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run frontend**:
   ```bash
   npm run dev
   ```

   Frontend should be running at: http://localhost:5173

## 📚 Project Structure

```
.
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── routers.py           # Main API endpoints
│   │   │   └── schemas.py           # Request/response schemas
│   │   ├── core/
│   │   │   ├── config.py            # Settings
│   │   │   └── logger.py            # Logging
│   │   ├── db/
│   │   │   ├── models.py            # Database models
│   │   │   ├── crud.py              # Database operations
│   │   │   └── session.py           # Database connection
│   │   ├── services/
│   │   │   ├── input_processing.py  # Text cleaning
│   │   │   ├── context_analyzer.py  # Language/sentiment
│   │   │   └── localization_engine.py # AI localization
│   │   └── main.py                  # App entry point
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── LocalizerForm.jsx
│   │   │   ├── OutputPreview.jsx
│   │   │   └── FeedbackWidget.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docs/                            # Documentation
│   ├── BACKEND_GUIDE.md             # Backend architecture
│   ├── API_SPEC.md                  # API reference
│   ├── SETUP_GUIDE.md               # Setup instructions
│   └── MODULE_REFERENCE.md          # Module details
│
├── docker-compose.yml               # Docker Compose config
└── README.md                        # This file
```

## 🔌 API Endpoints

### POST /v1/localize
Generate localized content.

**Request**:
```json
{
  "text": "Hello everyone!",
  "target_language": "es",
  "tone": "casual"
}
```

**Response**:
```json
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

### GET /v1/history
Retrieve localization history.

**Query Parameters**:
- `page` (default: 1) - Page number
- `limit` (default: 20, max: 100) - Records per page
- `target_language` (optional) - Filter by language

**Response**:
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

### POST /v1/feedback
Submit user feedback.

**Request**:
```json
{
  "request_id": 1,
  "rating": 5,
  "comment": "Perfect translation!"
}
```

### GET /v1/health
Health check endpoint.

## 📖 Documentation

- **[Backend Architecture Guide](docs/BACKEND_GUIDE.md)** - How the backend works
- **[API Specification](docs/API_SPEC.md)** - Complete API reference
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed setup instructions
- **[Module Reference](docs/MODULE_REFERENCE.md)** - Code-level reference

**Interactive API Docs**: http://localhost:8000/v1/docs

## 🧪 Testing

### Test Endpoints with cURL

```bash
# Health check
curl http://localhost:8000/v1/health

# Simple localization
curl -X POST http://localhost:8000/v1/localize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello","target_language":"fr"}'

# Get history
curl http://localhost:8000/v1/history?page=1

# Submit feedback
curl -X POST http://localhost:8000/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{"request_id":1,"rating":5,"comment":"Great!"}'
```

### Run Unit Tests

```bash
cd backend
pytest -v
```

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# From project root
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Individual Docker Containers

```bash
# Backend
docker build -t localization-backend ./backend
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... localization-backend

# Frontend
docker build -t localization-frontend ./frontend
docker run -p 5173:5173 localization-frontend
```

## 📤 Deployment to Render

1. **Connect to GitHub**: Push this repo to GitHub
2. **Create Render services**:
   - Backend: New Web Service → Select repo → Build Command: `pip install -r requirements.txt`
   - Frontend: New Static Site → Build Command: `npm run build`
3. **Set Environment Variables**:
   - Backend: `OPENAI_API_KEY`, `DATABASE_URL`
4. **Deploy**: Render auto-deploys on push

## 🛠️ Development

### Run Backend in Development Mode

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

- Code changes auto-reload
- Access Swagger UI at: http://localhost:8000/v1/docs

### Run Frontend in Development Mode

```bash
cd frontend
npm run dev
```

- Frontend HMR (hot module replacement) enabled
- Access at: http://localhost:5173

### Database Management

**Reset database** (SQLite):
```bash
cd backend
rm localization.db
# Restart server - new database created
```

**Inspect database**:
```bash
sqlite3 localization.db ".schema"
sqlite3 localization.db "SELECT * FROM localizationrequest LIMIT 5;"
```

**Migrate to PostgreSQL**:
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@localhost/db_name

# Restart server
```

## 🔐 Configuration

### Environment Variables (.env)

```
# Required
OPENAI_API_KEY=sk-your-actual-key

# Optional
DATABASE_URL=sqlite:///./localization.db
OPENAI_MODEL=gpt-4o-mini
DEBUG=True
```

### Security (Production)

- [ ] Use exact CORS origins (not `*`)
- [ ] Enable HTTPS only
- [ ] Add API key authentication
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS for database
- [ ] Setup rate limiting
- [ ] Add logging and monitoring
- [ ] Use secrets management (AWS Secrets, Render Environ)

## 🚨 Troubleshooting

### "Module not found" Error
```bash
# Ensure venv is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### OpenAI API Key Error
- Verify key in `.env` file
- Key should start with `sk-`
- Check key validity at https://platform.openai.com/api-keys

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill process using port 8000
lsof -i :8000 | kill -9 <PID>  # Mac/Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process  # Windows
```

### CORS Errors
- Frontend and backend must be on different ports
- Backend allows frontend origin in `CORSMiddleware`
- Check browser console for specific error

## 📊 Performance

| Operation | Typical Time |
|-----------|-------------|
| Text cleaning | <1ms |
| Language detection | 5-10ms |
| Sentiment analysis | 10-20ms |
| OpenAI API call | 2-5s |
| Database storage | <5ms |
| **Total per localization** | **2-5 seconds** |

## 📈 Future Enhancements

- [ ] User authentication (JWT)
- [ ] API rate limiting
- [ ] Advanced analytics dashboard
- [ ] Audio localization support
- [ ] Fine-tuned models for specific domains
- [ ] Batch processing API
- [ ] Webhook notifications
- [ ] Integration with translation memory
- [ ] A/B testing for translations
- [ ] Mobile app (React Native)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📞 Support

- **Documentation**: See [docs/](docs/) folder
- **Issues**: Report on GitHub Issues
- **Email**: support@example.com

## 🙏 Acknowledgments

- OpenAI for GPT models
- FastAPI for the excellent framework
- React team for the frontend library
- Render for deployment platform

---

**Built with ❤️ by the AI Localization Team**

Last updated: March 2024

