"""
Task service layer for business logic.

This module provides CRUD operations for tasks with user isolation
enforcement. All operations are scoped to a specific user_id.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from src.models.task import Task


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
