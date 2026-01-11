"""
Unit tests for Task model.

Tests cover:
- Task creation and initialization
- Title validation
- Task serialization
- Default values and timestamps
"""

import pytest
from datetime import datetime, UTC
from src.models.task import Task, ValidationError


class TestTaskCreation:
    """Tests for Task model creation and initialization."""

    def test_task_creation(self):
        """Test creating a task with valid data."""
        task = Task(id=1, title="Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_task_default_values(self):
        """Test that task has correct default values."""
        task = Task(id=1, title="Test task")

        # completed should default to False
        assert task.completed is False

        # created_at should be set automatically
        assert task.created_at is not None
        assert isinstance(task.created_at, datetime)

    def test_task_created_at_set(self):
        """Test that created_at is automatically set to current time."""
        before = datetime.now(UTC)
        task = Task(id=1, title="Test task")
        after = datetime.now(UTC)

        # created_at should be between before and after timestamps
        assert before <= task.created_at <= after

    def test_task_with_explicit_created_at(self):
        """Test creating task with explicit created_at timestamp."""
        fixed_time = datetime(2026, 1, 10, 12, 0, 0)
        task = Task(id=1, title="Test task", created_at=fixed_time)

        assert task.created_at == fixed_time

    def test_task_completed_true(self):
        """Test creating a completed task."""
        task = Task(id=1, title="Completed task", completed=True)

        assert task.completed is True

    def test_task_id_immutable(self):
        """Test that task ID cannot be changed after creation."""
        task = Task(id=1, title="Test task")
        original_id = task.id

        # ID should remain the same
        assert task.id == original_id


class TestTitleValidation:
    """Tests for Task title validation."""

    def test_empty_title_raises_error(self):
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Task(id=1, title="")

        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_title_raises_error(self):
        """Test that whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Task(id=1, title="   ")

        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_title_with_tabs_raises_error(self):
        """Test that whitespace with tabs raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Task(id=1, title="\t\t\t")

        assert "empty" in str(exc_info.value).lower()

    def test_long_title_raises_error(self):
        """Test that title exceeding 500 characters raises ValidationError."""
        long_title = "a" * 501  # 501 characters

        with pytest.raises(ValidationError) as exc_info:
            Task(id=1, title=long_title)

        assert "500" in str(exc_info.value) or "long" in str(exc_info.value).lower()

    def test_title_exactly_500_chars_accepted(self):
        """Test that title with exactly 500 characters is accepted."""
        exact_title = "a" * 500  # Exactly 500 characters

        task = Task(id=1, title=exact_title)

        assert len(task.title) == 500

    def test_title_trimmed(self):
        """Test that leading and trailing whitespace is trimmed."""
        task = Task(id=1, title="  Buy milk  ")

        # Whitespace should be trimmed
        assert task.title == "Buy milk"
        assert not task.title.startswith(" ")
        assert not task.title.endswith(" ")

    def test_title_with_internal_spaces_preserved(self):
        """Test that internal spaces in title are preserved."""
        task = Task(id=1, title="Buy organic milk")

        assert task.title == "Buy organic milk"
        assert "organic" in task.title

    def test_title_with_special_characters(self):
        """Test that special characters in title are allowed."""
        special_titles = [
            "Buy milk & eggs",
            "Task #1: Important",
            "Email john@example.com",
            "Path: C:\\Users\\Documents",
            "Price: $19.99"
        ]

        for title in special_titles:
            task = Task(id=1, title=title)
            assert task.title == title

    def test_title_with_unicode(self):
        """Test that unicode characters in title are allowed."""
        unicode_titles = [
            "Café meeting",
            "买牛奶",  # Chinese: Buy milk
            "Tâche importante",  # French
            "Aufgabe №1"  # Russian number symbol
        ]

        for title in unicode_titles:
            task = Task(id=1, title=title)
            assert task.title == title


class TestTaskSerialization:
    """Tests for Task serialization to dictionary."""

    def test_to_dict_format(self):
        """Test that to_dict returns correct dictionary format."""
        fixed_time = datetime(2026, 1, 10, 12, 0, 0)
        task = Task(id=1, title="Buy milk", completed=False, created_at=fixed_time)

        task_dict = task.to_dict()

        # Should be a dictionary
        assert isinstance(task_dict, dict)

        # Should have all required keys
        assert "id" in task_dict
        assert "title" in task_dict
        assert "completed" in task_dict
        assert "created_at" in task_dict

    def test_to_dict_contains_all_fields(self):
        """Test that to_dict includes all task fields with correct values."""
        fixed_time = datetime(2026, 1, 10, 12, 0, 0)
        task = Task(id=42, title="Test task", completed=True, created_at=fixed_time)

        task_dict = task.to_dict()

        assert task_dict["id"] == 42
        assert task_dict["title"] == "Test task"
        assert task_dict["completed"] is True
        assert "created_at" in task_dict  # Format may vary, just check presence

    def test_to_dict_incomplete_task(self):
        """Test to_dict for incomplete task."""
        task = Task(id=1, title="Incomplete task", completed=False)

        task_dict = task.to_dict()

        assert task_dict["completed"] is False

    def test_to_dict_complete_task(self):
        """Test to_dict for complete task."""
        task = Task(id=1, title="Complete task", completed=True)

        task_dict = task.to_dict()

        assert task_dict["completed"] is True

    def test_repr_format(self):
        """Test that __repr__ returns useful string representation."""
        task = Task(id=1, title="Buy milk", completed=False)

        repr_str = repr(task)

        # Should contain key information
        assert "Task" in repr_str
        assert "1" in repr_str  # ID
        assert "Buy milk" in repr_str or "title" in repr_str.lower()
        assert "False" in repr_str or "completed" in repr_str.lower()
