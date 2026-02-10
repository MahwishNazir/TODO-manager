"""
update_task MCP tool implementation.

Updates an existing task's mutable fields.
"""

from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from src.mcp.errors import ErrorCode, build_success_response, build_error_response
from src.mcp.schemas import UpdateTaskInput
from src.mcp.server import mcp, get_db_session
from src.services.task_service import get_task_by_id, update_task_title


def _task_to_output(task: Any) -> dict[str, Any]:
    """Convert Task model to output format."""
    status = "completed" if task.is_completed else "pending"
    completed_at = None
    if task.is_completed and hasattr(task, "updated_at") and task.updated_at:
        completed_at = task.updated_at.isoformat()

    return {
        "id": str(task.id),
        "user_id": task.user_id,
        "title": task.title,
        "description": None,  # Task model doesn't have description field
        "status": status,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "completed_at": completed_at,
    }


def update_task_handler(input_data: UpdateTaskInput) -> dict[str, Any]:
    """Handle update_task tool invocation.

    Args:
        input_data: Validated UpdateTaskInput with user_id, task_id, and fields to update.

    Returns:
        Response envelope with updated task or error.
    """
    try:
        with get_db_session() as session:
            # Parse task_id
            try:
                task_id_int = int(input_data.task_id)
            except ValueError:
                return build_error_response(
                    ErrorCode.INVALID_INPUT,
                    "Invalid task_id format",
                    {"task_id": input_data.task_id},
                )

            # Get task by ID (also verifies ownership via user_id filter)
            task = get_task_by_id(session, input_data.user_id, task_id_int)

            if task is None:
                return build_error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task with ID {task_id_int} not found",
                    {"task_id": input_data.task_id},
                )

            # Update title if provided
            if input_data.title is not None:
                task.title = input_data.title.strip()

            # Note: description is in MCP schema but Task model doesn't have this field

            # Commit changes
            from datetime import datetime, timezone
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)

            return build_success_response({
                "task": _task_to_output(task),
            })

    except SQLAlchemyError as e:
        return build_error_response(
            ErrorCode.SERVICE_UNAVAILABLE,
            "Database operation failed",
            {"error": str(e)},
        )
    except Exception as e:
        return build_error_response(
            ErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred",
            {"error": str(e)},
        )


@mcp.tool()
def update_task(
    user_id: str,
    task_id: str,
    title: str | None = None,
    description: str | None = None,
) -> str:
    """Update an existing task's mutable fields.

    Args:
        user_id: Unique identifier of the task owner.
        task_id: Unique identifier of the task to update.
        title: New task title (1-500 characters).
        description: New task description (0-5000 characters, empty string clears).

    Returns:
        JSON response with updated task or error details.
    """
    import json

    # Check at least one field provided
    if title is None and description is None:
        response = build_error_response(
            ErrorCode.NO_FIELDS_TO_UPDATE,
            "At least one of 'title' or 'description' must be provided",
        )
        return json.dumps(response)

    # Validate input
    try:
        input_data = UpdateTaskInput(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
        )
    except Exception as e:
        response = build_error_response(
            ErrorCode.INVALID_INPUT,
            "Input validation failed",
            {"validation_error": str(e)},
        )
        return json.dumps(response)

    # Execute handler
    response = update_task_handler(input_data)
    return json.dumps(response)
