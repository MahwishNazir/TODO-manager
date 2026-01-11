"""
CLI menu interface for TODO application.

Provides interactive menu-driven interface for task management.
Handles user input, displays menus and task lists, and coordinates
with TaskManager service.
"""

from typing import Optional
from src.services.task_manager import TaskManager
from src.models.task import ValidationError, TaskNotFoundError


def display_menu() -> None:
    """Display the main menu options.
    
    Shows all available commands numbered 1-6:
    1. View tasks
    2. Add task
    3. Mark task complete
    4. Update task
    5. Delete task
    6. Exit
    
    Side Effects:
        Prints menu to stdout.
    
    Example:
        >>> display_menu()
        
        === TODO Application ===
        1. View all tasks
        2. Add new task
        3. Mark task complete
        4. Update task
        5. Delete task
        6. Exit
    """
    print("\n" + "=" * 30)
    print("    TODO Application")
    print("=" * 30)
    print("1. View all tasks")
    print("2. Add new task")
    print("3. Mark task complete")
    print("4. Update task")
    print("5. Delete task")
    print("6. Exit")
    print("=" * 30)


def get_user_choice() -> Optional[int]:
    """Get and validate user's menu choice.
    
    Prompts user for menu selection and validates input:
    - Must be an integer
    - Must be in range 1-6
    - Invalid input shows error and returns None
    
    Returns:
        int: Valid menu choice (1-6), or None if invalid.
    
    Side Effects:
        - Prints prompt to stdout
        - Prints error message if input is invalid
    
    Example:
        >>> choice = get_user_choice()
        Enter your choice (1-6): 2
        >>> choice
        2
        
        >>> choice = get_user_choice()
        Enter your choice (1-6): 99
        Invalid choice. Please enter a number between 1 and 6.
        >>> choice
        None
    """
    try:
        choice = input("\nEnter your choice (1-6): ").strip()
        choice_int = int(choice)
        
        if 1 <= choice_int <= 6:
            return choice_int
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 6.")
            return None
            
    except ValueError:
        print("[ERROR] Invalid input. Please enter a number.")
        return None


def view_tasks(task_manager: TaskManager) -> None:
    """Display all tasks in formatted list.
    
    Retrieves all tasks from TaskManager and displays them with:
    - Task ID
    - Completion status (checkbox or indicator)
    - Task title
    
    If no tasks exist, displays empty state message.
    
    Args:
        task_manager: TaskManager instance to retrieve tasks from.
    
    Returns:
        None
    
    Side Effects:
        Prints formatted task list or empty message to stdout.
    
    Example:
        >>> manager = TaskManager()
        >>> view_tasks(manager)
        
        📋 Your Tasks:
        No tasks yet. Add one to get started!
        
        >>> manager.add_task("Buy milk")
        >>> manager.add_task("Write tests")
        >>> view_tasks(manager)
        
        📋 Your Tasks:
        [ ] 1. Buy milk
        [ ] 2. Write tests
    """
    tasks = task_manager.get_all_tasks()
    
    print("\n" + "=" * 30)
    print("Your Tasks:")
    print("=" * 30)
    
    if not tasks:
        print("No tasks yet. Add one to get started!")
    else:
        # Sort tasks by ID for consistent display
        sorted_tasks = sorted(tasks, key=lambda t: t.id)
        
        for task in sorted_tasks:
            # Use checkbox notation for completion status
            status = "[X]" if task.completed else "[ ]"
            print(f"{status} {task.id}. {task.title}")
    
    print("=" * 30)


def add_task_interactive(task_manager: TaskManager) -> None:
    """Interactively add a new task.
    
    Prompts user for task title, validates input, and adds task
    to TaskManager. Handles validation errors gracefully.
    
    Args:
        task_manager: TaskManager instance to add task to.
    
    Returns:
        None
    
    Side Effects:
        - Prompts user for input
        - Adds task to TaskManager (if valid)
        - Prints success or error message
    
    Example:
        >>> manager = TaskManager()
        >>> add_task_interactive(manager)
        Enter task title: Buy milk
        ✅ Task added successfully! (ID: 1)
        
        >>> add_task_interactive(manager)
        Enter task title: 
        ❌ Error: Task title cannot be empty
    """
    try:
        title = input("\nEnter task title: ")
        task = task_manager.add_task(title)
        print(f"[SUCCESS] Task added successfully! (ID: {task.id})")
        
    except ValidationError as e:
        print(f"[ERROR] {e}")


def mark_task_interactive(task_manager: TaskManager) -> None:
    """Interactively mark a task as complete or incomplete.

    Prompts user for task ID and completion status (y/n),
    validates input, and updates task completion status.
    Handles errors gracefully.

    Args:
        task_manager: TaskManager instance to modify task in.

    Returns:
        None

    Side Effects:
        - Prompts user for input (task ID and status)
        - Updates task completion status (if valid)
        - Prints success or error message

    Example:
        >>> manager = TaskManager()
        >>> task = manager.add_task("Buy milk")
        >>> mark_task_interactive(manager)
        Enter task ID: 1
        Mark as complete? (y/n): y
        [SUCCESS] Task marked as complete!

        >>> mark_task_interactive(manager)
        Enter task ID: 999
        Mark as complete? (y/n): y
        [ERROR] Task not found: 999
    """
    try:
        # Get task ID from user
        task_id_str = input("\nEnter task ID: ")

        # Validate task ID is numeric
        try:
            task_id = int(task_id_str)
        except ValueError:
            print(f"[ERROR] Invalid task ID. Please enter a number.")
            return

        # Get completion status from user
        status_input = input("Mark as complete? (y/n): ").strip().lower()

        # Validate status input
        if status_input not in ['y', 'n', 'yes', 'no']:
            print(f"[ERROR] Invalid input. Please enter 'y' or 'n'.")
            return

        # Convert to boolean
        completed = status_input in ['y', 'yes']

        # Update task
        task = task_manager.mark_complete(task_id, completed)

        # Show success message with task details
        status_text = "complete" if completed else "incomplete"
        print(f"[SUCCESS] Task marked as {status_text}!")
        print(f"  [{('X' if completed else ' ')}] {task.id}. {task.title}")

    except TaskNotFoundError as e:
        print(f"[ERROR] Task not found: {task_id}")


