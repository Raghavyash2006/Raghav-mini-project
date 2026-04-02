# Database Schema Design - AI Content Localization Platform

## Overview

Comprehensive relational database schema designed for the AI Content Localization Platform. Supports multi-language localization, user management, feedback collection, and detailed analytics.

**Technology Stack:**
- **ORM**: SQLAlchemy 2.0+
- **Databases**: SQLite (development), PostgreSQL (production)
- **Connection Pool**: StaticPool (SQLite) / QueuePool (PostgreSQL)
- **Indexing Strategy**: Composite + selective indexes for query optimization

---

## Schema Architecture

### Entity Relationship Diagram

```
┌─────────────(1) users (N)─────────────────┐
│                ▼                          │
│    ┌──────────────────────────────┐      │
│    │  localization_history        │      │
│    │  (request history)           │      │
│    └──────────────────────────────┘      │
│           ▲        ▲         ▲            │
│           │        │         │            │
│       (1-N relation across   │            │
│       multiple tables)        │            │
│                               │            │
│         ┌─────────────────────┼────────┐  │
│         ▼                     ▼        ▼  ▼
│   ┌──────────────┐    ┌──────────┐  ┌────────────┐
│   │ cultural_    │    │ feedback │  │ analytics  │
│   │ adaptations  │    │          │  │            │
│   └──────────────┘    └──────────┘  └────────────┘
│                                                    │
└────────────────────────────────────────────────────┘

Supporting Tables:
├── language_metadata (lookup)
├── tone_profiles (lookup)
├── usage_quotas (m2m relation)
├── api_logs (audit trail)
```

---

## Core Tables

### 1. USERS TABLE

**Purpose:** Store user accounts, authentication, and subscription information

**Schema:**
```sql
users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    api_key VARCHAR(255) UNIQUE,
    subscription_tier VARCHAR(20) [free|pro|enterprise],
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Relationships:**
- 1:N → localization_history (user has many requests)
- 1:N → feedback (user can provide feedback)
- 1:1 → usage_quotas (tracks monthly usage)
- 1:N → api_logs (tracks API calls)

**Indexes:**
```
idx_user_email          - O(1) email lookup
idx_user_api_key        - O(1) API key validation
idx_user_created_at     - Query recent users
```

**Typical Queries:**
```python
# Get user by email (authentication)
user = session.query(User).filter_by(email="user@example.com").first()

# Find active users in pro tier
pro_users = session.query(User).filter_by(
    subscription_tier="pro",
    is_active=True
).all()

# Get user with all localizations
from sqlalchemy.orm import joinedload
user = session.query(User).options(
    joinedload(User.localizations)
).filter_by(user_id="...").first()
```

---

### 2. LOCALIZATION_HISTORY TABLE

**Purpose:** Store all localization requests and results

**Schema:**
```sql
localization_history (
    request_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) FOREIGN KEY,
    
    -- Input Parameters
    source_text TEXT NOT NULL,
    source_language VARCHAR(10),
    target_language VARCHAR(10),
    tone VARCHAR(20),
    
    -- Output Data
    localized_text TEXT NOT NULL,
    explanation TEXT,
    
    -- Quality Metrics
    detected_sentiment VARCHAR(20),
    quality_score FLOAT,
    character_count INTEGER,
    word_count INTEGER,
    execution_time_ms INTEGER,
    
    -- Processing Info
    model_used VARCHAR(50),
    idioms_detected INTEGER,
    idioms_replaced INTEGER,
    cultural_adaptations_applied JSON,
    
    -- Metadata
    created_at TIMESTAMP
)
```

**Relationships:**
- N:1 → users (many requests per user)
- 1:N → cultural_adaptations (one request can have multiple idiom replacements)
- 1:1 → feedback (optional feedback on request)

**Indexes:**
```
idx_localization_user_id            - Find user's requests
idx_localization_target_lang        - Query by language
idx_localization_tone               - Query by tone
idx_localization_quality_score      - Filter by quality
idx_localization_created_at         - Time-based queries
idx_localization_composite          - (user_id, created_at)
```

**Typical Queries:**
```python
# Get user's recent requests
requests = session.query(LocalizationHistory).filter(
    LocalizationHistory.user_id == user_id,
    LocalizationHistory.created_at >= datetime.now() - timedelta(days=30)
).order_by(LocalizationHistory.created_at.desc()).limit(10).all()

# Get high-quality localizations to Spanish
quality_requests = session.query(LocalizationHistory).filter(
    LocalizationHistory.target_language == "es",
    LocalizationHistory.quality_score >= 80
).all()

