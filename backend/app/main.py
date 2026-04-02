"""
Main FastAPI application entry point.

Initializes the AI Content Localization Platform backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.api.v1.routers import router as v1_router
from app.db.session import engine, init_db
from app.core.config import settings
from app.core.logger import get_logger


logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI instance
    """
    app = FastAPI(
        title="AI Content Localization Platform",
        description="AI-powered text localization with cultural awareness",
        version="1.0.0",
        docs_url="/v1/docs",
        openapi_url="/v1/openapi.json",
    )
    
    # CORS middleware - allow frontend to call backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(v1_router)
    
    # Startup event
    @app.on_event("startup")
    def startup():
        """Initialize database on startup"""
        logger.info("Starting up AI Content Localization Platform")
        init_db()
        logger.info("Database initialized")
    
    # Shutdown event
    @app.on_event("shutdown")
    def shutdown():
        """Cleanup on shutdown"""
        logger.info("Shutting down application")
    
    # Root endpoint
    @app.get("/", tags=["root"])
    def root():
        """Root endpoint with API info"""
        return {
            "app": settings.app_name,
            "version": "1.0.0",
            "docs": "/v1/docs",
            "health": "/v1/health",
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )

