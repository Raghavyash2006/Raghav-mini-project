# AI Localization Platform

A Django + DRF full-stack localization platform with text and image input, OCR extraction, context-aware rewriting, audience targeting, variation generation, cultural checks, feedback capture, and history/versioning.

## Features

- Dual input: text and image upload
- OCR via `pytesseract`
- Context-aware localization by language, region, tone, and audience
- Intent and sentiment preservation
- Idiom and cultural adaptation
- Multiple output variants: formal, casual, marketing
- Explanation panel for generated changes
- Cultural sensitivity checks
- Like/dislike feedback
- Request history and versioning

## Run

1. Create a virtual environment and install dependencies from `requirements.txt`.
2. Copy `.env.example` to `.env` and adjust values as needed.
3. Run database migrations.
4. Start the Django development server.

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## API

- `POST /api/localize/`
- `GET /api/history/`
- `GET /api/history/<id>/`
- `POST /api/feedback/`
- `GET /api/health/`
