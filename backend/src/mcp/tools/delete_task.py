"""
delete_task MCP tool implementation.

Permanently removes a task (soft delete, idempotent operation).
"""

from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from src.mcp.errors import ErrorCode, build_success_response, build_error_response
from src.mcp.schemas import DeleteTaskInput
from src.mcp.server import mcp, get_db_session
from src.services.task_service import get_task_by_id, delete_task as service_delete_task


def delete_task_handler(input_data: DeleteTaskInput) -> dict[str, Any]:
    """Handle delete_task tool invocation.

    Args:
        input_data: Validated DeleteTaskInput with user_id and task_id.

    Returns:
        Response envelope with deletion confirmation or error.
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

            # If task doesn't exist, operation is idempotent (success)
            if task is None:
                return build_success_response({
                    "deleted": True,
                    "task_id": input_data.task_id,
                })

            # Delete task
            service_delete_task(session, input_data.user_id, task_id)

            return build_success_response({
                "deleted": True,
                "task_id": input_data.task_id,
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
def delete_task(
    user_id: str,
    task_id: str,
) -> str:
    """Permanently remove a task.

    This operation is idempotent - deleting a non-existent task succeeds without error.
    This cannot be undone.

    Args:
        user_id: Unique identifier of the task owner.
        task_id: Unique identifier of the task to delete.

    Returns:
        JSON response with deletion confirmation or error details.
    """
    import json

    # Validate input
    try:
        input_data = DeleteTaskInput(
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
    response = delete_task_handler(input_data)
    return json.dumps(response)
