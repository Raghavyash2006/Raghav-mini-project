# Database Schema - Quick Reference

## What's Included

### Files Created

1. **`app/models.py`** (450+ lines)
   - 9 SQLAlchemy ORM models
   - Complete with relationships and indexes
   - Enum types for languages, tones, etc.

2. **`app/database.py`** (400+ lines)
   - SQLAlchemy engine configuration
   - Session management
   - Connection pooling
   - Health checks and initialization
   - Helper classes for common operations

3. **`DATABASE_SCHEMA.sql`** (250+ lines)
   - DDL for all tables
   - Indexes and constraints
   - Initial data population
   - 3 query views

4. **`DATABASE_DESIGN.md`** (500+ lines)
   - Complete schema architecture
   - ER diagram
   - Detailed table documentation
   - Query patterns
   - Performance optimization

5. **`FASTAPI_DATABASE_INTEGRATION.py`** (400+ lines)
   - 15+ route handlers
   - Complete examples
   - Error handling
   - Pagination

6. **`DATABASE_SETUP_GUIDE.md`** (400+ lines)
   - Installation & configuration
   - Usage examples
   - Best practices
   - Troubleshooting

---

## Database Structure

### Tables (9 Total)

```
Core Business Logic:
├── users                      (User accounts & subscriptions)
├── localization_history       (Request/response history)
├── cultural_adaptations       (Idiom replacements)
├── feedback                   (User ratings & comments)
└── analytics                  (Aggregated metrics)

Supporting:
├── language_metadata          (Language information)
├── tone_profiles              (Tone configurations)
├── usage_quotas               (Rate limiting)
└── api_logs                   (Audit trail)
```

### Relationships (13+)

```
users (1) ──────→ (N) localization_history
users (1) ──────→ (N) feedback
users (1) ──────→ (1) usage_quotas
users (1) ──────→ (N) api_logs

localization_history (1) ──→ (N) cultural_adaptations
localization_history (1) ──→ (1) feedback

feedback (N) ──→ (1) users
feedback (N) ──→ (1) localization_history
```

### Indexes (35+)

**High Priority:**
- users(email) - Fast authentication
- users(api_key) - API validation
- localization_history(user_id, created_at) - User history queries
- localization_history(quality_score) - Quality filtering
- feedback(rating) - Feedback analytics

**Medium Priority:**
- localization_history(target_language) - Language stats
- localization_history(tone) - Tone analysis
- analytics(user_id, metric_date) - User analytics
- api_logs(created_at) - Recent logs

---

## Quick Setup

```python
# 1. Import and initialize
from app.database import init_db
init_db()  # Creates all tables

# 2. Get a session
from app.database import get_session_context

with get_session_context() as session:
    user = session.query(User).first()

# 3. Use in FastAPI
from app.database import get_db
from sqlalchemy.orm import Session

@app.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    return db.query(User).filter_by(user_id=user_id).first()
```

---

## Key Features

### 1. Multiple Language Support

```python
# Supported languages
languages = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "hi": "Hindi",
    "zh": "Chinese",
    "ja": "Japanese",
    "ar": "Arabic",
    "ru": "Russian",
    "ko": "Korean"
}
```

### 2. Tone Preservation

```python
tones = {
    "formal": "Professional, business-appropriate",
    "casual": "Conversational, friendly",
    "marketing": "Persuasive, sales-oriented",
    "technical": "Technical, precise terminology",
    "neutral": "Balanced, objective"
}
```

### 3. Cultural Adaptation Tracking

```python
# Each idiom replacement tracked:
{
    "source_idiom": "piece of cake",
    "target_idiom": "pan comido",
    "equivalence_type": "direct",
    "semantic_preservation": 0.92,
    "category": "idiom"
}
```

### 4. Comprehensive Feedback

```python
# Detailed feedback with aspects:
{
    "rating": 5,
    "comment": "Perfect translation!",
    "aspects": {
        "accuracy": 5,
        "tone_preserved": true,
        "cultural_fit": 5,
        "readability": 5,
        "idiom_handling": 4
    }
}
```

### 5. Subscription Tiers

```python
# Quota management:
tiers = {
    "free": {
        "requests": 100,
        "characters": 50000  # 50K per month
    },
    "pro": {
        "requests": 10000,
        "characters": 5000000  # 5M per month
    },
    "enterprise": {
        "requests": "unlimited",
        "characters": "unlimited"
    }
}
```

---

## Common Queries

### User Authentication
```python
user = session.query(User).filter_by(email="user@example.com").first()
```

### Get User's Recent Localizations
```python
from datetime import datetime, timedelta

recent = session.query(LocalizationHistory).filter(
    LocalizationHistory.user_id == user_id,
    LocalizationHistory.created_at >= datetime.now() - timedelta(days=30)
).order_by(LocalizationHistory.created_at.desc()).limit(20)
```

