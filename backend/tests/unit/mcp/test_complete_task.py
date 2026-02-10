"""
Unit tests for complete_task MCP tool.
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from src.mcp.schemas import CompleteTaskInput
from src.mcp.errors import ErrorCode


class TestCompleteTaskInputValidation:
    """Test input validation for complete_task tool."""

    def test_valid_input(self):
        """Test that valid input is accepted."""
        input_data = CompleteTaskInput(
            user_id="user123",
            task_id="42",
        )
        assert input_data.user_id == "user123"
        assert input_data.task_id == "42"

    def test_missing_task_id_rejected(self):
        """Test that missing task_id is rejected."""
        with pytest.raises(ValidationError):
            CompleteTaskInput(user_id="user123")


class TestCompleteTaskSuccessResponse:
    """Test complete_task success response format."""

    @pytest.fixture
    def mock_task(self):
        """Create a mock task object."""
        task = Mock()
        task.id = 42
        task.user_id = "user123"
        task.title = "Task"
        task.description = None
        task.is_completed = True
        task.created_at.isoformat.return_value = "2026-01-29T10:00:00+00:00"
        task.updated_at.isoformat.return_value = "2026-01-29T12:00:00+00:00"
        return task

    def test_complete_success(self, mock_task):
        """Test that completing task returns success."""
        from src.mcp.tools.complete_task import complete_task_handler

        # Task starts as not completed
        mock_task.is_completed = False

        with patch("src.mcp.tools.complete_task.get_task_by_id", return_value=mock_task):
            with patch("src.mcp.tools.complete_task.toggle_task_completion") as mock_toggle:
                # After toggle, task is completed
                completed_task = Mock()
                completed_task.id = 42
                completed_task.user_id = "user123"
                completed_task.title = "Task"
                completed_task.description = None
                completed_task.is_completed = True
                completed_task.created_at.isoformat.return_value = "2026-01-29T10:00:00+00:00"
                completed_task.updated_at.isoformat.return_value = "2026-01-29T12:00:00+00:00"
                mock_toggle.return_value = completed_task

                with patch("src.mcp.tools.complete_task.get_db_session") as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = CompleteTaskInput(user_id="user123", task_id="42")
                    response = complete_task_handler(input_data)

                    assert response["success"] is True
                    assert response["data"]["task"]["status"] == "completed"

    def test_idempotent_already_completed(self, mock_task):
        """Test that completing already-completed task succeeds."""
        from src.mcp.tools.complete_task import complete_task_handler

        # Task is already completed
        mock_task.is_completed = True

        with patch("src.mcp.tools.complete_task.get_task_by_id", return_value=mock_task):
            with patch("src.mcp.tools.complete_task.toggle_task_completion") as mock_toggle:
                with patch("src.mcp.tools.complete_task.get_db_session") as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = CompleteTaskInput(user_id="user123", task_id="42")
                    response = complete_task_handler(input_data)

                    assert response["success"] is True
                    # toggle should NOT be called for already completed
                    mock_toggle.assert_not_called()


class TestCompleteTaskErrorCases:
    """Test complete_task error handling."""

    def test_task_not_found_error(self):
        """Test that non-existent task returns TASK_NOT_FOUND."""
        from src.mcp.tools.complete_task import complete_task_handler

        with patch("src.mcp.tools.complete_task.get_task_by_id", return_value=None):
            with patch("src.mcp.tools.complete_task.get_db_session") as mock_get_db:
                mock_session = MagicMock()
                mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                mock_get_db.return_value.__exit__ = Mock(return_value=False)

                input_data = CompleteTaskInput(user_id="user123", task_id="999")
                response = complete_task_handler(input_data)

                assert response["success"] is False
                assert response["error"]["code"] == ErrorCode.TASK_NOT_FOUND.value
