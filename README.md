# 🌍 AI Localization Platform

> **Intelligent text and image localization engine** powered by AI, designed to adapt content for different languages, regions, tones, and audiences while preserving intent, sentiment, and cultural nuances.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Docker Support](#docker-support)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 📖 Overview

The **AI Localization Platform** is a Django + Django REST Framework full-stack application that intelligently localizes content across multiple languages and cultural contexts. It supports both direct text input and image-based text extraction via OCR, making it a comprehensive solution for global content adaptation.

### Use Cases
- **Content Creators**: Adapt blog posts, marketing materials, and social media content for different regions
- **Enterprises**: Localize product documentation, UI strings, and user-facing content
- **E-Commerce**: Generate market-specific product descriptions with appropriate tone and cultural context
- **SaaS Platforms**: Scale content for international audiences without manual translation

## 🎯 Key Features

### Core Localization
- ✅ **Dual Input Modes**: Direct text input or image upload with automatic OCR extraction
- ✅ **Multi-Language Support**: English, Hindi, Spanish, German, French, and 100+ languages via deep_translator
- ✅ **Language Aliases**: User-friendly input (e.g., "spanish" → "es", "hindi" → "hi")
- ✅ **Smart Tone Adaptation**: Professional, casual, marketing, friendly, persuasive, technical, empathetic
- ✅ **Audience Targeting**: Customize tone and language for specific demographics
- ✅ **Context Awareness**: Preserve original intent, sentiment, and stylistic nuances

### Advanced Features
- 🔤 **OCR Text Extraction**: Pytesseract integration for scanned documents and images
- 🎭 **Idiom & Cultural Adaptation**: HuggingFace-powered cultural sensitivity checks and idiom transformation
- 📊 **Variation Generation**: Create multiple output variants with distinct phrasing and vocabulary
- 🔍 **Sentiment & Intent Preservation**: Maintains emotional tone and user intent throughout transformation
- 📝 **Explanation Engine**: Detailed breakdown of what changed and why
- 💬 **Cultural Sensitivity Checks**: Flag potentially sensitive content before publishing
- 👍 **User Feedback Loop**: Like/dislike variations to improve model performance
- 📜 **Request History & Versioning**: Track all localization requests with timestamps

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend Framework** | Django 5.2.12, Django REST Framework |
| **Language** | Python 3.11 |
| **Database** | SQLite (development), PostgreSQL-ready |
| **Translation** | deep_translator (Google Translator backend) |
| **OCR** | pytesseract + Tesseract executable |
| **AI/ML** | HuggingFace API (idiom/cultural validation) |
| **Frontend** | Django Templates, Vanilla JavaScript, CSS |
| **Testing** | Django unittest with mock patching |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker + Docker Compose |

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────┐
│     Django REST API (DRF)               │
│  Localization Endpoints & Auth          │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼─────┐        ┌─────▼────┐
   │ Frontend  │        │ Services  │
   │(Templates)│        │  Layer    │
   └──────────┘        └─────┬────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
       ┌────▼────┐    ┌─────▼──────┐   ┌────▼────┐
       │Translate │    │OCR Service │   │Context  │
       │Service   │    │(pytesseract)   │Analysis │
       └──────────┘    └────────────┘   └────┬────┘
                                             │
                            ┌────────────────┼────────────────┐
                            │                │                │
                       ┌────▼──────┐  ┌─────▼──┐      ┌───────▼──┐
                       │Idiom      │  │Tone    │      │Cultural  │
                       │Adapter    │  │Engine  │      │Checker   │
                       └───────────┘  └───┬────┘      └──────────┘
                                          │
                                   ┌──────▼───────┐
                                   │HuggingFace   │
                                   │API (Optional)│
                                   └──────────────┘
```

## 📦 Prerequisites

- **Python 3.11+**
- **Tesseract OCR** (Windows path: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- **Virtual Environment** (venv or virtualenv)
- **Git** (for version control)
- **Docker** (optional, for containerized deployment)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Raghavyash2006/Raghav-mini-project.git
cd Raghav-mini-project
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Update `.env` with your settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
HUGGINGFACE_API_KEY=your-api-key-optional
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## 🎮 Running the Application

### Development Server

```bash
python manage.py runserver
```

Access the application at: `http://127.0.0.1:8000/`

### Production Server

```bash
python manage.py collectstatic --noinput
gunicorn mini_localize.wsgi:application --bind 0.0.0.0:8000
```

## 🐳 Docker Support

### Build and Run with Docker Compose

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000/`

### Build Docker Image Manually

```bash
docker build -t mini-localize .
docker run -p 8000:8000 mini-localize
```

### Environment Variables for Docker

```bash
DEBUG=1
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

## 📡 API Documentation

### Core Localization Endpoint

**POST** `/api/localize/`

Create a new localization request with text or image input.

**Request Body:**

```json
{
  "source_text": "Hello, welcome to our store!",
  "source_language": "en",
  "target_language": "es",
  "tone": "marketing",
  "region": "Mexico",
  "audience": "young_professionals",
  "image": null
}
```

**Response (Success - 201):**

```json
{
  "id": 1,
  "localized_text": "¡Tenga en cuenta: Hola, bienvenido a nuestra tienda!",
  "variations": [
    "¡Hola! Bienvenido a nuestra fantástica tienda.",
    "¡Te damos la bienvenida a nuestra tienda!",
    "Nos alegra que te unas a nosotros."
  ],
  "explanation": {
    "tone_applied": "marketing",
    "translation_model": "google",
    "cultural_notes": "Adapted for Spanish-speaking market",
    "idiom_changes": ["welcome → bienvenido"]
  },
  "sentiment_preserved": true,
  "intent_preserved": true,
  "created_at": "2026-04-30T10:30:00Z"
}
```

### History Endpoint

**GET** `/api/history/`

Retrieve all localization requests.

**Query Parameters:**
- `language`: Filter by target language
- `tone`: Filter by tone
- `limit`: Number of results (default: 20)
- `offset`: Pagination offset

**Response:**

```json
{
  "count": 45,
  "next": "http://localhost:8000/api/history/?offset=20",
  "previous": null,
  "results": [...]
}
```

### Get Specific Request

**GET** `/api/history/<id>/`

Retrieve details of a specific localization request.

### Feedback Endpoint

**POST** `/api/feedback/`

Submit feedback on a localization variant.

**Request Body:**

```json
{
  "job_id": 1,
  "variation_index": 0,
  "liked": true,
  "comment": "Perfect tone for our marketing campaign"
}
```

### Health Check

**GET** `/api/health/`

System health and dependency status.

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "translation_service": "operational",
  "ocr_service": "ready",
  "timestamp": "2026-04-30T10:30:00Z"
}
```

## 🧪 Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific Test Suite

```bash
# Unit tests
python manage.py test apps.localization.tests.unit

