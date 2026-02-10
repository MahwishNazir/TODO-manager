"""
Unit tests for delete_task MCP tool.
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from src.mcp.schemas import DeleteTaskInput
from src.mcp.errors import ErrorCode


class TestDeleteTaskInputValidation:
    """Test input validation for delete_task tool."""

    def test_valid_input(self):
        """Test that valid input is accepted."""
        input_data = DeleteTaskInput(
            user_id="user123",
            task_id="42",
        )
        assert input_data.user_id == "user123"
        assert input_data.task_id == "42"


class TestDeleteTaskSuccessResponse:
    """Test delete_task success response format."""

    def test_delete_success(self):
        """Test that deleting task returns success."""
        from src.mcp.tools.delete_task import delete_task_handler

        mock_task = Mock()
        mock_task.id = 42
        mock_task.user_id = "user123"

        with patch("src.mcp.tools.delete_task.get_task_by_id", return_value=mock_task):
            with patch("src.mcp.tools.delete_task.service_delete_task") as mock_delete:
                with patch("src.mcp.tools.delete_task.get_db_session") as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = DeleteTaskInput(user_id="user123", task_id="42")
                    response = delete_task_handler(input_data)

                    assert response["success"] is True
                    assert response["data"]["deleted"] is True
                    assert response["data"]["task_id"] == "42"
                    mock_delete.assert_called_once()

    def test_idempotent_nonexistent(self):
        """Test that deleting non-existent task succeeds (idempotent)."""
        from src.mcp.tools.delete_task import delete_task_handler

        with patch("src.mcp.tools.delete_task.get_task_by_id", return_value=None):
            with patch("src.mcp.tools.delete_task.get_db_session") as mock_get_db:
                mock_session = MagicMock()
                mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                mock_get_db.return_value.__exit__ = Mock(return_value=False)

                input_data = DeleteTaskInput(user_id="user123", task_id="999")
                response = delete_task_handler(input_data)

                # Should succeed even if task doesn't exist
                assert response["success"] is True
                assert response["data"]["deleted"] is True


class TestDeleteTaskErrorCases:
    """Test delete_task error handling."""

    def test_unauthorized_returns_idempotent_success(self):
        """Test that wrong user returns idempotent success (task not found for that user)."""
        from src.mcp.tools.delete_task import delete_task_handler

        # get_task_by_id filters by user_id, so wrong user gets None
        with patch("src.mcp.tools.delete_task.get_task_by_id", return_value=None):
            with patch("src.mcp.tools.delete_task.get_db_session") as mock_get_db:
                mock_session = MagicMock()
                mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                mock_get_db.return_value.__exit__ = Mock(return_value=False)

                input_data = DeleteTaskInput(user_id="user123", task_id="42")
                response = delete_task_handler(input_data)

                # Delete is idempotent, so task not found is success
                assert response["success"] is True
                assert response["data"]["deleted"] is True
