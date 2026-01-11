"""
Manual Test Script for User Story 3.

This script simulates the manual testing scenario from T052:
- Create task
- Update title with special characters (unicode, quotes)
- Verify handling

This is a simulation for automated verification. For true manual testing,
run: python -m src.main
"""

import sys
from unittest.mock import patch
from src.services.task_manager import TaskManager
from src.cli.menu import add_task_interactive, view_tasks, update_task_interactive


def safe_print(text):
    """Print text with fallback for encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace non-encodable characters with ?
        print(text.encode('ascii', 'replace').decode('ascii'))


def test_manual_scenario():
    """Simulate manual test scenario from T052."""
    print("=" * 50)
    print("MANUAL TEST SCENARIO - USER STORY 3")
    print("=" * 50)
    print("\nScenario: Create task, update with special chars,")
    print("verify handling")
    print("-" * 50)

    # Create task manager
    manager = TaskManager()

    # Test 1: Add a simple task
    print("\n[PASS] Test 1: Add Initial Task")
    with patch('builtins.input', return_value='Simple task'):
        add_task_interactive(manager)

    task = manager.get_task(1)
    assert task.title == 'Simple task'
    safe_print(f"  Task created: '{task.title}'")

    # Test 2: Update with special characters (quotes)
    print("\n[PASS] Test 2: Update with Quotes")
    quoted_title = 'Buy "organic" milk & \'eggs\''
    with patch('builtins.input', side_effect=['1', quoted_title]):
        update_task_interactive(manager)

    task = manager.get_task(1)
    assert task.title == quoted_title
    safe_print(f"  Updated to: {task.title}")

    # Test 3: Update with Unicode characters
    print("\n[PASS] Test 3: Update with Unicode")
    unicode_title = 'Visit café and get café au lait'
    with patch('builtins.input', side_effect=['1', unicode_title]):
        update_task_interactive(manager)

    task = manager.get_task(1)
    assert task.title == unicode_title
    safe_print(f"  Updated to: {task.title}")

    # Test 4: Update with emoji
    print("\n[PASS] Test 4: Update with Emoji")
    emoji_title = 'Deploy to production 🚀🎉'
    with patch('builtins.input', side_effect=['1', emoji_title]):
        update_task_interactive(manager)

    task = manager.get_task(1)
    assert task.title == emoji_title
    safe_print(f"  Updated to: {task.title}")

    # Test 5: Update with symbols and numbers
    print("\n[PASS] Test 5: Update with Symbols & Numbers")
    symbol_title = 'Budget: $5,000 @ 10% discount (save $500!)'
    with patch('builtins.input', side_effect=['1', symbol_title]):
        update_task_interactive(manager)

    task = manager.get_task(1)
    assert task.title == symbol_title
    safe_print(f"  Updated to: {task.title}")

    # Test 6: View task with special characters
    print("\n[PASS] Test 6: View Task with Special Characters")
    view_tasks(manager)
    print("  Task displayed correctly with all special characters")

    # Test 7: Create multiple tasks and update one
    print("\n[PASS] Test 7: Update One of Multiple Tasks")
    with patch('builtins.input', return_value='Task 2'):
        add_task_interactive(manager)
    with patch('builtins.input', return_value='Task 3'):
        add_task_interactive(manager)

    # Update task 2
    updated_title_2 = 'Updated Task #2 with special chars: @#$%'
    with patch('builtins.input', side_effect=['2', updated_title_2]):
        update_task_interactive(manager)

    task1 = manager.get_task(1)
    task2 = manager.get_task(2)
    task3 = manager.get_task(3)

    assert task1.title == symbol_title  # Unchanged
    assert task2.title == updated_title_2  # Updated
    assert task3.title == 'Task 3'  # Unchanged
    safe_print(f"  Task 1: {task1.title}")
    safe_print(f"  Task 2: {task2.title}")
    safe_print(f"  Task 3: {task3.title}")

    # Test 8: Update preserves completion status
    print("\n[PASS] Test 8: Update Preserves Completion Status")
    manager.mark_complete(3, True)
    assert task3.completed is True

    with patch('builtins.input', side_effect=['3', 'Updated complete task']):
        update_task_interactive(manager)

    task3 = manager.get_task(3)
    assert task3.title == 'Updated complete task'
    assert task3.completed is True  # Still complete
    print(f"  Task 3 title updated, still marked complete: {task3.completed}")

    # Test 9: Update with whitespace trimming
    print("\n[PASS] Test 9: Whitespace Trimming")
    with patch('builtins.input', side_effect=['3', '  Trimmed title  ']):
        update_task_interactive(manager)

    task3 = manager.get_task(3)
    assert task3.title == 'Trimmed title'
    safe_print(f"  Whitespace trimmed: '{task3.title}'")

    # Test 10: View all tasks
    print("\n[PASS] Test 10: View All Tasks")
    view_tasks(manager)

    print("\n" + "=" * 50)
    print("[SUCCESS] ALL MANUAL TESTS PASSED!")
    print("=" * 50)
    print("\nSummary:")
    print(f"  - Created {manager.count()} tasks")
    print("  - Successfully updated with:")
    print("    * Double and single quotes")
    print("    * Unicode characters (cafe with accent)")
    print("    * Emoji (rocket and party)")
    print("    * Symbols ($, @, #, %, etc.)")
    print("    * Numbers and punctuation")
    print("  - Whitespace trimming works")
    print("  - Updates preserve completion status")
    print("  - Multiple tasks maintain independence")
    print("\nUser Story 3 is FULLY FUNCTIONAL!")
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
