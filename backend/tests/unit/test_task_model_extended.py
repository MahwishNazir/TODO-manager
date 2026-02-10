"""
Unit tests for extended Task model with Phase III fields.

Tests for priority, status, due_date, and is_deleted fields
added to the Task model for AI chatbot functionality.

TDD: RED phase - Write tests before implementation.
"""

import pytest
from datetime import date, datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from src.models.task import Task
from src.models.enums import Priority, TaskStatus


# Create in-memory SQLite database for unit tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="function")
def session():
    """Provide a clean database session for each test."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


class TestTaskModelExtendedFields:
    """Tests for extended Task model fields (FR-001 to FR-004)."""

    def test_task_has_priority_field(self):
        """Task model should have a priority field."""
        task = Task(
            user_id="user123",
            title="Test task",
            priority=Priority.HIGH,
        )
        assert hasattr(task, "priority")
        assert task.priority == Priority.HIGH

    def test_task_priority_default_is_medium(self):
        """Task priority should default to MEDIUM."""
        task = Task(
            user_id="user123",
            title="Test task",
        )
        assert task.priority == Priority.MEDIUM

    def test_task_has_status_field(self):
        """Task model should have a status field."""
        task = Task(
            user_id="user123",
            title="Test task",
            status=TaskStatus.COMPLETE,
        )
        assert hasattr(task, "status")
        assert task.status == TaskStatus.COMPLETE

    def test_task_status_default_is_incomplete(self):
        """Task status should default to INCOMPLETE."""
        task = Task(
            user_id="user123",
            title="Test task",
        )
        assert task.status == TaskStatus.INCOMPLETE

    def test_task_has_due_date_field(self):
        """Task model should have a due_date field."""
        due = date.today() + timedelta(days=7)
        task = Task(
            user_id="user123",
            title="Test task",
            due_date=due,
        )
        assert hasattr(task, "due_date")
        assert task.due_date == due

    def test_task_due_date_is_optional(self):
        """Task due_date should be optional (nullable)."""
        task = Task(
            user_id="user123",
            title="Test task",
        )
        assert task.due_date is None

    def test_task_has_is_deleted_field(self):
        """Task model should have an is_deleted field for soft delete."""
        task = Task(
            user_id="user123",
            title="Test task",
            is_deleted=True,
        )
        assert hasattr(task, "is_deleted")
        assert task.is_deleted is True

    def test_task_is_deleted_default_is_false(self):
        """Task is_deleted should default to False."""
        task = Task(
            user_id="user123",
            title="Test task",
        )
        assert task.is_deleted is False


class TestTaskModelPersistence:
    """Tests for Task persistence with extended fields."""

    def test_create_task_with_all_extended_fields(self, session: Session):
        """Should persist task with all extended fields."""
        due = date.today() + timedelta(days=7)
        task = Task(
            user_id="user123",
            title="Extended task",
            priority=Priority.HIGH,
            status=TaskStatus.INCOMPLETE,
            due_date=due,
            is_deleted=False,
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.id is not None
        assert task.priority == Priority.HIGH
        assert task.status == TaskStatus.INCOMPLETE
        assert task.due_date == due
        assert task.is_deleted is False

    def test_read_task_with_extended_fields(self, session: Session):
        """Should read task with all extended fields from database."""
        due = date.today() + timedelta(days=3)
        task = Task(
            user_id="user123",
            title="Read test task",
            priority=Priority.LOW,
            status=TaskStatus.COMPLETE,
            due_date=due,
            is_deleted=False,
        )

        session.add(task)
        session.commit()

        # Read from database
        statement = select(Task).where(Task.id == task.id)
        result = session.exec(statement).first()

        assert result is not None
        assert result.priority == Priority.LOW
        assert result.status == TaskStatus.COMPLETE
        assert result.due_date == due

    def test_update_task_priority(self, session: Session):
        """Should update task priority."""
        task = Task(
            user_id="user123",
            title="Update priority test",
            priority=Priority.LOW,
        )

        session.add(task)
        session.commit()

        # Update priority
        task.priority = Priority.HIGH
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.priority == Priority.HIGH

    def test_update_task_status(self, session: Session):
        """Should update task status."""
        task = Task(
            user_id="user123",
            title="Update status test",
            status=TaskStatus.INCOMPLETE,
        )

        session.add(task)
        session.commit()

        # Update status
        task.status = TaskStatus.COMPLETE
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.status == TaskStatus.COMPLETE

    def test_update_task_due_date(self, session: Session):
        """Should update task due_date."""
        original_due = date.today() + timedelta(days=7)
        new_due = date.today() + timedelta(days=14)

        task = Task(
            user_id="user123",
            title="Update due date test",
            due_date=original_due,
        )

        session.add(task)
        session.commit()

        # Update due_date
        task.due_date = new_due
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.due_date == new_due

    def test_soft_delete_task(self, session: Session):
        """Should soft delete task by setting is_deleted=True."""
        task = Task(
            user_id="user123",
            title="Soft delete test",
            is_deleted=False,
        )

        session.add(task)
        session.commit()

        # Soft delete
        task.is_deleted = True
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.is_deleted is True
        # Task should still exist in database
        assert task.id is not None


class TestTaskModelFiltering:
    """Tests for filtering tasks by extended fields."""

    def test_filter_tasks_by_priority(self, session: Session):
        """Should filter tasks by priority."""
        # Create tasks with different priorities
        task_low = Task(user_id="user123", title="Low priority", priority=Priority.LOW)
        task_medium = Task(user_id="user123", title="Medium priority", priority=Priority.MEDIUM)
        task_high = Task(user_id="user123", title="High priority", priority=Priority.HIGH)

        session.add_all([task_low, task_medium, task_high])
        session.commit()

        # Filter by high priority
        statement = select(Task).where(Task.priority == Priority.HIGH)
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].title == "High priority"

    def test_filter_tasks_by_status(self, session: Session):
        """Should filter tasks by status."""
        task_incomplete = Task(
            user_id="user123",
            title="Incomplete task",
            status=TaskStatus.INCOMPLETE,
        )
        task_complete = Task(
            user_id="user123",
            title="Complete task",
            status=TaskStatus.COMPLETE,
        )

        session.add_all([task_incomplete, task_complete])
        session.commit()

        # Filter by incomplete status
        statement = select(Task).where(Task.status == TaskStatus.INCOMPLETE)
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].title == "Incomplete task"

    def test_filter_tasks_by_due_date(self, session: Session):
        """Should filter tasks by due_date."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)

        task_today = Task(user_id="user123", title="Due today", due_date=today)
        task_tomorrow = Task(user_id="user123", title="Due tomorrow", due_date=tomorrow)
        task_next_week = Task(user_id="user123", title="Due next week", due_date=next_week)

        session.add_all([task_today, task_tomorrow, task_next_week])
        session.commit()

        # Filter tasks due today or earlier
        statement = select(Task).where(Task.due_date <= today)
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].title == "Due today"

    def test_filter_excludes_deleted_tasks(self, session: Session):
        """Should exclude soft-deleted tasks when filtering."""
        task_active = Task(
            user_id="user123",
            title="Active task",
            is_deleted=False,
        )
        task_deleted = Task(
            user_id="user123",
            title="Deleted task",
            is_deleted=True,
        )

        session.add_all([task_active, task_deleted])
        session.commit()

        # Filter only non-deleted tasks
        statement = select(Task).where(Task.is_deleted == False)
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].title == "Active task"

    def test_combined_filter_priority_and_status(self, session: Session):
        """Should filter by multiple fields."""
        task1 = Task(
            user_id="user123",
            title="High incomplete",
            priority=Priority.HIGH,
            status=TaskStatus.INCOMPLETE,
        )
        task2 = Task(
            user_id="user123",
            title="High complete",
            priority=Priority.HIGH,
            status=TaskStatus.COMPLETE,
        )
        task3 = Task(
            user_id="user123",
            title="Low incomplete",
            priority=Priority.LOW,
            status=TaskStatus.INCOMPLETE,
        )

        session.add_all([task1, task2, task3])
        session.commit()

        # Filter high priority AND incomplete
        statement = select(Task).where(
            Task.priority == Priority.HIGH,
            Task.status == TaskStatus.INCOMPLETE,
        )
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].title == "High incomplete"


class TestTaskModelBackwardCompatibility:
    """Tests for backward compatibility with Phase II."""

    def test_is_completed_field_still_exists(self):
        """Task should still have is_completed field for backward compatibility."""
        task = Task(
            user_id="user123",
            title="Test task",
            is_completed=True,
        )
        assert hasattr(task, "is_completed")
        assert task.is_completed is True

    def test_existing_fields_unchanged(self, session: Session):
        """Original Task fields should work unchanged."""
        task = Task(
            user_id="user123",
            title="Original task",
            is_completed=False,
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.id is not None
        assert task.user_id == "user123"
        assert task.title == "Original task"
        assert task.is_completed is False
        assert task.created_at is not None
        assert task.updated_at is not None
