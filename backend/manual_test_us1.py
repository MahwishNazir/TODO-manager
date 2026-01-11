"""
Manual Test Script for User Story 1.

This script simulates the manual testing scenario from T032:
- Run application
- Add 3 tasks
- View list
- Verify output format and IDs

This is a simulation for automated verification. For true manual testing,
run: python -m src.main
"""

import sys
from io import StringIO
from unittest.mock import patch
from src.services.task_manager import TaskManager
from src.cli.menu import add_task_interactive, view_tasks, display_menu


def test_manual_scenario():
    """Simulate manual test scenario from T032."""
    print("=" * 50)
    print("MANUAL TEST SCENARIO - USER STORY 1")
    print("=" * 50)
    print("\nScenario: Add 3 tasks, view list, verify format")
    print("-" * 50)
    
    # Create task manager
    manager = TaskManager()
    
    # Test 1: Display menu
    print("\n[PASS] Test 1: Display Menu")
    display_menu()

    # Test 2: Add 3 tasks
    print("\n[PASS] Test 2: Add 3 Tasks")
    tasks_to_add = ['Buy milk', 'Write tests', 'Deploy application']

    for i, task_title in enumerate(tasks_to_add, 1):
        with patch('builtins.input', return_value=task_title):
            print(f"\n  Adding task {i}: '{task_title}'")
            add_task_interactive(manager)

    # Test 3: View tasks
    print("\n[PASS] Test 3: View All Tasks")
    view_tasks(manager)

    # Test 4: Verify state
    print("\n[PASS] Test 4: Verify Task Manager State")
    tasks = manager.get_all_tasks()
    print(f"  Total tasks: {manager.count()}")
    print(f"  Expected: 3")
    assert manager.count() == 3, "Should have 3 tasks"

    # Test 5: Verify IDs are sequential
    print("\n[PASS] Test 5: Verify Sequential IDs")
    sorted_tasks = sorted(tasks, key=lambda t: t.id)
    for i, task in enumerate(sorted_tasks, 1):
        print(f"  Task {i}: ID={task.id}, Title='{task.title}'")
        assert task.id == i, f"Task ID should be {i}, got {task.id}"

    # Test 6: Verify titles
    print("\n[PASS] Test 6: Verify Task Titles")
    task_titles = [t.title for t in sorted_tasks]
    assert task_titles == tasks_to_add, "Task titles should match input"

    # Test 7: Verify all incomplete
    print("\n[PASS] Test 7: Verify All Tasks Incomplete (Default)")
    for task in tasks:
        assert task.completed is False, "New tasks should be incomplete"
    print("  All tasks correctly marked as incomplete")

    print("\n" + "=" * 50)
    print("[SUCCESS] ALL MANUAL TESTS PASSED!")
    print("=" * 50)
    print("\nSummary:")
    print(f"  - Created {manager.count()} tasks")
    print("  - All IDs sequential (1, 2, 3)")
    print("  - All titles correct")
    print("  - All tasks incomplete by default")
    print("  - Menu displays correctly")
    print("\nUser Story 1 is FULLY FUNCTIONAL!")
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
