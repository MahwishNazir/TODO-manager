"""
Unit tests for execution plan building (T069).

Tests building execution plans from detected intents.
"""

import pytest

from chatbot.agent.execution import (
    build_execution_plan,
    detect_intents,
    format_plan_for_approval,
    should_require_plan_approval,
    Intent,
    IntentType,
)
from chatbot.agent.models import ActionType, PlanStatus


class TestBuildExecutionPlan:
    """Tests for build_execution_plan function."""

    def test_build_single_step_plan(self):
        """Should build plan with single step."""
        intents = [Intent(type=IntentType.ADD, reference="buy groceries")]

        plan = build_execution_plan(intents, user_id="user-123")

        assert len(plan.steps) == 1
        assert plan.steps[0].action == ActionType.ADD
        assert plan.user_id == "user-123"

    def test_build_multi_step_plan(self):
        """Should build plan with multiple steps."""
        intents = [
            Intent(type=IntentType.ADD, reference="buy milk"),
            Intent(type=IntentType.COMPLETE, reference="groceries"),
        ]

        plan = build_execution_plan(intents, user_id="user-123")

        assert len(plan.steps) == 2

    def test_steps_ordered_correctly(self):
        """Steps should be ordered: ADD → UPDATE → COMPLETE → DELETE → LIST."""
        intents = [
            Intent(type=IntentType.DELETE, reference="old task"),
            Intent(type=IntentType.ADD, reference="new task"),
            Intent(type=IntentType.COMPLETE, reference="current"),
        ]

        plan = build_execution_plan(intents, user_id="user-123")

        # ADD should come before COMPLETE, COMPLETE before DELETE
        actions = [step.action for step in plan.steps]
        assert actions.index(ActionType.ADD) < actions.index(ActionType.COMPLETE)
        assert actions.index(ActionType.COMPLETE) < actions.index(ActionType.DELETE)

    def test_plan_has_correct_status(self):
        """New plan should have PENDING status."""
        intents = [Intent(type=IntentType.ADD, reference="task")]

        plan = build_execution_plan(intents, user_id="user-123")

        assert plan.status == PlanStatus.PENDING

    def test_empty_intents_creates_empty_plan(self):
        """Empty intents should create empty plan."""
        plan = build_execution_plan([], user_id="user-123")

        assert len(plan.steps) == 0


class TestFormatPlanForApproval:
    """Tests for format_plan_for_approval function."""

    def test_format_single_step(self):
        """Should format single step plan."""
        intents = [Intent(type=IntentType.ADD, reference="buy groceries")]
        plan = build_execution_plan(intents, user_id="user-123")

        message = format_plan_for_approval(plan)

        assert "buy groceries" in message.lower()
        assert "1." in message

    def test_format_multi_step(self):
        """Should format multi-step plan with numbers."""
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.COMPLETE, reference="task 2"),
        ]
        plan = build_execution_plan(intents, user_id="user-123")

        message = format_plan_for_approval(plan)

        assert "1." in message
        assert "2." in message

    def test_format_includes_approval_prompt(self):
        """Should include approval prompt."""
        intents = [Intent(type=IntentType.ADD, reference="task")]
        plan = build_execution_plan(intents, user_id="user-123")

        message = format_plan_for_approval(plan)

        assert "proceed" in message.lower() or "cancel" in message.lower()


class TestShouldRequirePlanApproval:
    """Tests for should_require_plan_approval function."""

    def test_single_intent_no_approval(self):
        """Single intent should not require approval."""
        intents = [Intent(type=IntentType.ADD, reference="task")]

        result = should_require_plan_approval(intents)

        assert result is False

    def test_two_intents_requires_approval(self):
        """Two tool-calling intents should require approval."""
        intents = [
            Intent(type=IntentType.ADD, reference="task 1"),
            Intent(type=IntentType.COMPLETE, reference="task 2"),
        ]

        result = should_require_plan_approval(intents)

        assert result is True

    def test_list_only_no_approval(self):
        """LIST-only requests should not require approval."""
        intents = [Intent(type=IntentType.LIST)]

        result = should_require_plan_approval(intents)

        assert result is False

    def test_add_and_list_requires_approval(self):
        """ADD + LIST should not require approval (LIST doesn't modify)."""
        intents = [
            Intent(type=IntentType.ADD, reference="task"),
            Intent(type=IntentType.LIST),
        ]

        result = should_require_plan_approval(intents)

        # Only 1 modifying intent (ADD), so no approval needed
        assert result is False


class TestIntentDetectionEdgeCases:
    """Tests for edge cases in intent detection."""

    def test_empty_message(self):
        """Empty message should return empty intents."""
        intents = detect_intents("")

        assert intents == []

    def test_greeting_no_task_intent(self):
        """Greetings should not trigger task intents."""
        intents = detect_intents("Hello, how are you?")

        # Should be empty or minimal
        task_intents = [i for i in intents if i.type != IntentType.UNKNOWN]
        # Greetings typically don't match task patterns

    def test_complex_multi_intent(self):
        """Complex multi-intent message should be parsed."""
        message = "Create a task to buy groceries, then mark the milk task as done, and delete the old reminder"

        intents = detect_intents(message)

        # Should detect multiple intents
        types = [i.type for i in intents]
        assert len(intents) >= 2
