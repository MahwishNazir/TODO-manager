"""
Pytest configuration and fixtures for TODO application tests.

This module provides shared fixtures for all test modules.
"""

import pytest
from datetime import datetime


@pytest.fixture
def task_manager():
    """Provide a fresh TaskManager instance for each test.

    Returns:
        TaskManager: Empty task manager with no tasks.

    Example:
        def test_add_task(task_manager):
            task = task_manager.add_task("Buy milk")
            assert task.id == 1
    """
    # Import here to avoid circular imports during test collection
    from src.services.task_manager import TaskManager
    return TaskManager()


@pytest.fixture
def sample_tasks():
    """Provide sample task data for testing.

    Returns:
        list: List of dictionaries with sample task data.

    Example:
        def test_multiple_tasks(task_manager, sample_tasks):
            for task_data in sample_tasks:
                task_manager.add_task(task_data['title'])
            assert task_manager.count() == len(sample_tasks)
    """
    return [
        {
            'title': 'Buy groceries',
            'completed': False
        },
        {
            'title': 'Walk the dog',
            'completed': False
        },
        {
            'title': 'Write code',
            'completed': True
        }
    ]


@pytest.fixture
def populated_task_manager(task_manager, sample_tasks):
    """Provide a TaskManager pre-populated with sample tasks.

    Args:
        task_manager: Empty task manager fixture
        sample_tasks: Sample task data fixture

    Returns:
        TaskManager: Task manager with 3 tasks added.

    Example:
        def test_view_tasks(populated_task_manager):
            tasks = populated_task_manager.get_all_tasks()
            assert len(tasks) == 3
    """
    for task_data in sample_tasks:
        task = task_manager.add_task(task_data['title'])
        if task_data['completed']:
            task_manager.mark_complete(task.id, True)
    return task_manager


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime.utcnow() for consistent timestamps in tests.

    Args:
        monkeypatch: pytest monkeypatch fixture

    Returns:
        datetime: Fixed datetime object (2026-01-10 12:00:00 UTC)

    Example:
        def test_task_created_at(mock_datetime):
            from src.models.task import Task
            task = Task(id=1, title="Test")
            assert task.created_at == mock_datetime
    """
    fixed_time = datetime(2026, 1, 10, 12, 0, 0)

    class MockDatetime:
        @staticmethod
        def utcnow():
            return fixed_time

    import src.models.task as task_module
    monkeypatch.setattr(task_module, 'datetime', MockDatetime)

    return fixed_time
