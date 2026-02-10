"""
Integration tests for Task CRUD operations with extended fields.

Tests for creating, reading, updating tasks with priority, status,
due_date, and is_deleted fields via the API endpoints.

TDD: RED phase - Write tests before implementation.
"""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

from src.models.enums import Priority, TaskStatus


class TestTaskCreateWithExtendedFields:
    """Integration tests for creating tasks with extended fields."""

    def test_create_task_with_priority(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should create task with specified priority."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={
                "title": "High priority task",
                "priority": "high",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "high"

    def test_create_task_with_default_priority(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should create task with default priority (medium) when not specified."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Default priority task"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "medium"

    def test_create_task_with_due_date(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should create task with due_date."""
        due_date = (date.today() + timedelta(days=7)).isoformat()

        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={
                "title": "Task with due date",
                "due_date": due_date,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] == due_date

    def test_create_task_without_due_date(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should create task with null due_date when not specified."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "No due date task"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is None

    def test_create_task_with_all_extended_fields(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should create task with all extended fields."""
        due_date = (date.today() + timedelta(days=3)).isoformat()

        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={
                "title": "Full task",
                "priority": "low",
                "due_date": due_date,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Full task"
        assert data["priority"] == "low"
        assert data["status"] == "incomplete"
        assert data["due_date"] == due_date
        assert data["is_deleted"] is False

    def test_create_task_invalid_priority_rejected(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should reject task creation with invalid priority."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={
                "title": "Invalid priority task",
                "priority": "urgent",  # Invalid value
            },
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestTaskReadWithExtendedFields:
    """Integration tests for reading tasks with extended fields."""

    def test_get_task_includes_extended_fields(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """GET task should include all extended fields."""
        # Create task first
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={
                "title": "Task with extended fields",
                "priority": "high",
                "due_date": date.today().isoformat(),
            },
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Get task
        response = client.get(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "priority" in data
        assert "status" in data
        assert "due_date" in data
        assert "is_deleted" in data

    def test_list_tasks_includes_extended_fields(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """GET tasks list should include extended fields for each task."""
        # Create task
        client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "List test task", "priority": "low"},
            headers=auth_headers,
        )

        # List tasks
        response = client.get(
            f"/api/{sample_user_id}/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        task = data["tasks"][0]
        assert "priority" in task
        assert "status" in task


class TestTaskUpdateWithExtendedFields:
    """Integration tests for updating tasks with extended fields."""

    def test_update_task_priority(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should update task priority."""
        # Create task with low priority
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Update priority test", "priority": "low"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Update to high priority
        response = client.put(
            f"/api/{sample_user_id}/tasks/{task_id}",
            json={"title": "Update priority test", "priority": "high"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "high"

    def test_update_task_status_to_complete(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should update task status to complete."""
        # Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Complete me"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Update status
        response = client.put(
            f"/api/{sample_user_id}/tasks/{task_id}",
            json={"title": "Complete me", "status": "complete"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"

    def test_update_task_due_date(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should update task due_date."""
        original_due = date.today() + timedelta(days=7)
        new_due = date.today() + timedelta(days=14)

        # Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Due date test", "due_date": original_due.isoformat()},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Update due date
        response = client.put(
            f"/api/{sample_user_id}/tasks/{task_id}",
            json={"title": "Due date test", "due_date": new_due.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["due_date"] == new_due.isoformat()

    def test_clear_task_due_date(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should clear task due_date by setting to null."""
        # Create task with due date
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={
                "title": "Clear due date test",
                "due_date": date.today().isoformat(),
            },
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Clear due date
        response = client.put(
            f"/api/{sample_user_id}/tasks/{task_id}",
            json={"title": "Clear due date test", "due_date": None},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["due_date"] is None


class TestTaskSoftDelete:
    """Integration tests for soft delete functionality."""

    def test_delete_task_sets_is_deleted_flag(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """DELETE should set is_deleted=True (soft delete)."""
        # Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Soft delete test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Delete task
        response = client.delete(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_deleted_task_excluded_from_list(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Soft-deleted tasks should not appear in task list."""
        # Create and delete task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Will be deleted"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Delete task
        client.delete(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        # List tasks should not include deleted task
        response = client.get(
            f"/api/{sample_user_id}/tasks",
            headers=auth_headers,
        )

        data = response.json()
        task_ids = [t["id"] for t in data["tasks"]]
        assert task_id not in task_ids

    def test_get_deleted_task_returns_404(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """GET on soft-deleted task should return 404."""
        # Create and delete task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Will be deleted"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        client.delete(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        # Get should return 404
        response = client.get(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestTaskFilteringByExtendedFields:
    """Integration tests for filtering tasks by extended fields."""

    def test_filter_tasks_by_priority_query_param(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should filter tasks by priority query parameter."""
        # Create tasks with different priorities
        client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "High task", "priority": "high"},
            headers=auth_headers,
        )
        client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Low task", "priority": "low"},
            headers=auth_headers,
        )

        # Filter by high priority
        response = client.get(
            f"/api/{sample_user_id}/tasks?priority=high",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["priority"] == "high"

    def test_filter_tasks_by_status_query_param(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should filter tasks by status query parameter."""
        # Create incomplete task
        client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Incomplete task"},
            headers=auth_headers,
        )

        # Filter by incomplete status
        response = client.get(
            f"/api/{sample_user_id}/tasks?status=incomplete",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "incomplete"

    def test_filter_tasks_by_due_date_range(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """Should filter tasks by due date range."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)

        # Create tasks with different due dates
        client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Due today", "due_date": today.isoformat()},
            headers=auth_headers,
        )
        client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Due next week", "due_date": next_week.isoformat()},
            headers=auth_headers,
        )

        # Filter by due before tomorrow
        response = client.get(
            f"/api/{sample_user_id}/tasks?due_before={tomorrow.isoformat()}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            if task["due_date"]:
                assert task["due_date"] <= tomorrow.isoformat()


class TestTaskResponseSchema:
    """Tests for TaskResponse schema with extended fields."""

    def test_task_response_includes_all_fields(
        self, client: TestClient, auth_headers: dict, sample_user_id: str
    ):
        """TaskResponse should include all Phase III fields."""
        # Create task
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Schema test"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        # Verify all required fields
        required_fields = [
            "id",
            "user_id",
            "title",
            "is_completed",
            "priority",
            "status",
            "due_date",
            "is_deleted",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"
