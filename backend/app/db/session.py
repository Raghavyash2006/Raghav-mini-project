from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings
from typing import Generator

# Create database engine with SQLite optimizations
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)


def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI routes"""
    with Session(engine) as session:
        yield session
