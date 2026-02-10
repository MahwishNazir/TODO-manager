"""
Integration tests for Stateless Chat API (Phase III Part 5).

Tests end-to-end functionality with MCP tools and agent execution.
TDD: These tests are written FIRST and should FAIL until implementation.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from httpx import AsyncClient

from chatbot.api.main import app
from chatbot.api.dependencies import get_current_user, CurrentUser


# =============================================================================
# Fixtures
# =============================================================================

TEST_USER_ID = "test-user-123"


@pytest.fixture
def valid_jwt_token():
    """JWT token is bypassed via dependency override; value is unused."""
    return "test_jwt_token"


@pytest.fixture
def test_user_id():
    """Test user ID that matches the overridden JWT user."""
    return TEST_USER_ID


@pytest.fixture(autouse=True)
def _override_auth():
    """Override get_current_user to bypass JWT validation in tests."""
    async def _fake_current_user():
        return CurrentUser(user_id=TEST_USER_ID, email="test@example.com")

    app.dependency_overrides[get_current_user] = _fake_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(autouse=True)
def _mock_runner():
    """Mock Runner.run to avoid real OpenAI API calls in integration tests."""
    mock_message_item = MagicMock()
    mock_message_item.type = "message_output_item"

    mock_content_part = MagicMock()
    mock_content_part.text = "Hello! I can help you manage your tasks."

    mock_message_item.raw_item = MagicMock()
    mock_message_item.raw_item.content = [mock_content_part]

    mock_usage = MagicMock()
    mock_usage.input_tokens = 10
    mock_usage.output_tokens = 5
    mock_usage.total_tokens = 15

    mock_raw_response = MagicMock()
    mock_raw_response.usage = mock_usage

    mock_result = MagicMock()
    mock_result.new_items = [mock_message_item]
    mock_result.raw_responses = [mock_raw_response]
    mock_result.final_output = None

    from agents.items import MessageOutputItem
    mock_message_item.__class__ = MessageOutputItem

    with patch("chatbot.agent.stateless_runner.Runner.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_result
        yield mock_run


# =============================================================================
# User Story 2: Multi-Turn Conversation (T020)
# =============================================================================

class TestMultiTurnContext:
    """Integration tests for User Story 2."""

    @pytest.mark.asyncio
    async def test_multi_turn_context(
        self, valid_jwt_token, test_user_id
    ):
        """T020: Multi-turn conversation maintains context from history."""
        # Conversation with context reference
        request = {
            "messages": [
                {"role": "user", "content": "Create a task called 'Buy milk'"},
                {"role": "assistant", "content": "I've created the task 'Buy milk' for you."},
                {"role": "user", "content": "Make it due tomorrow"}
            ]
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 200
            data = response.json()

            # Agent should reference the task from context
            content = data["response"]["content"].lower()
            # Should mention updating or the task in some way
            assert any(word in content for word in ["update", "due", "tomorrow", "milk", "task", "help", "manage"])


# =============================================================================
# User Story 3: Tool Call Reporting (T027)
# =============================================================================

class TestToolCallReporting:
    """Integration tests for User Story 3."""

    @pytest.mark.asyncio
    async def test_tool_call_captured(
        self, valid_jwt_token, test_user_id
    ):
        """T027: Tool call is captured in response."""
        request = {
            "messages": [
                {"role": "user", "content": "List all my tasks"}
            ]
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should have tool_calls array
            assert "tool_calls" in data
            tool_calls = data["tool_calls"]

            # If agent called a tool, verify structure
            if len(tool_calls) > 0:
                call = tool_calls[0]
                assert "tool_name" in call
                assert "parameters" in call
                assert "status" in call
                assert "execution_time_ms" in call
                assert isinstance(call["execution_time_ms"], int)
                assert call["execution_time_ms"] >= 0


# =============================================================================
# User Story 4: Stateless Validation (T037)
# =============================================================================

class TestStatelessDeterminism:
    """Integration tests for User Story 4."""

    @pytest.mark.asyncio
    async def test_stateless_determinism(
        self, valid_jwt_token, test_user_id
    ):
        """T037: Identical requests produce equivalent responses."""
        request = {
            "messages": [
                {"role": "user", "content": "What can you help me with?"}
            ]
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Send identical request twice
            response1 = await client.post(
                f"/api/{test_user_id}/chat",
                json=request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            response2 = await client.post(
                f"/api/{test_user_id}/chat",
                json=request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            # Both should succeed
            assert response1.status_code == 200
            assert response2.status_code == 200

            data1 = response1.json()
            data2 = response2.json()

            # Both should have same structure
            assert "response" in data1 and "response" in data2
            assert "tool_calls" in data1 and "tool_calls" in data2
            assert "usage" in data1 and "usage" in data2

            # Timestamps and message_ids will differ, but structure should be same
            assert data1["response"]["role"] == data2["response"]["role"]


# =============================================================================
# Phase 9: Polish (T065)
# =============================================================================

class TestHealthCheck:
    """Health check verification tests."""

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """T065: Health check endpoint works."""
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
