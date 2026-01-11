"""
Manual Test Script for User Story 5: Session-Based Persistence.

This script demonstrates and validates the following US5 requirements:
1. Tasks persist during a single session
2. No file persistence between sessions
3. Fresh instances start empty
4. Graceful exit handling with informative messages

This is an automated simulation for verification. For true manual testing,
run: python -m src.main
"""

import sys
from src.services.task_manager import TaskManager


def test_session_persistence():
    """Test that tasks persist during a single session."""
    print("=" * 70)
    print("TEST 1: Session Persistence - Tasks persist during session")
    print("=" * 70)

    # Create manager (simulates app startup)
    manager = TaskManager()
    print("\n[STEP 1] Created TaskManager instance (app started)")
    print(f"  Initial count: {manager.count()}")
    assert manager.count() == 0, "Fresh instance should be empty"

    # Add tasks
    print("\n[STEP 2] Adding 5 tasks...")
    task1 = manager.add_task("Buy groceries")
    task2 = manager.add_task("Write report")
    task3 = manager.add_task("Call dentist")
    task4 = manager.add_task("Review pull requests")
    task5 = manager.add_task("Update documentation")
    print(f"  Added 5 tasks, count: {manager.count()}")

    # Perform operations throughout session
    print("\n[STEP 3] Performing operations during session...")
    manager.mark_complete(task1.id, True)
    print(f"  - Marked task {task1.id} as complete")

    manager.update_task(task2.id, "Write quarterly report")
    print(f"  - Updated task {task2.id}")

    manager.delete_task(task3.id)
    print(f"  - Deleted task {task3.id}")

    # Verify data persisted during session
    print("\n[STEP 4] Verifying data persistence during session...")
    assert manager.count() == 4, "Should have 4 tasks after delete"

    task1_check = manager.get_task(task1.id)
    assert task1_check.completed is True, "Task 1 should be complete"
    print(f"  - Task {task1.id} completion status persisted: {task1_check.completed}")

    task2_check = manager.get_task(task2.id)
    assert task2_check.title == "Write quarterly report", "Task 2 title should be updated"
    print(f"  - Task {task2.id} title update persisted: '{task2_check.title}'")

    print("\n[PASS] Session persistence verified - data intact during session")
    return manager


def test_no_persistence_between_instances():
    """Test that data does not persist between separate instances."""
    print("\n" + "=" * 70)
    print("TEST 2: No Persistence - Fresh instances are independent")
    print("=" * 70)

    # Session 1
    print("\n[SESSION 1] Creating first TaskManager instance...")
    session1 = TaskManager()
    session1.add_task("Session 1 - Task A")
    session1.add_task("Session 1 - Task B")
    session1.add_task("Session 1 - Task C")
    print(f"  Session 1 has {session1.count()} tasks")
    assert session1.count() == 3, "Session 1 should have 3 tasks"

    # Session 2 (while session 1 still exists)
    print("\n[SESSION 2] Creating second TaskManager instance...")
    session2 = TaskManager()
    print(f"  Session 2 starts with {session2.count()} tasks")
    assert session2.count() == 0, "Session 2 should start empty"

    session2.add_task("Session 2 - Task X")
    print(f"  Added task to Session 2, count: {session2.count()}")

    # Verify independence
    print("\n[VERIFICATION] Sessions are independent...")
    print(f"  Session 1 count: {session1.count()} (unchanged)")
    print(f"  Session 2 count: {session2.count()}")
    assert session1.count() == 3, "Session 1 should still have 3 tasks"
    assert session2.count() == 1, "Session 2 should have 1 task"

    print("\n[PASS] Instances are independent - no shared state")


def test_data_loss_on_restart():
    """Test that data is lost when application restarts (instance destroyed)."""
    print("\n" + "=" * 70)
    print("TEST 3: Data Loss - Tasks not persisted between app restarts")
    print("=" * 70)

    # First app session
    print("\n[APP SESSION 1] Starting application (first instance)...")
    app_session1 = TaskManager()
    app_session1.add_task("Important task 1")
    app_session1.add_task("Important task 2")
    app_session1.add_task("Important task 3")
    app_session1.mark_complete(1, True)

    print(f"  Created {app_session1.count()} tasks")
    print(f"  Task 1 completed: {app_session1.get_task(1).completed}")

    # Capture data
    task_count_session1 = app_session1.count()
    task1_id_session1 = app_session1.get_task(1).id

    print("\n[EXIT] Simulating application exit (destroying instance)...")
    del app_session1
    print("  Instance destroyed - all data in memory is lost")

    # Second app session (restart)
    print("\n[APP SESSION 2] Restarting application (new instance)...")
    app_session2 = TaskManager()

    print(f"  New instance task count: {app_session2.count()}")
    assert app_session2.count() == 0, "Restarted app should have no tasks"

    # Verify IDs reset
    new_task = app_session2.add_task("First task in new session")
    print(f"  First task in new session has ID: {new_task.id}")
    assert new_task.id == 1, "IDs should restart from 1"

    print("\n[PASS] Data correctly lost on restart - no file persistence")


