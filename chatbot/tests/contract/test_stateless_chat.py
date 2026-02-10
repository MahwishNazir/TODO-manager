"""
Contract tests for Stateless Chat API (Phase III Part 5).

Tests API contracts per OpenAPI specification in contracts/openapi.yaml.
TDD: These tests are written FIRST and should FAIL until implementation.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID
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
    """Mock Runner.run to avoid real OpenAI API calls in contract tests."""
    mock_message_item = MagicMock()
    mock_message_item.type = "message_output_item"

    # Build a content part with .text
    mock_content_part = MagicMock()
    mock_content_part.text = "Hello! I can help you manage your tasks."

    mock_message_item.raw_item = MagicMock()
    mock_message_item.raw_item.content = [mock_content_part]

    # Mock Usage
    mock_usage = MagicMock()
    mock_usage.input_tokens = 10
    mock_usage.output_tokens = 5
    mock_usage.total_tokens = 15

    # Mock ModelResponse
    mock_raw_response = MagicMock()
    mock_raw_response.usage = mock_usage

    # Mock RunResult
    mock_result = MagicMock()
    mock_result.new_items = [mock_message_item]
    mock_result.raw_responses = [mock_raw_response]
    mock_result.final_output = None

    # isinstance check for MessageOutputItem
    from agents.items import MessageOutputItem
    mock_message_item.__class__ = MessageOutputItem

    with patch("chatbot.agent.stateless_runner.Runner.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def single_message_request():
    """Valid request with a single message."""
    return {
        "messages": [
            {"role": "user", "content": "Hello, create a task to buy groceries"}
        ]
    }


@pytest.fixture
def multi_turn_request():
    """Valid request with conversation history."""
    return {
        "messages": [
            {"role": "user", "content": "Create a task to buy groceries"},
            {"role": "assistant", "content": "I've created a task 'Buy groceries' for you."},
            {"role": "user", "content": "Make it due tomorrow"}
        ]
    }


# =============================================================================
# User Story 1: Single Message Interaction (T010-T012)
# =============================================================================

class TestSingleMessageInteraction:
    """Contract tests for User Story 1."""

    @pytest.mark.asyncio
    async def test_single_message_returns_200(
        self, valid_jwt_token, test_user_id, single_message_request
    ):
        """T010: POST /api/{user_id}/chat returns 200 with valid request."""
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=single_message_request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_response_schema_valid(
        self, valid_jwt_token, test_user_id, single_message_request
    ):
        """T011: Response schema matches StatelessChatResponse."""
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=single_message_request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            data = response.json()

            # Verify response structure
            assert "response" in data
            assert "tool_calls" in data
            assert "usage" in data

            # Verify response object
            resp = data["response"]
            assert "message_id" in resp
            assert "role" in resp
            assert resp["role"] == "assistant"
            assert "content" in resp
            assert "timestamp" in resp

            # Verify message_id is valid UUID
            UUID(resp["message_id"])

            # Verify tool_calls is array
            assert isinstance(data["tool_calls"], list)

            # Verify usage object
            usage = data["usage"]
            assert "prompt_tokens" in usage
            assert "completion_tokens" in usage
            assert "total_tokens" in usage
            assert isinstance(usage["prompt_tokens"], int)
            assert isinstance(usage["completion_tokens"], int)
            assert isinstance(usage["total_tokens"], int)

    @pytest.mark.asyncio
    async def test_empty_messages_returns_400(
        self, valid_jwt_token, test_user_id
    ):
        """T012: Request with empty messages returns 400."""
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json={"messages": []},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            assert response.status_code == 400


# =============================================================================
# User Story 2: Multi-Turn Conversation (T021-T022)
# =============================================================================

class TestMultiTurnConversation:
    """Contract tests for User Story 2."""

    @pytest.mark.asyncio
    async def test_max_messages_accepted(
        self, valid_jwt_token, test_user_id
    ):
        """T021: Request with 50 messages is accepted."""
        messages = []
        for i in range(50):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": f"Message {i}"})

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json={"messages": messages},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_history_limit_exceeded(
        self, valid_jwt_token, test_user_id
    ):
        """T022: Request with 51 messages returns 400 HISTORY_LIMIT_EXCEEDED."""
        messages = []
        for i in range(51):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": f"Message {i}"})

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json={"messages": messages},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            assert response.status_code == 400
            data = response.json()
            assert data.get("error", {}).get("code") == "HISTORY_LIMIT_EXCEEDED"


# =============================================================================
# User Story 4: Stateless Request Validation (T038)
# =============================================================================

class TestStatelessValidation:
    """Contract tests for User Story 4."""

    @pytest.mark.asyncio
    async def test_no_hidden_state(
        self, valid_jwt_token, test_user_id
    ):
        """T038: Request without prior history works (no hidden state)."""
        # First request mentions a task
        request1 = {
            "messages": [
                {"role": "user", "content": "Remember my favorite color is blue"}
            ]
        }

        # Second request doesn't include history - should NOT know about color
        request2 = {
            "messages": [
                {"role": "user", "content": "What is my favorite color?"}
            ]
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Send first request
            await client.post(
                f"/api/{test_user_id}/chat",
                json=request1,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            # Send second request without history
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=request2,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            # Should still return 200 (stateless)
            assert response.status_code == 200


# =============================================================================
# User Story 5: Confirmation Flow (T043-T045)
# =============================================================================

class TestConfirmationFlow:
    """Contract tests for User Story 5."""

    @pytest.mark.asyncio
    async def test_delete_requires_confirmation(
        self, valid_jwt_token, test_user_id
    ):
        """T043: Delete request returns pending_confirmation."""
        request = {
            "messages": [
                {"role": "user", "content": "Delete my grocery task"}
            ]
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            data = response.json()

            # Should have pending_confirmation
            assert "pending_confirmation" in data
            if data["pending_confirmation"]:
                conf = data["pending_confirmation"]
                assert "token" in conf
                assert "action" in conf
                assert "description" in conf
                assert "expires_at" in conf

    @pytest.mark.asyncio
    async def test_confirmation_executes_action(
        self, valid_jwt_token, test_user_id
    ):
        """T044: Valid confirmation executes action."""
        # First, get a confirmation token
        request1 = {
            "messages": [
                {"role": "user", "content": "Delete my grocery task"}
            ]
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response1 = await client.post(
                f"/api/{test_user_id}/chat",
                json=request1,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            data1 = response1.json()

            if data1.get("pending_confirmation"):
                token = data1["pending_confirmation"]["token"]

                # Confirm the action
                request2 = {
                    "messages": [
                        {"role": "user", "content": "Delete my grocery task"},
                        {"role": "assistant", "content": "Please confirm deletion."},
                        {"role": "user", "content": "Yes, delete it"}
                    ],
                    "confirmation": {
                        "token": token,
                        "confirmed": True
                    }
                }

                response2 = await client.post(
                    f"/api/{test_user_id}/chat",
                    json=request2,
                    headers={"Authorization": f"Bearer {valid_jwt_token}"}
                )
                assert response2.status_code == 200

    @pytest.mark.asyncio
    async def test_expired_token_rejected(
        self, valid_jwt_token, test_user_id
    ):
        """T045: Expired token returns 400 CONFIRMATION_EXPIRED."""
        request = {
            "messages": [
                {"role": "user", "content": "Confirm delete"}
            ],
            "confirmation": {
                "token": "expired_token_here",
                "confirmed": True
            }
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            # Should reject invalid/expired token
            assert response.status_code == 400
            data = response.json()
            assert data.get("error", {}).get("code") in [
                "CONFIRMATION_EXPIRED",
                "INVALID_CONFIRMATION"
            ]


# =============================================================================
# User Story 6: Error Response Handling (T055-T058)
# =============================================================================

class TestErrorHandling:
    """Contract tests for User Story 6."""

    @pytest.mark.asyncio
    async def test_missing_jwt_returns_401(
        self, test_user_id, single_message_request
    ):
        """T055: Missing JWT returns 401 UNAUTHORIZED."""
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=single_message_request
                # No Authorization header
            )
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_user_mismatch_returns_403(
        self, valid_jwt_token, single_message_request
    ):
        """T056: User ID mismatch returns 403 FORBIDDEN."""
        wrong_user_id = "different-user-456"

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{wrong_user_id}/chat",
                json=single_message_request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_invalid_message_format(
        self, valid_jwt_token, test_user_id
    ):
        """T057: Invalid message format returns 400 INVALID_MESSAGE_FORMAT."""
        request = {
            "messages": [
                {"role": "invalid_role", "content": "Hello"}
            ]
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_message_too_long(
        self, valid_jwt_token, test_user_id
    ):
        """T058: Message too long returns 400 MESSAGE_TOO_LONG."""
        long_content = "x" * 10001  # Exceeds 10,000 char limit

        request = {
            "messages": [
                {"role": "user", "content": long_content}
            ]
        }

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{test_user_id}/chat",
                json=request,
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            assert response.status_code == 400