# Get requests with cultural adaptations
adapted = session.query(LocalizationHistory).filter(
    LocalizationHistory.idioms_replaced > 0
).all()

# Pagination with quality filter
page = 1
page_size = 20
query = session.query(LocalizationHistory).filter_by(user_id=user_id)
total = query.count()
offset = (page - 1) * page_size
items = query.offset(offset).limit(page_size).all()
```

---

### 3. CULTURAL_ADAPTATIONS TABLE

**Purpose:** Track idiom/metaphor replacements in detail

**Schema:**
```sql
cultural_adaptations (
    adaptation_id VARCHAR(36) PRIMARY KEY,
    request_id VARCHAR(36) FOREIGN KEY,
    
    -- Adaptation Details
    source_idiom VARCHAR(255),
    target_idiom VARCHAR(255),
    category VARCHAR(50),  -- idiom, metaphor, proverb, etc.
    equivalence_type VARCHAR(20),  -- direct, partial, conceptual, none
    
    -- Quality Metrics
    semantic_preservation FLOAT,  -- 0-1
    confidence_score FLOAT,
    
    -- Context
    explanation TEXT,
    source_language VARCHAR(10),
    target_language VARCHAR(10),
    
    created_at TIMESTAMP
)
```

**Relationships:**
- N:1 → localization_history (many adaptations per request)

**Indexes:**
```
idx_adaptation_request_id           - Find adaptations for request
idx_adaptation_category             - Query by idiom type
idx_adaptation_equivalence          - Filter by equivalence quality
```

**Typical Queries:**
```python
# Get all adaptations for a localization request
adaptations = session.query(CulturalAdaptation).filter_by(
    request_id=request_id
).all()

# Find direct equivalents in Spanish
direct = session.query(CulturalAdaptation).filter(
    CulturalAdaptation.target_language == "es",
    CulturalAdaptation.equivalence_type == "direct"
).all()

