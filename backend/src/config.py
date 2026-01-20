"""
Configuration module for Phase II Step 1.

Loads environment variables from .env file and provides
centralized configuration settings for the application.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


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

    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/dbname"
    )

    # API settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS configuration
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001"
    )

    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # JWT Authentication (Phase II Step 2)
    BETTER_AUTH_SECRET: str = os.getenv(
        "BETTER_AUTH_SECRET",
        "your-256-bit-secret-key-here-replace-with-actual-secret"
    )
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

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
