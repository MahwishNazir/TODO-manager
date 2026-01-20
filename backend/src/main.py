"""
FastAPI application entry point for Phase II Step 1.

This module initializes the FastAPI application with middleware,
exception handlers, and API routes.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.config import settings
from src.api.middleware import setup_logging_middleware


# Create FastAPI application instance
app = FastAPI(
    title="TODO Application API",
    description="REST API for task management with persistent storage (Phase II Step 1)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)


# Setup logging middleware
setup_logging_middleware(app)


# Global exception handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.

    Args:
        request: FastAPI request object
        exc: SQLAlchemy exception

    Returns:
        JSONResponse with 500 status code
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error",
            "detail": "An error occurred while accessing the database",
            "type": "database_error",
        },
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(
    request: Request, exc: ValueError
) -> JSONResponse:
    """
    Handle validation errors (ValueError).

    Args:
        request: FastAPI request object
        exc: ValueError exception

    Returns:
        JSONResponse with 422 status code
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "detail": str(exc),
            "type": "validation_error",
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.

    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "phase": "II Step 1 - REST API",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: Welcome message and documentation link
    """
    return {
        "message": "TODO Application REST API - Phase II Step 1",
        "docs": "/docs",
        "health": "/health",
    }


# Register task routes
from src.api.routes import tasks
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
