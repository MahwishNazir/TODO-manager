"""
list_tasks MCP tool implementation.

Retrieves tasks for the specified user with optional filtering.
"""

from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from src.mcp.errors import ErrorCode, build_success_response, build_error_response
from src.mcp.schemas import ListTasksInput
from src.mcp.server import mcp, get_db_session
from src.services.task_service import get_all_tasks
from src.models.enums import TaskStatus


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


def list_tasks_handler(input_data: ListTasksInput) -> dict[str, Any]:
    """Handle list_tasks tool invocation.

    Args:
        input_data: Validated ListTasksInput with user_id and optional filters.

    Returns:
        Response envelope with tasks list or error.
    """
    try:
        with get_db_session() as session:
            # Map MCP status to TaskStatus enum
            status_filter = None
            if input_data.status == "pending":
                status_filter = TaskStatus.INCOMPLETE
            elif input_data.status == "completed":
                status_filter = TaskStatus.COMPLETE
            # "all" means no filter

            # Get all tasks for user via existing service
            all_tasks = get_all_tasks(session, input_data.user_id)

            # Apply status filter if specified
            if status_filter is not None:
                if status_filter == TaskStatus.COMPLETE:
                    tasks = [t for t in all_tasks if t.is_completed]
                else:
                    tasks = [t for t in all_tasks if not t.is_completed]
            else:
                tasks = all_tasks

            # Apply offset
            tasks = tasks[input_data.offset :]

            # Check if more exist beyond limit
            has_more = len(tasks) > input_data.limit

            # Apply limit
            tasks = tasks[: input_data.limit]

            # Convert to output format
            task_outputs = [_task_to_output(task) for task in tasks]

            return build_success_response({
                "tasks": task_outputs,
                "total_count": len(task_outputs),
                "has_more": has_more,
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
def list_tasks(
    user_id: str,
    status: str = "all",
    limit: int = 50,
    offset: int = 0,
) -> str:
    """Retrieve tasks for the specified user with optional filtering.

    Args:
        user_id: Unique identifier of the task owner.
        status: Filter by status: "pending", "completed", or "all" (default: "all").
        limit: Maximum tasks to return (1-100, default: 50).
        offset: Number of tasks to skip (default: 0).

    Returns:
        JSON response with tasks list or error details.
    """
    import json

    # Validate input
    try:
        input_data = ListTasksInput(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        response = build_error_response(
            ErrorCode.INVALID_INPUT,
            "Input validation failed",
            {"validation_error": str(e)},
        )
        return json.dumps(response)

    # Execute handler
    response = list_tasks_handler(input_data)
    return json.dumps(response)
