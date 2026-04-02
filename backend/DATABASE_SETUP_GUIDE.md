# Complete Database Setup Guide

## Quick Start

### 1. Installation

```bash
# Install database dependencies
pip install sqlalchemy alembic psycopg2-binary

# Or via requirements.txt
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:
```env
# Database URL
DATABASE_URL=sqlite:///./localization.db
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/localization_db

# Environment
ENVIRONMENT=development
DEBUG=True
```

### 3. Initialize Database

```python
from app.database import init_db

# Create all tables
init_db()
print("Database initialized!")
```

---

## File Structure

```
backend/
├── app/
│   ├── models.py                          # SQLAlchemy ORM models
│   ├── database.py                        # Connection & session management
│   ├── services/
│   │   ├── localization_engine.py         # Localization logic
│   │   ├── cultural_adapter.py            # Idiom replacement
│   │   └── input_processing.py            # Text preprocessing
│   └── main.py                            # FastAPI app
├── DATABASE_SCHEMA.sql                    # SQL DDL statements
├── DATABASE_DESIGN.md                     # Schema documentation
├── FASTAPI_DATABASE_INTEGRATION.py        # Integration examples
└── .env                                   # Environment variables
```

---

## Database Models Summary

### Core Models

| Model | Purpose | Key Fields |
|-------|---------|-----------|
| **User** | User accounts | user_id, email, api_key, subscription_tier |
| **LocalizationHistory** | Requests & results | request_id, source_text, localized_text, quality_score |
| **CulturalAdaptation** | Idiom replacements | source_idiom, target_idiom, equivalence_type |
| **Feedback** | User ratings | feedback_id, rating, comment, aspects |
| **Analytics** | Aggregated metrics | total_requests, avg_quality_score, languages_used |
| **LanguageMetadata** | Language info | lang_code, language_name, complexity_score |
| **ToneProfile** | Tone configurations | tone_name, system_prompt, characteristics |
| **UsageQuota** | Rate limiting | requests_this_month, quota_limit_requests |
| **APILog** | API audit trail | endpoint, status_code, response_time_ms |

---

## Usage Examples

### Example 1: Create User and First Localization

```python
from app.database import get_session_context
from app.models import User, LocalizationHistory
import uuid
from datetime import datetime

with get_session_context() as session:
    # Create user
    user = User(
        user_id=str(uuid.uuid4()),
        email="john@example.com",
        username="John",
        subscription_tier="pro",
    )
    session.add(user)
    session.commit()
    
    # Create localization
    localization = LocalizationHistory(
        request_id=str(uuid.uuid4()),
        user_id=user.user_id,
        source_text="It's raining cats and dogs!",
        target_language="es",
        tone="casual",
        localized_text="¡Llueve a cántaros!",
        quality_score=94.5,
        character_count=31,
        word_count=5,
        execution_time_ms=243,
        model_used="gpt-4o-mini",
    )
    session.add(localization)
    session.commit()
    
    print(f"Created user: {user.email}")
    print(f"Created localization: {localization.request_id}")
```

### Example 2: Query with Relationships

```python
from app.database import get_session_context
from app.models import User
from sqlalchemy.orm import joinedload

with get_session_context() as session:
    # Get user with all localizations
    user = session.query(User).options(
        joinedload(User.localizations),
        joinedload(User.feedbacks)
    ).filter_by(email="john@example.com").first()
    
    if user:
        print(f"User: {user.email}")
        print(f"Localizations: {len(user.localizations)}")
        print(f"Feedback count: {len(user.feedbacks)}")
        
        for loc in user.localizations:
            print(f"  - {loc.source_text[:30]}... -> {loc.target_language}")
            if loc.feedback:
                print(f"    Rating: {loc.feedback.rating}/5")
```

### Example 3: Analytics Query

```python
from app.database import get_session_context
from app.models import LocalizationHistory, Feedback
from sqlalchemy import func
from datetime import datetime, timedelta

with get_session_context() as session:
    # Get last 30 days stats
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    stats = session.query(
        LocalizationHistory.target_language,
        func.count(LocalizationHistory.request_id).label("requests"),
        func.avg(LocalizationHistory.quality_score).label("avg_quality"),
    ).filter(
        LocalizationHistory.created_at >= thirty_days_ago
    ).group_by(
        LocalizationHistory.target_language
    ).all()
    
    for stat in stats:
        print(f"{stat.target_language}: {stat.requests} requests, {stat.avg_quality:.1f}% quality")
```

### Example 4: Feedback Analysis

```python
from app.database import get_session_context
from app.models import Feedback
from sqlalchemy import func

with get_session_context() as session:
    # Get feedback summary
    summary = session.query(
        func.count(Feedback.feedback_id).label("total"),
        func.avg(Feedback.rating).label("avg_rating"),
        func.count(
            Feedback.feedback_id
        ).filter(Feedback.helpful == True).label("helpful_count")
    ).first()
    
    print(f"Total feedback: {summary.total}")
    print(f"Average rating: {summary.avg_rating:.1f}/5")
    print(f"Helpful ratings: {summary.helpful_count}")
```

---

## Pagination Pattern

```python
def paginate_localizations(user_id, page=1, page_size=20):
    """Get paginated localization history"""
    with get_session_context() as session:
        query = session.query(LocalizationHistory).filter_by(
            user_id=user_id
        )
        
        # Get total count
        total = query.count()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get page items
        items = query.order_by(
            LocalizationHistory.created_at.desc()
        ).offset(offset).limit(page_size).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
            "has_next": page < (total + page_size - 1) // page_size,
            "has_prev": page > 1
        }

