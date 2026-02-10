"""
Agent configuration module.

Loads configuration from environment variables with sensible defaults.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


# Compute path to .env file relative to this module
_ENV_FILE = Path(__file__).parent.parent / ".env"


class AgentSettings(BaseSettings):
    """Configuration settings for the AI Agent."""

    # OpenAI API
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for Agents SDK"
    )

    # MCP Server (legacy, kept for compatibility)
    mcp_server_url: str = Field(
        default="http://localhost:8001",
        description="URL of the MCP server (legacy)"
    )
    mcp_timeout_seconds: int = Field(
        default=30,
        description="Timeout for MCP tool invocations (FR-024)"
    )

    # Backend API
    backend_api_url: str = Field(
        default="http://localhost:8000",
        description="URL of the backend REST API"
    )

    # Agent Model Configuration
    agent_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use for the agent"
    )
    agent_temperature: float = Field(
        default=0.0,
        description="Temperature for deterministic outputs (FR-060)"
    )
    agent_max_tokens: int = Field(
        default=1000,
        description="Maximum tokens for agent responses"
    )

    # Session Configuration
    session_ttl_seconds: int = Field(
        default=1800,
        description="Session expiration time (30 minutes)"
    )
    session_store: str = Field(
        default="memory",
        description="Session storage backend (memory or redis)"
    )

    # Redis (optional)
    redis_url: str | None = Field(
        default=None,
        description="Redis URL for session storage"
    )

    # Confirmation Settings
    confirmation_timeout_seconds: int = Field(
        default=300,
        description="Timeout for pending confirmations (5 minutes)"
    )

    # Audit Settings
    audit_enabled: bool = Field(
        default=True,
        description="Enable tool invocation audit logging"
    )
    database_url: str | None = Field(
        default=None,
        description="Database URL for audit storage"
    )

    # JWT Settings (shared with backend - must match backend/src/config.py)
    better_auth_secret: str = Field(
        default="",
        description="Shared JWT secret for authentication (same as backend BETTER_AUTH_SECRET)"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    jwt_issuer: str = Field(
        default="todo-app",
        description="JWT issuer claim"
    )
    jwt_audience: str = Field(
        default="todo-api",
        description="JWT audience claim"
    )

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Singleton instance
_settings: AgentSettings | None = None


def get_settings() -> AgentSettings:
    """Get the agent settings singleton."""
    global _settings
    if _settings is None:
        _settings = AgentSettings()
    return _settings
