"""
Entry point for running the MCP server as a module.

Usage:
    python -m backend.src.mcp.server
    or from backend directory:
    python -m src.mcp.server
"""

from src.mcp.server import main

if __name__ == "__main__":
    main()
