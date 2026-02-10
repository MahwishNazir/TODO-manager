"""
MCP Server for TODO Application Task Management Tools.

This module provides the FastMCP server that exposes task management
tools for AI agents. The server is stateless and delegates to the
existing TaskService for all data operations.

Usage:
    python -m backend.src.mcp.server
"""

from contextlib import contextmanager
from typing import Generator

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

from src.database import engine

# Initialize FastMCP server
mcp = FastMCP(
    "todo-mcp-server",
    instructions="""
    MCP Server for TODO Application Task Management.

    Available tools:
    - add_task: Create a new task
    - list_tasks: Retrieve tasks with optional filters
    - update_task: Modify task title/description
    - complete_task: Mark task as completed
    - delete_task: Remove a task (soft delete)

    All tools require a user_id parameter for user isolation.
    """,
)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions in MCP tool handlers.

    Yields:
        SQLModel Session that auto-commits on success, rolls back on error.

    Example:
        with get_db_session() as session:
            task = create_task(session, user_id, task_data)
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Tool imports and registration happen here
# Each tool is registered via @mcp.tool() decorator in its own module
# Import tools to register them with the server

def register_tools():
    """Register all MCP tools with the server.

    This function imports tool modules, which triggers their
    @mcp.tool() decorators and registers them with the server.
    """
    # Import tools to register them with the server
    from src.mcp.tools import add_task  # noqa: F401
    from src.mcp.tools import list_tasks  # noqa: F401
    from src.mcp.tools import update_task  # noqa: F401
    from src.mcp.tools import complete_task  # noqa: F401
    from src.mcp.tools import delete_task  # noqa: F401


# Register tools on module load
register_tools()


def main():
    """Run the MCP server.

    IMPORTANT: When running as __main__, Python creates a separate module
    namespace. To ensure tools are registered with the correct mcp instance,
    we import from src.mcp.server explicitly.
    """
    # Import the mcp instance from the package to ensure we get the one
    # that has tools registered (not a duplicate __main__ instance)
    from src.mcp.server import mcp as server_mcp
    server_mcp.run()


if __name__ == "__main__":
    main()
