"""
Task Interface Definitions - Phase I TODO Application

This file defines the contracts (interfaces) for Task and TaskManager.
These serve as:
1. Documentation of expected behavior
2. Type hints for static type checking
3. Contract tests for validation
4. Blueprint for Phase II migration

DO NOT implement business logic here - this is specification only.
"""

from typing import Protocol, List, Dict
from datetime import datetime


class TaskProtocol(Protocol):
    """Protocol defining the Task interface.

    A Task represents a single todo item with a title, completion status,
    and metadata.

    Attributes:
        id: Unique integer identifier (auto-generated, immutable)
        title: Description of the task (non-empty string, ≤500 chars)
        completed: Boolean indicating if task is finished
        created_at: Timestamp when task was created (immutable)
    """

    id: int
    title: str
    completed: bool
    created_at: datetime

    def __init__(
        self,
        id: int,
        title: str,
        completed: bool = False,
        created_at: datetime | None = None,
    ) -> None:
        """Initialize a Task.

        Args:
            id: Unique task identifier (positive integer)
            title: Task description (non-empty, ≤500 chars)
            completed: Initial completion status (default: False)
            created_at: Creation timestamp (default: current UTC time)

        Raises:
            ValidationError: If title is empty or exceeds 500 characters
        """
        ...

    def to_dict(self) -> Dict[str, any]:
        """Serialize task to dictionary.

        Returns:
            Dictionary with keys: id, title, completed, created_at

        Example:
            {
                "id": 1,
                "title": "Buy groceries",
                "completed": false,
                "created_at": "2026-01-10T14:30:00Z"
            }
        """
        ...

    def __repr__(self) -> str:
        """Return string representation for debugging.

        Returns:
            String like: Task(id=1, title='Buy groceries', completed=False)
        """
        ...


class TaskManagerProtocol(Protocol):
    """Protocol defining the TaskManager interface.

    TaskManager manages a collection of tasks and provides CRUD operations.
    All operations are guaranteed to complete in O(1) time except get_all_tasks
    which is O(n).

    Attributes:
        _tasks: Internal storage (private, do not access directly)
        _next_id: ID counter for new tasks (private, do not access directly)
    """

    def add_task(self, title: str) -> TaskProtocol:
        """Create and add a new task.

        Args:
            title: Task description (non-empty, ≤500 chars)

        Returns:
            Newly created Task object with auto-generated ID

        Raises:
            ValidationError: If title is invalid

        Time Complexity: O(1)

        Side Effects:
            - Increments internal ID counter
            - Adds task to internal storage

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Buy milk")
            >>> task.id
            1
            >>> task.title
            "Buy milk"
        """
        ...

    def get_task(self, task_id: int) -> TaskProtocol:
        """Retrieve a task by its ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task object with matching ID

        Raises:
            TaskNotFoundError: If no task exists with given ID

        Time Complexity: O(1)

        Side Effects: None

        Example:
            >>> task = manager.get_task(1)
            >>> task.title
            "Buy milk"
        """
        ...

    def update_task(self, task_id: int, title: str) -> TaskProtocol:
        """Update a task's title.

        Args:
            task_id: ID of task to update
            title: New task description (non-empty, ≤500 chars)

        Returns:
            Updated Task object

        Raises:
            TaskNotFoundError: If no task exists with given ID
            ValidationError: If new title is invalid

        Time Complexity: O(1)

        Side Effects:
            - Modifies task.title in storage

        Note:
            - Only title can be updated via this method
            - Use mark_complete() to change completion status

        Example:
            >>> task = manager.update_task(1, "Buy organic milk")
            >>> task.title
            "Buy organic milk"
        """
        ...

    def delete_task(self, task_id: int) -> None:
        """Remove a task from storage.

        Args:
            task_id: ID of task to delete

        Returns:
            None

        Raises:
            TaskNotFoundError: If no task exists with given ID

        Time Complexity: O(1)

        Side Effects:
            - Removes task from internal storage
            - Task ID is not reused

        Note:
            - Operation is irreversible
            - Deleted IDs are never reassigned

        Example:
            >>> manager.delete_task(1)
            >>> manager.get_task(1)  # Raises TaskNotFoundError
        """
        ...

    def mark_complete(self, task_id: int, completed: bool) -> TaskProtocol:
        """Mark a task as complete or incomplete.

        Args:
            task_id: ID of task to update
            completed: New completion status (True = complete, False = incomplete)

        Returns:
            Updated Task object

        Raises:
            TaskNotFoundError: If no task exists with given ID

        Time Complexity: O(1)

        Side Effects:
            - Modifies task.completed in storage

        Note:
            - Can toggle between True and False freely
            - No state validation (can mark complete task as incomplete)

        Example:
            >>> task = manager.mark_complete(1, True)
            >>> task.completed
            True
            >>> task = manager.mark_complete(1, False)
            >>> task.completed
            False
        """
        ...

    def get_all_tasks(self) -> List[TaskProtocol]:
        """Return all tasks in storage.

        Returns:
            List of all Task objects (may be empty)

        Raises:
            None

        Time Complexity: O(n) where n = number of tasks

        Side Effects: None

        Note:
            - Returns a new list (not a reference to internal storage)
            - Order is not guaranteed
            - Empty list if no tasks exist

        Example:
            >>> tasks = manager.get_all_tasks()
            >>> len(tasks)
            3
            >>> [t.title for t in tasks]
            ["Buy milk", "Walk dog", "Write code"]
        """
        ...

    def count(self) -> int:
        """Return the number of tasks in storage.

        Returns:
            Integer count of tasks (≥ 0)

        Raises:
            None

        Time Complexity: O(1)

        Side Effects: None

        Example:
            >>> manager.count()
            3
        """
        ...


