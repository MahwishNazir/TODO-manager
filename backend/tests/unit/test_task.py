"""
Unit tests for Task SQLModel.

These tests validate the Task model field validation,
defaults, and constraints.
"""

import pytest
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from src.models.task import Task


# Create in-memory database for unit tests
@pytest.fixture
def memory_session():
    """Provide in-memory database session for unit tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestTaskModel:
    """Tests for Task SQLModel."""

    def test_task_creation_with_all_fields(self, memory_session):
        """Test creating Task with all fields specified."""
        task = Task(
            user_id="user123",
            title="Buy groceries",
            is_completed=False,
        )

        memory_session.add(task)
        memory_session.commit()
        memory_session.refresh(task)

        assert task.id is not None  # Auto-generated
        assert task.user_id == "user123"
        assert task.title == "Buy groceries"
        assert task.is_completed is False
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_default_is_completed_false(self, memory_session):
        """Test Task defaults is_completed to False."""
        task = Task(user_id="user123", title="Test task")

        memory_session.add(task)
        memory_session.commit()
        memory_session.refresh(task)

        assert task.is_completed is False

    def test_task_created_at_auto_generated(self, memory_session):
        """Test Task automatically sets created_at timestamp."""
        before = datetime.utcnow()
        task = Task(user_id="user123", title="Test task")

        memory_session.add(task)
        memory_session.commit()
        memory_session.refresh(task)

        after = datetime.utcnow()

        assert task.created_at is not None
        assert before <= task.created_at <= after

    def test_task_updated_at_auto_generated(self, memory_session):
        """Test Task automatically sets updated_at timestamp."""
        before = datetime.utcnow()
        task = Task(user_id="user123", title="Test task")

        memory_session.add(task)
        memory_session.commit()
        memory_session.refresh(task)

        after = datetime.utcnow()

        assert task.updated_at is not None
        assert before <= task.updated_at <= after

    def test_task_id_auto_increments(self, memory_session):
        """Test Task id auto-increments."""
        task1 = Task(user_id="user123", title="Task 1")
        task2 = Task(user_id="user123", title="Task 2")

        memory_session.add(task1)
        memory_session.add(task2)
        memory_session.commit()
        memory_session.refresh(task1)
        memory_session.refresh(task2)

        assert task1.id is not None
        assert task2.id is not None
        assert task2.id > task1.id

    def test_task_user_id_required(self, memory_session):
        """Test Task requires user_id field."""
        with pytest.raises(Exception):  # Will raise validation or integrity error
            task = Task(title="Task without user_id")
            memory_session.add(task)
            memory_session.commit()

    def test_task_title_required(self, memory_session):
        """Test Task requires title field."""
        with pytest.raises(Exception):  # Will raise validation or integrity error
            task = Task(user_id="user123")
            memory_session.add(task)
            memory_session.commit()

    def test_task_user_id_max_length(self, memory_session):
        """Test Task user_id respects max length of 50."""
        long_user_id = "x" * 51  # Exceeds max length
        task = Task(user_id=long_user_id, title="Test task")

        with pytest.raises(Exception):  # Database or validation error
            memory_session.add(task)
            memory_session.commit()

    def test_task_title_max_length(self, memory_session):
        """Test Task title respects max length of 500."""
        long_title = "x" * 501  # Exceeds max length
        task = Task(user_id="user123", title=long_title)

        with pytest.raises(Exception):  # Database or validation error
            memory_session.add(task)
            memory_session.commit()

    def test_multiple_tasks_same_user(self, memory_session):
        """Test multiple tasks can belong to same user."""
        task1 = Task(user_id="user123", title="Task 1")
        task2 = Task(user_id="user123", title="Task 2")

        memory_session.add(task1)
        memory_session.add(task2)
        memory_session.commit()

        memory_session.refresh(task1)
        memory_session.refresh(task2)

        assert task1.user_id == task2.user_id == "user123"
        assert task1.id != task2.id
