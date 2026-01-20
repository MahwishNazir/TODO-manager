"""
Task API routes for Phase II Step 2.

This module provides RESTful endpoints for task management with
JWT authentication and user isolation via user_id path parameter.
"""

import re
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from src.api.dependencies import get_db
from src.auth.jwt_handler import get_current_user, CurrentUser
from src.models.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from src.services import task_service


# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


def validate_user_id(user_id: str) -> str:
    """
    Validate user_id format.

    User ID must be alphanumeric with optional hyphens/underscores,
    max 50 characters.

    Args:
        user_id: User identifier from path parameter

    Returns:
        str: Validated user_id

    Raises:
        HTTPException: If user_id format is invalid
    """
    if not user_id or len(user_id) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must be 1-50 characters",
        )

    # Allow alphanumeric, hyphens, and underscores only
    if not re.match(r"^[a-zA-Z0-9_-]+$", user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must contain only alphanumeric characters, hyphens, and underscores",
        )

    return user_id


def validate_user_access(user_id: str, current_user: CurrentUser) -> None:
    """
    Validate that path user_id matches JWT user_id.

    CRITICAL: This ensures users can only access their own resources.
    T036 implementation - user_id path parameter validation.

    Args:
        user_id: User identifier from path parameter
        current_user: Authenticated user from JWT token

    Raises:
        HTTPException: 403 if path user_id doesn't match JWT user_id
    """
    if user_id != current_user.user_id:
        logger.warning(
            f"Access denied: user {current_user.user_id} attempted to access resources for user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access other user's resources",
        )


