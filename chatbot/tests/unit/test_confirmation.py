"""
Unit tests for confirmation state machine (T058).

Tests confirmation state transitions and expiration logic.
"""

import pytest
from datetime import datetime, timedelta, timezone

from chatbot.agent.models import ConfirmationState, ConfirmationStatus
from chatbot.agent.confirmation import (
    ConfirmationManager,
    parse_confirmation_response,
    ConfirmationResponse,
)


class TestConfirmationStateMachine:
    """Tests for ConfirmationState model transitions."""

    def test_initial_state_is_idle(self):
        """Initial state should be IDLE."""
        state = ConfirmationState()

        assert state.state == ConfirmationStatus.IDLE
        assert state.is_idle()
        assert not state.is_awaiting_confirmation()

    def test_transition_to_awaiting_delete(self):
        """Should transition to AWAITING_DELETE."""
        state = ConfirmationState()
        state.set_awaiting_delete(["task-123"], "Delete 'Buy groceries'")

        assert state.state == ConfirmationStatus.AWAITING_DELETE
        assert state.pending_action == "delete"
        assert state.affected_ids == ["task-123"]
        assert state.is_awaiting_confirmation()
        assert state.requested_at is not None

    def test_transition_to_awaiting_bulk(self):
        """Should transition to AWAITING_BULK."""
        state = ConfirmationState()
        state.set_awaiting_bulk(
            action="complete_all",
            task_ids=["t1", "t2", "t3"],
            description="Complete 3 tasks"
        )

        assert state.state == ConfirmationStatus.AWAITING_BULK
        assert state.pending_action == "complete_all"
        assert len(state.affected_ids) == 3

    def test_transition_to_awaiting_plan_approval(self):
        """Should transition to AWAITING_PLAN_APPROVAL."""
        state = ConfirmationState()
        state.set_awaiting_plan_approval("plan-1", "Execute 3-step plan")

        assert state.state == ConfirmationStatus.AWAITING_PLAN_APPROVAL
        assert state.pending_action == "plan_approval"

    def test_reset_to_idle(self):
        """reset() should return to IDLE."""
        state = ConfirmationState()
        state.set_awaiting_delete(["task-123"], "Delete task")
        state.reset()

        assert state.is_idle()
        assert state.pending_action is None
        assert state.affected_ids == []

    def test_expiration_detection(self):
        """Should detect expired confirmations."""
        state = ConfirmationState()
        state.set_awaiting_delete(["task-123"], "Delete task")

        # Not expired immediately
        assert not state.is_expired(timeout_seconds=300)

        # Manually set to expired time
        state.requested_at = datetime.now(timezone.utc) - timedelta(seconds=400)
        assert state.is_expired(timeout_seconds=300)

    def test_idle_state_not_expired(self):
        """IDLE state should never be expired."""
        state = ConfirmationState()

        assert not state.is_expired(timeout_seconds=1)


class TestConfirmationManager:
    """Tests for ConfirmationManager class."""

    def test_request_delete_confirmation(self):
        """Should request delete confirmation."""
        manager = ConfirmationManager()
        task = {"id": "task-123", "title": "Buy groceries"}

        message = manager.request_delete_confirmation(task)

        assert manager.state.state == ConfirmationStatus.AWAITING_DELETE
        assert "Buy groceries" in message
        assert "yes" in message.lower()

    def test_request_bulk_confirmation(self):
        """Should request bulk operation confirmation."""
        manager = ConfirmationManager()
        tasks = [
            {"id": "t1", "title": "Task 1"},
            {"id": "t2", "title": "Task 2"},
        ]

        message = manager.request_bulk_confirmation("delete", tasks)

        assert manager.state.state == ConfirmationStatus.AWAITING_BULK
        assert "2 tasks" in message

    def test_confirm_action(self):
        """Should confirm pending action."""
        manager = ConfirmationManager()
        task = {"id": "task-123", "title": "Buy groceries"}
        manager.request_delete_confirmation(task)

        result = manager.confirm()

        assert result is True
        assert manager.state.is_idle()

    def test_cancel_action(self):
        """Should cancel pending action."""
        manager = ConfirmationManager()
        task = {"id": "task-123", "title": "Buy groceries"}
        manager.request_delete_confirmation(task)

        result = manager.cancel()

        assert result is True
        assert manager.state.is_idle()

    def test_confirm_without_pending(self):
        """Confirm without pending should return False."""
        manager = ConfirmationManager()

        result = manager.confirm()

        assert result is False

    def test_auto_expire(self):
        """Should auto-expire old confirmations."""
        manager = ConfirmationManager(timeout_seconds=1)
        task = {"id": "task-123", "title": "Test"}
        manager.request_delete_confirmation(task)

        # Manually expire
        manager.state.requested_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        # Check should trigger auto-expire
        is_pending = manager.has_pending_confirmation()

        assert not is_pending
        assert manager.state.is_idle()


class TestParseConfirmationResponse:
    """Tests for confirmation response parsing (T060)."""

    def test_parse_yes_variations(self):
        """Should recognize yes variations."""
        yes_inputs = ["yes", "Yes", "YES", "y", "Y", "yeah", "yep", "sure", "ok", "okay"]

        for inp in yes_inputs:
            result = parse_confirmation_response(inp)
            assert result == ConfirmationResponse.YES, f"Failed for '{inp}'"

    def test_parse_no_variations(self):
        """Should recognize no variations."""
        no_inputs = ["no", "No", "NO", "n", "N", "nope", "nah", "cancel"]

        for inp in no_inputs:
            result = parse_confirmation_response(inp)
            assert result == ConfirmationResponse.NO, f"Failed for '{inp}'"

    def test_parse_unclear_input(self):
        """Should return UNCLEAR for ambiguous input."""
        unclear_inputs = ["maybe", "perhaps", "I don't know", "hmm", ""]

        for inp in unclear_inputs:
            result = parse_confirmation_response(inp)
            assert result == ConfirmationResponse.UNCLEAR, f"Failed for '{inp}'"

    def test_parse_whitespace_handling(self):
        """Should handle leading/trailing whitespace."""
        result = parse_confirmation_response("  yes  ")
        assert result == ConfirmationResponse.YES

    def test_parse_proceed_for_plans(self):
        """Should recognize proceed for plan approval."""
        proceed_inputs = ["proceed", "go ahead", "do it", "execute"]

        for inp in proceed_inputs:
            result = parse_confirmation_response(inp)
            assert result == ConfirmationResponse.YES, f"Failed for '{inp}'"

    def test_parse_abort_for_plans(self):
        """Should recognize abort for plan cancellation."""
        abort_inputs = ["abort", "stop", "don't", "never mind"]

        for inp in abort_inputs:
            result = parse_confirmation_response(inp)
            assert result == ConfirmationResponse.NO, f"Failed for '{inp}'"
