"""
Contract tests for OpenAPI spec validation.

These tests ensure API endpoints conform to the OpenAPI/Swagger
specification and return correct schemas.
"""

import pytest


class TestTaskEndpointsContract:
    """Contract tests for task API endpoints."""

    def test_post_tasks_endpoint_exists(self, client, sample_user_id, auth_headers):
        """Test POST /api/{user_id}/tasks endpoint exists."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        # Should not be 404 (endpoint should exist)
        assert response.status_code != 404

    def test_get_tasks_list_endpoint_exists(self, client, sample_user_id, auth_headers):
        """Test GET /api/{user_id}/tasks endpoint exists."""
        response = client.get(f"/api/{sample_user_id}/tasks", headers=auth_headers)
        # Should not be 404 (endpoint should exist)
        assert response.status_code != 404

    def test_get_single_task_endpoint_exists(self, client, sample_user_id, auth_headers):
        """Test GET /api/{user_id}/tasks/{id} endpoint exists."""
        # First create a task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        if create_response.status_code == 201:
            task_id = create_response.json()["id"]
            response = client.get(f"/api/{sample_user_id}/tasks/{task_id}", headers=auth_headers)
            # Should not be 404 (endpoint should exist)
            assert response.status_code != 404

    def test_post_tasks_returns_201_on_success(self, client, sample_user_id, auth_headers):
        """Test POST /api/{user_id}/tasks returns 201 Created."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Buy groceries"},
            headers=auth_headers,
        )
        assert response.status_code == 201

    def test_post_tasks_response_schema(self, client, sample_user_id, auth_headers):
        """Test POST /api/{user_id}/tasks returns correct schema."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Buy groceries"},
            headers=auth_headers,
        )

        if response.status_code == 201:
            data = response.json()

            # Validate response schema
            assert "id" in data
            assert "user_id" in data
            assert "title" in data
            assert "is_completed" in data
            assert "created_at" in data
            assert "updated_at" in data

            # Validate field types
            assert isinstance(data["id"], int)
            assert isinstance(data["user_id"], str)
            assert isinstance(data["title"], str)
            assert isinstance(data["is_completed"], bool)
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)

    def test_get_tasks_list_returns_200(self, client, sample_user_id, auth_headers):
        """Test GET /api/{user_id}/tasks returns 200 OK."""
        response = client.get(f"/api/{sample_user_id}/tasks", headers=auth_headers)
        assert response.status_code == 200

    def test_get_tasks_list_response_schema(self, client, sample_user_id, auth_headers):
        """Test GET /api/{user_id}/tasks returns correct schema."""
        response = client.get(f"/api/{sample_user_id}/tasks", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()

            # Validate response schema
            assert "tasks" in data
            assert "count" in data

            # Validate field types
            assert isinstance(data["tasks"], list)
            assert isinstance(data["count"], int)

    def test_get_single_task_returns_200(self, client, sample_user_id, auth_headers):
        """Test GET /api/{user_id}/tasks/{id} returns 200 OK."""
        # First create a task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )

        if create_response.status_code == 201:
            task_id = create_response.json()["id"]
            response = client.get(f"/api/{sample_user_id}/tasks/{task_id}", headers=auth_headers)
            assert response.status_code == 200

    def test_get_single_task_response_schema(self, client, sample_user_id, auth_headers):
        """Test GET /api/{user_id}/tasks/{id} returns correct schema."""
        # First create a task
        create_response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )

        if create_response.status_code == 201:
            task_id = create_response.json()["id"]
            response = client.get(f"/api/{sample_user_id}/tasks/{task_id}", headers=auth_headers)

            if response.status_code == 200:
                data = response.json()

                # Validate response schema
                assert "id" in data
                assert "user_id" in data
                assert "title" in data
                assert "is_completed" in data
                assert "created_at" in data
                assert "updated_at" in data

    def test_post_tasks_invalid_request_returns_422(self, client, sample_user_id, auth_headers):
        """Test POST /api/{user_id}/tasks with invalid data returns 422."""
        response = client.post(
            f"/api/{sample_user_id}/tasks",
            json={"title": ""},  # Empty title should fail
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_get_nonexistent_task_returns_404(self, client, sample_user_id, auth_headers):
        """Test GET /api/{user_id}/tasks/{id} returns 404 for non-existent task."""
        response = client.get(f"/api/{sample_user_id}/tasks/99999", headers=auth_headers)
        assert response.status_code == 404