# Type Aliases for convenience
TaskDict = Dict[str, any]  # Dictionary representation of Task
TaskID = int  # Task identifier type


# Contract validation helpers (for testing)
def validate_task_contract(task: any) -> bool:
    """Validate that an object satisfies the Task contract.

    Args:
        task: Object to validate

    Returns:
        True if object has all required Task attributes with correct types

    Example:
        >>> task = Task(id=1, title="Test")
        >>> validate_task_contract(task)
        True
    """
    required_attrs = {
        "id": int,
        "title": str,
        "completed": bool,
        "created_at": datetime,
    }

    for attr, expected_type in required_attrs.items():
        if not hasattr(task, attr):
            return False
        if not isinstance(getattr(task, attr), expected_type):
            return False

    return True


def validate_task_manager_contract(manager: any) -> bool:
    """Validate that an object satisfies the TaskManager contract.

    Args:
        manager: Object to validate

    Returns:
        True if object has all required TaskManager methods

    Example:
        >>> manager = TaskManager()
        >>> validate_task_manager_contract(manager)
        True
    """
    required_methods = [
        "add_task",
        "get_task",
        "update_task",
        "delete_task",
        "mark_complete",
        "get_all_tasks",
        "count",
    ]

    for method in required_methods:
        if not hasattr(manager, method):
            return False
        if not callable(getattr(manager, method)):
            return False

    return True


# Exception contracts
class TodoErrorProtocol(Protocol):
    """Base exception for TODO application errors."""

    pass


class TaskNotFoundErrorProtocol(TodoErrorProtocol, Protocol):
    """Exception raised when task ID doesn't exist."""

    task_id: int

    def __init__(self, task_id: int) -> None:
        """Initialize with task ID that wasn't found."""
        ...


class ValidationErrorProtocol(TodoErrorProtocol, Protocol):
    """Exception raised when validation fails."""

    pass


class InvalidTaskDataErrorProtocol(TodoErrorProtocol, Protocol):
    """Exception raised when task data is malformed."""

    pass


# Constants
MAX_TITLE_LENGTH = 500  # Maximum characters for task title
MIN_TASK_ID = 1  # Minimum valid task ID


# Performance Requirements (for contract testing)
class PerformanceRequirements:
    """Performance contract for Phase I implementation."""

    # Maximum time (in seconds) for operations
    MAX_ADD_TIME = 0.1  # Add task must complete in <100ms
    MAX_GET_TIME = 0.1  # Get task must complete in <100ms
    MAX_UPDATE_TIME = 0.1  # Update task must complete in <100ms
    MAX_DELETE_TIME = 0.1  # Delete task must complete in <100ms
    MAX_MARK_TIME = 0.1  # Mark complete must complete in <100ms
    MAX_LIST_TIME_PER_1000 = 0.1  # List 1000 tasks in <100ms

    # Scale requirements
    MIN_SUPPORTED_TASKS = 1000  # Must support at least 1000 tasks


# Data Integrity Requirements (for contract testing)
class DataIntegrityRequirements:
    """Data integrity contract for Phase I implementation."""

    # ID requirements
    IDS_ARE_UNIQUE = True  # All task IDs must be unique
    IDS_ARE_SEQUENTIAL = True  # IDs increment by 1
    IDS_START_AT_ONE = True  # First task gets ID = 1
    IDS_NEVER_REUSED = True  # Deleted IDs are never reassigned

    # Title requirements
    TITLES_NOT_EMPTY = True  # Titles must be non-empty after trimming
    TITLES_MAX_LENGTH = MAX_TITLE_LENGTH  # Titles must be ≤500 chars
    TITLES_TRIMMED = True  # Leading/trailing whitespace removed

    # State requirements
    COMPLETED_IS_BOOLEAN = True  # Completed must be True or False
    CREATED_AT_IMMUTABLE = True  # created_at never changes
    ID_IMMUTABLE = True  # ID never changes


"""
Usage Notes:

1. **For Implementation**:
   Implement classes that satisfy these protocols:
   - Task class matching TaskProtocol
   - TaskManager class matching TaskManagerProtocol
   - Exception classes matching error protocols

2. **For Testing**:
   Use contract validation functions to verify implementations:
   - validate_task_contract(task) → ensure Task is correct
   - validate_task_manager_contract(manager) → ensure TaskManager is correct

3. **For Type Checking**:
   Use mypy to verify implementations match protocols:
   $ mypy src/

4. **For Migration**:
   Phase II implementations must also satisfy these contracts to ensure
   compatibility with Phase I data exports.

5. **Performance Testing**:
   Use PerformanceRequirements constants in performance tests.

6. **Data Integrity Testing**:
   Use DataIntegrityRequirements constants in validation tests.
"""
