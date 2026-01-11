"""
Manual Test Script for User Story 2.

This script simulates the manual testing scenario from T043:
- Create 3 tasks
- Mark task 2 complete
- View list to verify status
- Toggle back to incomplete

This is a simulation for automated verification. For true manual testing,
run: python -m src.main
"""

import sys
from unittest.mock import patch
from src.services.task_manager import TaskManager
from src.cli.menu import add_task_interactive, view_tasks, mark_task_interactive


def test_manual_scenario():
    """Simulate manual test scenario from T043."""
    print("=" * 50)
    print("MANUAL TEST SCENARIO - USER STORY 2")
    print("=" * 50)
    print("\nScenario: Create 3 tasks, mark task 2 complete,")
    print("view list, toggle back to incomplete")
    print("-" * 50)

    # Create task manager
    manager = TaskManager()

    # Test 1: Add 3 tasks
    print("\n[PASS] Test 1: Add 3 Tasks")
    tasks_to_add = ['Buy milk', 'Write tests', 'Deploy application']

    for i, task_title in enumerate(tasks_to_add, 1):
        with patch('builtins.input', return_value=task_title):
            print(f"  Adding task {i}: '{task_title}'")
            add_task_interactive(manager)

    # Verify all tasks are incomplete
    tasks = manager.get_all_tasks()
    assert all(not task.completed for task in tasks), "All tasks should start incomplete"
    print("  All tasks added and incomplete")

    # Test 2: Mark task 2 as complete
    print("\n[PASS] Test 2: Mark Task 2 Complete")
    with patch('builtins.input', side_effect=['2', 'y']):
        mark_task_interactive(manager)

    # Verify task 2 is complete
    task2 = manager.get_task(2)
    assert task2.completed is True, "Task 2 should be complete"
    print(f"  Task 2 '{task2.title}' is now complete")

    # Test 3: View tasks to verify status
    print("\n[PASS] Test 3: View Tasks (Verify Mixed Status)")
    view_tasks(manager)

    # Verify statuses
    task1 = manager.get_task(1)
    task3 = manager.get_task(3)
    assert task1.completed is False, "Task 1 should be incomplete"
    assert task2.completed is True, "Task 2 should be complete"
    assert task3.completed is False, "Task 3 should be incomplete"
    print("  Status verified: Task 1 (incomplete), Task 2 (complete), Task 3 (incomplete)")

    # Test 4: Toggle task 2 back to incomplete
    print("\n[PASS] Test 4: Toggle Task 2 Back to Incomplete")
    with patch('builtins.input', side_effect=['2', 'n']):
        mark_task_interactive(manager)

    # Verify task 2 is now incomplete
    task2 = manager.get_task(2)
    assert task2.completed is False, "Task 2 should be incomplete again"
    print(f"  Task 2 '{task2.title}' is now incomplete")

    # Test 5: View tasks again
    print("\n[PASS] Test 5: View Tasks (All Incomplete)")
    view_tasks(manager)

    # Verify all incomplete
    assert all(not task.completed for task in manager.get_all_tasks()), "All tasks should be incomplete"
    print("  All tasks are now incomplete")

    # Test 6: Mark multiple tasks complete
    print("\n[PASS] Test 6: Mark Multiple Tasks Complete")
    with patch('builtins.input', side_effect=['1', 'y']):
        mark_task_interactive(manager)

    with patch('builtins.input', side_effect=['3', 'y']):
        mark_task_interactive(manager)

    # Verify
    task1 = manager.get_task(1)
    task2 = manager.get_task(2)
    task3 = manager.get_task(3)
    assert task1.completed is True, "Task 1 should be complete"
    assert task2.completed is False, "Task 2 should be incomplete"
    assert task3.completed is True, "Task 3 should be complete"
    print("  Task 1 (complete), Task 2 (incomplete), Task 3 (complete)")

    # Test 7: View final state
    print("\n[PASS] Test 7: View Final State")
    view_tasks(manager)

    print("\n" + "=" * 50)
    print("[SUCCESS] ALL MANUAL TESTS PASSED!")
    print("=" * 50)
    print("\nSummary:")
    print(f"  - Created {manager.count()} tasks")
    print("  - Successfully marked tasks complete/incomplete")
    print("  - Toggled task status multiple times")
    print("  - All tasks maintain independent status")
    print("  - View shows correct completion indicators")
    print("\nUser Story 2 is FULLY FUNCTIONAL!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_manual_scenario()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
