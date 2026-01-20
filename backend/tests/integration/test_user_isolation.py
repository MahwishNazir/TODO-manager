"""
Integration tests for user isolation with JWT authentication (T027).

These tests verify that users cannot access each other's tasks even with
valid JWT tokens. The user_id from JWT must match the user_id in the URL.

RED PHASE: These tests will FAIL until endpoints validate JWT user_id matches URL user_id.
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


@pytest.fixture
def user_a_id():
    """Provide user A ID for testing."""
    return "user-alice-123"


@pytest.fixture
def user_b_id():
    """Provide user B ID for testing."""
    return "user-bob-456"


@pytest.fixture
def user_a_token(user_a_id):
    """Provide valid JWT token for user A."""
    return create_test_token(user_id=user_a_id, email="alice@example.com")


@pytest.fixture
def user_b_token(user_b_id):
    """Provide valid JWT token for user B."""
    return create_test_token(user_id=user_b_id, email="bob@example.com")


class TestUserIsolationList:
    """Test user isolation when listing tasks."""

    def test_user_a_cannot_list_user_b_tasks(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User A cannot list User B's tasks."""
        # User B creates tasks
        for i in range(3):
            client.post(
                f"/api/{user_b_id}/tasks",
                json={"title": f"User B Task {i+1}"},
                headers={"Authorization": f"Bearer {user_b_token}"}
            )

        # User A tries to list User B's tasks with their own token
        response = client.get(
            f"/api/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"}  # Token is for user A
        )

        # RED PHASE: This should return 403 but currently returns 200
        # because endpoints don't validate JWT user_id matches URL user_id
        assert response.status_code == 403
        assert "detail" in response.json()
        assert "not authorized" in response.json()["detail"].lower() or "forbidden" in response.json()["detail"].lower()

    def test_user_b_cannot_list_user_a_tasks(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User B cannot list User A's tasks."""
        # User A creates tasks
        for i in range(2):
            client.post(
                f"/api/{user_a_id}/tasks",
                json={"title": f"User A Task {i+1}"},
                headers={"Authorization": f"Bearer {user_a_token}"}
            )

        # User B tries to list User A's tasks with their own token
        response = client.get(
            f"/api/{user_a_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"}  # Token is for user B
        )

        # RED PHASE: This should return 403 but currently returns 200
        assert response.status_code == 403

    def test_users_can_only_see_their_own_tasks(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test each user can only see their own tasks."""
        # User A creates tasks
        client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A Task 1"},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A Task 2"},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # User B creates tasks
        client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "User B Task 1"},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

        # User A lists their tasks - should only see their own
        response_a = client.get(
            f"/api/{user_a_id}/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # RED PHASE: This should work but verify count
        assert response_a.status_code == 200
        data_a = response_a.json()
        assert data_a["count"] == 2

        # User B lists their tasks - should only see their own
        response_b = client.get(
            f"/api/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

        # RED PHASE: This should work but verify count
        assert response_b.status_code == 200
        data_b = response_b.json()
        assert data_b["count"] == 1


class TestUserIsolationCreate:
    """Test user isolation when creating tasks."""

    def test_user_a_cannot_create_task_for_user_b(self, client, user_a_id, user_b_id, user_a_token):
        """Test User A cannot create tasks in User B's space."""
        # User A tries to create task for User B using their own token
        response = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "Unauthorized task"},
            headers={"Authorization": f"Bearer {user_a_token}"}  # Token is for user A, but URL is for user B
        )

        # RED PHASE: This should return 403 but currently returns 201
        assert response.status_code == 403
        assert "detail" in response.json()

    def test_user_b_cannot_create_task_for_user_a(self, client, user_a_id, user_b_id, user_b_token):
        """Test User B cannot create tasks in User A's space."""
        # User B tries to create task for User A using their own token
        response = client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "Unauthorized task"},
            headers={"Authorization": f"Bearer {user_b_token}"}  # Token is for user B, but URL is for user A
        )

        # RED PHASE: This should return 403 but currently returns 201
        assert response.status_code == 403