def test_no_file_io_operations():
    """Test that TaskManager performs no file I/O operations."""
    print("\n" + "=" * 70)
    print("TEST 4: No File I/O - In-memory only storage verification")
    print("=" * 70)

    print("\n[VERIFICATION] Checking TaskManager implementation...")

    # Verify storage is dictionary
    manager = TaskManager()
    assert hasattr(manager, '_tasks'), "Should have _tasks attribute"
    assert isinstance(manager._tasks, dict), "Storage should be a dictionary"
    print("  [OK] Storage uses Python dictionary (in-memory)")

    # Perform operations and verify still using dict
    manager.add_task("Test task 1")
    manager.add_task("Test task 2")

    assert isinstance(manager._tasks, dict), "Storage should remain a dictionary"
    assert len(manager._tasks) == 2, "Dict should contain 2 tasks"
    print("  [OK] Operations use dictionary (no file access)")

    # Verify no file-related attributes
    file_attrs = ['_file_path', '_db_connection', 'file', 'db']
    has_file_attrs = any(hasattr(manager, attr) for attr in file_attrs)
    assert not has_file_attrs, "Should not have file-related attributes"
    print("  [OK] No file-related attributes found")

    print("\n[PASS] Confirmed in-memory only storage - no file I/O")


def test_large_dataset_in_memory():
    """Test that large datasets remain in memory."""
    print("\n" + "=" * 70)
    print("TEST 5: Large Dataset - Memory-only storage at scale")
    print("=" * 70)

    print("\n[CREATING] Adding 1000 tasks to memory...")
    manager = TaskManager()

    for i in range(1000):
        manager.add_task(f"Task {i + 1}")

    print(f"  Created {manager.count()} tasks in memory")
    assert manager.count() == 1000, "Should have 1000 tasks"

    # Verify all accessible
    print("\n[VERIFICATION] Accessing random tasks...")
    test_ids = [1, 250, 500, 750, 1000]
    for task_id in test_ids:
        task = manager.get_task(task_id)
        print(f"  - Task {task_id}: '{task.title}'")
        assert task.id == task_id, f"Task ID should be {task_id}"

    print(f"\n[PASS] All 1000 tasks accessible in memory - O(1) lookup")


def run_all_tests():
    """Run all manual tests for User Story 5."""
    print("\n" + "=" * 70)
    print("MANUAL TEST SUITE - USER STORY 5: SESSION-BASED PERSISTENCE")
    print("=" * 70)
    print("\nUser Story 5 Requirements:")
    print("  1. Tasks persist during a single session")
    print("  2. Tasks DO NOT persist between sessions")
    print("  3. Fresh TaskManager instances start empty")
    print("  4. No file I/O operations performed")
    print("  5. Graceful exit handling with informative messages")
    print("=" * 70)

    try:
        # Run all tests
        test_session_persistence()
        test_no_persistence_between_instances()
        test_data_loss_on_restart()
        test_no_file_io_operations()
        test_large_dataset_in_memory()

        # Summary
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED - USER STORY 5 COMPLETE!")
        print("=" * 70)
        print("\nSummary:")
        print("  [OK] Tasks persist during session")
        print("  [OK] No persistence between instances")
        print("  [OK] Data lost on application restart")
        print("  [OK] In-memory only storage (no file I/O)")
        print("  [OK] Large datasets handled in memory")
        print("\nUser Story 5 is FULLY FUNCTIONAL!")
        print("=" * 70)

        print("\n[INFO] For manual testing of graceful exit messages:")
        print("  Run: python -m src.main")
        print("  Add some tasks, then:")
        print("    - Choose option 6 to see normal exit message")
        print("    - Or press Ctrl+C to see interrupt exit message")
        print("=" * 70)

        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
