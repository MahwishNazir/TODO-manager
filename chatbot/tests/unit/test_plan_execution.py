"""
Unit tests for plan approval and sequential execution (T071).

Tests plan approval flow and step-by-step execution.
"""

import pytest
from unittest.mock import AsyncMock

from chatbot.agent.execution import (
    execute_plan,
    execute_plan_step,
    format_execution_results,
    Intent,
    IntentType,
    build_execution_plan,
)
from chatbot.agent.models import (
    ExecutionPlan,
    PlanStep,
    StepResult,
    ActionType,
    PlanStatus,
)


class TestExecutePlanStep:
    """Tests for execute_plan_step function."""

    @pytest.mark.asyncio
    async def test_execute_add_step(self):
        """Should execute ADD step successfully."""
        step = PlanStep(
            order=0,
            action=ActionType.ADD,
            params={"reference": "buy groceries"},
        )

        mock_add = AsyncMock(return_value={
            "success": True,
            "data": {"task": {"id": "task-123", "title": "buy groceries"}}
        })

        tools = {"add_task": mock_add}

        result = await execute_plan_step(step, "user-123", tools)

        assert result.success is True
        assert result.order == 0
        mock_add.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_step_failure(self):
        """Should handle step failure."""
        step = PlanStep(
            order=0,
            action=ActionType.COMPLETE,
            params={"reference": "nonexistent"},
        )

        mock_complete = AsyncMock(return_value={
            "success": False,
            "error": {"code": "TASK_NOT_FOUND", "message": "Task not found"}
        })

        tools = {"complete_task": mock_complete}

        result = await execute_plan_step(step, "user-123", tools)

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_step_exception(self):
        """Should handle exceptions during execution."""
        step = PlanStep(
            order=0,
            action=ActionType.DELETE,
            params={},
        )

        mock_delete = AsyncMock(side_effect=Exception("Connection error"))

        tools = {"delete_task": mock_delete}

        result = await execute_plan_step(step, "user-123", tools)

        assert result.success is False
        assert "Connection error" in result.error

    @pytest.mark.asyncio
    async def test_execute_unknown_action(self):
        """Should handle unknown action type."""
        step = PlanStep(
            order=0,
            action=ActionType.ADD,
            params={},
        )

        # No tools provided
        tools = {}

        result = await execute_plan_step(step, "user-123", tools)

        assert result.success is False


class TestExecutePlan:
    """Tests for execute_plan function."""

    @pytest.mark.asyncio
    async def test_execute_all_steps_success(self):
        """Should execute all steps when all succeed."""
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.ADD, reference="task 2"),
        ]
        plan = build_execution_plan(intents, user_id="user-123")

        mock_add = AsyncMock(return_value={"success": True, "data": {}})
        tools = {"add_task": mock_add}

        success, results = await execute_plan(plan, "user-123", tools)

        assert success is True
        assert len(results) == 2
        assert mock_add.call_count == 2

    @pytest.mark.asyncio
    async def test_halt_on_first_failure(self):
        """Should halt on first failure when halt_on_failure=True."""
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.ADD, reference="task 2"),
            Intent(type=IntentType.ADD, reference="task 3"),
        ]
        plan = build_execution_plan(intents, user_id="user-123")

        # First succeeds, second fails
        mock_add = AsyncMock(side_effect=[
            {"success": True, "data": {}},
            {"success": False, "error": {"message": "Error"}},
            {"success": True, "data": {}},  # Should not be called
        ])
        tools = {"add_task": mock_add}

        success, results = await execute_plan(plan, "user-123", tools, halt_on_failure=True)

        assert success is False
        assert len(results) == 2  # Only 2 executed
        assert mock_add.call_count == 2

    @pytest.mark.asyncio
    async def test_continue_on_failure(self):
        """Should continue execution when halt_on_failure=False."""
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.ADD, reference="task 2"),
        ]
        plan = build_execution_plan(intents, user_id="user-123")

        mock_add = AsyncMock(side_effect=[
            {"success": False, "error": {"message": "Error"}},
            {"success": True, "data": {}},
        ])
        tools = {"add_task": mock_add}

        success, results = await execute_plan(plan, "user-123", tools, halt_on_failure=False)

        assert success is False  # Not all succeeded
        assert len(results) == 2  # Both executed
        assert mock_add.call_count == 2

    @pytest.mark.asyncio
    async def test_empty_plan(self):
        """Should handle empty plan."""
        plan = ExecutionPlan(user_id="user-123")

        success, results = await execute_plan(plan, "user-123", {})

        assert success is True
        assert len(results) == 0


class TestFormatExecutionResults:
    """Tests for format_execution_results function."""

    def test_format_all_success(self):
        """Should format successful execution."""
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.COMPLETE, reference="task 2"),
        ]
        plan = build_execution_plan(intents, user_id="user-123")

        results = [
            StepResult(order=0, success=True),
            StepResult(order=1, success=True),
        ]

        message = format_execution_results(plan, results)

        assert "2" in message
        assert "success" in message.lower() or "completed" in message.lower()

    def test_format_partial_failure(self):
        """Should format partial failure."""
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.DELETE, reference="task 2"),
        ]
        plan = build_execution_plan(intents, user_id="user-123")

        results = [
            StepResult(order=0, success=True),
            StepResult(order=1, success=False, error="Task not found"),
        ]

        message = format_execution_results(plan, results)

        assert "1 of 2" in message or "failed" in message.lower()


class TestPlanStatus:
    """Tests for plan status transitions."""

    def test_new_plan_is_pending(self):
        """New plan should have PENDING status."""
        plan = ExecutionPlan(user_id="user-123")

        assert plan.status == PlanStatus.PENDING

    def test_plan_tracks_current_step(self):
        """Plan should track current step during execution."""
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.ADD, reference="task 2"),
        ]
        plan = build_execution_plan(intents, user_id="user-123")

        # Record first result
        plan.record_step_result(0, success=True, result={})

        # Should have one result recorded
        assert len(plan.results) == 1
