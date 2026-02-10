"""
complete_task MCP tool implementation.

Marks a task as completed (idempotent operation).
"""

from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from src.mcp.errors import ErrorCode, build_success_response, build_error_response
from src.mcp.schemas import CompleteTaskInput
from src.mcp.server import mcp, get_db_session
from src.services.task_service import get_task_by_id, toggle_task_completion


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


def complete_task_handler(input_data: CompleteTaskInput) -> dict[str, Any]:
    """Handle complete_task tool invocation.

    Args:
        input_data: Validated CompleteTaskInput with user_id and task_id.

    Returns:
        Response envelope with completed task or error.
    """
    try:
        with get_db_session() as session:
            # Parse task_id
            try:
                task_id = int(input_data.task_id)
            except ValueError:
                return build_error_response(
                    ErrorCode.INVALID_INPUT,
                    "Invalid task_id format",
                    {"task_id": input_data.task_id},
                )

            # Get task by ID (also verifies ownership via user_id filter)
            task = get_task_by_id(session, input_data.user_id, task_id)

            if task is None:
                return build_error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task with ID {task_id} not found",
                    {"task_id": input_data.task_id},
                )

            # Complete task (idempotent - if already completed, just return it)
            if not task.is_completed:
                task = toggle_task_completion(session, input_data.user_id, task_id)

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
def complete_task(
    user_id: str,
    task_id: str,
) -> str:
    """Mark a task as completed.

    This operation is idempotent - completing an already-completed task succeeds without error.

    Args:
        user_id: Unique identifier of the task owner.
        task_id: Unique identifier of the task to complete.

    Returns:
        JSON response with completed task or error details.
    """
    import json

    # Validate input
    try:
        input_data = CompleteTaskInput(
            user_id=user_id,
            task_id=task_id,
        )
    except Exception as e:
        response = build_error_response(
            ErrorCode.INVALID_INPUT,
            "Input validation failed",
            {"validation_error": str(e)},
        )
        return json.dumps(response)

    # Execute handler
    response = complete_task_handler(input_data)
    return json.dumps(response)
