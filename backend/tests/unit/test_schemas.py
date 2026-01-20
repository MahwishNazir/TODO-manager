"""
Unit tests for Pydantic schemas (TaskCreate, TaskUpdate, etc.).

These tests validate schema-level validation rules before
any database or API interaction.
"""

import pytest
from pydantic import ValidationError

from src.models.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    ErrorResponse,
)


class TestTaskCreateSchema:
    """Tests for TaskCreate schema validation."""

    def test_valid_task_create(self):
        """Test TaskCreate with valid title."""
        task_data = TaskCreate(title="Buy groceries")
        assert task_data.title == "Buy groceries"

    def test_task_create_trims_whitespace(self):
        """Test TaskCreate trims leading and trailing whitespace."""
        task_data = TaskCreate(title="  Buy groceries  ")
        assert task_data.title == "Buy groceries"

    def test_task_create_empty_title_fails(self):
        """Test TaskCreate rejects empty title."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")

        errors = exc_info.value.errors()
        assert any("title" in str(error) for error in errors)

    def test_task_create_whitespace_only_title_fails(self):
        """Test TaskCreate rejects whitespace-only title."""
        with pytest.raises(ValueError) as exc_info:
            TaskCreate(title="   ")

        assert "empty" in str(exc_info.value).lower() or "whitespace" in str(exc_info.value).lower()

    def test_task_create_too_long_title_fails(self):
        """Test TaskCreate rejects title > 500 characters."""
        long_title = "x" * 501
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)

        errors = exc_info.value.errors()
        assert any("title" in str(error) for error in errors)

    def test_task_create_max_length_title_succeeds(self):
        """Test TaskCreate accepts title with exactly 500 characters."""
        max_title = "x" * 500
        task_data = TaskCreate(title=max_title)
        assert len(task_data.title) == 500


class TestTaskUpdateSchema:
    """Tests for TaskUpdate schema validation."""

    def test_valid_task_update(self):
        """Test TaskUpdate with valid title."""
        task_data = TaskUpdate(title="Updated title")
        assert task_data.title == "Updated title"

    def test_task_update_trims_whitespace(self):
        """Test TaskUpdate trims leading and trailing whitespace."""
        task_data = TaskUpdate(title="  Updated title  ")
        assert task_data.title == "Updated title"

    def test_task_update_empty_title_fails(self):
        """Test TaskUpdate rejects empty title."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(title="")

        errors = exc_info.value.errors()
        assert any("title" in str(error) for error in errors)

    def test_task_update_whitespace_only_title_fails(self):
        """Test TaskUpdate rejects whitespace-only title."""
        with pytest.raises(ValueError) as exc_info:
            TaskUpdate(title="   ")

        assert "empty" in str(exc_info.value).lower() or "whitespace" in str(exc_info.value).lower()


class TestTaskResponseSchema:
    """Tests for TaskResponse schema."""

    def test_task_response_structure(self):
        """Test TaskResponse has all required fields."""
        from datetime import datetime

        response = TaskResponse(
            id=1,
            user_id="user123",
            title="Buy groceries",
            is_completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert response.id == 1
        assert response.user_id == "user123"
        assert response.title == "Buy groceries"
        assert response.is_completed is False
        assert response.created_at is not None
        assert response.updated_at is not None


class TestTaskListResponseSchema:
    """Tests for TaskListResponse schema."""

    def test_empty_task_list_response(self):
        """Test TaskListResponse with empty list."""
        response = TaskListResponse(tasks=[], count=0)
        assert response.tasks == []
        assert response.count == 0

    def test_task_list_response_with_tasks(self):
        """Test TaskListResponse with multiple tasks."""
        from datetime import datetime

        tasks = [
            TaskResponse(
                id=1,
                user_id="user123",
                title="Task 1",
                is_completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            TaskResponse(
                id=2,
                user_id="user123",
                title="Task 2",
                is_completed=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]

        response = TaskListResponse(tasks=tasks, count=2)
        assert len(response.tasks) == 2
        assert response.count == 2


class TestErrorResponseSchema:
    """Tests for ErrorResponse schema."""

    def test_error_response_structure(self):
        """Test ErrorResponse has all required fields."""
        error = ErrorResponse(
            error="Validation error",
            detail="Task title cannot be empty",
            type="validation_error",
        )

        assert error.error == "Validation error"
        assert error.detail == "Task title cannot be empty"
        assert error.type == "validation_error"
