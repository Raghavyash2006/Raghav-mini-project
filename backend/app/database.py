"""
Database Configuration and Connection Management

Handles:
- SQLAlchemy engine setup
- Database session management
- Connection pooling
- SQLite vs PostgreSQL support
- Automatic migration and schema creation
"""

import os
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool

from app.models import Base

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./localization.db"
)

# Environment
ENV = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


# ============================================================================
# ENGINE CONFIGURATION
# ============================================================================

def create_db_engine(database_url: str = DATABASE_URL) -> Engine:
    """
    Create SQLAlchemy database engine with appropriate configuration.
    
    Features:
    - SQLite for development (with proper connection handling)
    - PostgreSQL for production
    - Connection pooling and retry logic
    - Echo for SQL debugging
    
    Args:
        database_url: Connection string
        
    Returns:
        SQLAlchemy Engine
    """
    
    # Database-specific configuration
    if "sqlite" in database_url:
        # SQLite Configuration
        engine = create_engine(
            database_url,
            # Important: SingletonThreadPool for SQLite to avoid threading issues
            poolclass=StaticPool,
            # Enable foreign key constraints
            connect_args={"check_same_thread": False},
            # Show SQL in logs
            echo=DEBUG,
            # Future mode for better warnings
            future=True,
        )
        
        # Enable foreign key support in SQLite
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    else:
        # PostgreSQL/MySQL Configuration
        engine = create_engine(
            database_url,
            # QueuePool for production (handles concurrent connections)
            pool_size=20,
            max_overflow=40,
            pool_recycle=3600,  # Recycle connections every hour
            pool_pre_ping=True,  # Verify connections before using
            echo=DEBUG,
            future=True,
        )
    
    return engine


# Initialize engine
engine = create_db_engine()


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    future=True
)


def get_session() -> Session:
    """
    Create a new database session.
    
    Returns:
        SQLAlchemy Session
        
    Usage (in FastAPI):
        session = get_session()
        try:
            # Use session
            user = session.query(User).filter_by(user_id="123").first()
        finally:
            session.close()
    """
    session = SessionLocal()
    return session


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """
    Context manager for database session.
    
    Usage:
        with get_session_context() as session:
            user = session.query(User).filter_by(user_id="123").first()
        # Session automatically closed
    
    Yields:
        SQLAlchemy Session
    """
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# FastAPI dependency for automatic session injection
def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to inject database session.
    
    Usage in route handler:
        @app.get("/users/{user_id}")
        def get_user(user_id: str, db: Session = Depends(get_db)):
            user = db.query(User).filter_by(user_id=user_id).first()
            return user
    
    Yields:
        SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db(database_url: str = DATABASE_URL) -> None:
    """
    Initialize database schema.
    
    Creates all tables if they don't exist.
    Safe to call multiple times.
    
    Args:
        database_url: Connection string
    """
    # Create engine for this operation
    init_engine = create_db_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(bind=init_engine)
    
    print(f"✓ Database initialized: {database_url}")
    
    init_engine.dispose()


def drop_db(database_url: str = DATABASE_URL) -> None:
    """
    Drop all database tables.
    
    WARNING: This deletes all data! Use only in development/testing.
    
    Args:
        database_url: Connection string
    """
    # Create engine for this operation
    drop_engine = create_db_engine(database_url)
    
    # Drop all tables
    Base.metadata.drop_all(bind=drop_engine)
    
    print(f"✓ Database dropped: {database_url}")
    
    drop_engine.dispose()


def reset_db(database_url: str = DATABASE_URL) -> None:
    """
    Reset database: drop all tables and recreate schema.
    
    WARNING: This deletes all data!
    
    Args:
        database_url: Connection string
    """
    drop_db(database_url)
    init_db(database_url)
    print("✓ Database reset complete")


def get_db_info() -> dict:
    """
    Get database connection information and statistics.
    
    Returns:
        Dictionary with database info
    """
    return {
        "database_url": DATABASE_URL,
        "environment": ENV,
        "debug_mode": DEBUG,
        "engine_url": str(engine.url),
        "engine_dialect": engine.dialect.name,
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_session_context() as session:
            # Simple query to verify connection
            session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

async def startup_db():
    """
    Database startup sequence.
    
    Call this in FastAPI lifespan/startup event:
        @app.on_event("startup")
        async def startup():
            await startup_db()
    """
    print("Starting database...")
    
    # Check configuration
    db_info = get_db_info()
    print(f"  Database: {db_info['database_url']}")
    print(f"  Environment: {db_info['environment']}")
    
    # Initialize schema
    init_db()
    
    # Verify connection
    if check_db_connection():
        print("✓ Database ready")
    else:
        raise RuntimeError("Failed to connect to database")


async def shutdown_db():
    """
    Database shutdown sequence.
    
    Call this in FastAPI lifespan/shutdown event:
        @app.on_event("shutdown")
        async def shutdown():
            await shutdown_db()
    """
    print("Closing database connections...")
    engine.dispose()
    print("✓ Database connections closed")


# ============================================================================
# BULK OPERATIONS
# ============================================================================

def bulk_insert(items: list, session: Session = None) -> None:
    """
    Efficiently insert multiple items.
    
    Args:
        items: List of model instances
        session: Optional session (creates new if not provided)
    """
    if not session:
        session = get_session()
        should_close = True
    else:
        should_close = False
    
    try:
        session.add_all(items)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if should_close:
            session.close()


def bulk_update(updates: dict, model_class, session: Session = None) -> None:
    """
    Efficiently update multiple records.
    
    Args:
        updates: Dict mapping filter criteria to update values
        model_class: SQLAlchemy model class
        session: Optional session
    """
    if not session:
        session = get_session()
        should_close = True
    else:
        should_close = False
    
    try:
        for filters, values in updates.items():
            session.query(model_class).filter_by(**filters).update(values)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if should_close:
            session.close()


# ============================================================================
# QUERY HELPERS
# ============================================================================

class QueryHelper:
    """Helper class for common database queries"""
    
    @staticmethod
    def paginate(query, page: int = 1, page_size: int = 10):
        """
        Paginate query results.
        
        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            page_size: Items per page
            
        Returns:
            Tuple of (items, total_count)
        """
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        return items, total
    
    @staticmethod
    def get_by_id(model_class, id_value, session: Session = None):
        """
        Get single record by ID.
        
        Args:
            model_class: SQLAlchemy model
            id_value: ID value to search for
            session: Optional session
            
        Returns:
            Model instance or None
        """
        if not session:
            session = get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            # Get primary key column name
            pk_name = model_class.__table__.primary_key.columns.keys()
            if len(pk_name) == 1:
                filter_kwargs = {pk_name[0]: id_value}
                return session.query(model_class).filter_by(**filter_kwargs).first()
        finally:
            if should_close:
                session.close()
    
    @staticmethod
    def filter_by(model_class, filters: dict, session: Session = None):
        """
        Filter records by criteria.
        
        Args:
            model_class: SQLAlchemy model
            filters: Dictionary of filter criteria
            session: Optional session
            
        Returns:
            Query results
        """
        if not session:
            session = get_session()
            should_close = True
        else:
            should_close = False
        
        try:
            return session.query(model_class).filter_by(**filters).all()
        finally:
            if should_close:
                session.close()
