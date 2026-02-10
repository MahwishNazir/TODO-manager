"""
Database configuration module for chatbot audit storage.

Configures SQLModel engine with connection pooling for PostgreSQL/Neon.
Used for tool invocation audit logging (FR-022, FR-062).
"""

from typing import Generator, Optional
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import QueuePool, NullPool

from chatbot.agent.config import get_settings


# Database engine singleton
_engine = None


def get_engine():
    """
    Get the database engine singleton.

    Creates engine on first call using settings from config.

    Returns:
        SQLModel engine or None if database_url not configured
    """
    global _engine
    settings = get_settings()

    if not settings.database_url:
        return None

    if _engine is None:
        # Use NullPool for serverless environments
        # Use QueuePool for persistent connections
        pool_class = NullPool if "neon" in settings.database_url else QueuePool
        pool_config = {}

        if pool_class == QueuePool:
            pool_config = {
                "pool_size": 3,
                "max_overflow": 5,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            }

        _engine = create_engine(
            settings.database_url,
            echo=False,
            poolclass=pool_class,
            **pool_config,
        )

    return _engine


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.

    Yields:
        SQLModel Session

    Raises:
        RuntimeError: If database is not configured
    """
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL in environment.")

    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def init_db() -> bool:
    """
    Initialize database tables.

    Creates all tables defined in SQLModel metadata.

    Returns:
        True if successful, False if database not configured
    """
    engine = get_engine()
    if engine is None:
        return False

    # Import models to register them with SQLModel
    from chatbot.agent.models.audit_db import ToolInvocationDB  # noqa: F401

    SQLModel.metadata.create_all(engine)
    return True


def reset_engine() -> None:
    """Reset the engine singleton (for testing)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None