### Language Usage Statistics
```python
from sqlalchemy import func

stats = session.query(
    LocalizationHistory.target_language,
    func.count(LocalizationHistory.request_id)
).group_by(LocalizationHistory.target_language).all()
```

### Feedback Summary
```python
summary = session.query(
    func.count(Feedback.feedback_id),
    func.avg(Feedback.rating)
).first()
```

### Cultural Adaptations Report
```python
adaptations = session.query(CulturalAdaptation).filter(
    CulturalAdaptation.equivalence_type == "direct"
).order_by(CulturalAdaptation.semantic_preservation.desc())
```

---

## Performance Characteristics

| Operation | Time | Query |
|-----------|------|-------|
| User login | O(1) | Indexed email lookup |
| Get user history | O(log n) | B-tree index on user_id |
| Language statistics | O(n) | Group by with aggregation |
| Feedback average | O(n) | Full table scan (fast) |
| Pagination | O(1) | Index with limit/offset |

### Database Sizes

**Typical Usage (100,000 users):**
- Users: ~10MB
- Localizations (10M requests): ~2GB
- Feedback (500K): ~50MB
- Total: ~2.5GB

**3-Year Retention Scenario:**
- Archive old api_logs monthly
- Keep analytics rolled up
- Estimated size: ~8-10GB

---

## Migration Path

### Current (Development)
```
SQLite (file-based, single-file deployment)
```

### Production
```
PostgreSQL (multi-user, better performance, backups)
```

### Switching Database

```python
# Change one line in .env
# From:
DATABASE_URL=sqlite:///./localization.db
# To:
DATABASE_URL=postgresql://user:password@localhost:5432/db

# All models and code work the same!
```

---

## Backup & Recovery

### SQLite Backup
```bash
cp localization.db localization.db.$(date +%Y%m%d_%H%M%S).backup
```

### PostgreSQL Backup
```bash
pg_dump -U postgres -d localization_db > backup.sql
```

### Recovery
```bash
# SQLite
cp localization.db.backup localization.db

# PostgreSQL
psql -U postgres < backup.sql
```

---

## Monitoring Queries

### Database Health
```python
@app.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"database": "healthy"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}
```

### Check Quota Usage
```python
user_quota = session.query(UsageQuota).filter_by(user_id=user_id).first()
usage_pct = (user_quota.requests_this_month / user_quota.quota_limit_requests) * 100
```

### Find Slow Translations
```python
slow_translations = session.query(LocalizationHistory).filter(
    LocalizationHistory.quality_score < 60
).order_by(LocalizationHistory.created_at.desc())
```

---

## Integration with Services

### With Localization Engine
```python
from app.services.localization_engine import LocalizationEngine
from app.database import get_session_context

engine = LocalizationEngine()

with get_session_context() as session:
    result = engine.localize(text, target_lang, tone)
    
    # Save to database
    loc = LocalizationHistory(
        request_id=result['request_id'],
        user_id=user_id,
        source_text=text,
        localized_text=result['translated_text'],
        quality_score=result['quality'],
        # ... more fields
    )
    session.add(loc)
    session.commit()
```

### With Cultural Adapter
```python
from app.services.cultural_adapter import get_cultural_adapter

adapter = get_cultural_adapter()

result = adapter.replace_idioms(text, "en", "es")

for replacement in result['replacements']:
    adaptation = CulturalAdaptation(
        request_id=request_id,
        source_idiom=replacement['source_idiom'],
        target_idiom=replacement['target_idiom'],
        equivalence_type=replacement['equivalence_type'],
        semantic_preservation=replacement['semantic_preservation']
    )
    session.add(adaptation)
```

---

## Deployment Checklist

- [ ] Run `init_db()` to create schema
- [ ] Insert language_metadata records
- [ ] Insert tone_profile records
- [ ] Configure DATABASE_URL for environment
- [ ] Set up automated backups
- [ ] Configure monitoring
- [ ] Test connection pool
- [ ] Load test with target QPS
- [ ] Set up log rotation
- [ ] Document schema for team
- [ ] Create runbooks for common issues

---

## Support & Troubleshooting

### Q: Foreign key error on insert
**A:** Enable foreign keys in SQLite:
```python
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
```

### Q: Slow queries after millions of rows
**A:** Add indexes:
```python
# Check missing indexes
EXPLAIN QUERY PLAN SELECT * FROM localization_history WHERE user_id = ?
```

### Q: Connection pool exhausted
**A:** Increase pool size:
```python
pool_size=50, max_overflow=100
```

### Q: OutOfMemory on large joins
**A:** Use pagination:
```python
offset = (page - 1) * 100
items = query.offset(offset).limit(100)
```

---

**Database Version**: 1.0.0  
**Tables**: 9  
**Relationships**: 13+  
**Indexes**: 35+  
**Production Ready**: ✓  
**Last Updated**: March 2026
