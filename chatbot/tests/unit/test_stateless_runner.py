"""
Unit tests for StatelessAgentRunner (Phase III Part 5).

TDD: These tests are written FIRST and should FAIL until implementation.
Tests T013-T014 for User Story 1, and T036 for User Story 4.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID


def _make_mock_run_result(content_text="Hello! How can I help?", input_tokens=10, output_tokens=5, total_tokens=15):
    """Build a mock RunResult matching the real OpenAI Agents SDK shape."""
    from agents.items import MessageOutputItem

    mock_message_item = MagicMock()
    mock_message_item.type = "message_output_item"
    mock_message_item.__class__ = MessageOutputItem

    mock_content_part = MagicMock()
    mock_content_part.text = content_text

    mock_message_item.raw_item = MagicMock()
    mock_message_item.raw_item.content = [mock_content_part]

    mock_usage = MagicMock()
    mock_usage.input_tokens = input_tokens
    mock_usage.output_tokens = output_tokens
    mock_usage.total_tokens = total_tokens

    mock_raw_response = MagicMock()
    mock_raw_response.usage = mock_usage

    mock_result = MagicMock()
    mock_result.new_items = [mock_message_item]
    mock_result.raw_responses = [mock_raw_response]
    mock_result.final_output = None

    return mock_result


# =============================================================================
# User Story 1: Single Message Interaction (T013-T014)
# =============================================================================

class TestStatelessAgentRunnerUS1:
    """Unit tests for User Story 1."""

    @pytest.mark.asyncio
    async def test_run_returns_message_id(self):
        """T013: StatelessAgentRunner.run() returns response with message_id."""
        with patch("chatbot.agent.stateless_runner.Agent") as mock_agent_class:
            mock_agent_class.return_value = MagicMock()

            from chatbot.agent.stateless_runner import StatelessAgentRunner
            import chatbot.agent.stateless_runner as runner_module
            runner_module._runner = None

            runner = StatelessAgentRunner()
            messages = [{"role": "user", "content": "Hello"}]
            user_id = "test-user-123"

            with patch("chatbot.agent.stateless_runner.Runner.run", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = _make_mock_run_result()

                result = await runner.run(messages=messages, user_id=user_id)

            assert "response" in result
            assert "message_id" in result["response"]
            UUID(result["response"]["message_id"])

    @pytest.mark.asyncio
    async def test_token_usage_populated(self):
        """T014: TokenUsage populated from agent result."""
        with patch("chatbot.agent.stateless_runner.Agent") as mock_agent_class:
            mock_agent_class.return_value = MagicMock()

            from chatbot.agent.stateless_runner import StatelessAgentRunner
            import chatbot.agent.stateless_runner as runner_module
            runner_module._runner = None

            runner = StatelessAgentRunner()
            messages = [{"role": "user", "content": "List tasks"}]
            user_id = "test-user-123"

            with patch("chatbot.agent.stateless_runner.Runner.run", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = _make_mock_run_result(
                    content_text="Here are your tasks.",
                    input_tokens=25,
                    output_tokens=12,
                    total_tokens=37,
                )

                result = await runner.run(messages=messages, user_id=user_id)

            assert "usage" in result
            usage = result["usage"]
            assert "prompt_tokens" in usage
            assert "completion_tokens" in usage
            assert "total_tokens" in usage

            assert isinstance(usage["prompt_tokens"], int)
            assert isinstance(usage["completion_tokens"], int)
            assert isinstance(usage["total_tokens"], int)

    @pytest.mark.asyncio
    async def test_response_has_required_fields(self):
        """Response should have message_id, role, content, timestamp."""
        with patch("chatbot.agent.stateless_runner.Agent") as mock_agent_class:
            mock_agent_class.return_value = MagicMock()

            from chatbot.agent.stateless_runner import StatelessAgentRunner
            import chatbot.agent.stateless_runner as runner_module
            runner_module._runner = None

            runner = StatelessAgentRunner()
            messages = [{"role": "user", "content": "Test message"}]
            user_id = "test-user-123"

            with patch("chatbot.agent.stateless_runner.Runner.run", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = _make_mock_run_result(
                    content_text="Test response",
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                )

                result = await runner.run(messages=messages, user_id=user_id)

            response = result["response"]

            assert "message_id" in response
            assert "role" in response
            assert "content" in response
            assert "timestamp" in response

            assert response["role"] == "assistant"

            # Timestamp should be ISO format
            datetime.fromisoformat(response["timestamp"].replace("Z", "+00:00"))


# =============================================================================
# User Story 4: Stateless Validation (T036)
# =============================================================================

class TestStatelessValidation:
    """Unit tests for User Story 4."""

    @pytest.mark.asyncio
    async def test_no_state_between_requests(self):
        """T036: No server-side state stored between requests."""
        with patch("chatbot.agent.stateless_runner.Agent") as mock_agent_class:
            mock_agent_class.return_value = MagicMock()

            from chatbot.agent.stateless_runner import StatelessAgentRunner
            import chatbot.agent.stateless_runner as runner_module
            runner_module._runner = None

            runner = StatelessAgentRunner()
            user_id = "test-user-123"

            # Track what input is passed to Runner.run
            captured_inputs = []

            async def capture_run(starting_agent, input, **kwargs):
                captured_inputs.append(input)
                return _make_mock_run_result(content_text="Response")

            with patch("chatbot.agent.stateless_runner.Runner.run", side_effect=capture_run):
                # First request with context
                await runner.run(
                    messages=[{"role": "user", "content": "My name is Alice"}],
                    user_id=user_id,
                )

            with patch("chatbot.agent.stateless_runner.Runner.run", side_effect=capture_run):
                # Second request WITHOUT including previous context
                await runner.run(
                    messages=[{"role": "user", "content": "What is my name?"}],
                    user_id=user_id,
                )

            # Verify second request only received the single message
            assert len(captured_inputs) == 2
            assert len(captured_inputs[1]) == 1
            assert captured_inputs[1][0]["content"] == "What is my name?"

    @pytest.mark.asyncio
    async def test_fresh_context_per_request(self):
        """Each request should create fresh tool collector context."""
        with patch("chatbot.agent.stateless_runner.Agent") as mock_agent_class:
            mock_agent_class.return_value = MagicMock()

            from chatbot.agent.stateless_runner import StatelessAgentRunner
            from chatbot.agent.tool_collector import ToolCallCollector
            import chatbot.agent.stateless_runner as runner_module
            runner_module._runner = None

            runner = StatelessAgentRunner()
            user_id = "test-user-123"

            collectors_created = []
            original_init = ToolCallCollector.__init__

            def tracking_init(self, *args, **kwargs):
                collectors_created.append(self)
                return original_init(self, *args, **kwargs)

            with patch.object(ToolCallCollector, '__init__', tracking_init):
                with patch("chatbot.agent.stateless_runner.Runner.run", new_callable=AsyncMock) as mock_run:
                    mock_run.return_value = _make_mock_run_result()

                    await runner.run(
                        messages=[{"role": "user", "content": "Request 1"}],
                        user_id=user_id,
                    )
                    await runner.run(
                        messages=[{"role": "user", "content": "Request 2"}],
                        user_id=user_id,
                    )

            # Two fresh collectors should have been created
            assert len(collectors_created) == 2


# =============================================================================
# Error Handling
# =============================================================================

class TestStatelessRunnerErrors:
    """Unit tests for error handling."""

    @pytest.mark.asyncio
    async def test_handles_agent_exception(self):
        """Runner should handle agent exceptions gracefully."""
        with patch("chatbot.agent.stateless_runner.Agent") as mock_agent_class:
            mock_agent_class.return_value = MagicMock()

            from chatbot.agent.stateless_runner import StatelessAgentRunner
            import chatbot.agent.stateless_runner as runner_module
            runner_module._runner = None

            runner = StatelessAgentRunner()
            messages = [{"role": "user", "content": "Test"}]
            user_id = "test-user-123"

            with patch("chatbot.agent.stateless_runner.Runner.run", new_callable=AsyncMock) as mock_run:
                mock_run.side_effect = Exception("Agent error")

                result = await runner.run(messages=messages, user_id=user_id)

            assert "response" in result
            assert "error" in result["response"]["content"].lower()
            assert result["usage"]["total_tokens"] == 0
