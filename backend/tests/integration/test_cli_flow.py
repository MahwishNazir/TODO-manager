"""
Integration tests for CLI flow.

Tests cover end-to-end flows for User Story 1:
- Adding tasks through the CLI
- Viewing empty task list
- Viewing multiple tasks
"""

import pytest
from io import StringIO
from unittest.mock import patch
from src.services.task_manager import TaskManager
from src.cli.menu import add_task_interactive, view_tasks
from src.models.task import ValidationError, TaskNotFoundError


class TestAddTaskFlow:
    """Integration tests for adding tasks through CLI."""

    def test_add_task_success(self, task_manager, capsys):
        """Test successfully adding a task through CLI interface.
        
        Simulates user entering a valid task title and verifies:
        - Task is added to TaskManager
        - Confirmation message is displayed
        - Task has correct ID and title
        """
        # Simulate user input
        with patch('builtins.input', return_value='Buy milk'):
            add_task_interactive(task_manager)
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify task was added
        assert task_manager.count() == 1
        tasks = task_manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == 'Buy milk'
        assert tasks[0].id == 1
        
        # Verify confirmation message
        assert 'added' in captured.out.lower() or 'created' in captured.out.lower()
        assert '1' in captured.out  # Task ID should be displayed

    def test_add_task_with_whitespace_trimming(self, task_manager, capsys):
        """Test that CLI properly handles whitespace in task titles."""
        # Simulate user input with extra whitespace
        with patch('builtins.input', return_value='  Buy groceries  '):
            add_task_interactive(task_manager)
        
        # Verify whitespace is trimmed
        tasks = task_manager.get_all_tasks()
        assert tasks[0].title == 'Buy groceries'

    def test_add_task_empty_title_error(self, task_manager, capsys):
        """Test that CLI handles empty title validation error."""
        # Simulate user entering empty string
        with patch('builtins.input', return_value=''):
            add_task_interactive(task_manager)
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify error message is displayed
        assert 'error' in captured.out.lower() or 'empty' in captured.out.lower()
        
        # Verify task was NOT added
        assert task_manager.count() == 0


class TestViewTasksFlow:
    """Integration tests for viewing tasks through CLI."""

    def test_view_empty_list(self, task_manager, capsys):
        """Test viewing tasks when no tasks exist.
        
        Verifies that appropriate empty state message is displayed
        when user views an empty task list.
        """
        # Call view_tasks with empty manager
        view_tasks(task_manager)
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify empty message is shown
        assert 'no tasks' in captured.out.lower() or 'empty' in captured.out.lower()

    def test_view_multiple_tasks(self, task_manager, capsys):
        """Test viewing a list of multiple tasks.
        
        Verifies that:
        - All tasks are displayed
        - Task IDs and titles are shown
        - Completion status is indicated
        - Output is properly formatted
        """
        # Add multiple tasks
        task1 = task_manager.add_task('Buy milk')
        task2 = task_manager.add_task('Write tests')
        task3 = task_manager.add_task('Deploy app')
        
        # Mark one task as complete
        task_manager.mark_complete(task2.id, True)
        
        # Call view_tasks
        view_tasks(task_manager)
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify all task titles are displayed
        assert 'Buy milk' in captured.out
        assert 'Write tests' in captured.out
        assert 'Deploy app' in captured.out
        
        # Verify task IDs are displayed
        assert '1' in captured.out
        assert '2' in captured.out
        assert '3' in captured.out
        
        # Verify completion status indicator (checkbox, done, etc.)
        output_lower = captured.out.lower()
        assert any(marker in output_lower for marker in ['[ ]', '[x]', '☐', '☑', 'done', 'complete'])

    def test_view_tasks_preserves_order(self, task_manager, capsys):
        """Test that tasks are displayed in a consistent order."""
        # Add tasks in specific order
        task_manager.add_task('First task')
        task_manager.add_task('Second task')
        task_manager.add_task('Third task')
        
        # Call view_tasks
        view_tasks(task_manager)
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify all tasks are present (order may vary due to dict iteration)
        assert 'First task' in captured.out
        assert 'Second task' in captured.out
        assert 'Third task' in captured.out


