"""
Unit tests for TaskManager service.

Tests cover:
- Adding tasks
- Retrieving tasks
- Counting tasks
- ID generation
- Error handling
"""

import pytest
from src.services.task_manager import TaskManager
from src.models.task import Task, ValidationError, TaskNotFoundError


class TestAddTask:
    """Tests for TaskManager.add_task method."""

    def test_add_task_returns_task(self, task_manager):
        """Test that add_task returns a Task object."""
        task = task_manager.add_task("Buy milk")

        assert isinstance(task, Task)
        assert task.title == "Buy milk"

    def test_add_task_assigns_id(self, task_manager):
        """Test that add_task assigns a unique ID to the task."""
        task = task_manager.add_task("First task")

        assert task.id is not None
        assert isinstance(task.id, int)
        assert task.id >= 1

    def test_add_task_increments_id(self, task_manager):
        """Test that IDs increment for each new task."""
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")

        # IDs should increment by 1
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_empty_title_raises_error(self, task_manager):
        """Test that adding task with empty title raises ValidationError."""
        with pytest.raises(ValidationError):
            task_manager.add_task("")

    def test_add_task_whitespace_title_raises_error(self, task_manager):
        """Test that adding task with whitespace-only title raises error."""
        with pytest.raises(ValidationError):
            task_manager.add_task("   ")

    def test_add_task_sets_default_completed_false(self, task_manager):
        """Test that new tasks are incomplete by default."""
        task = task_manager.add_task("New task")

        assert task.completed is False

    def test_add_task_sets_created_at(self, task_manager):
        """Test that new tasks have created_at timestamp."""
        task = task_manager.add_task("New task")

        assert task.created_at is not None

    def test_add_multiple_tasks(self, task_manager):
        """Test adding multiple tasks in sequence."""
        titles = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"]

        for i, title in enumerate(titles, start=1):
            task = task_manager.add_task(title)
            assert task.id == i
            assert task.title == title

    def test_add_task_with_special_characters(self, task_manager):
        """Test adding tasks with special characters in title."""
        special_title = "Buy milk & eggs (urgent!)"
        task = task_manager.add_task(special_title)

        assert task.title == special_title

    def test_add_task_trims_whitespace(self, task_manager):
        """Test that add_task trims leading/trailing whitespace."""
        task = task_manager.add_task("  Buy milk  ")

        assert task.title == "Buy milk"


class TestGetAllTasks:
    """Tests for TaskManager.get_all_tasks method."""

    def test_get_all_tasks_empty_list(self, task_manager):
        """Test that get_all_tasks returns empty list when no tasks exist."""
        tasks = task_manager.get_all_tasks()

        assert tasks == []
        assert isinstance(tasks, list)

    def test_get_all_tasks_returns_all(self, task_manager):
        """Test that get_all_tasks returns all added tasks."""
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")

        tasks = task_manager.get_all_tasks()

        assert len(tasks) == 3
        assert task1 in tasks
        assert task2 in tasks
        assert task3 in tasks

    def test_get_all_tasks_returns_copy(self, task_manager):
        """Test that get_all_tasks returns a new list (not reference)."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")

        tasks1 = task_manager.get_all_tasks()
        tasks2 = task_manager.get_all_tasks()

        # Should be different list objects
        assert tasks1 is not tasks2

        # But should contain same tasks
        assert len(tasks1) == len(tasks2)

    def test_get_all_tasks_after_multiple_adds(self, task_manager):
        """Test get_all_tasks after adding many tasks."""
        num_tasks = 10
        for i in range(1, num_tasks + 1):
            task_manager.add_task(f"Task {i}")

        tasks = task_manager.get_all_tasks()

        assert len(tasks) == num_tasks

    def test_get_all_tasks_returns_task_objects(self, task_manager):
        """Test that get_all_tasks returns Task objects."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")

        tasks = task_manager.get_all_tasks()

        for task in tasks:
            assert isinstance(task, Task)


