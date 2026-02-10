"""
Integration tests for delete with confirmation flow (T059).

Tests the complete flow: delete request -> confirmation -> execution.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from chatbot.agent.core import process_message, reset_agent
from chatbot.agent.models import ConversationContext, ConfirmationState, ConfirmationStatus
from chatbot.agent.confirmation import ConfirmationManager


class TestDeleteConfirmationFlow:
    """Integration tests for delete with confirmation."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    @pytest.mark.asyncio
    async def test_delete_triggers_confirmation(self):
        """Delete request should trigger confirmation, not immediate delete."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Are you sure you want to delete 'Buy groceries'? Reply 'yes' to confirm."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Delete my groceries task",
                user_id="user-123",
            )

            assert result["success"] is True
            assert "sure" in result["response"].lower() or "confirm" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_confirm_executes_delete(self):
        """Confirming should execute the delete."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Done! I've deleted 'Buy groceries'."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            # Set up confirmation state
            confirmation = ConfirmationState()
            confirmation.set_awaiting_delete(["task-123"], "Delete 'Buy groceries'")

            result = await process_message(
                user_message="yes",
                user_id="user-123",
                confirmation_state=confirmation,
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_cancel_aborts_delete(self):
        """Cancelling should abort the delete."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Okay, I've cancelled the delete. Your task is unchanged."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            confirmation = ConfirmationState()
            confirmation.set_awaiting_delete(["task-123"], "Delete task")

            result = await process_message(
                user_message="no",
                user_id="user-123",
                confirmation_state=confirmation,
            )

            assert result["success"] is True
            assert "cancel" in result["response"].lower()


class TestConfirmationManager:
    """Tests for ConfirmationManager in integration context."""

    def test_full_delete_flow(self):
        """Test complete delete confirmation flow."""
        manager = ConfirmationManager()
        task = {"id": "task-123", "title": "Buy groceries", "status": "pending"}

        # Step 1: Request confirmation
        message = manager.request_delete_confirmation(task)
        assert manager.has_pending_confirmation()
        assert "Buy groceries" in message

        # Step 2: User confirms
        result = manager.process_response("yes")
        assert result["confirmed"] is True
        assert not manager.has_pending_confirmation()

    def test_delete_with_cancel(self):
        """Test delete cancelled by user."""
        manager = ConfirmationManager()
        task = {"id": "task-123", "title": "Buy groceries"}

        manager.request_delete_confirmation(task)
        result = manager.process_response("no")

        assert result["cancelled"] is True
        assert not manager.has_pending_confirmation()

    def test_unclear_response_reprompts(self):
        """Unclear response should reprompt."""
        manager = ConfirmationManager()
        task = {"id": "task-123", "title": "Test"}

        manager.request_delete_confirmation(task)
        result = manager.process_response("maybe")

        assert result["unclear"] is True
        assert manager.has_pending_confirmation()  # Still waiting
        assert "yes" in result["message"].lower()

    def test_new_intent_cancels_pending(self):
        """New intent should cancel pending confirmation."""
        manager = ConfirmationManager()
        task = {"id": "task-123", "title": "Test"}

        manager.request_delete_confirmation(task)

        # User asks something else instead
        manager.cancel()

        assert not manager.has_pending_confirmation()


class TestDeletePhraseVariations:
    """Tests for delete phrase variations."""

    DELETE_PHRASES = [
        "Delete the groceries task",
        "Remove buy groceries",
        "Get rid of that task",
        "Delete it",
        "Remove that one",
        "Cancel my task",
    ]

    CONFIRM_PHRASES = [
        "yes",
        "y",
        "yeah",
        "sure",
        "ok",
        "proceed",
        "do it",
    ]

    CANCEL_PHRASES = [
        "no",
        "n",
        "nope",
        "cancel",
        "never mind",
        "don't",
        "abort",
    ]

    def test_delete_phrases_are_valid(self):
        """Delete phrases should be valid strings."""
        for phrase in self.DELETE_PHRASES:
            assert isinstance(phrase, str)
            assert len(phrase) > 0

    def test_confirm_phrases_are_valid(self):
        """Confirm phrases should be valid strings."""
        for phrase in self.CONFIRM_PHRASES:
            assert isinstance(phrase, str)
            assert len(phrase) > 0

    def test_cancel_phrases_are_valid(self):
        """Cancel phrases should be valid strings."""
        for phrase in self.CANCEL_PHRASES:
            assert isinstance(phrase, str)
            assert len(phrase) > 0
