"""
Integration tests for task creation flow (T029).

Tests the complete flow: user message -> agent -> tool invocation -> response.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from chatbot.agent.core import (
    process_message,
    AgentRunner,
    create_agent,
    reset_agent,
)
from chatbot.agent.models import (
    AgentSession,
    ConversationContext,
)


class TestTaskCreationFlow:
    """Integration tests for task creation via agent."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    @pytest.fixture
    def mock_agent_response(self):
        """Create mock agent response for task creation."""
        return MagicMock(
            messages=[
                {"role": "user", "content": "Create a task to buy groceries"},
                {"role": "assistant", "content": "I've created a task 'Buy groceries' for you."},
            ]
        )

    @pytest.mark.asyncio
    async def test_create_task_via_natural_language(self, mock_agent_response):
        """Should create task from natural language request."""
        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_agent_response)
            MockRunner.return_value = mock_runner_instance

            # Also mock the MCP tool invocation
            with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_mcp:
                mock_mcp.return_value = {
                    "success": True,
                    "data": {"task": {"id": "task-123", "title": "Buy groceries"}}
                }

                result = await process_message(
                    user_message="Create a task to buy groceries",
                    user_id="user-123",
                )

                assert result["success"] is True
                assert "created" in result["response"].lower() or "buy groceries" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_context_updated_after_creation(self, mock_agent_response):
        """Context should be updated with the conversation."""
        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_agent_response)
            MockRunner.return_value = mock_runner_instance

            context = ConversationContext()

            result = await process_message(
                user_message="Create a task to buy groceries",
                user_id="user-123",
                context=context,
            )

            # Context should have messages
            updated_context = result["context"]
            assert len(updated_context.messages) >= 1

    @pytest.mark.asyncio
    async def test_session_context_passed_to_runner(self, mock_agent_response):
        """Session info should be passed to runner for audit."""
        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_agent_response)
            MockRunner.return_value = mock_runner_instance

            session = AgentSession(user_id="user-123")

            runner = AgentRunner(session=session)
            await runner.run(
                user_message="Create a task",
                user_id="user-123",
            )

            # Runner should have session for context
            assert runner._session == session


class TestAgentRunnerCreation:
    """Tests for agent runner initialization."""

    def test_runner_uses_singleton_agent(self):
        """Runner should use singleton agent by default."""
        reset_agent()

        runner1 = AgentRunner()
        runner2 = AgentRunner()

        # Both should use the same agent
        assert runner1._agent is runner2._agent

    def test_runner_accepts_custom_agent(self):
        """Runner should accept custom agent."""
        custom_agent = create_agent(model="gpt-3.5-turbo")
        runner = AgentRunner(agent=custom_agent)

        assert runner._agent == custom_agent

    def test_runner_context_management(self):
        """Runner should manage context correctly."""
        runner = AgentRunner()
        context = ConversationContext()

        runner.set_context(context)
        retrieved = runner.get_context()

        assert retrieved is context


class TestTaskCreationEdgeCases:
    """Tests for edge cases in task creation."""

    @pytest.fixture
    def mock_error_response(self):
        """Create mock agent response for error."""
        return MagicMock(
            messages=[
                {"role": "user", "content": "Create a task"},
                {"role": "assistant", "content": "I couldn't understand what task you'd like to create. Please provide a title."},
            ]
        )

    @pytest.mark.asyncio
    async def test_create_task_with_description(self):
        """Should handle task with description."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Created 'Buy groceries': Get milk and bread"}
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Create a task called 'Buy groceries' with description 'Get milk and bread'",
                user_id="user-123",
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_create_task_with_date(self):
        """Should handle task with due date."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Created 'Buy groceries' due tomorrow"}
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Create a task to buy groceries tomorrow",
                user_id="user-123",
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handles_agent_error(self):
        """Should handle agent execution errors."""
        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(side_effect=Exception("Agent error"))
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Create a task",
                user_id="user-123",
            )

            assert result["success"] is False
            assert "error" in result
