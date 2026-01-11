"""
Manual Test Script for User Story 4.

This script simulates the manual testing scenario from T061:
- Create 10 tasks
- Delete tasks 2, 5, 8
- Verify remaining tasks keep original IDs

This is a simulation for automated verification. For true manual testing,
run: python -m src.main
"""

import sys
from unittest.mock import patch
from src.services.task_manager import TaskManager
from src.cli.menu import add_task_interactive, view_tasks, delete_task_interactive


def test_manual_scenario():
    """Simulate manual test scenario from T061."""
    print("=" * 50)
    print("MANUAL TEST SCENARIO - USER STORY 4")
    print("=" * 50)
    print("\nScenario: Create 10 tasks, delete tasks 2, 5, 8,")
    print("verify remaining keep original IDs")
    print("-" * 50)

    # Create task manager
    manager = TaskManager()

    # Test 1: Add 10 tasks
    print("\n[PASS] Test 1: Add 10 Tasks")
    for i in range(1, 11):
        with patch('builtins.input', return_value=f'Task {i}'):
            add_task_interactive(manager)

    assert manager.count() == 10
    print(f"  Created {manager.count()} tasks")

    # Verify all tasks have sequential IDs
    for i in range(1, 11):
        task = manager.get_task(i)
        assert task.id == i
        assert task.title == f'Task {i}'
    print("  All tasks have sequential IDs (1-10)")

    # Test 2: View all tasks
    print("\n[PASS] Test 2: View All 10 Tasks")
    view_tasks(manager)

    # Test 3: Delete task 2
    print("\n[PASS] Test 3: Delete Task 2")
    with patch('builtins.input', return_value='2'):
        delete_task_interactive(manager)

    assert manager.count() == 9
    print("  Task 2 deleted, count now 9")

    # Test 4: Delete task 5
    print("\n[PASS] Test 4: Delete Task 5")
    with patch('builtins.input', return_value='5'):
        delete_task_interactive(manager)

    assert manager.count() == 8
    print("  Task 5 deleted, count now 8")

    # Test 5: Delete task 8
    print("\n[PASS] Test 5: Delete Task 8")
    with patch('builtins.input', return_value='8'):
        delete_task_interactive(manager)

    assert manager.count() == 7
    print("  Task 8 deleted, count now 7")

    # Test 6: Verify remaining tasks
    print("\n[PASS] Test 6: Verify Remaining Tasks Keep Original IDs")
    remaining = manager.get_all_tasks()
    remaining_ids = sorted([t.id for t in remaining])
    expected_ids = [1, 3, 4, 6, 7, 9, 10]

    assert remaining_ids == expected_ids
    print(f"  Remaining IDs: {remaining_ids}")
    print(f"  Expected IDs:  {expected_ids}")
    print("  IDs match! Tasks keep original IDs after deletion")

    # Test 7: Verify task titles unchanged
    print("\n[PASS] Test 7: Verify Task Titles Unchanged")
    for task_id in expected_ids:
        task = manager.get_task(task_id)
        assert task.title == f'Task {task_id}'
        print(f"  Task {task_id}: '{task.title}' - Correct!")

    # Test 8: View remaining tasks
    print("\n[PASS] Test 8: View Remaining Tasks")
    view_tasks(manager)

    # Test 9: Add new task - should get ID 11, not reuse deleted IDs
    print("\n[PASS] Test 9: Add New Task (ID Should Be 11)")
    with patch('builtins.input', return_value='Task 11'):
        add_task_interactive(manager)

    new_task = manager.get_task(11)
    assert new_task.id == 11
    assert new_task.title == 'Task 11'
    print(f"  New task ID: {new_task.id} (not 2, 5, or 8)")
    print("  Deleted IDs are NOT reused - Correct!")

    # Test 10: Verify final state
    print("\n[PASS] Test 10: Verify Final State")
    assert manager.count() == 8
    final_ids = sorted([t.id for t in manager.get_all_tasks()])
    assert final_ids == [1, 3, 4, 6, 7, 9, 10, 11]
    print(f"  Final task count: {manager.count()}")
    print(f"  Final IDs: {final_ids}")

    # Test 11: Delete all remaining tasks
    print("\n[PASS] Test 11: Delete All Remaining Tasks")
    for task_id in final_ids:
        with patch('builtins.input', return_value=str(task_id)):
            delete_task_interactive(manager)

    assert manager.count() == 0
    print("  All tasks deleted successfully")

    # Test 12: Verify empty state
    print("\n[PASS] Test 12: Verify Empty State")
    view_tasks(manager)
    assert manager.get_all_tasks() == []
    print("  Task list is empty")

    print("\n" + "=" * 50)
    print("[SUCCESS] ALL MANUAL TESTS PASSED!")
    print("=" * 50)
    print("\nSummary:")
    print("  - Created 10 tasks with sequential IDs")
    print("  - Deleted tasks 2, 5, 8")
    print("  - Remaining tasks kept original IDs (1,3,4,6,7,9,10)")
    print("  - Deleted IDs NOT reused (new task got ID 11)")
    print("  - Successfully deleted all tasks to empty state")
    print("  - View correctly shows remaining tasks")
    print("\nUser Story 4 is FULLY FUNCTIONAL!")
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
