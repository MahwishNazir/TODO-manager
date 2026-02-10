"""
Pytest fixtures for AI Agent tests.

Provides common fixtures for unit, integration, and contract tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from chatbot.agent.config import AgentSettings


@pytest.fixture
def test_settings() -> AgentSettings:
    """Create test settings with mock values."""
    return AgentSettings(
        openai_api_key="test-api-key",
        mcp_server_url="http://localhost:8001",
        mcp_timeout_seconds=5,
        agent_model="gpt-4",
        agent_temperature=0.0,
        session_ttl_seconds=300,
        session_store="memory",
        confirmation_timeout_seconds=60,
        audit_enabled=False,
        jwt_secret="test-secret-key",
    )


@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client for testing."""
    client = AsyncMock()
    client.call_tool = AsyncMock()
    return client


@pytest.fixture
def sample_user_id() -> str:
    """Generate a sample user ID for tests."""
    return str(uuid4())


@pytest.fixture
def sample_session_id() -> str:
    """Generate a sample session ID for tests."""
    return str(uuid4())


@pytest.fixture
def sample_task():
    """Create a sample task response."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "title": "Buy groceries",
        "description": "Get milk, eggs, and bread",
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_task_list(sample_task):
    """Create a sample task list response."""
    return {
        "tasks": [
            sample_task,
            {
                **sample_task,
                "id": str(uuid4()),
                "title": "Call mom",
                "description": None,
            },
            {
                **sample_task,
                "id": str(uuid4()),
                "title": "Finish report",
                "status": "completed",
            },
        ],
        "total_count": 3,
        "has_more": False,
    }


@pytest.fixture
def mock_mcp_success_response(sample_task):
    """Create a mock successful MCP response."""
    return {
        "success": True,
        "data": {"task": sample_task},
        "error": None,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": str(uuid4()),
        },
    }


@pytest.fixture
def mock_mcp_error_response():
    """Create a mock error MCP response."""
    return {
        "success": False,
        "data": None,
        "error": {
            "code": "TASK_NOT_FOUND",
            "message": "Task with the specified ID was not found",
            "details": {"task_id": "nonexistent-id"},
        },
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": str(uuid4()),
        },
    }


@pytest.fixture
def mock_agent_context():
    """Create a mock agent context for testing."""
    return {
        "messages": [],
        "last_mentioned_task_id": None,
        "last_mentioned_task_ref": None,
        "confirmation_state": {
            "state": "IDLE",
            "pending_action": None,
            "affected_ids": [],
            "requested_at": None,
        },
    }