# Integration tests
python manage.py test apps.localization.tests.integration

# Tone system tests
python manage.py test apps.localization.tests.unit.test_localization_service

# Smoke tests
python manage.py test apps.localization.tests.unit.test_smoke_translation
python manage.py test apps.localization.tests.unit.test_smoke_ocr
```

### Test Coverage

Current coverage includes:
- ✅ Tone generation with language-aware prefixes
- ✅ Language alias resolution (spanish → es, hindi → hi)
- ✅ Translation service with mock deep_translator
- ✅ OCR service with mocked pytesseract
- ✅ API endpoints (text input, image upload, history, feedback)
- ✅ Cultural sensitivity checks
- ✅ Idiom adaptation

## 🔄 CI/CD Pipeline

GitHub Actions workflow automatically:
- ✅ Triggers on push to `main`/`master` and pull requests
- ✅ Runs on Python 3.11
- ✅ Installs dependencies from `requirements.txt`
- ✅ Executes full test suite: `python manage.py test`
- ✅ Reports test results

**Workflow File:** `.github/workflows/ci.yml`

## ⚙️ Configuration

### Django Settings

Key settings in `mini_localize/settings.py`:

```python
# Translation Service
TRANSLATION_PROVIDER = 'google'  # Via deep_translator
DEFAULT_SOURCE_LANGUAGE = 'en'

# OCR Configuration
TESSERACT_PATH = os.getenv('TESSERACT_PATH')
OCR_TIMEOUT = 30  # seconds

# AI Services (Optional)
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
USE_CULTURAL_CHECKS = True
USE_IDIOM_ADAPTER = True
```

### Tone Prefixes

The system supports language-aware tone prefixes in `apps/localization/services/localization.py`:

```python
TONE_PREFIXES = {
    'en': {
        'professional': 'Please note that ',
        'casual': 'Hey, ',
        'marketing': 'Heads up! ',
        'friendly': 'Hi there! ',
        'persuasive': 'Consider that ',
        'technical': 'Technically speaking, ',
        'empathetic': 'I understand that '
    },
    'hi': {
        'professional': 'कृपया ध्यान दें: ',
        'casual': 'अरे, ',
        'marketing': 'ध्यान दें! ',
        ...
    },
    'es': {
        'professional': 'Tenga en cuenta: ',
        'casual': '¡Oye! ',
        'marketing': '¡Heads up! ',
        ...
    }
}
```

## 📁 Project Structure

```
MINI_PROJECT/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── db.sqlite3               # SQLite database
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose orchestration
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD pipeline
├── apps/
│   └── localization/
│       ├── models.py        # Django models (LocalizationJob, Variation, Feedback)
│       ├── views.py         # API views and endpoints
│       ├── serializers.py   # DRF serializers
│       ├── forms.py         # Django forms
│       ├── urls.py          # URL routing
│       ├── admin.py         # Django admin configuration
│       ├── services/        # Business logic layer
│       │   ├── localization.py      # Core engine orchestration
│       │   ├── translation.py       # Translation service wrapper
│       │   ├── ocr_service.py       # OCR wrapper
│       │   ├── idiom_adapter.py     # Idiom transformation
│       │   ├── cultural.py          # Cultural sensitivity checks
│       │   ├── context_analysis.py  # Context understanding
│       │   └── ai_client.py         # HuggingFace integration
│       ├── tests/           # Test suites
│       │   ├── unit/        # Unit tests
│       │   └── integration/ # Integration tests
│       └── migrations/      # Database migrations
├── mini_localize/
│   ├── settings.py         # Django configuration
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
├── templates/
│   ├── index.html          # Main UI template
│   ├── auth.html           # Authentication template
│   └── admin/              # Admin templates
└── static/
    ├── css/
    │   └── app.css         # Styling
    └── js/
        └── app.js          # Frontend JavaScript
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Add unit tests for new features
- Update documentation in README
- Ensure all tests pass before submitting PR

## 📄 License

This project is open source and available under the MIT License. See LICENSE file for details.

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/Raghavyash2006/Raghav-mini-project/issues)
- Check existing [Documentation](https://github.com/Raghavyash2006/Raghav-mini-project/wiki)
- Review [API Examples](./API_EXAMPLES.md)

---

**Built with ❤️ by [Raghav](https://github.com/Raghavyash2006)**

Last Updated: April 30, 2026
