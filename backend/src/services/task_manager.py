"""
TaskManager service for managing task collection and CRUD operations.

This module provides the business logic layer for task management,
handling task storage, ID generation, and all CRUD operations.
"""

from typing import Dict, List
from src.models.task import Task, TaskNotFoundError, ValidationError


class TaskManager:
    """Manages collection of tasks and provides CRUD operations.

    TaskManager maintains an in-memory collection of tasks using a dictionary
    for O(1) lookup by ID. It handles ID generation, task validation, and all
    task operations.

    **Session-Based Persistence (User Story 5):**
    - Storage is IN-MEMORY ONLY using a Python dictionary
    - Data persists ONLY during the current application session
    - NO file I/O operations are performed (no saving/loading)
    - Fresh TaskManager instances start completely empty
    - All data is LOST when the application exits or instance is destroyed
    - No persistence between separate TaskManager instances

    All operations except get_all_tasks() complete in O(1) time.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects (private).
                Data stored here is session-only and never persisted to disk.
        _next_id: Counter for generating new task IDs (private).
                  Resets to 1 for each new TaskManager instance.

    Example:
        >>> manager = TaskManager()
        >>> task = manager.add_task("Buy milk")
        >>> task.id
        1
        >>> manager.count()
        1
        >>> # Data is lost when instance is destroyed:
        >>> del manager
        >>> new_manager = TaskManager()
        >>> new_manager.count()  # Fresh instance, no persisted data
        0
    """

    def __init__(self) -> None:
        """Initialize an empty task manager.

        Creates a new TaskManager with no tasks and ID counter starting at 1.

        **Session-Based Storage:**
        Each new instance starts completely empty. No data is loaded from
        persistent storage because this is an in-memory-only implementation.

        Example:
            >>> manager = TaskManager()
            >>> manager.count()
            0
            >>> # Each instance is independent:
            >>> manager2 = TaskManager()
            >>> manager2.count()  # Also starts at 0
            0
        """
        # In-memory storage: dictionary for O(1) lookups (session-only)
        self._tasks: Dict[int, Task] = {}

        # ID counter: starts at 1 for each new instance (no persistence)
        self._next_id: int = 1

    def add_task(self, title: str) -> Task:
        """Create and add a new task.

        Creates a new task with the given title, assigns it a unique ID,
        and adds it to the task collection.

        Args:
            title: Task description (non-empty, ≤500 chars, will be trimmed).

        Returns:
            Task: The newly created task with auto-generated ID.

        Raises:
            ValidationError: If title is empty or exceeds 500 characters.

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
            'Buy milk'
            >>> task.completed
            False
        """
        # Create task with current ID (Task.__init__ will validate title)
        task = Task(id=self._next_id, title=title)

        # Add task to storage
        self._tasks[task.id] = task

        # Increment ID counter for next task
        self._next_id += 1

        return task

    def get_task(self, task_id: int) -> Task:
        """Retrieve a task by its ID.

        Args:
            task_id: Unique task identifier.

        Returns:
            Task: The task with matching ID.

        Raises:
            TaskNotFoundError: If no task exists with given ID.

        Time Complexity: O(1)

        Side Effects: None

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Buy milk")
            >>> retrieved = manager.get_task(1)
            >>> retrieved.title
            'Buy milk'
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        return self._tasks[task_id]

    def update_task(self, task_id: int, title: str) -> Task:
        """Update a task's title.

        Args:
            task_id: ID of task to update.
            title: New task description (non-empty, ≤500 chars).

        Returns:
            Task: The updated task object.

        Raises:
            TaskNotFoundError: If no task exists with given ID.
            ValidationError: If new title is invalid.

        Time Complexity: O(1)

        Side Effects:
            - Modifies task.title in storage

        Note:
            Only title can be updated via this method.
            Use mark_complete() to change completion status.

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Buy milk")
            >>> updated = manager.update_task(1, "Buy organic milk")
            >>> updated.title
            'Buy organic milk'
        """
        # Get task (will raise TaskNotFoundError if not found)
        task = self.get_task(task_id)

        # Validate and update title (Task._validate_title will raise ValidationError if invalid)
        task.title = Task._validate_title(title)

        return task

    def delete_task(self, task_id: int) -> None:
        """Remove a task from storage.

        Args:
            task_id: ID of task to delete.

        Returns:
            None

        Raises:
            TaskNotFoundError: If no task exists with given ID.

        Time Complexity: O(1)

        Side Effects:
            - Removes task from internal storage
            - Task ID is not reused (counter continues incrementing)

        Note:
            Operation is irreversible. Deleted IDs are never reassigned.

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Buy milk")
            >>> manager.delete_task(1)
            >>> manager.count()
            0
        """
        # Verify task exists (will raise TaskNotFoundError if not found)
        self.get_task(task_id)

        # Remove task from storage
        del self._tasks[task_id]

        # Note: _next_id counter is NOT decremented
        # Deleted IDs are never reused

    def mark_complete(self, task_id: int, completed: bool) -> Task:
        """Mark a task as complete or incomplete.

        Args:
            task_id: ID of task to update.
            completed: New completion status (True = complete, False = incomplete).

        Returns:
            Task: The updated task object.

        Raises:
            TaskNotFoundError: If no task exists with given ID.

        Time Complexity: O(1)

        Side Effects:
            - Modifies task.completed in storage

        Note:
            Can toggle between True and False freely.
            No state validation (can mark complete task as incomplete).

        Example:
            >>> manager = TaskManager()
            >>> task = manager.add_task("Buy milk")
            >>> updated = manager.mark_complete(1, True)
            >>> updated.completed
            True
            >>> updated = manager.mark_complete(1, False)
            >>> updated.completed
            False
        """
        # Get task (will raise TaskNotFoundError if not found)
        task = self.get_task(task_id)

        # Update completion status
        task.completed = completed

        return task

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks in storage.

        Returns:
            list: List of all Task objects (may be empty).
                 Returns a new list, not a reference to internal storage.

        Raises:
            None

        Time Complexity: O(n) where n = number of tasks

        Side Effects: None

        Note:
            - Order is not guaranteed (dict iteration order)
            - Returns empty list if no tasks exist
            - Returns a copy, not reference to internal storage

        Example:
            >>> manager = TaskManager()
            >>> manager.add_task("Task 1")
            >>> manager.add_task("Task 2")
            >>> tasks = manager.get_all_tasks()
            >>> len(tasks)
            2
        """
        return list(self._tasks.values())

    def count(self) -> int:
        """Return the number of tasks in storage.

        Returns:
            int: Count of tasks (≥ 0).

        Raises:
            None

        Time Complexity: O(1)

        Side Effects: None

        Example:
            >>> manager = TaskManager()
            >>> manager.count()
            0
            >>> manager.add_task("Task 1")
            >>> manager.count()
            1
        """
        return len(self._tasks)
