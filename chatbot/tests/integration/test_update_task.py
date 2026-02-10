"""
Integration tests for task update flow (T048).

Tests the complete flow for updating tasks via natural language.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from chatbot.agent.core import process_message, reset_agent


class TestTaskUpdateFlow:
    """Integration tests for task update via agent."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    @pytest.mark.asyncio
    async def test_update_task_title(self):
        """Should update task title via natural language."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "I've updated 'Buy groceries' to 'Buy groceries and snacks'."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Change 'Buy groceries' to 'Buy groceries and snacks'",
                user_id="user-123",
            )

            assert result["success"] is True
            assert "updated" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_complete_task_via_natural_language(self):
        """Should mark task as complete via natural language."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Great! I've marked 'Buy groceries' as complete."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Mark buy groceries as done",
                user_id="user-123",
            )

            assert result["success"] is True
            assert "complete" in result["response"].lower() or "done" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_update_with_pronoun_reference(self):
        """Should resolve 'that task' from context."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "I've updated the priority for that task."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            # First set up context with a recently mentioned task
            from chatbot.agent.models import ConversationContext
            context = ConversationContext()
            context.set_last_mentioned_task("task-123", "buy groceries")

            result = await process_message(
                user_message="Make that one high priority",
                user_id="user-123",
                context=context,
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_task_not_found(self):
        """Should handle task not found gracefully."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "I couldn't find a task called 'nonexistent task'. Would you like to see your tasks?"},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Update nonexistent task",
                user_id="user-123",
            )

            assert result["success"] is True
            # Agent should provide helpful response even for not found


class TestUpdatePhraseVariations:
    """Tests for various natural language phrases for updating."""

    UPDATE_PHRASES = [
        "Change the groceries task to high priority",
        "Update my task",
        "Rename 'buy groceries' to 'buy food'",
        "Edit the task title",
        "Modify the description",
    ]

    COMPLETE_PHRASES = [
        "Mark groceries as done",
        "Complete the buy groceries task",
        "I finished buying groceries",
        "Check off buy groceries",
        "Done with groceries",
    ]

    def test_update_phrases_are_valid(self):
        """Update phrases should be non-empty strings."""
        for phrase in self.UPDATE_PHRASES:
            assert isinstance(phrase, str)
            assert len(phrase) > 0

    def test_complete_phrases_are_valid(self):
        """Complete phrases should be non-empty strings."""
        for phrase in self.COMPLETE_PHRASES:
            assert isinstance(phrase, str)
            assert len(phrase) > 0
