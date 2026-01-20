"""
Integration tests for task API endpoints with JWT authentication (T026).

These tests verify that API endpoints require valid JWT tokens and properly
validate user_id from the token matches the URL parameter.

RED PHASE: These tests will FAIL until endpoints require JWT authentication.
"""

import jwt
import pytest
from datetime import datetime, timedelta, timezone

from src.config import settings


def create_test_token(
    user_id: str = "test-user-123",
    email: str = "test@example.com",
    exp_minutes: int = 60,
    **extra_claims
) -> str:
    """
    Create a test JWT token with specified claims.

    Args:
        user_id: User ID for 'sub' claim
        email: Email for 'email' claim
        exp_minutes: Expiration time in minutes from now
        **extra_claims: Additional claims to include

    Returns:
        str: Encoded JWT token
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(minutes=exp_minutes),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        **extra_claims,
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


class TestCreateTaskWithAuth:
    """Integration tests for creating tasks with authentication."""

    def test_create_task_with_valid_token_succeeds(self, client, sample_user_id):
        """Test creating task with valid JWT token succeeds."""
        # Create valid token for this user
        token = create_test_token(user_id=sample_user_id)

        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Buy groceries"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 201 but currently doesn't check auth
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == sample_user_id
        assert data["title"] == "Buy groceries"

    def test_create_task_without_token_fails(self, client, sample_user_id):
        """Test creating task without JWT token returns 401."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Buy groceries"}
            # No Authorization header
        )

        # RED PHASE: This should return 401 but currently returns 201
        assert response.status_code == 401

    def test_create_task_with_mismatched_user_id_fails(self, client):
        """Test creating task with JWT user_id not matching URL user_id returns 403."""
        # Token is for user-123 but URL is for user-456
        token = create_test_token(user_id="user-123")

        response = client.post(
            "/api/user-456/tasks",
            json={"title": "Unauthorized task"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 403 but currently returns 201
        assert response.status_code == 403
        assert "detail" in response.json()


class TestListTasksWithAuth:
    """Integration tests for listing tasks with authentication."""

    def test_list_tasks_with_valid_token_succeeds(self, client, sample_user_id):
        """Test listing tasks with valid JWT token succeeds."""
        # Create token for user
        token = create_test_token(user_id=sample_user_id)

        # Create some tasks first (with token)
        for i in range(3):
            client.post(
                f"/api/{sample_user_id}/tasks",
                json={"title": f"Task {i+1}"},
                headers={"Authorization": f"Bearer {token}"}
            )

        # List tasks with token
        response = client.get(
            f"/api/{sample_user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 200 but currently doesn't check auth
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 3

    def test_list_tasks_without_token_fails(self, client, sample_user_id):
        """Test listing tasks without JWT token returns 401."""
        response = client.get(f"/api/{sample_user_id}/tasks")

        # RED PHASE: This should return 401 but currently returns 200
        assert response.status_code == 401

    def test_list_tasks_with_mismatched_user_id_fails(self, client):
        """Test listing tasks with JWT user_id not matching URL user_id returns 403."""
        # Token is for user-123 but URL is for user-456
        token = create_test_token(user_id="user-123")

        response = client.get(
            "/api/user-456/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 403 but currently returns 200
        assert response.status_code == 403


class TestGetSingleTaskWithAuth:
    """Integration tests for retrieving single task with authentication."""

    def test_get_task_with_valid_token_succeeds(self, client, sample_user_id):
        """Test getting task with valid JWT token succeeds."""
        token = create_test_token(user_id=sample_user_id)

        # Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Test task"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_response.json()["id"]

        # Get task with token
        response = client.get(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 200 but currently doesn't check auth
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id

    def test_get_task_without_token_fails(self, client, sample_user_id):
        """Test getting task without JWT token returns 401."""
        response = client.get(f"/api/{sample_user_id}/tasks/1")

        # RED PHASE: This should return 401 but currently returns 404
        assert response.status_code == 401

    def test_get_task_with_mismatched_user_id_fails(self, client):
        """Test getting task with JWT user_id not matching URL user_id returns 403."""
        token = create_test_token(user_id="user-123")

        response = client.get(
            "/api/user-456/tasks/1",
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 403 but currently returns 404
        assert response.status_code == 403


class TestUpdateTaskWithAuth:
    """Integration tests for updating tasks with authentication."""

    def test_update_task_with_valid_token_succeeds(self, client, sample_user_id):
        """Test updating task with valid JWT token succeeds."""
        token = create_test_token(user_id=sample_user_id)

        # Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Original title"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_response.json()["id"]

        # Update task with token
        response = client.put(
            f"/api/{sample_user_id}/tasks/{task_id}",
            json={"title": "Updated title"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 200 but currently doesn't check auth
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"

    def test_update_task_without_token_fails(self, client, sample_user_id):
        """Test updating task without JWT token returns 401."""
        response = client.put(
            f"/api/{sample_user_id}/tasks/1",
            json={"title": "Updated title"}
        )

        # RED PHASE: This should return 401 but currently returns 404
        assert response.status_code == 401

    def test_update_task_with_mismatched_user_id_fails(self, client):
        """Test updating task with JWT user_id not matching URL user_id returns 403."""
        token = create_test_token(user_id="user-123")

        response = client.put(
            "/api/user-456/tasks/1",
            json={"title": "Hacked title"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 403 but currently returns 404
        assert response.status_code == 403


class TestDeleteTaskWithAuth:
    """Integration tests for deleting tasks with authentication."""

    def test_delete_task_with_valid_token_succeeds(self, client, sample_user_id):
        """Test deleting task with valid JWT token succeeds."""
        token = create_test_token(user_id=sample_user_id)

        # Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Task to delete"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_response.json()["id"]

        # Delete task with token
        response = client.delete(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 204 but currently doesn't check auth
        assert response.status_code == 204

    def test_delete_task_without_token_fails(self, client, sample_user_id):
        """Test deleting task without JWT token returns 401."""
        response = client.delete(f"/api/{sample_user_id}/tasks/1")

        # RED PHASE: This should return 401 but currently returns 404
        assert response.status_code == 401

    def test_delete_task_with_mismatched_user_id_fails(self, client):
        """Test deleting task with JWT user_id not matching URL user_id returns 403."""
        token = create_test_token(user_id="user-123")

        response = client.delete(
            "/api/user-456/tasks/1",
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 403 but currently returns 404
        assert response.status_code == 403


class TestToggleCompletionWithAuth:
    """Integration tests for toggling task completion with authentication."""

    def test_toggle_completion_with_valid_token_succeeds(self, client, sample_user_id):
        """Test toggling completion with valid JWT token succeeds."""
        token = create_test_token(user_id=sample_user_id)

        # Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Task to complete"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_response.json()["id"]

        # Toggle completion with token
        response = client.patch(
            f"/api/{sample_user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 200 but currently doesn't check auth
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True

    def test_toggle_completion_without_token_fails(self, client, sample_user_id):
        """Test toggling completion without JWT token returns 401."""
        response = client.patch(f"/api/{sample_user_id}/tasks/1/complete")

        # RED PHASE: This should return 401 but currently returns 404
        assert response.status_code == 401

    def test_toggle_completion_with_mismatched_user_id_fails(self, client):
        """Test toggling completion with JWT user_id not matching URL user_id returns 403."""
        token = create_test_token(user_id="user-123")

        response = client.patch(
            "/api/user-456/tasks/1/complete",
            headers={"Authorization": f"Bearer {token}"}
        )

        # RED PHASE: This should return 403 but currently returns 404
        assert response.status_code == 403


class TestAuthenticationJourney:
    """End-to-end journey tests with authentication."""

    def test_complete_task_workflow_with_auth(self, client, sample_user_id):
        """Test complete task workflow with authentication."""
        token = create_test_token(user_id=sample_user_id)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Complete workflow task"},
            headers=headers
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # 2. List tasks
        list_response = client.get(
            f"/api/{sample_user_id}/tasks",
            headers=headers
        )
        assert list_response.status_code == 200
        assert list_response.json()["count"] >= 1

        # 3. Get specific task
        get_response = client.get(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers=headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Complete workflow task"

        # 4. Update task
        update_response = client.put(
            f"/api/{sample_user_id}/tasks/{task_id}",
            json={"title": "Updated workflow task"},
            headers=headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated workflow task"

        # 5. Toggle completion
        toggle_response = client.patch(
            f"/api/{sample_user_id}/tasks/{task_id}/complete",
            headers=headers
        )
        assert toggle_response.status_code == 200
        assert toggle_response.json()["is_completed"] is True

        # 6. Delete task
        delete_response = client.delete(
            f"/api/{sample_user_id}/tasks/{task_id}",
            headers=headers
        )
        assert delete_response.status_code == 204

    def test_expired_token_fails_throughout_workflow(self, client, sample_user_id):
        """Test that expired token fails at every step of workflow."""
        # Create expired token
        expired_token = create_test_token(user_id=sample_user_id, exp_minutes=-10)
        headers = {"Authorization": f"Bearer {expired_token}"}

        # All operations should fail with 401
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Should fail"},
            headers=headers
        )
        assert create_response.status_code == 401

        list_response = client.get(
            f"/api/{sample_user_id}/tasks",
            headers=headers
        )
        assert list_response.status_code == 401

        get_response = client.get(
            f"/api/{sample_user_id}/tasks/1",
            headers=headers
        )
        assert get_response.status_code == 401
