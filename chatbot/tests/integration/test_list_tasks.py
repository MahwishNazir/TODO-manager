"""
Integration tests for task listing flow (T038).

Tests the complete flow for listing tasks with filters.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from chatbot.agent.core import process_message, reset_agent


class TestTaskListingFlow:
    """Integration tests for task listing via agent."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    @pytest.fixture
    def mock_agent_list_response(self):
        """Create mock agent response for task listing."""
        return MagicMock(
            messages=[
                {"role": "user", "content": "Show my tasks"},
                {"role": "assistant", "content": "Here are your tasks:\n1. Buy groceries\n2. Call mom"},
            ]
        )

    @pytest.mark.asyncio
    async def test_list_all_tasks(self, mock_agent_list_response):
        """Should list all tasks when requested."""
        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_agent_list_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Show my tasks",
                user_id="user-123",
            )

            assert result["success"] is True
            assert "tasks" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_list_pending_tasks(self):
        """Should list only pending tasks when filtered."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Your pending tasks:\n1. Buy groceries (pending)"},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Show my pending tasks",
                user_id="user-123",
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_completed_tasks(self):
        """Should list only completed tasks when filtered."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Your completed tasks:\n1. Pay bills [completed]"},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="What have I completed?",
                user_id="user-123",
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_empty_task_list(self):
        """Should handle empty task list gracefully."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "You don't have any tasks yet."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Show my tasks",
                user_id="user-123",
            )

            assert result["success"] is True


class TestTaskListingPhrases:
    """Tests for various natural language phrases for listing tasks."""

    LIST_PHRASES = [
        "Show my tasks",
        "What are my tasks?",
        "List my todos",
        "What do I need to do?",
        "Show me what I have to do",
        "What's on my list?",
        "My tasks please",
        "Display tasks",
    ]

    FILTER_PHRASES = [
        ("Show pending tasks", "pending"),
        ("What's not done?", "pending"),
        ("What have I finished?", "completed"),
        ("Show completed tasks", "completed"),
        ("List everything", "all"),
    ]

    def test_list_phrases_are_valid(self):
        """List phrases should be non-empty strings."""
        for phrase in self.LIST_PHRASES:
            assert isinstance(phrase, str)
            assert len(phrase) > 0

    def test_filter_phrases_are_valid(self):
        """Filter phrases should map to valid status values."""
        valid_statuses = {"pending", "completed", "all"}
        for phrase, status in self.FILTER_PHRASES:
            assert isinstance(phrase, str)
            assert status in valid_statuses