# Usage
result = paginate_localizations(user_id="user-123", page=2, page_size=10)
print(f"Page 2 has {len(result['items'])} items")
print(f"Total pages: {result['pages']}")
```

---

## FastAPI Integration

### Setup in main.py

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, startup_db, shutdown_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    await startup_db()

@app.on_event("shutdown")
async def shutdown():
    await shutdown_db()

@app.get("/status")
def status(db: Session = Depends(get_db)):
    # db is automatically managed by FastAPI
    return {"status": "ok"}
```

### Route Handler with Database

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User, LocalizationHistory

app = FastAPI()

@app.get("/users/{user_id}/localizations")
def get_user_localizations(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get user's recent localizations"""
    user = db.query(User).filter_by(user_id=user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    localizations = db.query(LocalizationHistory).filter_by(
        user_id=user_id
    ).order_by(
        LocalizationHistory.created_at.desc()
    ).limit(limit).all()
    
    return {
        "user": {
            "user_id": user.user_id,
            "email": user.email
        },
        "localizations": [
            {
                "request_id": loc.request_id,
                "source_text": loc.source_text,
                "target_language": loc.target_language,
                "quality_score": loc.quality_score
            }
            for loc in localizations
        ]
    }
```

---

## Transaction Management

### Automatic Rollback on Error

```python
from app.database import get_session_context

def create_localization_with_feedback(
    user_id, source_text, target_language, localized_text, quality_score, rating
):
    with get_session_context() as session:
        try:
            # Create localization
            loc = LocalizationHistory(
                request_id=str(uuid.uuid4()),
                user_id=user_id,
                source_text=source_text,
                target_language=target_language,
                localized_text=localized_text,
                quality_score=quality_score,
                character_count=len(source_text),
                word_count=len(source_text.split()),
                execution_time_ms=100,
                model_used="gpt-4o-mini",
            )
            session.add(loc)
            session.flush()  # Get request_id
            
            # Create feedback
            feedback = Feedback(
                feedback_id=str(uuid.uuid4()),
                request_id=loc.request_id,
                user_id=user_id,
                rating=rating,
            )
            session.add(feedback)
            
            session.commit()
            return loc.request_id
            
        except Exception as e:
            session.rollback()  # Automatic on context exit
            raise
```

---

## Performance Tips

### 1. Use Bulk Inserts

```python
from app.database import bulk_insert

# Efficient: Single commit
items = [
    LocalizationHistory(...),
    LocalizationHistory(...),
    LocalizationHistory(...),
]
bulk_insert(items)

# Instead of:
# for item in items:
#     session.add(item)
#     session.commit()  # Multiple commits = slow
```

### 2. Use Selective Columns

```python
# Get only needed columns
query = session.query(
    LocalizationHistory.request_id,
    LocalizationHistory.quality_score,
    LocalizationHistory.created_at
).filter_by(user_id=user_id)

# Not:
# query = session.query(LocalizationHistory)  # All columns
```

### 3. Use Joins Instead of Relationships

```python
# Efficient: Single query with join
from sqlalchemy.orm import joinedload

user = session.query(User).options(
    joinedload(User.localizations)
).filter_by(user_id=user_id).first()

# Not:
# user = session.query(User).filter_by(user_id=user_id).first()
# requests = user.localizations  # Separate query (N+1)
```

---

## Database Maintenance

### Backup

```bash
# SQLite
cp localization.db localization.db.backup

# PostgreSQL
pg_dump -U user -d localization_db > backup.sql
```

### Cleanup Old Logs

```python
from app.database import get_session_context
from app.models import APILog
from datetime import datetime, timedelta

def cleanup_old_logs(days=30):
    with get_session_context() as session:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = session.query(APILog).filter(
            APILog.created_at < cutoff_date
        ).delete()
        
        session.commit()
        print(f"Deleted {deleted} old API logs")

# Run periodically
cleanup_old_logs(days=30)
```

---

## Migration with Alembic

### Setup

```bash
pip install alembic

alembic init migrations
```

### Create Migration

```bash
# Auto-detect model changes
alembic revision --autogenerate -m "Add new column"

# Or manual
alembic revision -m "Description"
```

### Apply Migration

```bash
# Apply latest
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Monitoring & Debugging

### Enable SQL Echo

```python
import logging

# Set to DEBUG to see all SQL
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
```

### Connection Pool Statistics

```python
from app.database import engine

# Get pool stats (requires pool instrumentation)
print(f"Active connections: {engine.pool.checkedout()}")
print(f"Pool size: {engine.pool.size()}")
```

### Slow Query Detection

```python
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - context._query_start_time
    if total_time > 1.0:  # Log queries over 1 second
        print(f"Slow query ({total_time:.2f}s): {statement}")
```

---

## Troubleshooting

### Foreign Key Constraint Error

```python
# SQLite: Enable foreign key constraints
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

### Connection Pool Exhaustion

```python
# Increase pool_size in database.py
engine = create_engine(
    database_url,
    pool_size=50,      # Increase from 20
    max_overflow=100,  # Increase from 40
)
```

### Session Not Found Error

```python
# Always clean up sessions
session = get_session()
try:
    # do something
    pass
finally:
    session.close()

# Or use context manager
with get_session_context() as session:
    # Session auto-closed
    pass
```

---

## Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable connection pooling
- [ ] Set up automated backups
- [ ] Configure query logging
- [ ] Monitor slow queries
- [ ] Set up index monitoring
- [ ] Implement cleanup routines
- [ ] Use Alembic for migrations
- [ ] Test connection failover
- [ ] Document schema changes
- [ ] Set up monitoring alerts

---

**Database Setup Version**: 1.0  
**Last Updated**: March 2026  
**Status**: Production Ready ✓
