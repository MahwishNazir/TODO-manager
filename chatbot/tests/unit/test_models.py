"""
Unit tests for AI Agent data models (T024).

Tests all data models: AgentSession, ConfirmationState, ConversationContext,
ToolInvocation, ExecutionPlan, ErrorRecord.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from chatbot.agent.models import (
    AgentSession,
    SessionStatus,
    ConfirmationState,
    ConfirmationStatus,
    ConversationContext,
    Message,
    MessageRole,
    ToolInvocation,
    InvocationStatus,
    ExecutionPlan,
    PlanStep,
    PlanStatus,
    ActionType,
    ErrorRecord,
    ErrorCategory,
)


class TestAgentSession:
    """Tests for AgentSession model."""

    def test_create_session_with_defaults(self):
        """Session should be created with sensible defaults."""
        session = AgentSession(user_id="user-123")

        assert session.session_id is not None
        assert session.user_id == "user-123"
        assert session.status == SessionStatus.ACTIVE
        assert session.created_at is not None
        assert session.last_active is not None

    def test_session_touch_updates_last_active(self):
        """Touch should update last_active timestamp."""
        session = AgentSession(user_id="user-123")
        original_time = session.last_active

        # Wait a tiny bit to ensure time difference
        import time
        time.sleep(0.01)

        session.touch()

        assert session.last_active > original_time

    def test_session_expiration_check(self):
        """is_expired should detect expired sessions."""
        session = AgentSession(user_id="user-123")

        # Not expired immediately
        assert not session.is_expired(ttl_seconds=300)

        # Manually set last_active to past
        session.last_active = datetime.now(timezone.utc) - timedelta(seconds=400)
        assert session.is_expired(ttl_seconds=300)

    def test_session_expire_method(self):
        """expire() should mark session as expired."""
        session = AgentSession(user_id="user-123")
        session.expire()

        assert session.status == SessionStatus.EXPIRED
        assert session.is_expired(ttl_seconds=999999)  # Any TTL should report expired


class TestConfirmationState:
    """Tests for ConfirmationState model."""

    def test_create_idle_state(self):
        """Default state should be IDLE."""
        state = ConfirmationState()

        assert state.state == ConfirmationStatus.IDLE
        assert state.pending_action is None
        assert state.affected_ids == []
        assert state.is_idle()
        assert not state.is_awaiting_confirmation()

    def test_set_awaiting_delete(self):
        """set_awaiting_delete should transition to AWAITING_DELETE."""
        state = ConfirmationState()
        state.set_awaiting_delete(["task-123"], "Delete 'Buy groceries'")

        assert state.state == ConfirmationStatus.AWAITING_DELETE
        assert state.pending_action == "delete"
        assert state.affected_ids == ["task-123"]
        assert state.action_description == "Delete 'Buy groceries'"
        assert state.requested_at is not None
        assert state.is_awaiting_confirmation()

    def test_set_awaiting_bulk(self):
        """set_awaiting_bulk should transition to AWAITING_BULK."""
        state = ConfirmationState()
        state.set_awaiting_bulk(
            action="complete_all",
            task_ids=["task-1", "task-2"],
            description="Complete 2 tasks"
        )

        assert state.state == ConfirmationStatus.AWAITING_BULK
        assert state.pending_action == "complete_all"
        assert state.affected_ids == ["task-1", "task-2"]

    def test_set_awaiting_plan_approval(self):
        """set_awaiting_plan_approval should transition to AWAITING_PLAN_APPROVAL."""
        state = ConfirmationState()
        state.set_awaiting_plan_approval(
            plan_id="plan-123",
            description="Execute 3-step plan"
        )

        assert state.state == ConfirmationStatus.AWAITING_PLAN_APPROVAL
        assert state.pending_action == "plan_approval"
        assert state.affected_ids == ["plan-123"]

    def test_reset_clears_state(self):
        """reset() should return to IDLE state."""
        state = ConfirmationState()
        state.set_awaiting_delete(["task-123"], "Delete task")
        state.reset()

        assert state.is_idle()
        assert state.pending_action is None
        assert state.affected_ids == []
        assert state.requested_at is None

    def test_expiration_check(self):
        """is_expired should detect timed out confirmations."""
        state = ConfirmationState()
        state.set_awaiting_delete(["task-123"], "Delete task")

        # Not expired immediately
        assert not state.is_expired(timeout_seconds=300)

        # Set requested_at to past
        state.requested_at = datetime.now(timezone.utc) - timedelta(seconds=400)
        assert state.is_expired(timeout_seconds=300)

    def test_idle_state_cannot_have_pending_action(self):
        """IDLE state validator should clear pending data."""
        # Create a state with IDLE but try to set pending_action
        state = ConfirmationState(
            state=ConfirmationStatus.IDLE,
            pending_action="delete"  # This should be cleared
        )

        assert state.pending_action is None

    def test_non_idle_requires_pending_action(self):
        """Non-IDLE states must have pending_action."""
        with pytest.raises(ValueError, match="requires pending_action"):
            ConfirmationState(
                state=ConfirmationStatus.AWAITING_DELETE,
                pending_action=None
            )


class TestConversationContext:
    """Tests for ConversationContext model."""

    def test_create_empty_context(self):
        """Empty context should have sensible defaults."""
        context = ConversationContext()

        assert context.messages == []
        assert context.last_mentioned_task_id is None
        assert context.last_mentioned_task_ref is None
        assert context.disambiguation_candidates == []
        assert context.max_messages == 20

    def test_add_user_message(self):
        """add_user_message should add a user message."""
        context = ConversationContext()
        msg = context.add_user_message("Hello, agent")

        assert len(context.messages) == 1
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello, agent"
        assert msg.timestamp is not None

    def test_add_assistant_message(self):
        """add_assistant_message should add an assistant message."""
        context = ConversationContext()
        msg = context.add_assistant_message("How can I help you?")

        assert len(context.messages) == 1
        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "How can I help you?"

    def test_message_trimming(self):
        """Messages should be trimmed when exceeding max_messages."""
        context = ConversationContext(max_messages=5)

        for i in range(10):
            context.add_user_message(f"Message {i}")

        assert len(context.messages) == 5
        # Should keep the most recent messages
        assert context.messages[0].content == "Message 5"
        assert context.messages[4].content == "Message 9"

    def test_set_last_mentioned_task(self):
        """set_last_mentioned_task should update task reference."""
        context = ConversationContext()
        context.set_last_mentioned_task("task-123", "buy groceries")

        assert context.last_mentioned_task_id == "task-123"
        assert context.last_mentioned_task_ref == "buy groceries"

    def test_clear_last_mentioned_task(self):
        """clear_last_mentioned_task should remove reference."""
        context = ConversationContext()
        context.set_last_mentioned_task("task-123", "buy groceries")
        context.clear_last_mentioned_task()

        assert context.last_mentioned_task_id is None
        assert context.last_mentioned_task_ref is None

    def test_get_message_history_for_prompt(self):
        """get_message_history_for_prompt should format messages correctly."""
        context = ConversationContext()
        context.add_user_message("Create a task")
        context.add_assistant_message("Task created!")

        history = context.get_message_history_for_prompt()

        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "Create a task"}
        assert history[1] == {"role": "assistant", "content": "Task created!"}


class TestToolInvocation:
    """Tests for ToolInvocation model."""

    def test_create_invocation(self):
        """Invocation should be created with PENDING status."""
        invocation = ToolInvocation(
            session_id=uuid4(),
            tool_name="add_task",
            params={"title": "Test task"},
            user_id="user-123",
        )

        assert invocation.id is not None
        assert invocation.status == InvocationStatus.PENDING
        assert invocation.started_at is not None

    def test_complete_success(self):
        """complete_success should update status and result."""
        invocation = ToolInvocation(
            session_id=uuid4(),
            tool_name="add_task",
            params={},
            user_id="user-123",
        )

        result = {"task_id": "task-123"}
        invocation.complete_success(result)

        assert invocation.status == InvocationStatus.SUCCESS
        assert invocation.result == result
        assert invocation.completed_at is not None
        assert invocation.get_duration_ms() is not None

    def test_complete_error(self):
        """complete_error should update status and error info."""
        invocation = ToolInvocation(
            session_id=uuid4(),
            tool_name="add_task",
            params={},
            user_id="user-123",
        )

        error = {"code": "INVALID_INPUT", "message": "Title required"}
        invocation.complete_error(error)

        assert invocation.status == InvocationStatus.ERROR
        assert invocation.result == error
        assert invocation.completed_at is not None

    def test_complete_timeout(self):
        """complete_timeout should set TIMEOUT status."""
        invocation = ToolInvocation(
            session_id=uuid4(),
            tool_name="add_task",
            params={},
            user_id="user-123",
        )

        invocation.complete_timeout()

        assert invocation.status == InvocationStatus.TIMEOUT


class TestExecutionPlan:
    """Tests for ExecutionPlan model."""

    def test_create_plan(self):
        """Plan should be created with PENDING status."""
        plan = ExecutionPlan(user_id="user-123")

        assert plan.plan_id is not None
        assert plan.status == PlanStatus.PENDING
        assert plan.steps == []

    def test_add_steps(self):
        """add_step should add steps in order."""
        plan = ExecutionPlan(user_id="user-123")

        step1 = plan.add_step(ActionType.ADD, {"title": "Task 1"})
        step2 = plan.add_step(ActionType.COMPLETE, {"task_id": "task-1"})

        assert len(plan.steps) == 2
        assert step1.order == 0
        assert step2.order == 1
        assert plan.get_total_steps() == 2

    def test_get_next_step(self):
        """get_next_step should return the first pending step."""
        plan = ExecutionPlan(user_id="user-123")
        plan.add_step(ActionType.ADD, {"title": "Task 1"})
        plan.add_step(ActionType.COMPLETE, {"task_id": "task-1"})

        next_step = plan.get_next_step()

        assert next_step is not None
        assert next_step.order == 0
        assert next_step.action == ActionType.ADD

    def test_record_result_advances_plan(self):
        """record_step_result should mark step complete and advance."""
        plan = ExecutionPlan(user_id="user-123")
        step = plan.add_step(ActionType.ADD, {"title": "Task 1"})

        plan.record_step_result(step.order, success=True, result={"task_id": "new-123"})

        assert plan.results[0].success is True
        assert plan.results[0].result == {"task_id": "new-123"}

    def test_plan_is_complete(self):
        """is_complete should return True when all steps done."""
        plan = ExecutionPlan(user_id="user-123")
        step = plan.add_step(ActionType.ADD, {})

        assert not plan.is_complete()

        plan.record_step_result(step.order, success=True, result={})

        assert plan.is_complete()


class TestErrorRecord:
    """Tests for ErrorRecord model."""

    def test_from_mcp_error_user_correctable(self):
        """User-correctable errors should have correct category."""
        error = ErrorRecord.from_mcp_error(
            code="TASK_NOT_FOUND",
            message="Task not found",
            details={"task_id": "xyz"}
        )

        assert error.code == "TASK_NOT_FOUND"
        assert error.category == ErrorCategory.USER_CORRECTABLE
        assert error.suggestion is not None

    def test_from_mcp_error_system_temporary(self):
        """Temporary errors should have SYSTEM_TEMPORARY category."""
        error = ErrorRecord.from_mcp_error(
            code="TIMEOUT",
            message="Request timed out"
        )

        assert error.category == ErrorCategory.SYSTEM_TEMPORARY
        assert error.should_offer_retry()

    def test_from_mcp_error_system_permanent(self):
        """Permanent errors should have SYSTEM_PERMANENT category."""
        error = ErrorRecord.from_mcp_error(
            code="INTERNAL_ERROR",
            message="Internal server error"
        )

        assert error.category == ErrorCategory.SYSTEM_PERMANENT
        assert error.requires_escalation()

    def test_from_mcp_error_unknown_code(self):
        """Unknown error codes should default to SYSTEM_PERMANENT."""
        error = ErrorRecord.from_mcp_error(
            code="UNKNOWN_CODE",
            message="Something happened"
        )

        assert error.category == ErrorCategory.SYSTEM_PERMANENT

    def test_get_user_message_user_correctable(self):
        """User-correctable errors should return suggestion."""
        error = ErrorRecord.from_mcp_error(
            code="TASK_NOT_FOUND",
            message="Task not found"
        )

        user_msg = error.get_user_message()

        assert "task could not be found" in user_msg.lower()

    def test_get_user_message_system_temporary(self):
        """Temporary errors should suggest retry."""
        error = ErrorRecord.from_mcp_error(
            code="TIMEOUT",
            message="Request timed out"
        )

        user_msg = error.get_user_message()

        assert "try again" in user_msg.lower()

    def test_get_user_message_system_permanent(self):
        """Permanent errors should suggest contacting support."""
        error = ErrorRecord.from_mcp_error(
            code="INTERNAL_ERROR",
            message="Internal server error"
        )

        user_msg = error.get_user_message()

        assert "contact support" in user_msg.lower() or "went wrong" in user_msg.lower()
