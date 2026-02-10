"""
Configuration module for Phase II Step 1.

Loads environment variables from .env file and provides
centralized configuration settings for the application.
"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


# Get the backend directory (parent of src/)
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL: PostgreSQL connection string for Neon database
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        DEBUG: Enable debug mode (verbose SQL logging)
        CORS_ORIGINS: List of allowed CORS origins for frontend
        HOST: API server host (default: 0.0.0.0)
        PORT: API server port (default: 8000)
        BETTER_AUTH_SECRET: Shared secret for JWT signing (HS256)
        JWT_ALGORITHM: JWT signing algorithm (HS256)
        JWT_EXPIRATION_SECONDS: JWT token expiration time (3600 = 1 hour)
        JWT_ISSUER: JWT issuer claim (todo-app)
        JWT_AUDIENCE: JWT audience claim (todo-api)
    """

    # Use modern pydantic-settings configuration
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database configuration
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # API settings
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # CORS configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT Authentication (Phase II Step 2)
    BETTER_AUTH_SECRET: str = "your-256-bit-secret-key-here-replace-with-actual-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600  # 1 hour
    JWT_ISSUER: str = "todo-app"
    JWT_AUDIENCE: str = "todo-api"

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convert CORS_ORIGINS string to list of origins.

        Returns:
            List[str]: List of allowed CORS origins
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
