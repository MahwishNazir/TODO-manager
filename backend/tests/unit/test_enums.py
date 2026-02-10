"""
Unit tests for Phase III enum definitions.

Tests for Priority, TaskStatus, MessageRole, and OperationType enums
to verify string values, membership, and enum behavior.

TDD: RED phase - Write tests before implementation verification.
"""

import pytest
from src.models.enums import Priority, TaskStatus, MessageRole, OperationType


class TestPriorityEnum:
    """Tests for Priority enum (FR-001)."""

    def test_priority_has_three_values(self):
        """Priority enum should have exactly three values."""
        assert len(Priority) == 3

    def test_priority_low_value(self):
        """Priority.LOW should have string value 'low'."""
        assert Priority.LOW.value == "low"
        assert Priority.LOW == "low"

    def test_priority_medium_value(self):
        """Priority.MEDIUM should have string value 'medium'."""
        assert Priority.MEDIUM.value == "medium"
        assert Priority.MEDIUM == "medium"

    def test_priority_high_value(self):
        """Priority.HIGH should have string value 'high'."""
        assert Priority.HIGH.value == "high"
        assert Priority.HIGH == "high"

    def test_priority_is_str_enum(self):
        """Priority should inherit from str for PostgreSQL VARCHAR compatibility."""
        assert isinstance(Priority.LOW, str)
        assert isinstance(Priority.MEDIUM, str)
        assert isinstance(Priority.HIGH, str)

    def test_priority_default_is_medium(self):
        """Verify MEDIUM is a valid default value."""
        default = Priority.MEDIUM
        assert default.value == "medium"

    def test_priority_from_string(self):
        """Priority should be constructible from string values."""
        assert Priority("low") == Priority.LOW
        assert Priority("medium") == Priority.MEDIUM
        assert Priority("high") == Priority.HIGH

    def test_priority_invalid_value_raises(self):
        """Creating Priority from invalid string should raise ValueError."""
        with pytest.raises(ValueError):
            Priority("invalid")

        with pytest.raises(ValueError):
            Priority("MEDIUM")  # Case-sensitive

    def test_priority_in_check_constraint_values(self):
        """All priority values should match CHECK constraint in migration."""
        valid_values = {"low", "medium", "high"}
        enum_values = {p.value for p in Priority}
        assert enum_values == valid_values


class TestTaskStatusEnum:
    """Tests for TaskStatus enum (FR-002)."""

    def test_task_status_has_two_values(self):
        """TaskStatus enum should have exactly two values."""
        assert len(TaskStatus) == 2

    def test_task_status_incomplete_value(self):
        """TaskStatus.INCOMPLETE should have string value 'incomplete'."""
        assert TaskStatus.INCOMPLETE.value == "incomplete"
        assert TaskStatus.INCOMPLETE == "incomplete"

    def test_task_status_complete_value(self):
        """TaskStatus.COMPLETE should have string value 'complete'."""
        assert TaskStatus.COMPLETE.value == "complete"
        assert TaskStatus.COMPLETE == "complete"

    def test_task_status_is_str_enum(self):
        """TaskStatus should inherit from str for PostgreSQL VARCHAR compatibility."""
        assert isinstance(TaskStatus.INCOMPLETE, str)
        assert isinstance(TaskStatus.COMPLETE, str)

    def test_task_status_default_is_incomplete(self):
        """Verify INCOMPLETE is a valid default value."""
        default = TaskStatus.INCOMPLETE
        assert default.value == "incomplete"

    def test_task_status_from_string(self):
        """TaskStatus should be constructible from string values."""
        assert TaskStatus("incomplete") == TaskStatus.INCOMPLETE
        assert TaskStatus("complete") == TaskStatus.COMPLETE

    def test_task_status_invalid_value_raises(self):
        """Creating TaskStatus from invalid string should raise ValueError."""
        with pytest.raises(ValueError):
            TaskStatus("pending")

        with pytest.raises(ValueError):
            TaskStatus("INCOMPLETE")  # Case-sensitive

    def test_task_status_in_check_constraint_values(self):
        """All status values should match CHECK constraint in migration."""
        valid_values = {"incomplete", "complete"}
        enum_values = {s.value for s in TaskStatus}
        assert enum_values == valid_values


class TestMessageRoleEnum:
    """Tests for MessageRole enum (FR-013)."""

    def test_message_role_has_three_values(self):
        """MessageRole enum should have exactly three values."""
        assert len(MessageRole) == 3

    def test_message_role_user_value(self):
        """MessageRole.USER should have string value 'user'."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.USER == "user"

    def test_message_role_assistant_value(self):
        """MessageRole.ASSISTANT should have string value 'assistant'."""
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.ASSISTANT == "assistant"

    def test_message_role_system_value(self):
        """MessageRole.SYSTEM should have string value 'system'."""
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.SYSTEM == "system"

    def test_message_role_is_str_enum(self):
        """MessageRole should inherit from str for PostgreSQL VARCHAR compatibility."""
        assert isinstance(MessageRole.USER, str)
        assert isinstance(MessageRole.ASSISTANT, str)
        assert isinstance(MessageRole.SYSTEM, str)

    def test_message_role_from_string(self):
        """MessageRole should be constructible from string values."""
        assert MessageRole("user") == MessageRole.USER
        assert MessageRole("assistant") == MessageRole.ASSISTANT
        assert MessageRole("system") == MessageRole.SYSTEM

    def test_message_role_in_check_constraint_values(self):
        """All role values should match CHECK constraint in migration."""
        valid_values = {"user", "assistant", "system"}
        enum_values = {r.value for r in MessageRole}
        assert enum_values == valid_values


class TestOperationTypeEnum:
    """Tests for OperationType enum."""

    def test_operation_type_has_three_values(self):
        """OperationType enum should have exactly three values."""
        assert len(OperationType) == 3

    def test_operation_type_delete_value(self):
        """OperationType.DELETE should have string value 'delete'."""
        assert OperationType.DELETE.value == "delete"
        assert OperationType.DELETE == "delete"

    def test_operation_type_bulk_delete_value(self):
        """OperationType.BULK_DELETE should have string value 'bulk_delete'."""
        assert OperationType.BULK_DELETE.value == "bulk_delete"
        assert OperationType.BULK_DELETE == "bulk_delete"

    def test_operation_type_bulk_complete_value(self):
        """OperationType.BULK_COMPLETE should have string value 'bulk_complete'."""
        assert OperationType.BULK_COMPLETE.value == "bulk_complete"
        assert OperationType.BULK_COMPLETE == "bulk_complete"

    def test_operation_type_is_str_enum(self):
        """OperationType should inherit from str."""
        assert isinstance(OperationType.DELETE, str)
        assert isinstance(OperationType.BULK_DELETE, str)
        assert isinstance(OperationType.BULK_COMPLETE, str)

    def test_operation_type_from_string(self):
        """OperationType should be constructible from string values."""
        assert OperationType("delete") == OperationType.DELETE
        assert OperationType("bulk_delete") == OperationType.BULK_DELETE
        assert OperationType("bulk_complete") == OperationType.BULK_COMPLETE
