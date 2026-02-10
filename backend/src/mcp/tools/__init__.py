"""
MCP Tools for TODO Application Task Management.

Each tool is implemented in its own module and registered with the
MCP server via the @mcp.tool() decorator.

Tools:
    - add_task: Create a new task
    - list_tasks: Retrieve tasks with optional filters
    - update_task: Modify task title/description
    - complete_task: Mark task as completed
    - delete_task: Remove a task (soft delete)
"""

# Import tools to register them
from src.mcp.tools.add_task import add_task  # noqa: F401
from src.mcp.tools.list_tasks import list_tasks  # noqa: F401
from src.mcp.tools.update_task import update_task  # noqa: F401
from src.mcp.tools.complete_task import complete_task  # noqa: F401
from src.mcp.tools.delete_task import delete_task  # noqa: F401

__all__ = ["add_task", "list_tasks", "update_task", "complete_task", "delete_task"]
