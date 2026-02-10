"""
MCP Server Tools Layer for TODO Application (Phase III).

This module provides an MCP (Model Context Protocol) server that exposes
task management tools for AI agents. Tools are stateless and delegate
to the existing TaskService for data operations.

Tools:
    - add_task: Create a new task
    - list_tasks: Retrieve tasks with optional filters
    - update_task: Modify task title/description
    - complete_task: Mark task as completed
    - delete_task: Remove a task (soft delete)
"""

from src.mcp.errors import (
    ErrorCode,
    build_success_response,
    build_error_response,
)
from src.mcp.schemas import (
    TaskOutput,
    ResponseEnvelope,
)

__all__ = [
    "ErrorCode",
    "build_success_response",
    "build_error_response",
    "TaskOutput",
    "ResponseEnvelope",
]
