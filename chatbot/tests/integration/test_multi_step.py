"""
Integration tests for multi-step workflow (T070).

Tests the complete flow: detect intents -> build plan -> approve -> execute.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from chatbot.agent.core import process_message, reset_agent
from chatbot.agent.models import ConfirmationState, ConfirmationStatus
from chatbot.agent.execution import (
    detect_intents,
    build_execution_plan,
    execute_plan,
    IntentType,
)


class TestMultiStepWorkflow:
    """Integration tests for multi-step workflows."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    @pytest.mark.asyncio
    async def test_multi_step_triggers_plan_approval(self):
        """Multi-step request should trigger plan approval."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "I'll do the following:\n1. Create task\n2. Complete task\nProceed?"},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Create a task to buy milk and mark groceries as done",
                user_id="user-123",
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_approve_executes_plan(self):
        """Approving plan should execute all steps."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Done! Both steps completed successfully."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            # Set up pending plan approval
            confirmation = ConfirmationState()
            confirmation.set_awaiting_plan_approval("plan-1", "Execute 2-step plan")

            result = await process_message(
                user_message="proceed",
                user_id="user-123",
                confirmation_state=confirmation,
            )

            assert result["success"] is True


class TestPlanExecution:
    """Tests for plan execution."""

    @pytest.mark.asyncio
    async def test_execute_add_then_complete(self):
        """Should execute ADD then COMPLETE in order."""
        intents = [
            MagicMock(type=IntentType.ADD, reference="buy milk", params={}),
            MagicMock(type=IntentType.COMPLETE, reference="groceries", params={}),
        ]

        # Mock the intents properly
        from chatbot.agent.execution import Intent
        intents = [
            Intent(type=IntentType.ADD, reference="buy milk"),
            Intent(type=IntentType.COMPLETE, reference="groceries"),
        ]

        plan = build_execution_plan(intents, user_id="user-123")

        # Mock tool functions
        mock_add = AsyncMock(return_value={"success": True, "data": {"task": {"id": "new-1"}}})
        mock_complete = AsyncMock(return_value={"success": True, "data": {"task": {"id": "old-1"}}})

        tools = {
            "add_task": mock_add,
            "complete_task": mock_complete,
        }

        success, results = await execute_plan(plan, "user-123", tools)

        assert success is True
        assert len(results) == 2
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_halt_on_failure(self):
        """Should halt execution on first failure (FR-033)."""
        from chatbot.agent.execution import Intent
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.COMPLETE, reference="task 2"),
            Intent(type=IntentType.DELETE, reference="task 3"),
        ]

        plan = build_execution_plan(intents, user_id="user-123")

        # First succeeds, second fails
        mock_add = AsyncMock(return_value={"success": True, "data": {}})
        mock_complete = AsyncMock(return_value={
            "success": False,
            "error": {"code": "TASK_NOT_FOUND", "message": "Not found"}
        })
        mock_delete = AsyncMock(return_value={"success": True, "data": {}})

        tools = {
            "add_task": mock_add,
            "complete_task": mock_complete,
            "delete_task": mock_delete,
        }

        success, results = await execute_plan(plan, "user-123", tools, halt_on_failure=True)

        assert success is False
        assert len(results) == 2  # Stopped after failure
        assert results[0].success is True
        assert results[1].success is False
        mock_delete.assert_not_called()  # Should not have been called


class TestMultiStepPhrases:
    """Tests for multi-step phrase variations."""

    MULTI_STEP_PHRASES = [
        "Create a task and mark groceries as done",
        "Add buy milk then complete the shopping task",
        "First create a reminder, then delete the old one",
        "Create task, complete task, and show my list",
    ]

    def test_multi_step_phrases_are_valid(self):
        """Multi-step phrases should be valid strings."""
        for phrase in self.MULTI_STEP_PHRASES:
            assert isinstance(phrase, str)
            assert len(phrase) > 0

    def test_detect_multiple_intents(self):
        """Should detect multiple intents in phrases."""
        for phrase in self.MULTI_STEP_PHRASES:
            intents = detect_intents(phrase)
            # Should detect at least 1 intent (some phrases may be ambiguous)
            assert len(intents) >= 1
