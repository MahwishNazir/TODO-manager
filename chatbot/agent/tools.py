"""
Tool functions for OpenAI Agents SDK.

Calls the backend REST API directly with service JWT authentication,
eliminating the need for a separate MCP HTTP Bridge server.
"""

import time
from typing import Any, Dict, Optional
from uuid import UUID

import httpx
import jwt as pyjwt

from agents import function_tool

from chatbot.agent.config import get_settings


# Tool context for passing session/user info
_tool_context: Dict[str, Any] = {}


def set_tool_context(session_id: Optional[UUID], user_id: Optional[str]) -> None:
    """Set context for tool invocations (session and user for audit)."""
    _tool_context["session_id"] = session_id
    _tool_context["user_id"] = user_id


def clear_tool_context() -> None:
    """Clear tool context."""
    _tool_context.clear()


def get_tool_context() -> Dict[str, Any]:
    """Get current tool context."""
    return _tool_context.copy()


def _create_service_jwt(user_id: str) -> str:
    """
    Create a short-lived JWT for calling the backend API on behalf of a user.

    Uses the shared BETTER_AUTH_SECRET to sign a JWT that the backend will accept.
    """
    settings = get_settings()
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": f"{user_id}@agent.internal",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + 300,  # 5 minute expiry
    }
    return pyjwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm=settings.jwt_algorithm,
    )


async def _backend_request(
    method: str,
    path: str,
    user_id: str,
    json_body: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Make an authenticated request to the backend REST API.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        path: API path (e.g., /api/{user_id}/tasks)
        user_id: User ID for JWT generation
        json_body: Optional JSON request body

    Returns:
        Dict with success status and data or error
    """
    settings = get_settings()
    token = _create_service_jwt(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(
        base_url=settings.backend_api_url,
        timeout=30.0,
    ) as client:
        response = await client.request(
            method, path, headers=headers, json=json_body,
        )

        # Handle 204 No Content (delete success)
        if response.status_code == 204:
            return {"success": True, "data": {"deleted": True}}

        # Handle errors
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"detail": response.text}
            return {
                "success": False,
                "error": {
                    "code": str(response.status_code),
                    "message": error_data.get("detail", "Request failed"),
                },
            }

        # Success
        data = response.json()
        return {"success": True, "data": data}


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: Unique identifier of the task owner
        title: Task title (1-500 characters)
        description: Optional task description
    """
    return await _backend_request(
        "POST",
        f"/api/{user_id}/tasks",
        user_id,
        json_body={"title": title},
    )


async def list_tasks(
    user_id: str,
    status: Optional[str] = "all",
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
) -> Dict[str, Any]:
    """
    Retrieve tasks for the user with optional filtering.

    Args:
        user_id: Unique identifier of the task owner
        status: Filter by status ("pending", "completed", "all")
        limit: Maximum tasks to return (1-100, default 50)
        offset: Number of tasks to skip (default 0)
    """
    return await _backend_request(
        "GET",
        f"/api/{user_id}/tasks",
        user_id,
    )


async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing task's title.

    Args:
        user_id: Unique identifier of the task owner
        task_id: Unique identifier of the task to update
        title: New task title (optional)
        description: New task description (optional)
    """
    body = {}
    if title is not None:
        body["title"] = title

    return await _backend_request(
        "PUT",
        f"/api/{user_id}/tasks/{task_id}",
        user_id,
        json_body=body,
    )


async def complete_task(
    user_id: str,
    task_id: str,
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        user_id: Unique identifier of the task owner
        task_id: Unique identifier of the task to complete
    """
    return await _backend_request(
        "PATCH",
        f"/api/{user_id}/tasks/{task_id}/complete",
        user_id,
    )


async def delete_task(
    user_id: str,
    task_id: str,
) -> Dict[str, Any]:
    """
    Permanently remove a task.

    Args:
        user_id: Unique identifier of the task owner
        task_id: Unique identifier of the task to delete
    """
    return await _backend_request(
        "DELETE",
        f"/api/{user_id}/tasks/{task_id}",
        user_id,
    )


# Export all tools for agent registration
AGENT_TOOLS = [
    function_tool(add_task),
    function_tool(list_tasks),
    function_tool(update_task),
    function_tool(complete_task),
    function_tool(delete_task),
]
