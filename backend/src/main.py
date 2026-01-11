"""
Main entry point for TODO Application.

This module serves as the application entry point. It imports and
launches the main menu loop to start the interactive CLI session.

Usage:
    python -m src.main
    
    Or from backend directory:
    python src/main.py
"""

from src.cli.menu import main_loop


def main() -> None:
    """Application entry point.

    Creates a new TaskManager instance and starts the interactive
    menu loop. All tasks are stored in memory for the session.

    **Session-Based Persistence (User Story 5):**
    - Tasks persist only during the current session
    - All data is lost when application exits
    - No file persistence in Phase I

    Returns:
        None

    Side Effects:
        - Starts interactive CLI session
        - Blocks until user exits (option 6)
        - Tasks are lost when session ends (in-memory only for Phase I)

    Example:
        >>> if __name__ == "__main__":
        ...     main()
        # Launches interactive TODO application
    """
    try:
        main_loop()
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C (US5)
        print("\n\n" + "=" * 50)
        print("[WARNING] Application interrupted by user (Ctrl+C)")
        print("=" * 50)
        print("\n[INFO] Session-based storage:")
        print("  - All tasks have been lost (not saved)")
        print("  - No data persisted to disk")
        print("\nGoodbye!")
        print("=" * 50)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        print("Please report this issue if it persists.")
        raise


if __name__ == "__main__":
    main()
