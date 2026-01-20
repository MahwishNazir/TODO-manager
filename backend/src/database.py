"""
Database configuration module for Phase II Step 1.

This module configures SQLModel engine with connection pooling for Neon Serverless PostgreSQL.
Connection pooling settings are optimized for serverless database environments.
"""

from typing import Generator
from sqlmodel import Session, create_engine
from sqlalchemy.pool import QueuePool
from src.config import settings


# Create SQLModel engine with connection pooling
# - pool_size=5: Maximum connections to keep in pool
# - max_overflow=10: Additional connections when pool is exhausted
# - pool_pre_ping=True: Verify connections before using (essential for serverless)
# - pool_recycle=3600: Recycle connections after 1 hour to avoid stale connections
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries when DEBUG=True
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields a SQLModel Session that automatically commits on success
    and rolls back on exceptions. Use with FastAPI Depends() for
    automatic session management.

    Yields:
        Session: SQLModel database session

    Example:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            items = session.exec(select(Item)).all()
            return items
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
