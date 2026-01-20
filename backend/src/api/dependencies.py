"""
FastAPI dependency injection functions.

This module provides dependency functions for FastAPI routes,
including database session management.
"""

from typing import Generator
from sqlmodel import Session
from src.database import get_session


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get database session.

    This function provides a database session to route handlers
    using FastAPI's dependency injection system. The session is
    automatically committed on success or rolled back on error.

    Yields:
        Session: SQLModel database session

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.exec(select(Item)).all()
            return items
    """
    yield from get_session()
