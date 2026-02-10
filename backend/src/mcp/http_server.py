"""
HTTP wrapper for MCP tools.

Exposes MCP tools as REST endpoints for the AI Agent to invoke.
Runs on port 8001 by default.

Usage:
    uvicorn src.mcp.http_server:app --port 8001
"""

from typing import Any, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.mcp.server import get_db_session
from src.mcp.schemas import (
    AddTaskInput,
    ListTasksInput,
    UpdateTaskInput,
    CompleteTaskInput,
    DeleteTaskInput,
)
from src.mcp.errors import build_success_response, build_error_response, ErrorCode
from src.services.task_service import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    update_task_title,
    toggle_task_completion,
    delete_task as delete_task_service,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="MCP HTTP Bridge",
    description="HTTP API for MCP tools invocation",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for chatbot access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ToolRequest(BaseModel):
    """Generic tool request body."""
    user_id: str
    # Additional fields depend on the tool


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-http-bridge"}


@app.post("/tools/add_task")
async def add_task_handler(input_data: AddTaskInput) -> Dict[str, Any]:
    """
    Add a new task via MCP add_task tool.

    POST /tools/add_task
    """
    try:
        with get_db_session() as session:
            task = create_task(session, input_data.user_id, input_data.title)
            return build_success_response({
                "id": str(task.id),
                "title": task.title,
                "completed": task.is_completed,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat() if task.created_at else None,
            })
    except Exception as e:
        return build_error_response(
            ErrorCode.INTERNAL_ERROR,
            str(e),
        )


@app.post("/tools/list_tasks")
async def list_tasks_handler(input_data: ListTasksInput) -> Dict[str, Any]:
    """
    List tasks via MCP list_tasks tool.

    POST /tools/list_tasks
    """
    try:
        with get_db_session() as session:
            # Get all tasks for user
            all_tasks = get_all_tasks(session, input_data.user_id)

            # Apply status filter
            if input_data.status == "pending":
                all_tasks = [t for t in all_tasks if not t.is_completed]
            elif input_data.status == "completed":
                all_tasks = [t for t in all_tasks if t.is_completed]
            # "all" returns everything

            # Apply pagination
            offset = input_data.offset or 0
            limit = input_data.limit or 50
            paginated_tasks = all_tasks[offset:offset + limit]

            task_list = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "completed": task.is_completed,
                    "user_id": task.user_id,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                }
                for task in paginated_tasks
            ]

            return build_success_response({
                "tasks": task_list,
                "count": len(task_list),
                "has_more": offset + limit < len(all_tasks),
            })
    except Exception as e:
        return build_error_response(
            ErrorCode.INTERNAL_ERROR,
            str(e),
        )


@app.post("/tools/update_task")
async def update_task_handler(input_data: UpdateTaskInput) -> Dict[str, Any]:
    """
    Update a task via MCP update_task tool.

    POST /tools/update_task
    """
    try:
        with get_db_session() as session:
            # Check if at least one field provided
            if input_data.title is None and input_data.description is None:
                return build_error_response(
                    ErrorCode.NO_FIELDS_TO_UPDATE,
                    "At least one field (title or description) must be provided",
                )

            # Get existing task
            task = get_task_by_id(session, input_data.user_id, int(input_data.task_id))
            if task is None:
                return build_error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task with ID {input_data.task_id} not found",
                )

            # Update task (only title is supported)
            if input_data.title is not None:
                updated_task = update_task_title(
                    session,
                    input_data.user_id,
                    int(input_data.task_id),
                    input_data.title,
                )
            else:
                # No title change, return current task
                updated_task = task

            if updated_task is None:
                return build_error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task with ID {input_data.task_id} not found",
                )

            return build_success_response({
                "id": str(updated_task.id),
                "title": updated_task.title,
                "completed": updated_task.is_completed,
                "user_id": updated_task.user_id,
            })
    except Exception as e:
        return build_error_response(
            ErrorCode.INTERNAL_ERROR,
            str(e),
        )


@app.post("/tools/complete_task")
async def complete_task_handler(input_data: CompleteTaskInput) -> Dict[str, Any]:
    """
    Complete a task via MCP complete_task tool.

    POST /tools/complete_task
    """
    try:
        with get_db_session() as session:
            # Get task first to check existence
            task = get_task_by_id(session, input_data.user_id, int(input_data.task_id))
            if task is None:
                return build_error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task with ID {input_data.task_id} not found",
                )

            # If already completed, just return success (idempotent)
            if task.is_completed:
                return build_success_response({
                    "id": str(task.id),
                    "title": task.title,
                    "completed": task.is_completed,
                    "user_id": task.user_id,
                })

            # Toggle to complete
            completed_task = toggle_task_completion(
                session,
                input_data.user_id,
                int(input_data.task_id),
            )

            return build_success_response({
                "id": str(completed_task.id),
                "title": completed_task.title,
                "completed": completed_task.is_completed,
                "user_id": completed_task.user_id,
            })
    except Exception as e:
        return build_error_response(
            ErrorCode.INTERNAL_ERROR,
            str(e),
        )


@app.post("/tools/delete_task")
async def delete_task_handler(input_data: DeleteTaskInput) -> Dict[str, Any]:
    """
    Delete a task via MCP delete_task tool.

    POST /tools/delete_task
    """
    try:
        with get_db_session() as session:
            # Delete is idempotent - deleting non-existent task succeeds
            success = delete_task_service(
                session,
                input_data.user_id,
                int(input_data.task_id),
            )

            return build_success_response({
                "deleted": True,
                "task_id": input_data.task_id,
            })
    except Exception as e:
        return build_error_response(
            ErrorCode.INTERNAL_ERROR,
            str(e),
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
