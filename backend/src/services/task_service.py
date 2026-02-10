"""
Task service layer for business logic.

This module provides CRUD operations for tasks with user isolation
enforcement. All operations are scoped to a specific user_id.

Phase III Extensions:
- TaskService class for dependency injection pattern
- Support for priority, status, due_date, is_deleted fields
- Soft delete support (is_deleted flag)
"""

from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import Session, select

from src.models.task import Task
from src.models.enums import Priority, TaskStatus


class TaskService:
    """
    Service class for task operations with user isolation.

    All methods require user_id to ensure data isolation between users.
    """

    def __init__(self, session: Session):
        """Initialize service with database session."""
        self.session = session

    def get_tasks_by_user(
        self,
        user_id: str,
        priority: Optional[Priority] = None,
        status: Optional[TaskStatus] = None,
        include_deleted: bool = False,
    ) -> List[Task]:
        """
        Get all tasks for a user with optional filtering.

        Args:
            user_id: User identifier for isolation
            priority: Optional priority filter
            status: Optional status filter
            include_deleted: Whether to include soft-deleted tasks

        Returns:
            List of tasks belonging to the user
        """
        statement = select(Task).where(Task.user_id == user_id)

        if not include_deleted:
            statement = statement.where(Task.is_deleted == False)

        if priority is not None:
            statement = statement.where(Task.priority == priority)

        if status is not None:
            statement = statement.where(Task.status == status)

        statement = statement.order_by(Task.created_at)
        return list(self.session.exec(statement).all())

    def get_task_by_id(self, task_id: int, user_id: str) -> Optional[Task]:
        """
        Get a specific task by ID with user isolation.

        Returns None if task doesn't exist, belongs to another user,
        or is soft-deleted. This ensures security by obscurity.

        Args:
            task_id: Task ID to retrieve
            user_id: User identifier for isolation

        Returns:
            Task if found and accessible, None otherwise
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.is_deleted == False,
        )
        return self.session.exec(statement).first()

    def update_task(
        self,
        task_id: int,
        user_id: str,
        title: Optional[str] = None,
        priority: Optional[Priority] = None,
        status: Optional[TaskStatus] = None,
    ) -> Optional[Task]:
        """
        Update a task with user isolation.

        Args:
            task_id: Task ID to update
            user_id: User identifier for isolation
            title: New title (optional)
            priority: New priority (optional)
            status: New status (optional)

        Returns:
            Updated task if found and accessible, None otherwise
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        if title is not None:
            task.title = title.strip()
        if priority is not None:
            task.priority = priority
        if status is not None:
            task.status = status
            task.is_completed = status == TaskStatus.COMPLETE

        task.updated_at = datetime.now(timezone.utc)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def delete_task(self, task_id: int, user_id: str) -> bool:
        """
        Soft-delete a task with user isolation.

        Sets is_deleted=True rather than removing the record.

        Args:
            task_id: Task ID to delete
            user_id: User identifier for isolation

        Returns:
            True if task was deleted, False if not found or access denied
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return False

        task.is_deleted = True
        task.updated_at = datetime.now(timezone.utc)

        self.session.add(task)
        self.session.commit()

        return True


# Legacy function-based API for backward compatibility

def create_task(session: Session, user_id: str, title: str) -> Task:
    """
    Create a new task for the specified user.

    Args:
        session: Database session
        user_id: User identifier
        title: Task description (will be trimmed)

    Returns:
        Task: Created task with generated ID

    Example:
        task = create_task(session, "user123", "Buy groceries")
        print(task.id)  # Auto-generated ID
    """
    task = Task(
        user_id=user_id,
        title=title.strip(),
        is_completed=False,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def get_all_tasks(session: Session, user_id: str) -> List[Task]:
    """
    Get all tasks for the specified user.

    Tasks are filtered by user_id to ensure user isolation.
    Results are ordered by created_at timestamp (oldest first).

    Args:
        session: Database session
        user_id: User identifier

    Returns:
        List[Task]: List of tasks belonging to the user

    Example:
        tasks = get_all_tasks(session, "user123")
        print(f"Found {len(tasks)} tasks")
    """
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at)
    tasks = session.exec(statement).all()
    return list(tasks)


def get_task_by_id(session: Session, user_id: str, task_id: int) -> Optional[Task]:
    """
    Get a specific task by ID with user isolation.

    Returns None if task doesn't exist or belongs to a different user.
    This enforces user isolation at the service layer.

    Args:
        session: Database session
        user_id: User identifier (for isolation)
        task_id: Task ID to retrieve

    Returns:
        Optional[Task]: Task if found and belongs to user, None otherwise

    Example:
        task = get_task_by_id(session, "user123", 1)
        if task:
            print(task.title)
        else:
            print("Task not found or access denied")
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    return task


def update_task_title(
    session: Session, user_id: str, task_id: int, new_title: str
) -> Optional[Task]:
    """
    Update task title with user isolation.

    Args:
        session: Database session
        user_id: User identifier (for isolation)
        task_id: Task ID to update
        new_title: New task title (will be trimmed)

    Returns:
        Optional[Task]: Updated task if found and belongs to user, None otherwise

    Example:
        task = update_task_title(session, "user123", 1, "Buy organic groceries")
        if task:
            print(f"Updated: {task.title}")
    """
    task = get_task_by_id(session, user_id, task_id)
    if not task:
        return None

    task.title = new_title.strip()
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def toggle_task_completion(
    session: Session, user_id: str, task_id: int
) -> Optional[Task]:
    """
    Toggle task completion status with user isolation.

    Args:
        session: Database session
        user_id: User identifier (for isolation)
        task_id: Task ID to toggle

    Returns:
        Optional[Task]: Updated task if found and belongs to user, None otherwise

    Example:
        task = toggle_task_completion(session, "user123", 1)
        if task:
            print(f"Completed: {task.is_completed}")
    """
    task = get_task_by_id(session, user_id, task_id)
    if not task:
        return None

    task.is_completed = not task.is_completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(session: Session, user_id: str, task_id: int) -> bool:
    """
    Delete task with user isolation.

    Args:
        session: Database session
        user_id: User identifier (for isolation)
        task_id: Task ID to delete

    Returns:
        bool: True if task was deleted, False if not found or access denied

    Example:
        if delete_task(session, "user123", 1):
            print("Task deleted")
        else:
            print("Task not found or access denied")
    """
    task = get_task_by_id(session, user_id, task_id)
    if not task:
        return False

    session.delete(task)
    session.commit()

    return True