def update_task_interactive(task_manager: TaskManager) -> None:
    """Interactively update a task's title.

    Prompts user for task ID and new title,
    validates input, and updates task title.
    Handles errors gracefully.

    Args:
        task_manager: TaskManager instance to modify task in.

    Returns:
        None

    Side Effects:
        - Prompts user for input (task ID and new title)
        - Updates task title (if valid)
        - Prints success or error message

    Example:
        >>> manager = TaskManager()
        >>> task = manager.add_task("Buy milk")
        >>> update_task_interactive(manager)
        Enter task ID: 1
        Enter new title: Buy organic milk
        [SUCCESS] Task updated successfully!
          1. Buy organic milk

        >>> update_task_interactive(manager)
        Enter task ID: 999
        Enter new title: New task
        [ERROR] Task not found: 999
    """
    try:
        # Get task ID from user
        task_id_str = input("\nEnter task ID: ")

        # Validate task ID is numeric
        try:
            task_id = int(task_id_str)
        except ValueError:
            print(f"[ERROR] Invalid task ID. Please enter a number.")
            return

        # Get new title from user
        new_title = input("Enter new title: ")

        # Update task
        task = task_manager.update_task(task_id, new_title)

        # Show success message with task details
        print(f"[SUCCESS] Task updated successfully!")
        status = "[X]" if task.completed else "[ ]"
        try:
            print(f"  {status} {task.id}. {task.title}")
        except UnicodeEncodeError:
            # Handle encoding errors on Windows console
            print(f"  {status} {task.id}. {task.title.encode('ascii', 'replace').decode('ascii')}")

    except TaskNotFoundError:
        print(f"[ERROR] Task not found: {task_id}")
    except ValidationError as e:
        print(f"[ERROR] {e}")


def delete_task_interactive(task_manager: TaskManager) -> None:
    """Interactively delete a task.

    Prompts user for task ID, validates input, and deletes task.
    Handles errors gracefully.

    Args:
        task_manager: TaskManager instance to delete task from.

    Returns:
        None

    Side Effects:
        - Prompts user for input (task ID)
        - Deletes task from storage (if valid)
        - Prints success or error message

    Example:
        >>> manager = TaskManager()
        >>> task = manager.add_task("Buy milk")
        >>> delete_task_interactive(manager)
        Enter task ID to delete: 1
        [SUCCESS] Task deleted successfully!
          Deleted: 1. Buy milk

        >>> delete_task_interactive(manager)
        Enter task ID to delete: 999
        [ERROR] Task not found: 999
    """
    try:
        # Get task ID from user
        task_id_str = input("\nEnter task ID to delete: ")

        # Validate task ID is numeric
        try:
            task_id = int(task_id_str)
        except ValueError:
            print(f"[ERROR] Invalid task ID. Please enter a number.")
            return

        # Get task details before deletion (for confirmation message)
        task = task_manager.get_task(task_id)
        task_title = task.title

        # Delete task
        task_manager.delete_task(task_id)

        # Show success message with deleted task details
        print(f"[SUCCESS] Task deleted successfully!")
        try:
            print(f"  Deleted: {task_id}. {task_title}")
        except UnicodeEncodeError:
            # Handle encoding errors on Windows console
            print(f"  Deleted: {task_id}. {task_title.encode('ascii', 'replace').decode('ascii')}")

    except TaskNotFoundError:
        print(f"[ERROR] Task not found: {task_id}")


def main_loop(task_manager: Optional[TaskManager] = None) -> None:
    """Main application loop.
    
    Displays menu, gets user choice, and dispatches to appropriate
    function. Continues until user chooses to exit (option 6).
    
    Currently implements User Story 1 functionality:
    - Option 1: View all tasks
    - Option 2: Add new task
    - Option 6: Exit
    
    Options 3-5 are placeholders for future user stories.
    
    Args:
        task_manager: Optional TaskManager instance. If None, creates new one.
    
    Returns:
        None
    
    Side Effects:
        - Runs interactive menu loop
        - Modifies TaskManager state
        - Exits when user chooses option 6
    
    Example:
        >>> main_loop()  # Starts interactive session
    """
    # Create TaskManager if not provided
    if task_manager is None:
        task_manager = TaskManager()
    
    print("\nWelcome to TODO Application!")
    print("Manage your tasks efficiently.\n")
    
    while True:
        display_menu()
        choice = get_user_choice()
        
        if choice is None:
            continue  # Invalid input, show menu again
        
        if choice == 1:
            view_tasks(task_manager)
            
        elif choice == 2:
            add_task_interactive(task_manager)
            
        elif choice == 3:
            mark_task_interactive(task_manager)

        elif choice == 4:
            update_task_interactive(task_manager)

        elif choice == 5:
            delete_task_interactive(task_manager)

        elif choice == 6:
            # Graceful exit with session-based persistence reminder (US5)
            print("\n" + "=" * 50)
            print("Exiting TODO Application...")
            print("=" * 50)
            print("\n[INFO] Session-based storage (Phase I):")
            print("  - All tasks will be lost when you exit")
            print("  - No data is saved to disk")
            print("  - Next session will start fresh with no tasks")
            print("\nThank you for using TODO Application. Goodbye!")
            print("=" * 50)
            break