# Get poorly preserved adaptations
poor_preservation = session.query(CulturalAdaptation).filter(
    CulturalAdaptation.semantic_preservation < 0.7
).all()
```

---

### 4. FEEDBACK TABLE

**Purpose:** Store user ratings and comments on translations

**Schema:**
```sql
feedback (
    feedback_id VARCHAR(36) PRIMARY KEY,
    request_id VARCHAR(36) FOREIGN KEY UNIQUE,
    user_id VARCHAR(36) FOREIGN KEY,
    
    -- Rating
    rating INTEGER (1-5),
    comment TEXT,
    
    -- Detailed Aspects
    aspects JSON {
        "accuracy": 1-5,
        "tone_preserved": boolean,
        "cultural_fit": 1-5,
        "readability": 1-5,
        "idiom_handling": 1-5
    },
    
    -- Summary
    helpful BOOLEAN,
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Relationships:**
- N:1 → users (user can give multiple feedbacks)
- 1:1 → localization_history (one feedback per request, optional)

**Indexes:**
```
idx_feedback_request_id             - Find feedback for request
idx_feedback_user_id                - Find user's feedback
idx_feedback_rating                 - Query by rating level
idx_feedback_created_at             - Time-based queries
UNIQUE (request_id, user_id)        - One feedback per user+request
```

**Typical Queries:**
```python
# Get average rating for a user's localizations
avg_rating = session.query(func.avg(Feedback.rating)).filter(
    Feedback.user_id == user_id
).scalar()

# Get high-rated localizations
praised = session.query(Feedback).filter(Feedback.rating >= 4).all()

# Find problematic translations (low ratings)
problems = session.query(Feedback).filter(Feedback.rating <= 2).all()

# Get aspect-specific feedback
accuracy_data = session.query(Feedback).filter(
    func.json_extract(Feedback.aspects, "$.accuracy") <= 2
).all()
```

---

### 5. ANALYTICS TABLE

**Purpose:** Store aggregated daily metrics for reporting

**Schema:**
```sql
analytics (
    metric_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) FOREIGN KEY,  -- NULL for platform-wide
    metric_date TIMESTAMP,
    
    -- Volume Metrics
    total_requests INTEGER,
    total_characters INTEGER,
    total_words INTEGER,
    
    -- Quality Metrics
    avg_quality_score FLOAT,
    avg_execution_time_ms FLOAT,
    
    -- Usage Patterns
    languages_used JSON,  -- ["es", "hi", "fr"]
    tones_used JSON,      -- {"formal": 5, "casual": 3}
    top_language VARCHAR(10),
    top_tone VARCHAR(20),
    
    -- Feedback Metrics
    feedback_count INTEGER,
    avg_rating FLOAT,
    
    -- Cultural Adaptation Metrics
    cultural_adaptations_applied INTEGER,
    idioms_detected_avg FLOAT,
    
    -- Success Tracking
    error_count INTEGER,
    success_rate FLOAT,
    
    created_at TIMESTAMP
)
```

**Relationships:**
- N:1 → users (optional - NULL for platform metrics)

**Indexes:**
```
idx_analytics_user_id               - Find user's metrics
idx_analytics_metric_date           - Time-based queries
idx_analytics_composite             - (user_id, metric_date)
```

**Typical Queries:**
```python
# Get user's metrics for current month
from datetime import datetime, timedelta
today = datetime.now().date()
thirty_days_ago = today - timedelta(days=30)

user_metrics = session.query(Analytics).filter(
    Analytics.user_id == user_id,
    Analytics.metric_date >= thirty_days_ago
).all()

# Get platform-wide statistics
platform_stats = session.query(Analytics).filter(
    Analytics.user_id == None,
    Analytics.metric_date == today
).first()

# Find top performing days
top_days = session.query(Analytics).order_by(
    Analytics.avg_quality_score.desc()
).limit(10).all()
```

---

### 6. LOOKUP TABLES

#### LANGUAGE_METADATA
```sql
language_metadata (
    lang_code VARCHAR(10) PRIMARY KEY,
    language_name VARCHAR(100),
    native_name VARCHAR(100),
    region_code VARCHAR(10),
    is_active BOOLEAN,
    native_speakers INTEGER,
    linguistic_family VARCHAR(50),
    complexity_score INTEGER (1-10),
    supported_idioms INTEGER
)
```

#### TONE_PROFILES
```sql
tone_profiles (
    tone_id VARCHAR(36) PRIMARY KEY,
    tone_name VARCHAR(50) UNIQUE,
    description TEXT,
    characteristics JSON,
    system_prompt TEXT,
    example_output TEXT,
    is_active BOOLEAN
)
```

#### USAGE_QUOTAS
```sql
usage_quotas (
    user_id VARCHAR(36) PRIMARY KEY FOREIGN KEY,
    requests_this_month INTEGER,
    characters_this_month INTEGER,
    quota_limit_requests INTEGER,
    quota_limit_characters INTEGER,
    reset_date TIMESTAMP
)
```

#### API_LOGS
```sql
api_logs (
    log_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) FOREIGN KEY,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP
)
```

---

## Database Connection Management

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize database
    init_db()

@app.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(user_id=user_id).first()
    return user

@app.post("/localizations")
def create_localization(request: LocalizationRequest, db: Session = Depends(get_db)):
    # Create and save
    loc = LocalizationHistory(
        request_id=request.request_id,
        user_id=request.user_id,
        source_text=request.source_text,
        target_language=request.target_language,
        # ...
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc
```

### Context Manager Usage

```python
from app.database import get_session_context

with get_session_context() as session:
    user = session.query(User).filter_by(email="user@example.com").first()
    requests = session.query(LocalizationHistory).filter_by(
        user_id=user.user_id
    ).all()
```

---

## Query Patterns

### Pattern 1: User's Localization History

```python
def get_user_history(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    target_language: str = None,
    min_quality: float = None
):
    query = session.query(LocalizationHistory).filter_by(user_id=user_id)
    
    # Optional filters
    if target_language:
        query = query.filter_by(target_language=target_language)
    if min_quality:
        query = query.filter(LocalizationHistory.quality_score >= min_quality)
    
    # Pagination
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(LocalizationHistory.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }
```

### Pattern 2: Analytics with Relationships

```python
def get_detailed_metrics(user_id: str):
    # Use joinedload to avoid N+1 queries
    from sqlalchemy.orm import joinedload
    
    requests = session.query(LocalizationHistory).options(
        joinedload(LocalizationHistory.cultural_adaptations),
        joinedload(LocalizationHistory.feedback)
    ).filter_by(user_id=user_id).all()
    
    return {
        "total_requests": len(requests),
        "avg_quality": sum(r.quality_score for r in requests) / len(requests) if requests else 0,
        "total_adaptations": sum(len(r.cultural_adaptations) for r in requests),
        "feedback_received": sum(1 for r in requests if r.feedback),
    }
```

### Pattern 3: Aggregation and Grouping

```python
from sqlalchemy import func

def get_language_statistics():
    stats = session.query(
        LocalizationHistory.target_language,
        func.count(LocalizationHistory.request_id).label("request_count"),
        func.avg(LocalizationHistory.quality_score).label("avg_quality"),
        func.sum(LocalizationHistory.character_count).label("total_chars"),
        func.count(func.distinct(LocalizationHistory.user_id)).label("unique_users")
    ).group_by(LocalizationHistory.target_language).all()
    
    return [
        {
            "language": s.target_language,
            "requests": s.request_count,
            "avg_quality": round(s.avg_quality, 2),
            "total_characters": s.total_chars,
            "unique_users": s.unique_users
        }
        for s in stats
    ]
```

---

## Performance Optimization

### Index Strategy

**Primary Indexes:**
- All primary keys (automatic)
- user_id (frequent foreign key lookup)
- request_id (frequent lookups)
- created_at (time-based queries)

**Composite Indexes:**
```sql
-- Common query: get user's recent requests
INDEX idx_localization_composite ON localization_history(user_id, created_at DESC)

-- Fast pagination by user
INDEX idx_analytics_composite ON analytics(user_id, metric_date DESC)
```

### Query Optimization Tips

1. **Use joinedload for relationships:**
   ```python
   # Good: Single query with joins
   user = session.query(User).options(
       joinedload(User.localizations)
   ).filter_by(user_id="...").first()
   
   # Bad: N+1 queries
   user = session.query(User).filter_by(user_id="...").first()
   requests = user.localizations  # Secondary query
   ```

2. **Use selective loading:**
   ```python
   # Get only needed columns
   query = session.query(
       LocalizationHistory.request_id,
       LocalizationHistory.quality_score,
       LocalizationHistory.created_at
   )
   ```

3. **Batch operations:**
   ```python
   # Good: Single transaction
   session.add_all([item1, item2, item3])
   session.commit()
   
   # Bad: Multiple commits
   session.add(item1); session.commit()
   session.add(item2); session.commit()
   ```

---

## Views for Common Reports

### View 1: User Statistics
```sql
SELECT
    u.user_id,
    u.email,
    COUNT(DISTINCT lh.request_id) as total_requests,
    ROUND(AVG(lh.quality_score), 2) as avg_quality,
    COUNT(DISTINCT f.feedback_id) as feedback_count,
    ROUND(AVG(f.rating), 2) as avg_rating
FROM users u
LEFT JOIN localization_history lh ON u.user_id = lh.user_id
LEFT JOIN feedback f ON lh.request_id = f.request_id
GROUP BY u.user_id, u.email
```

### View 2: Language Usage
```sql
SELECT
    target_language,
    COUNT(*) as request_count,
    ROUND(AVG(quality_score), 2) as avg_quality,
    DATE(created_at) as usage_date
FROM localization_history
GROUP BY target_language, DATE(created_at)
ORDER BY usage_date DESC, request_count DESC
```

### View 3: Quality Metrics
```sql
SELECT
    DATE(created_at) as metric_date,
    COUNT(*) as total_requests,
    ROUND(AVG(quality_score), 2) as avg_quality,
    ROUND(AVG(execution_time_ms), 2) as avg_time_ms,
    ROUND(COUNT(CASE WHEN quality_score >= 80 THEN 1 END) * 100.0 / COUNT(*), 1) as success_rate_pct
FROM localization_history
GROUP BY DATE(created_at)
ORDER BY metric_date DESC
```

---

## Migration Strategy

### Development Workflow

```python
# First run: create all tables
from app.database import init_db
init_db()

# Later: modify models and regenerate schema
from app.database import reset_db
reset_db()  # WARNING: Deletes data!
```

### Production Workflow

Use Alembic for migration:
```bash
# Install
pip install alembic

# Init migrations
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new column to users"

# Apply migration
alembic upgrade head
```

---

## Best Practices

1. **Always use context managers or try/finally for sessions**
2. **Use indexes on frequently filtered columns**
3. **Use relationships (lazy="select") to avoid N+1 queries**
4. **Batch insert/update operations for performance**
5. **Use prepared statements (SQLAlchemy does this automatically)**
6. **Archive old data periodically (cleanup old api_logs)**
7. **Monitor query performance with SQLAlchemy's echo mode**
8. **Use connection pooling for production (automatic with PostgreSQL)**

---

**Schema Version**: 1.0  
**Last Updated**: March 2026  
**Total Tables**: 9  
**Total Relationships**: 13+  
**Production Ready**: ✓
