"""
add_task MCP tool implementation.

Creates a new task for the specified user.
"""

from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from src.mcp.errors import ErrorCode, build_success_response, build_error_response
from src.mcp.schemas import AddTaskInput
from src.mcp.server import mcp, get_db_session
from src.services.task_service import create_task


def _task_to_output(task: Any) -> dict[str, Any]:
    """Convert Task model to output format."""
    # Map status enum to MCP status string
    status = "completed" if task.is_completed else "pending"

    return {
        "id": str(task.id),
        "user_id": task.user_id,
        "title": task.title,
        "description": None,  # Task model doesn't have description field
        "status": status,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "completed_at": None,  # New tasks are never completed
    }


def add_task_handler(input_data: AddTaskInput) -> dict[str, Any]:
    """Handle add_task tool invocation.

    Args:
        input_data: Validated AddTaskInput with user_id, title, and optional description.

    Returns:
        Response envelope with created task or error.
    """
    try:
        with get_db_session() as session:
            # Create task via existing service (takes user_id and title string)
            # Note: description is in the MCP schema but not stored in the Task model
            task = create_task(session, input_data.user_id, input_data.title)

            # Build success response
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
def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
) -> str:
    """Create a new task for the specified user.

    Args:
        user_id: Unique identifier of the task owner.
        title: Task title (1-500 characters).
        description: Optional task description (0-5000 characters).

    Returns:
        JSON response with created task or error details.
    """
    import json

    # Validate input
    try:
        input_data = AddTaskInput(
            user_id=user_id,
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
    response = add_task_handler(input_data)
    return json.dumps(response)
