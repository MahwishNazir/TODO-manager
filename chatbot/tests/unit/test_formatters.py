"""
Unit tests for response formatters (T039).

Tests formatting functions for task lists and other responses.
"""

import pytest

from chatbot.agent.formatters import (
    format_task_created,
    format_task_updated,
    format_task_completed,
    format_task_deleted,
    format_task_list,
    format_delete_confirmation_request,
    format_bulk_operation_confirmation,
    format_plan_preview,
    format_plan_result,
)


class TestFormatTaskCreated:
    """Tests for task creation confirmation formatting."""

    def test_format_basic_task(self):
        """Should format basic task creation."""
        task = {"id": "t1", "title": "Buy groceries"}
        message = format_task_created(task)

        assert "Buy groceries" in message
        assert "created" in message.lower()

    def test_format_task_with_description(self):
        """Should include description preview."""
        task = {
            "id": "t1",
            "title": "Buy groceries",
            "description": "Get milk, eggs, and bread",
        }
        message = format_task_created(task)

        assert "Buy groceries" in message
        assert "milk, eggs" in message

    def test_format_task_with_long_description(self):
        """Should truncate long descriptions."""
        task = {
            "id": "t1",
            "title": "Buy groceries",
            "description": "A" * 200,  # Very long description
        }
        message = format_task_created(task)

        assert "..." in message
        assert len(message) < 300  # Should be truncated

    def test_format_task_without_title(self):
        """Should handle missing title."""
        task = {"id": "t1"}
        message = format_task_created(task)

        assert "Untitled" in message


class TestFormatTaskUpdated:
    """Tests for task update confirmation formatting."""

    def test_format_title_change(self):
        """Should show title change."""
        task = {"id": "t1", "title": "Buy groceries updated"}
        changes = {"title": ("Buy groceries", "Buy groceries updated")}

        message = format_task_updated(task, changes)

        assert "Buy groceries" in message
        assert "updated" in message.lower()
        assert "->" in message

    def test_format_multiple_changes(self):
        """Should show all changes."""
        task = {"id": "t1", "title": "New title"}
        changes = {
            "title": ("Old title", "New title"),
            "description": ("Old desc", "New desc"),
        }

        message = format_task_updated(task, changes)

        assert "title:" in message.lower()
        assert "description:" in message.lower()


class TestFormatTaskCompleted:
    """Tests for task completion confirmation formatting."""

    def test_format_completion(self):
        """Should confirm completion."""
        task = {"id": "t1", "title": "Buy groceries", "status": "completed"}
        message = format_task_completed(task)

        assert "Buy groceries" in message
        assert "complete" in message.lower()


class TestFormatTaskDeleted:
    """Tests for task deletion confirmation formatting."""

    def test_format_deletion(self):
        """Should confirm deletion."""
        task = {"id": "t1", "title": "Buy groceries"}
        message = format_task_deleted(task)

        assert "Buy groceries" in message
        assert "deleted" in message.lower()


class TestFormatTaskList:
    """Tests for task list formatting."""

    def test_format_basic_list(self):
        """Should format basic task list."""
        tasks = [
            {"id": "t1", "title": "Buy groceries", "status": "pending"},
            {"id": "t2", "title": "Call mom", "status": "completed"},
        ]

        message = format_task_list(tasks, total_count=2)

        assert "Buy groceries" in message
        assert "Call mom" in message
        assert "2 total" in message

    def test_format_empty_list(self):
        """Should handle empty list with suggestions."""
        message = format_task_list([], total_count=0)

        assert "don't have any tasks" in message.lower() or "no tasks" in message.lower()

    def test_format_with_filter_description(self):
        """Should include filter description."""
        tasks = [{"id": "t1", "title": "Task 1", "status": "pending"}]
        message = format_task_list(
            tasks,
            total_count=1,
            filter_description="pending"
        )

        assert "pending" in message.lower()

    def test_format_with_pagination(self):
        """Should show pagination info when more tasks available."""
        tasks = [{"id": "t1", "title": "Task 1", "status": "pending"}]
        message = format_task_list(tasks, total_count=50)

        assert "more" in message.lower()

    def test_format_shows_status_indicators(self):
        """Should show status indicators."""
        tasks = [
            {"id": "t1", "title": "Pending", "status": "pending"},
            {"id": "t2", "title": "Done", "status": "completed"},
        ]

        message = format_task_list(tasks, total_count=2)

        assert "[ ]" in message or "[x]" in message  # Status indicators

    def test_format_empty_pending_list(self):
        """Should show appropriate message for empty pending list."""
        message = format_task_list(
            [],
            total_count=0,
            filter_description="pending"
        )

        assert "pending" in message.lower()


class TestFormatDeleteConfirmationRequest:
    """Tests for delete confirmation request formatting."""

    def test_format_confirmation_request(self):
        """Should format confirmation with task details."""
        task = {
            "id": "t1",
            "title": "Buy groceries",
            "description": "Get milk and bread",
            "status": "pending",
        }

        message = format_delete_confirmation_request(task)

        assert "Buy groceries" in message
        assert "pending" in message
        assert "yes" in message.lower()
        assert "no" in message.lower()

    def test_format_confirmation_shows_description(self):
        """Should show description in confirmation."""
        task = {
            "id": "t1",
            "title": "Task",
            "description": "Important details",
        }

        message = format_delete_confirmation_request(task)

        assert "Important details" in message


class TestFormatBulkOperationConfirmation:
    """Tests for bulk operation confirmation formatting."""

    def test_format_bulk_delete(self):
        """Should format bulk delete confirmation."""
        tasks = [
            {"id": "t1", "title": "Task 1"},
            {"id": "t2", "title": "Task 2"},
        ]

        message = format_bulk_operation_confirmation("delete", tasks)

        assert "2 tasks" in message
        assert "Task 1" in message
        assert "Task 2" in message
        assert "yes" in message.lower()

    def test_format_bulk_with_many_tasks(self):
        """Should truncate long task lists."""
        tasks = [{"id": f"t{i}", "title": f"Task {i}"} for i in range(10)]

        message = format_bulk_operation_confirmation("complete", tasks)

        assert "...and" in message
        assert "5 more" in message


class TestFormatPlanPreview:
    """Tests for plan preview formatting."""

    def test_format_plan_steps(self):
        """Should format plan with numbered steps."""
        steps = [
            {"action": "ADD", "description": "Create 'Buy groceries'"},
            {"action": "COMPLETE", "description": "Mark 'Call mom' done"},
        ]

        message = format_plan_preview(steps)

        assert "1." in message
        assert "2." in message
        assert "Buy groceries" in message
        assert "proceed" in message.lower()


class TestFormatPlanResult:
    """Tests for plan result formatting."""

    def test_format_all_success(self):
        """Should format successful plan execution."""
        steps = [
            {"action": "ADD", "description": "Create task"},
            {"action": "COMPLETE", "description": "Complete task"},
        ]
        results = [
            {"success": True},
            {"success": True},
        ]

        message = format_plan_result(steps, results)

        assert "2 steps" in message
        assert "successfully" in message.lower()

    def test_format_partial_success(self):
        """Should show failed steps."""
        steps = [
            {"action": "ADD", "description": "Create task"},
            {"action": "DELETE", "description": "Delete task"},
        ]
        results = [
            {"success": True},
            {"success": False, "error": "Task not found"},
        ]

        message = format_plan_result(steps, results)

        assert "1 of 2" in message
        assert "[-]" in message  # Failed indicator
