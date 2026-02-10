"""
Integration tests for MCP Server.

T051: Test MCP server startup and tool discovery
T052: Test full tool lifecycle (add → list → update → complete → delete)
T053: Test error handling with real database
"""

import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import pytest
from unittest.mock import patch
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from src.mcp.server import mcp, register_tools
from src.mcp.schemas import (
    AddTaskInput,
    ListTasksInput,
    UpdateTaskInput,
    CompleteTaskInput,
    DeleteTaskInput,
)
from src.mcp.errors import ErrorCode


# Create isolated in-memory database for MCP integration tests
MCP_TEST_DATABASE_URL = "sqlite:///:memory:"

mcp_test_engine = create_engine(
    MCP_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@contextmanager
def get_mcp_test_session() -> Generator[Session, None, None]:
    """Test database session context manager for MCP tools."""
    session = Session(mcp_test_engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture(scope="function")
def mcp_test_db():
    """Set up and tear down MCP test database."""
    # Create all tables
    SQLModel.metadata.create_all(mcp_test_engine)
    yield mcp_test_engine
    # Drop all tables after test
    SQLModel.metadata.drop_all(mcp_test_engine)


@pytest.fixture(scope="function")
def sample_user_id():
    """Provide a sample user ID for MCP testing."""
    return "mcp_test_user_123"


@pytest.fixture(scope="function")
def another_user_id():
    """Provide another user ID for isolation testing."""
    return "mcp_test_user_456"


class TestMCPServerStartupAndDiscovery:
    """T051: Test MCP server startup and tool discovery."""

    def test_mcp_server_initialized(self):
        """Test that MCP server is properly initialized."""
        assert mcp is not None
        assert mcp.name == "todo-mcp-server"

    def test_tool_handlers_importable(self):
        """Test that all tool handlers can be imported."""
        from src.mcp.tools.add_task import add_task_handler
        from src.mcp.tools.list_tasks import list_tasks_handler
        from src.mcp.tools.update_task import update_task_handler
        from src.mcp.tools.complete_task import complete_task_handler
        from src.mcp.tools.delete_task import delete_task_handler

        assert add_task_handler is not None
        assert list_tasks_handler is not None
        assert update_task_handler is not None
        assert complete_task_handler is not None
        assert delete_task_handler is not None

    def test_schemas_importable(self):
        """Test that all input schemas can be imported."""
        from src.mcp.schemas import (
            AddTaskInput,
            ListTasksInput,
            UpdateTaskInput,
            CompleteTaskInput,
            DeleteTaskInput,
        )

        assert AddTaskInput is not None
        assert ListTasksInput is not None
        assert UpdateTaskInput is not None
        assert CompleteTaskInput is not None
        assert DeleteTaskInput is not None

    def test_error_codes_available(self):
        """Test that error codes are properly defined."""
        from src.mcp.errors import ErrorCode

        assert ErrorCode.INVALID_INPUT is not None
        assert ErrorCode.TASK_NOT_FOUND is not None
        assert ErrorCode.UNAUTHORIZED is not None

    def test_register_tools_callable(self):
        """Test that register_tools function is callable."""
        # Calling register_tools again should not raise
        register_tools()


class TestMCPToolLifecycle:
    """T052: Test full tool lifecycle (add → list → update → complete → delete)."""

    def test_full_task_lifecycle(self, mcp_test_db, sample_user_id):
        """Test complete CRUD lifecycle through MCP tools."""
        import json
        from src.mcp.tools.add_task import add_task_handler
        from src.mcp.tools.list_tasks import list_tasks_handler
        from src.mcp.tools.update_task import update_task_handler
        from src.mcp.tools.complete_task import complete_task_handler
        from src.mcp.tools.delete_task import delete_task_handler

        with patch("src.mcp.tools.add_task.get_db_session", get_mcp_test_session):
            with patch("src.mcp.tools.list_tasks.get_db_session", get_mcp_test_session):
                with patch("src.mcp.tools.update_task.get_db_session", get_mcp_test_session):
                    with patch("src.mcp.tools.complete_task.get_db_session", get_mcp_test_session):
                        with patch("src.mcp.tools.delete_task.get_db_session", get_mcp_test_session):
                            # Step 1: Add a task
                            add_input = AddTaskInput(
                                user_id=sample_user_id,
                                title="Test lifecycle task",
                                description="Testing full CRUD lifecycle",
                            )
                            add_response = add_task_handler(add_input)

                            assert add_response["success"] is True
                            task_id = add_response["data"]["task"]["id"]
                            assert task_id is not None
                            assert add_response["data"]["task"]["status"] == "pending"

                            # Step 2: List tasks - verify task exists
                            list_input = ListTasksInput(user_id=sample_user_id)
                            list_response = list_tasks_handler(list_input)

                            assert list_response["success"] is True
                            assert list_response["data"]["total_count"] == 1
                            assert len(list_response["data"]["tasks"]) == 1
                            assert list_response["data"]["tasks"][0]["id"] == task_id

                            # Step 3: Update task title
                            update_input = UpdateTaskInput(
                                user_id=sample_user_id,
                                task_id=task_id,
                                title="Updated lifecycle task",
                            )
                            update_response = update_task_handler(update_input)

                            assert update_response["success"] is True
                            assert update_response["data"]["task"]["title"] == "Updated lifecycle task"

                            # Step 4: Complete the task
                            complete_input = CompleteTaskInput(
                                user_id=sample_user_id,
                                task_id=task_id,
                            )
                            complete_response = complete_task_handler(complete_input)

                            assert complete_response["success"] is True
                            assert complete_response["data"]["task"]["status"] == "completed"

                            # Step 5: Delete the task
                            delete_input = DeleteTaskInput(
                                user_id=sample_user_id,
                                task_id=task_id,
                            )
                            delete_response = delete_task_handler(delete_input)

                            assert delete_response["success"] is True
                            assert delete_response["data"]["deleted"] is True

                            # Step 6: Verify task is gone from list
                            final_list_response = list_tasks_handler(list_input)
                            assert final_list_response["success"] is True
                            assert final_list_response["data"]["total_count"] == 0

    def test_add_multiple_tasks_and_list(self, mcp_test_db, sample_user_id):
        """Test adding multiple tasks and listing them."""
        from src.mcp.tools.add_task import add_task_handler
        from src.mcp.tools.list_tasks import list_tasks_handler

        with patch("src.mcp.tools.add_task.get_db_session", get_mcp_test_session):
            with patch("src.mcp.tools.list_tasks.get_db_session", get_mcp_test_session):
                # Add 3 tasks
                task_ids = []
                for i in range(3):
                    add_input = AddTaskInput(
                        user_id=sample_user_id,
                        title=f"Task {i + 1}",
                    )
                    response = add_task_handler(add_input)
                    assert response["success"] is True
                    task_ids.append(response["data"]["task"]["id"])

                # List all tasks
                list_input = ListTasksInput(user_id=sample_user_id)
                list_response = list_tasks_handler(list_input)

                assert list_response["success"] is True
                assert list_response["data"]["total_count"] == 3
                assert len(list_response["data"]["tasks"]) == 3


class TestMCPUserIsolation:
    """Test user isolation in MCP tools."""

    def test_users_only_see_own_tasks(self, mcp_test_db, sample_user_id, another_user_id):
        """Test that users can only see their own tasks."""
        from src.mcp.tools.add_task import add_task_handler
        from src.mcp.tools.list_tasks import list_tasks_handler

        with patch("src.mcp.tools.add_task.get_db_session", get_mcp_test_session):
            with patch("src.mcp.tools.list_tasks.get_db_session", get_mcp_test_session):
                # User 1 creates a task
                add_input_1 = AddTaskInput(
                    user_id=sample_user_id,
                    title="User 1 task",
                )
                response_1 = add_task_handler(add_input_1)
                assert response_1["success"] is True

                # User 2 creates a task
                add_input_2 = AddTaskInput(
                    user_id=another_user_id,
                    title="User 2 task",
                )
                response_2 = add_task_handler(add_input_2)
                assert response_2["success"] is True

                # User 1 should only see their own task
                list_input_1 = ListTasksInput(user_id=sample_user_id)
                list_response_1 = list_tasks_handler(list_input_1)

                assert list_response_1["success"] is True
                assert list_response_1["data"]["total_count"] == 1
                assert list_response_1["data"]["tasks"][0]["title"] == "User 1 task"

                # User 2 should only see their own task
                list_input_2 = ListTasksInput(user_id=another_user_id)
                list_response_2 = list_tasks_handler(list_input_2)

                assert list_response_2["success"] is True
                assert list_response_2["data"]["total_count"] == 1
                assert list_response_2["data"]["tasks"][0]["title"] == "User 2 task"

    def test_user_cannot_update_other_users_task(self, mcp_test_db, sample_user_id, another_user_id):
        """Test that a user cannot update another user's task."""
        from src.mcp.tools.add_task import add_task_handler
        from src.mcp.tools.update_task import update_task_handler

        with patch("src.mcp.tools.add_task.get_db_session", get_mcp_test_session):
            with patch("src.mcp.tools.update_task.get_db_session", get_mcp_test_session):
                # User 1 creates a task
                add_input = AddTaskInput(
                    user_id=sample_user_id,
                    title="User 1 task",
                )
                add_response = add_task_handler(add_input)
                task_id = add_response["data"]["task"]["id"]

                # User 2 tries to update it
                update_input = UpdateTaskInput(
                    user_id=another_user_id,
                    task_id=task_id,
                    title="Hacked!",
                )
                update_response = update_task_handler(update_input)

                # Should fail with TASK_NOT_FOUND (user isolation)
                assert update_response["success"] is False
                assert update_response["error"]["code"] == ErrorCode.TASK_NOT_FOUND.value


class TestMCPErrorHandling:
    """T053: Test error handling with real database."""

    def test_task_not_found_error(self, mcp_test_db, sample_user_id):
        """Test that updating non-existent task returns proper error."""
        from src.mcp.tools.update_task import update_task_handler

        with patch("src.mcp.tools.update_task.get_db_session", get_mcp_test_session):
            update_input = UpdateTaskInput(
                user_id=sample_user_id,
                task_id="99999",
                title="Won't work",
            )
            response = update_task_handler(update_input)

            assert response["success"] is False
            assert response["error"]["code"] == ErrorCode.TASK_NOT_FOUND.value
            assert "message" in response["error"]

    def test_complete_nonexistent_task_error(self, mcp_test_db, sample_user_id):
        """Test that completing non-existent task returns error."""
        from src.mcp.tools.complete_task import complete_task_handler

        with patch("src.mcp.tools.complete_task.get_db_session", get_mcp_test_session):
            complete_input = CompleteTaskInput(
                user_id=sample_user_id,
                task_id="99999",
            )
            response = complete_task_handler(complete_input)

            assert response["success"] is False
            assert response["error"]["code"] == ErrorCode.TASK_NOT_FOUND.value

    def test_delete_idempotent_success(self, mcp_test_db, sample_user_id):
        """Test that deleting non-existent task succeeds (idempotent)."""
        from src.mcp.tools.delete_task import delete_task_handler

        with patch("src.mcp.tools.delete_task.get_db_session", get_mcp_test_session):
            delete_input = DeleteTaskInput(
                user_id=sample_user_id,
                task_id="99999",
            )
            response = delete_task_handler(delete_input)

            # Delete is idempotent - should succeed
            assert response["success"] is True
            assert response["data"]["deleted"] is True

    def test_empty_list_returns_success(self, mcp_test_db, sample_user_id):
        """Test that listing empty tasks returns success with empty array."""
        from src.mcp.tools.list_tasks import list_tasks_handler

        with patch("src.mcp.tools.list_tasks.get_db_session", get_mcp_test_session):
            list_input = ListTasksInput(user_id=sample_user_id)
            response = list_tasks_handler(list_input)

            assert response["success"] is True
            assert response["data"]["tasks"] == []
            assert response["data"]["total_count"] == 0

    def test_response_envelope_structure(self, mcp_test_db, sample_user_id):
        """Test that all responses follow the envelope structure."""
        from src.mcp.tools.add_task import add_task_handler

        with patch("src.mcp.tools.add_task.get_db_session", get_mcp_test_session):
            add_input = AddTaskInput(
                user_id=sample_user_id,
                title="Test envelope",
            )
            response = add_task_handler(add_input)

            # Verify envelope structure
            assert "success" in response
            assert "data" in response or "error" in response
            assert "metadata" in response
            assert "timestamp" in response["metadata"]
            assert "request_id" in response["metadata"]


class TestMCPStatusFiltering:
    """Test status filtering in list_tasks."""

    def test_filter_pending_tasks(self, mcp_test_db, sample_user_id):
        """Test filtering tasks by pending status."""
        from src.mcp.tools.add_task import add_task_handler
        from src.mcp.tools.complete_task import complete_task_handler
        from src.mcp.tools.list_tasks import list_tasks_handler

        with patch("src.mcp.tools.add_task.get_db_session", get_mcp_test_session):
            with patch("src.mcp.tools.complete_task.get_db_session", get_mcp_test_session):
                with patch("src.mcp.tools.list_tasks.get_db_session", get_mcp_test_session):
                    # Create 2 tasks
                    for title in ["Pending task", "To complete task"]:
                        add_input = AddTaskInput(user_id=sample_user_id, title=title)
                        add_task_handler(add_input)

                    # Get list to find task id for completion
                    list_all = list_tasks_handler(ListTasksInput(user_id=sample_user_id))
                    to_complete_id = list_all["data"]["tasks"][1]["id"]

                    # Complete one task
                    complete_input = CompleteTaskInput(
                        user_id=sample_user_id,
                        task_id=to_complete_id,
                    )
                    complete_task_handler(complete_input)

                    # Filter for pending tasks
                    list_input = ListTasksInput(
                        user_id=sample_user_id,
                        status="pending",
                    )
                    response = list_tasks_handler(list_input)

                    assert response["success"] is True
                    assert len(response["data"]["tasks"]) == 1
                    assert response["data"]["tasks"][0]["status"] == "pending"

    def test_filter_completed_tasks(self, mcp_test_db, sample_user_id):
        """Test filtering tasks by completed status."""
        from src.mcp.tools.add_task import add_task_handler
        from src.mcp.tools.complete_task import complete_task_handler
        from src.mcp.tools.list_tasks import list_tasks_handler

        with patch("src.mcp.tools.add_task.get_db_session", get_mcp_test_session):
            with patch("src.mcp.tools.complete_task.get_db_session", get_mcp_test_session):
                with patch("src.mcp.tools.list_tasks.get_db_session", get_mcp_test_session):
                    # Create and complete a task
                    add_input = AddTaskInput(
                        user_id=sample_user_id,
                        title="Task to complete",
                    )
                    add_response = add_task_handler(add_input)
                    task_id = add_response["data"]["task"]["id"]

                    complete_input = CompleteTaskInput(
                        user_id=sample_user_id,
                        task_id=task_id,
                    )
                    complete_task_handler(complete_input)

                    # Filter for completed tasks
                    list_input = ListTasksInput(
                        user_id=sample_user_id,
                        status="completed",
                    )
                    response = list_tasks_handler(list_input)

                    assert response["success"] is True
                    assert len(response["data"]["tasks"]) == 1
                    assert response["data"]["tasks"][0]["status"] == "completed"