class TestCount:
    """Tests for TaskManager.count method."""

    def test_count_empty(self, task_manager):
        """Test that count returns 0 when no tasks exist."""
        count = task_manager.count()

        assert count == 0

    def test_count_after_adds(self, task_manager):
        """Test that count increases as tasks are added."""
        assert task_manager.count() == 0

        task_manager.add_task("Task 1")
        assert task_manager.count() == 1

        task_manager.add_task("Task 2")
        assert task_manager.count() == 2

        task_manager.add_task("Task 3")
        assert task_manager.count() == 3

    def test_count_matches_get_all_tasks_length(self, task_manager):
        """Test that count matches length of get_all_tasks."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        task_manager.add_task("Task 3")

        assert task_manager.count() == len(task_manager.get_all_tasks())

    def test_count_with_many_tasks(self, task_manager):
        """Test count with large number of tasks."""
        num_tasks = 100
        for i in range(num_tasks):
            task_manager.add_task(f"Task {i}")

        assert task_manager.count() == num_tasks


class TestTaskManagerInitialization:
    """Tests for TaskManager initialization."""

    def test_new_task_manager_empty(self):
        """Test that new TaskManager starts with no tasks."""
        manager = TaskManager()

        assert manager.count() == 0
        assert manager.get_all_tasks() == []

    def test_new_task_manager_starts_id_at_1(self):
        """Test that first task gets ID 1."""
        manager = TaskManager()
        task = manager.add_task("First task")

        assert task.id == 1

    def test_multiple_managers_independent(self):
        """Test that multiple TaskManager instances are independent."""
        manager1 = TaskManager()
        manager2 = TaskManager()

        task1 = manager1.add_task("Manager 1 task")
        task2 = manager2.add_task("Manager 2 task")

        # Both should start with ID 1
        assert task1.id == 1
        assert task2.id == 1

        # Counts should be independent
        assert manager1.count() == 1
        assert manager2.count() == 1


class TestTaskManagerEdgeCases:
    """Tests for TaskManager edge cases and error conditions."""

    def test_add_1000_tasks_performance(self, task_manager):
        """Test adding 1000 tasks (performance requirement)."""
        num_tasks = 1000

        for i in range(1, num_tasks + 1):
            task = task_manager.add_task(f"Task {i}")
            assert task.id == i

        assert task_manager.count() == num_tasks

    def test_task_titles_with_varying_lengths(self, task_manager):
        """Test tasks with titles of varying lengths."""
        titles = [
            "Short",
            "Medium length title",
            "A" * 100,  # Long title
            "A" * 500   # Max length title
        ]

        for title in titles:
            task = task_manager.add_task(title)
            assert task.title == title

    def test_concurrent_task_creation_simulation(self, task_manager):
        """Test rapid task creation (simulates concurrent usage)."""
        # Rapidly create tasks
        tasks = []
        for i in range(50):
            task = task_manager.add_task(f"Rapid task {i}")
            tasks.append(task)

        # All should have unique IDs
        ids = [task.id for task in tasks]
        assert len(ids) == len(set(ids))  # All unique

        # IDs should be sequential
        assert ids == list(range(1, 51))


class TestGetTask:
    """Tests for TaskManager.get_task method (User Story 2)."""

    def test_get_task_success(self, task_manager):
        """Test retrieving an existing task by ID.

        Verifies that get_task returns the correct task object
        when given a valid task ID.
        """
        # Add some tasks
        task1 = task_manager.add_task("First task")
        task2 = task_manager.add_task("Second task")
        task3 = task_manager.add_task("Third task")

        # Retrieve tasks by ID
        retrieved1 = task_manager.get_task(task1.id)
        retrieved2 = task_manager.get_task(task2.id)
        retrieved3 = task_manager.get_task(task3.id)

        # Verify correct tasks are returned
        assert retrieved1 is task1
        assert retrieved1.title == "First task"
        assert retrieved1.id == 1

        assert retrieved2 is task2
        assert retrieved2.title == "Second task"
        assert retrieved2.id == 2

        assert retrieved3 is task3
        assert retrieved3.title == "Third task"
        assert retrieved3.id == 3

    def test_get_task_not_found_raises_error(self, task_manager):
        """Test that get_task raises TaskNotFoundError for invalid ID.

        Verifies that attempting to retrieve a non-existent task
        raises the appropriate exception.
        """
        # Add a task (ID will be 1)
        task_manager.add_task("Test task")

        # Try to get non-existent tasks
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_manager.get_task(999)

        assert "999" in str(exc_info.value)

        with pytest.raises(TaskNotFoundError) as exc_info:
            task_manager.get_task(0)

        assert "0" in str(exc_info.value)

    def test_get_task_from_empty_manager(self, task_manager):
        """Test get_task on empty TaskManager raises error."""
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(1)

    def test_get_task_returns_same_object(self, task_manager):
        """Test that get_task returns the same object reference."""
        task = task_manager.add_task("Test task")

        # Get the task multiple times
        retrieved1 = task_manager.get_task(task.id)
        retrieved2 = task_manager.get_task(task.id)

        # Should be the exact same object
        assert retrieved1 is task
        assert retrieved2 is task
        assert retrieved1 is retrieved2


class TestMarkComplete:
    """Tests for TaskManager.mark_complete method (User Story 2)."""

    def test_mark_complete_true(self, task_manager):
        """Test marking a task as complete.

        Verifies that mark_complete(id, True) sets the task's
        completed status to True.
        """
        task = task_manager.add_task("Test task")
        assert task.completed is False

        # Mark as complete
        result = task_manager.mark_complete(task.id, True)

        # Verify task is now complete
        assert task.completed is True
        assert result.completed is True
        assert result is task  # Should return the same task object

    def test_mark_complete_false(self, task_manager):
        """Test marking a task as incomplete.

        Verifies that mark_complete(id, False) sets the task's
        completed status to False.
        """
        task = task_manager.add_task("Test task")

        # Mark as complete first
        task_manager.mark_complete(task.id, True)
        assert task.completed is True

        # Mark as incomplete
        result = task_manager.mark_complete(task.id, False)

        # Verify task is now incomplete
        assert task.completed is False
        assert result.completed is False

    def test_mark_complete_toggle(self, task_manager):
        """Test toggling task completion status multiple times.

        Verifies that completion status can be toggled
        back and forth multiple times.
        """
        task = task_manager.add_task("Test task")

        # Start incomplete
        assert task.completed is False

        # Toggle to complete
        task_manager.mark_complete(task.id, True)
        assert task.completed is True

        # Toggle back to incomplete
        task_manager.mark_complete(task.id, False)
        assert task.completed is False

        # Toggle to complete again
        task_manager.mark_complete(task.id, True)
        assert task.completed is True

        # Toggle back again
        task_manager.mark_complete(task.id, False)
        assert task.completed is False

    def test_mark_complete_not_found_raises_error(self, task_manager):
        """Test that mark_complete raises TaskNotFoundError for invalid ID.

        Verifies that attempting to mark a non-existent task
        raises the appropriate exception.
        """
        task_manager.add_task("Test task")

        # Try to mark non-existent task
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_manager.mark_complete(999, True)

        assert "999" in str(exc_info.value)

    def test_mark_complete_multiple_tasks(self, task_manager):
        """Test marking different tasks with different statuses.

        Verifies that each task maintains its own completion status
        independently.
        """
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")

        # Mark task2 as complete
        task_manager.mark_complete(task2.id, True)

        # Verify statuses
        assert task1.completed is False
        assert task2.completed is True
        assert task3.completed is False

        # Mark task1 and task3 as complete
        task_manager.mark_complete(task1.id, True)
        task_manager.mark_complete(task3.id, True)

        # Verify all complete
        assert task1.completed is True
        assert task2.completed is True
        assert task3.completed is True

        # Mark task2 back to incomplete
        task_manager.mark_complete(task2.id, False)

        # Verify mixed statuses
        assert task1.completed is True
        assert task2.completed is False
        assert task3.completed is True

    def test_mark_complete_returns_task(self, task_manager):
        """Test that mark_complete returns the updated task."""
        task = task_manager.add_task("Test task")

        result = task_manager.mark_complete(task.id, True)

        assert result is task
        assert isinstance(result, Task)
        assert result.id == task.id
        assert result.title == task.title
        assert result.completed is True

    def test_mark_complete_idempotent(self, task_manager):
        """Test that marking complete multiple times is safe.

        Verifies that calling mark_complete with the same status
        multiple times doesn't cause issues.
        """
        task = task_manager.add_task("Test task")

        # Mark complete multiple times
        task_manager.mark_complete(task.id, True)
        task_manager.mark_complete(task.id, True)
        task_manager.mark_complete(task.id, True)

        assert task.completed is True

        # Mark incomplete multiple times
        task_manager.mark_complete(task.id, False)
        task_manager.mark_complete(task.id, False)
        task_manager.mark_complete(task.id, False)

        assert task.completed is False


class TestUpdateTask:
    """Tests for TaskManager.update_task method (User Story 3)."""

    def test_update_task_success(self, task_manager):
        """Test successfully updating a task's title.

        Verifies that update_task changes the task title
        while preserving other attributes.
        """
        # Add a task
        task = task_manager.add_task("Original title")
        original_id = task.id
        original_completed = task.completed
        original_created_at = task.created_at

        # Update the title
        updated_task = task_manager.update_task(task.id, "Updated title")

        # Verify title was updated
        assert updated_task.title == "Updated title"
        assert task.title == "Updated title"  # Same object

        # Verify other attributes unchanged
        assert updated_task.id == original_id
        assert updated_task.completed == original_completed
        assert updated_task.created_at == original_created_at

        # Verify it's the same object
        assert updated_task is task

    def test_update_task_empty_title_raises_error(self, task_manager):
        """Test that updating with empty title raises ValidationError.

        Verifies that the same title validation rules apply
        when updating as when creating.
        """
        task = task_manager.add_task("Test task")
        original_title = task.title

        # Try to update with empty string
        with pytest.raises(ValidationError) as exc_info:
            task_manager.update_task(task.id, "")

        assert "empty" in str(exc_info.value).lower()

        # Verify title unchanged
        assert task.title == original_title

        # Try with whitespace-only string
        with pytest.raises(ValidationError) as exc_info:
            task_manager.update_task(task.id, "   ")

        assert task.title == original_title

    def test_update_task_not_found_raises_error(self, task_manager):
        """Test that updating non-existent task raises TaskNotFoundError.

        Verifies that update_task validates task existence
        before attempting update.
        """
        task_manager.add_task("Test task")

        # Try to update non-existent task
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_manager.update_task(999, "New title")

        assert "999" in str(exc_info.value)

    def test_update_task_trims_whitespace(self, task_manager):
        """Test that update_task trims whitespace from new title.

        Verifies that whitespace trimming applies to updates
        just as it does to task creation.
        """
        task = task_manager.add_task("Original title")

        # Update with title that has leading/trailing whitespace
        updated_task = task_manager.update_task(task.id, "  New title  ")

        # Verify whitespace was trimmed
        assert updated_task.title == "New title"
        assert task.title == "New title"

    def test_update_task_with_long_title(self, task_manager):
        """Test updating with various title lengths.

        Verifies that title length validation applies to updates.
        """
        task = task_manager.add_task("Short")

        # Update to max length (500 chars)
        long_title = "A" * 500
        updated_task = task_manager.update_task(task.id, long_title)
        assert updated_task.title == long_title

        # Try to update to too long (501 chars)
        too_long_title = "B" * 501
        with pytest.raises(ValidationError) as exc_info:
            task_manager.update_task(task.id, too_long_title)

        assert "too long" in str(exc_info.value).lower()

        # Verify title is still the valid long title
        assert task.title == long_title

    def test_update_task_with_special_characters(self, task_manager):
        """Test updating with special characters and unicode.

        Verifies that update_task handles special characters
        correctly, including unicode.
        """
        task = task_manager.add_task("Simple title")

        # Update with special characters
        special_title = "Buy \"milk\" & 'eggs' @ $5.00"
        updated_task = task_manager.update_task(task.id, special_title)
        assert updated_task.title == special_title

        # Update with unicode
        unicode_title = "Task with emoji 🚀 and unicode café"
        updated_task = task_manager.update_task(task.id, unicode_title)
        assert updated_task.title == unicode_title

    def test_update_task_multiple_times(self, task_manager):
        """Test updating the same task multiple times.

        Verifies that a task can be updated repeatedly
        without issues.
        """
        task = task_manager.add_task("Version 1")
        original_id = task.id

        # Update multiple times
        task_manager.update_task(task.id, "Version 2")
        assert task.title == "Version 2"

        task_manager.update_task(task.id, "Version 3")
        assert task.title == "Version 3"

        task_manager.update_task(task.id, "Final version")
        assert task.title == "Final version"

        # ID should remain unchanged
        assert task.id == original_id

    def test_update_task_does_not_affect_completion(self, task_manager):
        """Test that updating title doesn't change completion status.

        Verifies that update_task only modifies the title,
        not the completion status.
        """
        task = task_manager.add_task("Test task")
        task_manager.mark_complete(task.id, True)
        assert task.completed is True

        # Update title
        task_manager.update_task(task.id, "Updated title")

        # Completion status should remain True
        assert task.completed is True
        assert task.title == "Updated title"

    def test_update_multiple_tasks_independently(self, task_manager):
        """Test updating multiple tasks maintains independence.

        Verifies that updating one task doesn't affect others.
        """
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")

        # Update task2
        task_manager.update_task(task2.id, "Updated Task 2")

        # Verify only task2 was updated
        assert task1.title == "Task 1"
        assert task2.title == "Updated Task 2"
        assert task3.title == "Task 3"

    def test_update_task_returns_task(self, task_manager):
        """Test that update_task returns the updated task object.

        Verifies the return value is the task object with
        updated title.
        """
        task = task_manager.add_task("Original")

        result = task_manager.update_task(task.id, "Updated")

        assert result is task
        assert isinstance(result, Task)
        assert result.title == "Updated"
        assert result.id == task.id


class TestDeleteTask:
    """Tests for TaskManager.delete_task method (User Story 4)."""

    def test_delete_task_success(self, task_manager):
        """Test successfully deleting a task.

        Verifies that delete_task removes the task from storage
        and the task is no longer retrievable.
        """
        # Add some tasks
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")

        # Delete task2
        task_manager.delete_task(task2.id)

        # Verify task2 is gone
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(task2.id)

        # Verify other tasks still exist
        assert task_manager.get_task(task1.id) is task1
        assert task_manager.get_task(task3.id) is task3

        # Verify count is correct
        assert task_manager.count() == 2

    def test_delete_task_not_found_raises_error(self, task_manager):
        """Test that deleting non-existent task raises TaskNotFoundError.

        Verifies that delete_task validates task existence
        before attempting deletion.
        """
        task_manager.add_task("Test task")

        # Try to delete non-existent task
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_manager.delete_task(999)

        assert "999" in str(exc_info.value)

    def test_delete_task_ids_not_reused(self, task_manager):
        """Test that deleted task IDs are never reused.

        Verifies that the ID counter continues incrementing
        even after tasks are deleted.
        """
        # Add 3 tasks (IDs: 1, 2, 3)
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

        # Delete task2
        task_manager.delete_task(2)

        # Add new task - should get ID 4, not 2
        task4 = task_manager.add_task("Task 4")
        assert task4.id == 4

        # Verify ID 2 is not reused
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(2)

    def test_delete_reduces_count(self, task_manager):
        """Test that deleting tasks reduces the count correctly.

        Verifies that count() reflects the number of tasks
        after deletions.
        """
        # Add 5 tasks
        for i in range(1, 6):
            task_manager.add_task(f"Task {i}")

        assert task_manager.count() == 5

        # Delete 2 tasks
        task_manager.delete_task(2)
        assert task_manager.count() == 4

        task_manager.delete_task(4)
        assert task_manager.count() == 3

        # Verify remaining tasks are correct
        remaining = task_manager.get_all_tasks()
        assert len(remaining) == 3
        remaining_ids = [t.id for t in remaining]
        assert sorted(remaining_ids) == [1, 3, 5]

    def test_delete_from_empty_manager(self, task_manager):
        """Test deleting from empty TaskManager raises error."""
        with pytest.raises(TaskNotFoundError):
            task_manager.delete_task(1)

    def test_delete_all_tasks(self, task_manager):
        """Test deleting all tasks results in empty manager.

        Verifies that all tasks can be deleted and the
        manager returns to empty state.
        """
        # Add 3 tasks
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")

        # Delete all
        task_manager.delete_task(task1.id)
        task_manager.delete_task(task2.id)
        task_manager.delete_task(task3.id)

        # Verify empty
        assert task_manager.count() == 0
        assert task_manager.get_all_tasks() == []

    def test_delete_does_not_return_value(self, task_manager):
        """Test that delete_task returns None.

        Verifies the method signature (returns None).
        """
        task = task_manager.add_task("Test task")

        result = task_manager.delete_task(task.id)

        assert result is None

    def test_delete_task_with_completion_status(self, task_manager):
        """Test deleting tasks regardless of completion status.

        Verifies that both complete and incomplete tasks
        can be deleted.
        """
        task1 = task_manager.add_task("Incomplete task")
        task2 = task_manager.add_task("Complete task")
        task_manager.mark_complete(task2.id, True)

        # Delete both
        task_manager.delete_task(task1.id)
        task_manager.delete_task(task2.id)

        # Verify both gone
        assert task_manager.count() == 0

    def test_delete_middle_task(self, task_manager):
        """Test deleting a task from the middle of the collection.

        Verifies that surrounding tasks are unaffected.
        """
        task1 = task_manager.add_task("First")
        task2 = task_manager.add_task("Middle")
        task3 = task_manager.add_task("Last")

        # Delete middle task
        task_manager.delete_task(task2.id)

        # Verify first and last unchanged
        assert task1.title == "First"
        assert task3.title == "Last"
        assert task_manager.count() == 2

    def test_delete_same_task_twice_raises_error(self, task_manager):
        """Test that deleting the same task twice raises error.

        Verifies that the second deletion attempt fails
        with TaskNotFoundError.
        """
        task = task_manager.add_task("Test task")

        # First deletion succeeds
        task_manager.delete_task(task.id)

        # Second deletion fails
        with pytest.raises(TaskNotFoundError):
            task_manager.delete_task(task.id)

    def test_delete_and_add_pattern(self, task_manager):
        """Test alternating delete and add operations.

        Verifies that IDs continue incrementing correctly
        during mixed operations.
        """
        task1 = task_manager.add_task("Task 1")  # ID: 1
        task2 = task_manager.add_task("Task 2")  # ID: 2
        task_manager.delete_task(task1.id)
        task3 = task_manager.add_task("Task 3")  # ID: 3
        task_manager.delete_task(task2.id)
        task4 = task_manager.add_task("Task 4")  # ID: 4

        # Verify IDs
        assert task3.id == 3
        assert task4.id == 4

        # Verify only task3 and task4 exist
        assert task_manager.count() == 2
        remaining = task_manager.get_all_tasks()
        remaining_ids = sorted([t.id for t in remaining])
        assert remaining_ids == [3, 4]


class TestMemoryOnlyStorage:
    """Tests for User Story 5: Memory-only storage with no file persistence.

    These tests verify that:
    - TaskManager uses only in-memory storage
    - No file I/O operations are performed
    - Fresh instances start empty
    - No data persists between separate instances
    """

    def test_fresh_instance_starts_empty(self):
        """Test that a new TaskManager instance starts with no tasks.

        Verifies US5 requirement: new instances have no persisted data.
        """
        manager = TaskManager()

        assert manager.count() == 0
        assert manager.get_all_tasks() == []

    def test_multiple_fresh_instances_independent(self):
        """Test that multiple TaskManager instances are completely independent.

        Verifies US5 requirement: no shared state between instances.
        """
        # Create first instance and add tasks
        manager1 = TaskManager()
        manager1.add_task("Task in manager 1")
        manager1.add_task("Another task in manager 1")

        # Create second instance - should be empty
        manager2 = TaskManager()

        # Verify instances are independent
        assert manager1.count() == 2
        assert manager2.count() == 0

        # Add task to second instance
        manager2.add_task("Task in manager 2")

        # Verify still independent
        assert manager1.count() == 2
        assert manager2.count() == 1

    def test_instance_destruction_loses_data(self):
        """Test that data is lost when TaskManager instance is destroyed.

        Verifies US5 requirement: no persistence between sessions.
        Simulates application restart by creating and destroying instances.
        """
        # Session 1: Create instance, add tasks
        session1 = TaskManager()
        task1 = session1.add_task("Task from session 1")
        task2 = session1.add_task("Another task from session 1")

        # Verify session 1 has data
        assert session1.count() == 2

        # Capture IDs from session 1
        session1_ids = [task1.id, task2.id]

        # Destroy session 1 (simulate application exit)
        del session1

        # Session 2: Create new instance (simulate application restart)
        session2 = TaskManager()

        # Verify session 2 is empty (no persistence)
        assert session2.count() == 0
        assert session2.get_all_tasks() == []

        # Add tasks in session 2
        task3 = session2.add_task("Task from session 2")

        # Verify IDs restart from 1 (new counter)
        assert task3.id == 1

    def test_no_file_operations_in_add_task(self, task_manager, mocker):
        """Test that add_task performs no file I/O operations.

        Verifies US5 requirement: memory-only storage, no file writes.
        """
        # Mock file operations to ensure they're not called
        mock_open = mocker.patch('builtins.open')

        # Add task
        task_manager.add_task("Test task")

        # Verify no file operations occurred
        mock_open.assert_not_called()

    def test_no_file_operations_in_update_task(self, task_manager, mocker):
        """Test that update_task performs no file I/O operations.

        Verifies US5 requirement: memory-only storage, no file writes.
        """
        # Mock file operations to ensure they're not called
        mock_open = mocker.patch('builtins.open')

        # Add and update task
        task = task_manager.add_task("Test task")
        task_manager.update_task(task.id, "Updated task")

        # Verify no file operations occurred
        mock_open.assert_not_called()

    def test_no_file_operations_in_delete_task(self, task_manager, mocker):
        """Test that delete_task performs no file I/O operations.

        Verifies US5 requirement: memory-only storage, no file writes.
        """
        # Mock file operations to ensure they're not called
        mock_open = mocker.patch('builtins.open')

        # Add and delete task
        task = task_manager.add_task("Test task")
        task_manager.delete_task(task.id)

        # Verify no file operations occurred
        mock_open.assert_not_called()

    def test_no_file_operations_in_mark_complete(self, task_manager, mocker):
        """Test that mark_complete performs no file I/O operations.

        Verifies US5 requirement: memory-only storage, no file writes.
        """
        # Mock file operations to ensure they're not called
        mock_open = mocker.patch('builtins.open')

        # Add and mark task complete
        task = task_manager.add_task("Test task")
        task_manager.mark_complete(task.id, True)

        # Verify no file operations occurred
        mock_open.assert_not_called()

    def test_storage_is_dictionary(self, task_manager):
        """Test that internal storage is a dictionary (in-memory).

        Verifies US5 requirement: uses dict for O(1) in-memory lookups.
        """
        # Verify internal storage is a dict
        assert hasattr(task_manager, '_tasks')
        assert isinstance(task_manager._tasks, dict)

        # Add task and verify it's in the dict
        task = task_manager.add_task("Test task")
        assert task.id in task_manager._tasks
        assert task_manager._tasks[task.id] == task

    def test_large_dataset_remains_in_memory(self, task_manager):
        """Test that even large datasets remain in memory only.

        Verifies US5 requirement: all data kept in memory, no spillover to disk.
        """
        # Add many tasks
        task_count = 1000
        for i in range(task_count):
            task_manager.add_task(f"Task {i}")

        # Verify all tasks in memory
        assert task_manager.count() == task_count
        all_tasks = task_manager.get_all_tasks()
        assert len(all_tasks) == task_count

        # Verify all accessible via dict lookup (O(1) operation)
        for i in range(1, task_count + 1):
            task = task_manager.get_task(i)
            assert task.id == i
            assert task.title == f"Task {i - 1}"