@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    summary="Create a new task",
    description="Create a new task for the specified user. Task title will be trimmed of whitespace. Requires JWT authentication.",
)
def create_task(
    user_id: Annotated[str, Path(..., description="User identifier")],
    task_data: TaskCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Create a new task for the user.

    T030: JWT authentication with user_id validation.

    Args:
        user_id: User identifier from path
        task_data: Task creation data (title)
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        TaskResponse: Created task with generated ID

    Raises:
        HTTPException: 400 if user_id invalid, 401 if not authenticated, 403 if user_id mismatch, 422 if title invalid
    """
    # Validate user_id format
    validate_user_id(user_id)

    # CRITICAL: Validate JWT user_id matches path user_id (T036)
    validate_user_access(user_id, current_user)

    # Create task
    task = task_service.create_task(db, user_id, task_data.title)

    # Log operation
    logger.info(f"Created task {task.id} for user {user_id}: {task.title}")

    return task


@router.get(
    "/{user_id}/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    tags=["Tasks"],
    summary="List all tasks",
    description="Retrieve all tasks for the specified user. Tasks are filtered by user_id for isolation. Requires JWT authentication.",
)
def get_tasks(
    user_id: Annotated[str, Path(..., description="User identifier")],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> TaskListResponse:
    """
    Get all tasks for the user.

    T029: JWT authentication with user_id validation.

    Args:
        user_id: User identifier from path
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        TaskListResponse: List of tasks and count

    Raises:
        HTTPException: 400 if user_id invalid, 401 if not authenticated, 403 if user_id mismatch
    """
    # Validate user_id format
    validate_user_id(user_id)

    # CRITICAL: Validate JWT user_id matches path user_id (T036)
    validate_user_access(user_id, current_user)

    # Get tasks (T035: service layer filters by user_id)
    tasks = task_service.get_all_tasks(db, user_id)

    # Log operation
    logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")

    return TaskListResponse(tasks=tasks, count=len(tasks))


@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    tags=["Tasks"],
    summary="Get a single task",
    description="Retrieve a specific task by ID. Returns 404 if task doesn't exist or belongs to another user. Requires JWT authentication.",
)
def get_task(
    user_id: Annotated[str, Path(..., description="User identifier")],
    task_id: Annotated[int, Path(..., description="Task ID", gt=0)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Get a specific task by ID.

    T031: JWT authentication with user_id validation.

    Args:
        user_id: User identifier from path
        task_id: Task ID from path
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        TaskResponse: Task data

    Raises:
        HTTPException: 400 if user_id invalid, 401 if not authenticated, 403 if user_id mismatch, 404 if task not found
    """
    # Validate user_id format
    validate_user_id(user_id)

    # CRITICAL: Validate JWT user_id matches path user_id (T036)
    validate_user_access(user_id, current_user)

    # Get task (T035: service layer filters by user_id)
    task = task_service.get_task_by_id(db, user_id, task_id)

    if not task:
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    # Log operation
    logger.info(f"Retrieved task {task_id} for user {user_id}")

    return task


@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    tags=["Tasks"],
    summary="Update task title",
    description="Update the title of a specific task. Returns 404 if task doesn't exist or belongs to another user. Requires JWT authentication.",
)
def update_task(
    user_id: Annotated[str, Path(..., description="User identifier")],
    task_id: Annotated[int, Path(..., description="Task ID", gt=0)],
    task_data: TaskUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Update task title.

    T032: JWT authentication with user_id validation.

    Args:
        user_id: User identifier from path
        task_id: Task ID from path
        task_data: Task update data (new title)
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        TaskResponse: Updated task data

    Raises:
        HTTPException: 400 if user_id invalid, 401 if not authenticated, 403 if user_id mismatch, 404 if task not found, 422 if title invalid
    """
    # Validate user_id format
    validate_user_id(user_id)

    # CRITICAL: Validate JWT user_id matches path user_id (T036)
    validate_user_access(user_id, current_user)

    # Update task (T035: service layer filters by user_id)
    task = task_service.update_task_title(db, user_id, task_id, task_data.title)

    if not task:
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    # Log operation
    logger.info(f"Updated task {task_id} for user {user_id}: {task.title}")

    return task


@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    tags=["Tasks"],
    summary="Toggle task completion",
    description="Toggle the completion status of a task. Returns 404 if task doesn't exist or belongs to another user. Requires JWT authentication.",
)
def toggle_complete(
    user_id: Annotated[str, Path(..., description="User identifier")],
    task_id: Annotated[int, Path(..., description="Task ID", gt=0)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Toggle task completion status.

    T033: JWT authentication with user_id validation.

    Args:
        user_id: User identifier from path
        task_id: Task ID from path
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        TaskResponse: Updated task data

    Raises:
        HTTPException: 400 if user_id invalid, 401 if not authenticated, 403 if user_id mismatch, 404 if task not found
    """
    # Validate user_id format
    validate_user_id(user_id)

    # CRITICAL: Validate JWT user_id matches path user_id (T036)
    validate_user_access(user_id, current_user)

    # Toggle completion (T035: service layer filters by user_id)
    task = task_service.toggle_task_completion(db, user_id, task_id)

    if not task:
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    # Log operation
    logger.info(f"Toggled task {task_id} completion for user {user_id}: {task.is_completed}")

    return task


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
    summary="Delete a task",
    description="Delete a specific task. Returns 404 if task doesn't exist or belongs to another user. Requires JWT authentication.",
)
def delete_task(
    user_id: Annotated[str, Path(..., description="User identifier")],
    task_id: Annotated[int, Path(..., description="Task ID", gt=0)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Delete a task.

    T034: JWT authentication with user_id validation.

    Args:
        user_id: User identifier from path
        task_id: Task ID from path
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 400 if user_id invalid, 401 if not authenticated, 403 if user_id mismatch, 404 if task not found
    """
    # Validate user_id format
    validate_user_id(user_id)

    # CRITICAL: Validate JWT user_id matches path user_id (T036)
    validate_user_access(user_id, current_user)

    # Delete task (T035: service layer filters by user_id)
    success = task_service.delete_task(db, user_id, task_id)

    if not success:
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    # Log operation
    logger.info(f"Deleted task {task_id} for user {user_id}")

    return None