class TestUserIsolationGet:
    """Test user isolation when getting specific tasks."""

    def test_user_a_cannot_get_user_b_task(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User A cannot get User B's specific task."""
        # User B creates a task
        create_response = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "User B's private task"},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        task_id = create_response.json()["id"]

        # User A tries to get User B's task
        response = client.get(
            f"/api/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # RED PHASE: This should return 403 or 404 but currently might return 200
        assert response.status_code in [403, 404]

    def test_user_b_cannot_get_user_a_task(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User B cannot get User A's specific task."""
        # User A creates a task
        create_response = client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's private task"},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        task_id = create_response.json()["id"]

        # User B tries to get User A's task
        response = client.get(
            f"/api/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

        # RED PHASE: This should return 403 or 404 but currently might return 200
        assert response.status_code in [403, 404]


class TestUserIsolationUpdate:
    """Test user isolation when updating tasks."""

    def test_user_a_cannot_update_user_b_task(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User A cannot update User B's task."""
        # User B creates a task
        create_response = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "Original title"},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        task_id = create_response.json()["id"]

        # User A tries to update User B's task
        response = client.put(
            f"/api/{user_b_id}/tasks/{task_id}",
            json={"title": "Hacked title"},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # RED PHASE: This should return 403 or 404 but currently might return 200
        assert response.status_code in [403, 404]

        # Verify task was NOT updated by checking with User B's token
        verify_response = client.get(
            f"/api/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert verify_response.json()["title"] == "Original title"

    def test_user_b_cannot_update_user_a_task(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User B cannot update User A's task."""
        # User A creates a task
        create_response = client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's task"},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        task_id = create_response.json()["id"]

        # User B tries to update User A's task
        response = client.put(
            f"/api/{user_a_id}/tasks/{task_id}",
            json={"title": "Hacked by B"},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

        # RED PHASE: This should return 403 or 404 but currently might return 200
        assert response.status_code in [403, 404]


class TestUserIsolationDelete:
    """Test user isolation when deleting tasks."""

    def test_user_a_cannot_delete_user_b_task(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User A cannot delete User B's task."""
        # User B creates a task
        create_response = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "User B's task"},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        task_id = create_response.json()["id"]

        # User A tries to delete User B's task
        response = client.delete(
            f"/api/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # RED PHASE: This should return 403 or 404 but currently might return 204
        assert response.status_code in [403, 404]

        # Verify task still exists by checking with User B's token
        verify_response = client.get(
            f"/api/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert verify_response.status_code == 200

    def test_user_b_cannot_delete_user_a_task(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User B cannot delete User A's task."""
        # User A creates a task
        create_response = client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's task"},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        task_id = create_response.json()["id"]

        # User B tries to delete User A's task
        response = client.delete(
            f"/api/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

        # RED PHASE: This should return 403 or 404 but currently might return 204
        assert response.status_code in [403, 404]


class TestUserIsolationToggleCompletion:
    """Test user isolation when toggling task completion."""

    def test_user_a_cannot_toggle_user_b_task(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User A cannot toggle User B's task completion."""
        # User B creates a task
        create_response = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "User B's task"},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        task_id = create_response.json()["id"]

        # User A tries to toggle User B's task completion
        response = client.patch(
            f"/api/{user_b_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # RED PHASE: This should return 403 or 404 but currently might return 200
        assert response.status_code in [403, 404]

    def test_user_b_cannot_toggle_user_a_task(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test User B cannot toggle User A's task completion."""
        # User A creates a task
        create_response = client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's task"},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        task_id = create_response.json()["id"]

        # User B tries to toggle User A's task completion
        response = client.patch(
            f"/api/{user_a_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

        # RED PHASE: This should return 403 or 404 but currently might return 200
        assert response.status_code in [403, 404]


class TestCrossUserAttackScenarios:
    """Test various cross-user attack scenarios."""

    def test_user_cannot_impersonate_by_changing_url_only(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
        """Test that user cannot access another user's data just by changing URL."""
        # User A creates tasks
        for i in range(3):
            client.post(
                f"/api/{user_a_id}/tasks",
                json={"title": f"User A Task {i+1}"},
                headers={"Authorization": f"Bearer {user_a_token}"}
            )

        # User B creates tasks
        for i in range(2):
            client.post(
                f"/api/{user_b_id}/tasks",
                json={"title": f"User B Task {i+1}"},
                headers={"Authorization": f"Bearer {user_b_token}"}
            )

        # User B tries to access User A's tasks by changing URL only
        response = client.get(
            f"/api/{user_a_id}/tasks",  # User A's endpoint
            headers={"Authorization": f"Bearer {user_b_token}"}  # But User B's token
        )

        # RED PHASE: This should return 403 but currently returns 200
        assert response.status_code == 403

        # Verify User B can still access their own tasks
        own_response = client.get(
            f"/api/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert own_response.status_code == 200
        assert own_response.json()["count"] == 2

    def test_multiple_users_complete_isolation(self, client):
        """Test complete isolation across multiple users."""
        users = [
            ("user-1", "user1@example.com"),
            ("user-2", "user2@example.com"),
            ("user-3", "user3@example.com"),
        ]

        # Create tokens and tasks for each user
        for user_id, email in users:
            token = create_test_token(user_id=user_id, email=email)

            # Each user creates 2 tasks
            for i in range(2):
                response = client.post(
                    f"/api/{user_id}/tasks",
                    json={"title": f"{user_id} Task {i+1}"},
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 201

        # Verify each user can only see their own 2 tasks
        for user_id, email in users:
            token = create_test_token(user_id=user_id, email=email)
            response = client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 2
            # Verify all tasks belong to this user
            for task in data["tasks"]:
                assert task["user_id"] == user_id

        # Verify users cannot access each other's tasks
        for i, (user_id, email) in enumerate(users):
            token = create_test_token(user_id=user_id, email=email)

            # Try to access next user's tasks
            next_user_id = users[(i + 1) % len(users)][0]
            response = client.get(
                f"/api/{next_user_id}/tasks",
                headers={"Authorization": f"Bearer {token}"}
            )

            # RED PHASE: This should return 403 but currently returns 200
            assert response.status_code == 403
