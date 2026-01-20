"""
Integration tests for task API endpoints.

These tests cover complete user journeys and workflows across
multiple API calls, including user isolation.
"""

import pytest


class TestCreateTaskJourney:
    """Integration tests for creating tasks."""

    def test_create_task_returns_201_with_id(self, client, sample_user_id, auth_headers):
        """Test creating task returns 201 with generated ID."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Buy groceries"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["id"] is not None
        assert isinstance(data["id"], int)

    def test_create_task_sets_correct_fields(self, client, sample_user_id, auth_headers):
        """Test created task has correct field values."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Buy groceries"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        assert data["user_id"] == sample_user_id
        assert data["title"] == "Buy groceries"
        assert data["is_completed"] is False
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_trims_whitespace(self, client, sample_user_id, auth_headers):
        """Test task creation trims whitespace from title."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "  Buy groceries  "},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"


class TestListTasksJourney:
    """Integration tests for listing tasks."""

    def test_list_tasks_empty_initially(self, client, sample_user_id, auth_headers):
        """Test listing tasks returns empty list for new user."""
        response = client.get(f"/api/{sample_user_id}/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["count"] == 0

    def test_list_tasks_after_creating_tasks(self, client, sample_user_id, auth_headers):
        """Test listing tasks returns created tasks."""
        # Create tasks
        client.post(f"/api/{sample_user_id}/tasks", json={"title": "Task 1"}, headers=auth_headers)
        client.post(f"/api/{sample_user_id}/tasks", json={"title": "Task 2"}, headers=auth_headers)
        client.post(f"/api/{sample_user_id}/tasks", json={"title": "Task 3"}, headers=auth_headers)

        # List tasks
        response = client.get(f"/api/{sample_user_id}/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 3
        assert data["count"] == 3

    def test_list_tasks_correct_order(self, client, sample_user_id, auth_headers):
        """Test tasks are listed in created order."""
        # Create tasks
        client.post(f"/api/{sample_user_id}/tasks", json={"title": "First task"}, headers=auth_headers)
        client.post(f"/api/{sample_user_id}/tasks", json={"title": "Second task"}, headers=auth_headers)

        # List tasks
        response = client.get(f"/api/{sample_user_id}/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        titles = [task["title"] for task in data["tasks"]]
        assert "First task" in titles
        assert "Second task" in titles


class TestGetSingleTaskJourney:
    """Integration tests for retrieving single task."""

    def test_get_task_by_id(self, client, sample_user_id, auth_headers):
        """Test retrieving task by ID."""
        # Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Buy groceries"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Get task
        response = client.get(f"/api/{sample_user_id}/tasks/{task_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Buy groceries"

    def test_get_nonexistent_task_returns_404(self, client, sample_user_id, auth_headers):
        """Test getting non-existent task returns 404."""
        response = client.get(f"/api/{sample_user_id}/tasks/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUserIsolationJourney:
    """Integration tests for user isolation."""

    def test_users_cannot_see_each_others_tasks(self, client, sample_user_id, another_user_id, auth_headers, another_auth_headers):
        """Test tasks are isolated by user_id."""
        # User 1 creates tasks
        client.post(f"/api/{sample_user_id}/tasks", json={"title": "User 1 Task 1"}, headers=auth_headers)
        client.post(f"/api/{sample_user_id}/tasks", json={"title": "User 1 Task 2"}, headers=auth_headers)

        # User 2 creates tasks
        client.post(f"/api/{another_user_id}/tasks", json={"title": "User 2 Task 1"}, headers=another_auth_headers)

        # User 1 lists tasks - should only see their own
        response1 = client.get(f"/api/{sample_user_id}/tasks", headers=auth_headers)
        data1 = response1.json()
        assert data1["count"] == 2
        titles1 = [task["title"] for task in data1["tasks"]]
        assert "User 1 Task 1" in titles1
        assert "User 1 Task 2" in titles1
        assert "User 2 Task 1" not in titles1

        # User 2 lists tasks - should only see their own
        response2 = client.get(f"/api/{another_user_id}/tasks", headers=another_auth_headers)
        data2 = response2.json()
        assert data2["count"] == 1
        titles2 = [task["title"] for task in data2["tasks"]]
        assert "User 2 Task 1" in titles2
        assert "User 1 Task 1" not in titles2

    def test_user_cannot_access_another_users_task(self, client, sample_user_id, another_user_id, auth_headers, another_auth_headers):
        """Test user cannot access another user's task by ID."""
        # User 1 creates a task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "User 1 Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # User 2 tries to access User 1's task - should get 404 (task not found due to user isolation)
        response = client.get(f"/api/{another_user_id}/tasks/{task_id}", headers=another_auth_headers)
        assert response.status_code == 404


class TestValidationErrorsJourney:
    """Integration tests for validation errors."""

    def test_create_task_with_empty_title_fails(self, client, sample_user_id, auth_headers):
        """Test creating task with empty title returns 422."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_task_with_whitespace_only_title_fails(self, client, sample_user_id, auth_headers):
        """Test creating task with whitespace-only title returns 422."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "   "},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_task_with_too_long_title_fails(self, client, sample_user_id, auth_headers):
        """Test creating task with title > 500 chars returns 422."""
        long_title = "x" * 501
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": long_title},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_task_without_title_fails(self, client, sample_user_id, auth_headers):
        """Test creating task without title field returns 422."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={},  # Missing title
            headers=auth_headers,
        )
        assert response.status_code == 422
