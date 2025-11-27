"""Main FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        print(f"[STARTUP] Initializing {settings.PROJECT_NAME} v{settings.VERSION}...")
        print(f"[STARTUP] Environment: {settings.ENVIRONMENT}")
        print(f"[STARTUP] Database type: {'PostgreSQL' if 'postgresql' in settings.DATABASE_URL else 'SQLite'}")
        init_db()
        print(f"[STARTUP] Database initialized successfully!")
        print(f"[STARTUP] {settings.PROJECT_NAME} v{settings.VERSION} started successfully!")
        print(f"[INFO] API Documentation: /docs")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        print(f"[ERROR] Database URL pattern: {settings.DATABASE_URL[:30]}...")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"[SHUTDOWN] {settings.PROJECT_NAME} shutting down...")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API health check.
    
    Returns:
        API information
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.API_V1_STR
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

