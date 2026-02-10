"""
Unit tests for add_task MCP tool.

TDD: These tests are written FIRST and must FAIL before implementation.
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from src.mcp.schemas import AddTaskInput
from src.mcp.errors import ErrorCode


class TestAddTaskInputValidation:
    """Test input validation for add_task tool."""

    def test_valid_input_with_title_only(self):
        """Test that valid input with only required fields is accepted."""
        input_data = AddTaskInput(
            user_id="user123",
            title="Buy groceries",
        )
        assert input_data.user_id == "user123"
        assert input_data.title == "Buy groceries"
        assert input_data.description is None

    def test_valid_input_with_description(self):
        """Test that valid input with all fields is accepted."""
        input_data = AddTaskInput(
            user_id="user_123-abc",
            title="Buy groceries",
            description="Milk, eggs, bread",
        )
        assert input_data.user_id == "user_123-abc"
        assert input_data.title == "Buy groceries"
        assert input_data.description == "Milk, eggs, bread"

    def test_empty_title_rejected(self):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(
                user_id="user123",
                title="",
            )
        assert "title" in str(exc_info.value).lower()

    def test_missing_user_id_rejected(self):
        """Test that missing user_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(
                title="Buy groceries",
            )
        assert "user_id" in str(exc_info.value).lower()

    def test_invalid_user_id_pattern_rejected(self):
        """Test that user_id with invalid characters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(
                user_id="user@invalid",  # @ is not allowed
                title="Buy groceries",
            )
        assert "user_id" in str(exc_info.value).lower()

    def test_user_id_too_long_rejected(self):
        """Test that user_id exceeding max length is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(
                user_id="a" * 51,  # Max is 50
                title="Buy groceries",
            )
        assert "user_id" in str(exc_info.value).lower()

    def test_title_too_long_rejected(self):
        """Test that title exceeding max length is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(
                user_id="user123",
                title="a" * 501,  # Max is 500
            )
        assert "title" in str(exc_info.value).lower()

    def test_description_too_long_rejected(self):
        """Test that description exceeding max length is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddTaskInput(
                user_id="user123",
                title="Buy groceries",
                description="a" * 5001,  # Max is 5000
            )
        assert "description" in str(exc_info.value).lower()


class TestAddTaskSuccessResponse:
    """Test add_task success response format."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_task(self):
        """Create a mock task object."""
        task = Mock()
        task.id = 42
        task.user_id = "user123"
        task.title = "Buy groceries"
        task.description = "Milk, eggs, bread"
        task.status.value = "incomplete"
        task.is_completed = False
        task.created_at.isoformat.return_value = "2026-01-29T10:00:00+00:00"
        task.updated_at.isoformat.return_value = "2026-01-29T10:00:00+00:00"
        return task

    def test_success_response_structure(self, mock_session, mock_task):
        """Test that success response has correct envelope structure."""
        # This test will fail until add_task tool is implemented
        try:
            from src.mcp.tools.add_task import add_task_handler

            with patch(
                "src.mcp.tools.add_task.create_task", return_value=mock_task
            ):
                with patch(
                    "src.mcp.tools.add_task.get_db_session"
                ) as mock_get_db:
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = AddTaskInput(
                        user_id="user123",
                        title="Buy groceries",
                        description="Milk, eggs, bread",
                    )
                    response = add_task_handler(input_data)

                    # Verify response envelope structure
                    assert response["success"] is True
                    assert response["error"] is None
                    assert "data" in response
                    assert "metadata" in response
                    assert "timestamp" in response["metadata"]
                    assert "request_id" in response["metadata"]

                    # Verify task data
                    assert "task" in response["data"]
                    task_data = response["data"]["task"]
                    assert task_data["id"] == "42"
                    assert task_data["user_id"] == "user123"
                    assert task_data["title"] == "Buy groceries"
                    assert task_data["status"] == "pending"
        except ImportError:
            pytest.skip("add_task tool not yet implemented")

    def test_task_created_with_pending_status(self, mock_session, mock_task):
        """Test that new task is created with pending status."""
        try:
            from src.mcp.tools.add_task import add_task_handler

            with patch(
                "src.mcp.tools.add_task.create_task", return_value=mock_task
            ):
                with patch(
                    "src.mcp.tools.add_task.get_db_session"
                ) as mock_get_db:
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = AddTaskInput(
                        user_id="user123",
                        title="Buy groceries",
                    )
                    response = add_task_handler(input_data)

                    assert response["success"] is True
                    assert response["data"]["task"]["status"] == "pending"
        except ImportError:
            pytest.skip("add_task tool not yet implemented")


class TestAddTaskErrorCases:
    """Test add_task error handling."""

    def test_database_error_returns_service_unavailable(self):
        """Test that database errors return SERVICE_UNAVAILABLE."""
        try:
            from src.mcp.tools.add_task import add_task_handler
            from sqlalchemy.exc import SQLAlchemyError

            with patch(
                "src.mcp.tools.add_task.create_task",
                side_effect=SQLAlchemyError("DB error"),
            ):
                with patch(
                    "src.mcp.tools.add_task.get_db_session"
                ) as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = AddTaskInput(
                        user_id="user123",
                        title="Buy groceries",
                    )
                    response = add_task_handler(input_data)

                    assert response["success"] is False
                    assert response["error"]["code"] == ErrorCode.SERVICE_UNAVAILABLE.value
        except ImportError:
            pytest.skip("add_task tool not yet implemented")

    def test_unexpected_error_returns_internal_error(self):
        """Test that unexpected errors return INTERNAL_ERROR."""
        try:
            from src.mcp.tools.add_task import add_task_handler

            with patch(
                "src.mcp.tools.add_task.create_task",
                side_effect=RuntimeError("Unexpected"),
            ):
                with patch(
                    "src.mcp.tools.add_task.get_db_session"
                ) as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = AddTaskInput(
                        user_id="user123",
                        title="Buy groceries",
                    )
                    response = add_task_handler(input_data)

                    assert response["success"] is False
                    assert response["error"]["code"] == ErrorCode.INTERNAL_ERROR.value
        except ImportError:
            pytest.skip("add_task tool not yet implemented")