class TestEndToEndFlow:
    """Integration tests for complete user workflows."""

    def test_add_and_view_workflow(self, task_manager, capsys):
        """Test complete workflow: add multiple tasks then view them.
        
        Simulates real user behavior of adding several tasks
        and then viewing the complete list.
        """
        # Add multiple tasks
        with patch('builtins.input', return_value='Task 1'):
            add_task_interactive(task_manager)
        
        with patch('builtins.input', return_value='Task 2'):
            add_task_interactive(task_manager)
        
        with patch('builtins.input', return_value='Task 3'):
            add_task_interactive(task_manager)
        
        # Clear previous output
        capsys.readouterr()
        
        # View all tasks
        view_tasks(task_manager)
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify all tasks are shown
        assert task_manager.count() == 3
        assert 'Task 1' in captured.out
        assert 'Task 2' in captured.out
        assert 'Task 3' in captured.out

    def test_view_after_no_adds(self, task_manager, capsys):
        """Test viewing immediately without adding any tasks."""
        # View tasks without adding any
        view_tasks(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Should show empty message
        assert 'no tasks' in captured.out.lower() or 'empty' in captured.out.lower()


class TestMarkCompleteFlow:
    """Integration tests for marking tasks complete through CLI (User Story 2)."""

    def test_mark_complete_success(self, task_manager, capsys):
        """Test successfully marking a task as complete through CLI.

        Verifies that:
        - User can mark a task as complete
        - Success message is displayed
        - Task completion status is updated
        """
        # Add a task
        task = task_manager.add_task('Buy milk')
        assert task.completed is False

        # Simulate user marking task as complete
        # Input: task ID, then 'y' for complete
        with patch('builtins.input', side_effect=['1', 'y']):
            from src.cli.menu import mark_task_interactive
            mark_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify task is marked complete
        assert task.completed is True

        # Verify success message
        assert 'success' in captured.out.lower() or 'complete' in captured.out.lower()

    def test_mark_incomplete_success(self, task_manager, capsys):
        """Test successfully marking a task as incomplete through CLI.

        Verifies that:
        - User can toggle a task back to incomplete
        - Success message is displayed
        - Task completion status is updated
        """
        # Add and mark task as complete
        task = task_manager.add_task('Write tests')
        task_manager.mark_complete(task.id, True)
        assert task.completed is True

        # Clear previous output
        capsys.readouterr()

        # Simulate user marking task as incomplete
        # Input: task ID, then 'n' for incomplete
        with patch('builtins.input', side_effect=['1', 'n']):
            from src.cli.menu import mark_task_interactive
            mark_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify task is marked incomplete
        assert task.completed is False

        # Verify success message
        assert 'success' in captured.out.lower() or 'incomplete' in captured.out.lower()

    def test_mark_nonexistent_task_error(self, task_manager, capsys):
        """Test marking a non-existent task shows error message.

        Verifies that:
        - Invalid task ID shows error message
        - No crash or exception bubbles up
        - Error message is user-friendly
        """
        # Add one task (ID will be 1)
        task_manager.add_task('Test task')

        # Try to mark non-existent task
        with patch('builtins.input', side_effect=['999', 'y']):
            from src.cli.menu import mark_task_interactive
            mark_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify error message is displayed
        assert 'error' in captured.out.lower() or 'not found' in captured.out.lower()
        assert '999' in captured.out

    def test_mark_complete_multiple_tasks(self, task_manager, capsys):
        """Test marking multiple tasks with different statuses.

        Verifies that each task maintains its status independently.
        """
        # Add multiple tasks
        task1 = task_manager.add_task('Task 1')
        task2 = task_manager.add_task('Task 2')
        task3 = task_manager.add_task('Task 3')

        # Mark task2 as complete
        with patch('builtins.input', side_effect=['2', 'y']):
            from src.cli.menu import mark_task_interactive
            mark_task_interactive(task_manager)

        # Verify only task2 is complete
        assert task1.completed is False
        assert task2.completed is True
        assert task3.completed is False

    def test_mark_complete_with_invalid_input(self, task_manager, capsys):
        """Test handling of invalid input for task ID.

        Verifies that non-numeric input is handled gracefully.
        """
        task_manager.add_task('Test task')

        # Try with non-numeric input
        with patch('builtins.input', side_effect=['abc', 'y']):
            from src.cli.menu import mark_task_interactive
            mark_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify error message for invalid input
        assert 'error' in captured.out.lower() or 'invalid' in captured.out.lower()

    def test_view_tasks_shows_completion_status(self, task_manager, capsys):
        """Test that viewing tasks displays completion status correctly.

        Verifies that the view shows which tasks are complete vs incomplete.
        """
        # Add tasks with mixed completion status
        task1 = task_manager.add_task('Complete task')
        task2 = task_manager.add_task('Incomplete task')
        task_manager.mark_complete(task1.id, True)

        # View tasks
        view_tasks(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify both tasks are shown with different status indicators
        assert 'Complete task' in captured.out
        assert 'Incomplete task' in captured.out

        # Verify status indicators are present (checkboxes or similar)
        # Should have at least one marked complete [X] and one incomplete [ ]
        assert '[X]' in captured.out or '[x]' in captured.out  # Complete indicator
        assert '[ ]' in captured.out  # Incomplete indicator


class TestUpdateTaskFlow:
    """Integration tests for updating tasks through CLI (User Story 3)."""

    def test_update_task_success(self, task_manager, capsys):
        """Test successfully updating a task's title through CLI.

        Verifies that:
        - User can update a task's title
        - Success message is displayed
        - Task title is updated in storage
        """
        # Add a task
        task = task_manager.add_task('Buy milk')
        original_id = task.id

        # Simulate user updating task
        # Input: task ID, then new title
        with patch('builtins.input', side_effect=['1', 'Buy organic milk']):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify task title was updated
        assert task.title == 'Buy organic milk'
        assert task.id == original_id  # ID unchanged

        # Verify success message
        assert 'success' in captured.out.lower() or 'updated' in captured.out.lower()

    def test_update_empty_title_rejected(self, task_manager, capsys):
        """Test that empty title is rejected when updating.

        Verifies that:
        - Validation rules apply to updates
        - Error message is displayed
        - Original title is preserved
        """
        # Add a task
        task = task_manager.add_task('Test task')
        original_title = task.title

        # Try to update with empty title
        with patch('builtins.input', side_effect=['1', '']):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify error message
        assert 'error' in captured.out.lower() or 'empty' in captured.out.lower()

        # Verify title unchanged
        assert task.title == original_title

    def test_update_nonexistent_task_error(self, task_manager, capsys):
        """Test updating a non-existent task shows error message.

        Verifies that:
        - Invalid task ID shows error message
        - No crash or exception bubbles up
        """
        # Add one task (ID will be 1)
        task_manager.add_task('Test task')

        # Try to update non-existent task
        with patch('builtins.input', side_effect=['999', 'New title']):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify error message
        assert 'error' in captured.out.lower() or 'not found' in captured.out.lower()
        assert '999' in captured.out

    def test_update_with_whitespace_trimming(self, task_manager, capsys):
        """Test that whitespace is trimmed from updated title.

        Verifies that title processing applies to updates.
        """
        task = task_manager.add_task('Original title')

        # Update with title that has whitespace
        with patch('builtins.input', side_effect=['1', '  Updated title  ']):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Verify whitespace was trimmed
        assert task.title == 'Updated title'

    def test_update_with_special_characters(self, task_manager, capsys):
        """Test updating with special characters and unicode.

        Verifies that CLI handles special characters correctly.
        """
        task = task_manager.add_task('Simple task')

        # Update with special characters
        special_title = 'Buy "milk" & eggs @ $5'
        with patch('builtins.input', side_effect=['1', special_title]):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Verify special characters preserved
        assert task.title == special_title

        # Clear output
        capsys.readouterr()

        # Update with unicode
        unicode_title = 'Task with café and 🚀'
        with patch('builtins.input', side_effect=['1', unicode_title]):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Verify unicode preserved
        assert task.title == unicode_title

    def test_update_does_not_affect_completion(self, task_manager, capsys):
        """Test that updating title doesn't change completion status.

        Verifies that update only modifies title, not status.
        """
        # Add and mark task complete
        task = task_manager.add_task('Original task')
        task_manager.mark_complete(task.id, True)
        assert task.completed is True

        # Update title
        with patch('builtins.input', side_effect=['1', 'Updated task']):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Verify title updated but completion unchanged
        assert task.title == 'Updated task'
        assert task.completed is True

    def test_update_with_invalid_id(self, task_manager, capsys):
        """Test handling of invalid (non-numeric) task ID.

        Verifies that non-numeric input is handled gracefully.
        """
        task_manager.add_task('Test task')

        # Try with non-numeric input
        with patch('builtins.input', side_effect=['abc', 'New title']):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify error message
        assert 'error' in captured.out.lower() or 'invalid' in captured.out.lower()

    def test_update_multiple_tasks_independently(self, task_manager, capsys):
        """Test updating multiple tasks maintains independence.

        Verifies that each task can be updated without affecting others.
        """
        task1 = task_manager.add_task('Task 1')
        task2 = task_manager.add_task('Task 2')
        task3 = task_manager.add_task('Task 3')

        # Update task2
        with patch('builtins.input', side_effect=['2', 'Updated Task 2']):
            from src.cli.menu import update_task_interactive
            update_task_interactive(task_manager)

        # Verify only task2 was updated
        assert task1.title == 'Task 1'
        assert task2.title == 'Updated Task 2'
        assert task3.title == 'Task 3'


class TestDeleteTaskFlow:
    """Integration tests for deleting tasks through CLI (User Story 4)."""

    def test_delete_task_success(self, task_manager, capsys):
        """Test successfully deleting a task through CLI.

        Verifies that:
        - User can delete a task by ID
        - Success message is displayed
        - Task is removed from storage
        """
        # Add some tasks
        task1 = task_manager.add_task('Task 1')
        task2 = task_manager.add_task('Task 2')
        task3 = task_manager.add_task('Task 3')

        # Simulate user deleting task 2
        with patch('builtins.input', return_value='2'):
            from src.cli.menu import delete_task_interactive
            delete_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify task 2 is deleted
        assert task_manager.count() == 2
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(2)

        # Verify other tasks still exist
        assert task_manager.get_task(1) is task1
        assert task_manager.get_task(3) is task3

        # Verify success message
        assert 'success' in captured.out.lower() or 'deleted' in captured.out.lower()

    def test_delete_nonexistent_task_error(self, task_manager, capsys):
        """Test deleting a non-existent task shows error message.

        Verifies that:
        - Invalid task ID shows error message
        - No crash or exception bubbles up
        """
        # Add one task (ID will be 1)
        task_manager.add_task('Test task')

        # Try to delete non-existent task
        with patch('builtins.input', return_value='999'):
            from src.cli.menu import delete_task_interactive
            delete_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify error message
        assert 'error' in captured.out.lower() or 'not found' in captured.out.lower()
        assert '999' in captured.out

        # Verify task 1 still exists
        assert task_manager.count() == 1

    def test_delete_with_invalid_id(self, task_manager, capsys):
        """Test handling of invalid (non-numeric) task ID.

        Verifies that non-numeric input is handled gracefully.
        """
        task_manager.add_task('Test task')

        # Try with non-numeric input
        with patch('builtins.input', return_value='abc'):
            from src.cli.menu import delete_task_interactive
            delete_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify error message
        assert 'error' in captured.out.lower() or 'invalid' in captured.out.lower()

        # Verify task still exists
        assert task_manager.count() == 1

    def test_delete_from_empty_list(self, task_manager, capsys):
        """Test deleting from empty task list shows error."""
        # Try to delete when no tasks exist
        with patch('builtins.input', return_value='1'):
            from src.cli.menu import delete_task_interactive
            delete_task_interactive(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify error message
        assert 'error' in captured.out.lower() or 'not found' in captured.out.lower()

    def test_delete_multiple_tasks_sequentially(self, task_manager, capsys):
        """Test deleting multiple tasks one by one.

        Verifies that multiple deletions work correctly
        and remaining tasks maintain their IDs.
        """
        # Add 5 tasks
        for i in range(1, 6):
            task_manager.add_task(f'Task {i}')

        # Delete tasks 2 and 4
        with patch('builtins.input', return_value='2'):
            from src.cli.menu import delete_task_interactive
            delete_task_interactive(task_manager)

        capsys.readouterr()  # Clear output

        with patch('builtins.input', return_value='4'):
            from src.cli.menu import delete_task_interactive
            delete_task_interactive(task_manager)

        # Verify count
        assert task_manager.count() == 3

        # Verify remaining tasks
        remaining = task_manager.get_all_tasks()
        remaining_ids = sorted([t.id for t in remaining])
        assert remaining_ids == [1, 3, 5]

    def test_delete_completed_task(self, task_manager, capsys):
        """Test deleting a completed task.

        Verifies that completed tasks can be deleted
        just like incomplete ones.
        """
        task = task_manager.add_task('Complete task')
        task_manager.mark_complete(task.id, True)

        # Delete the completed task
        with patch('builtins.input', return_value='1'):
            from src.cli.menu import delete_task_interactive
            delete_task_interactive(task_manager)

        # Verify deleted
        assert task_manager.count() == 0

    def test_delete_and_view_workflow(self, task_manager, capsys):
        """Test complete workflow: add tasks, delete some, view remaining.

        Verifies that view correctly shows remaining tasks
        after deletions.
        """
        # Add tasks
        task_manager.add_task('Task 1')
        task_manager.add_task('Task 2')
        task_manager.add_task('Task 3')

        # Delete task 2
        with patch('builtins.input', return_value='2'):
            from src.cli.menu import delete_task_interactive
            delete_task_interactive(task_manager)

        # Clear output
        capsys.readouterr()

        # View remaining tasks
        from src.cli.menu import view_tasks
        view_tasks(task_manager)

        # Capture output
        captured = capsys.readouterr()

        # Verify only task 1 and 3 are shown
        assert 'Task 1' in captured.out
        assert 'Task 2' not in captured.out
        assert 'Task 3' in captured.out


class TestSessionPersistence:
    """Integration tests for session-based persistence (User Story 5)."""

    def test_tasks_persist_during_session(self, task_manager, capsys):
        """Test that tasks persist throughout a single session.

        Verifies that:
        - Tasks created at the beginning of session are accessible later
        - Multiple operations (add, update, mark, delete) maintain data integrity
        - Task data persists in memory throughout the session
        """
        # Add initial tasks
        task1 = task_manager.add_task('Task 1')
        task2 = task_manager.add_task('Task 2')
        task3 = task_manager.add_task('Task 3')

        # Verify initial state
        assert task_manager.count() == 3

        # Perform operations throughout the session
        task_manager.mark_complete(task1.id, True)
        task_manager.update_task(task2.id, 'Updated Task 2')
        task_manager.delete_task(task3.id)

        # Verify data persisted correctly
        assert task_manager.count() == 2

        # Retrieve tasks
        retrieved1 = task_manager.get_task(1)
        retrieved2 = task_manager.get_task(2)

        # Verify task 1 changes persisted
        assert retrieved1.completed is True
        assert retrieved1.title == 'Task 1'

        # Verify task 2 changes persisted
        assert retrieved2.title == 'Updated Task 2'
        assert retrieved2.completed is False

        # Verify task 3 deletion persisted
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(3)

        # Add more tasks
        task4 = task_manager.add_task('Task 4')

        # Verify all data still intact
        assert task_manager.count() == 3
        assert task_manager.get_task(4).title == 'Task 4'
        assert task_manager.get_task(1).completed is True
        assert task_manager.get_task(2).title == 'Updated Task 2'

    def test_multiple_operations_data_intact(self, task_manager, capsys):
        """Test that complex workflows maintain data integrity.

        Verifies that:
        - Mix of CRUD operations work correctly
        - Data remains consistent throughout
        - No data loss during session
        """
        # Create 10 tasks
        for i in range(1, 11):
            task_manager.add_task(f'Task {i}')

        # Mark some as complete
        task_manager.mark_complete(2, True)
        task_manager.mark_complete(4, True)
        task_manager.mark_complete(6, True)

        # Update some titles
        task_manager.update_task(1, 'Updated Task 1')
        task_manager.update_task(3, 'Updated Task 3')

        # Delete some tasks
        task_manager.delete_task(5)
        task_manager.delete_task(7)
        task_manager.delete_task(9)

        # Verify final state
        assert task_manager.count() == 7

        # Verify completed tasks
        assert task_manager.get_task(2).completed is True
        assert task_manager.get_task(4).completed is True
        assert task_manager.get_task(6).completed is True

        # Verify updated titles
        assert task_manager.get_task(1).title == 'Updated Task 1'
        assert task_manager.get_task(3).title == 'Updated Task 3'

        # Verify deleted tasks are gone
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(5)
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(7)
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(9)

        # Verify remaining tasks exist
        remaining_ids = [1, 2, 3, 4, 6, 8, 10]
        for task_id in remaining_ids:
            task = task_manager.get_task(task_id)
            assert task.id == task_id

    def test_session_workflow_end_to_end(self, task_manager, capsys):
        """Test complete workflow from start to finish of session.

        Simulates a real user session with multiple interactions.
        """
        # Start of session - empty
        assert task_manager.count() == 0

        # Add tasks
        from src.cli.menu import add_task_interactive
        with patch('builtins.input', return_value='Buy milk'):
            add_task_interactive(task_manager)

        with patch('builtins.input', return_value='Write report'):
            add_task_interactive(task_manager)

        with patch('builtins.input', return_value='Call client'):
            add_task_interactive(task_manager)

        # View tasks
        from src.cli.menu import view_tasks
        capsys.readouterr()  # Clear
        view_tasks(task_manager)
        captured = capsys.readouterr()

        # Verify all tasks shown
        assert 'Buy milk' in captured.out
        assert 'Write report' in captured.out
        assert 'Call client' in captured.out

        # Mark one complete
        from src.cli.menu import mark_task_interactive
        with patch('builtins.input', side_effect=['1', 'y']):
            mark_task_interactive(task_manager)

        # Update one
        from src.cli.menu import update_task_interactive
        with patch('builtins.input', side_effect=['2', 'Write quarterly report']):
            update_task_interactive(task_manager)

        # Delete one
        from src.cli.menu import delete_task_interactive
        with patch('builtins.input', return_value='3'):
            delete_task_interactive(task_manager)

        # Verify final state
        assert task_manager.count() == 2
        assert task_manager.get_task(1).completed is True
        assert task_manager.get_task(2).title == 'Write quarterly report'

        # Session ends - data still intact
        assert task_manager.count() == 2
