"""
Unit tests for update_task MCP tool.
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from src.mcp.schemas import UpdateTaskInput
from src.mcp.errors import ErrorCode


class TestUpdateTaskInputValidation:
    """Test input validation for update_task tool."""

    def test_valid_input_with_title(self):
        """Test that valid input with title is accepted."""
        input_data = UpdateTaskInput(
            user_id="user123",
            task_id="42",
            title="New title",
        )
        assert input_data.title == "New title"
        assert input_data.description is None

    def test_valid_input_with_description(self):
        """Test that valid input with description is accepted."""
        input_data = UpdateTaskInput(
            user_id="user123",
            task_id="42",
            description="New description",
        )
        assert input_data.description == "New description"

    def test_no_fields_rejected(self):
        """Test that input with no update fields is rejected."""
        with pytest.raises(ValidationError):
            UpdateTaskInput(
                user_id="user123",
                task_id="42",
            )


class TestUpdateTaskSuccessResponse:
    """Test update_task success response format."""

    @pytest.fixture
    def mock_task(self):
        """Create a mock task object."""
        task = Mock()
        task.id = 42
        task.user_id = "user123"
        task.title = "Updated title"
        task.description = "Updated desc"
        task.status.value = "incomplete"
        task.is_completed = False
        task.created_at.isoformat.return_value = "2026-01-29T10:00:00+00:00"
        task.updated_at.isoformat.return_value = "2026-01-29T12:00:00+00:00"
        return task

    def test_title_update_success(self, mock_task):
        """Test that title update returns success."""
        from src.mcp.tools.update_task import update_task_handler

        # Ensure mock task has correct user_id
        mock_task.user_id = "user123"

        with patch("src.mcp.tools.update_task.get_task_by_id", return_value=mock_task):
            with patch("src.mcp.tools.update_task.get_db_session") as mock_get_db:
                mock_session = MagicMock()
                mock_session.add = Mock()
                mock_session.commit = Mock()
                mock_session.refresh = Mock()
                mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                mock_get_db.return_value.__exit__ = Mock(return_value=False)

                input_data = UpdateTaskInput(
                    user_id="user123",
                    task_id="42",
                    title="Updated title",
                )
                response = update_task_handler(input_data)

                assert response["success"] is True
                assert response["data"]["task"]["title"] == "Updated title"


class TestUpdateTaskErrorCases:
    """Test update_task error handling."""

    def test_task_not_found_error(self):
        """Test that non-existent task returns TASK_NOT_FOUND."""
        from src.mcp.tools.update_task import update_task_handler

        with patch("src.mcp.tools.update_task.get_task_by_id", return_value=None):
            with patch("src.mcp.tools.update_task.get_db_session") as mock_get_db:
                mock_session = MagicMock()
                mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                mock_get_db.return_value.__exit__ = Mock(return_value=False)

                input_data = UpdateTaskInput(
                    user_id="user123",
                    task_id="999",
                    title="New title",
                )
                response = update_task_handler(input_data)

                assert response["success"] is False
                assert response["error"]["code"] == ErrorCode.TASK_NOT_FOUND.value

    def test_unauthorized_error(self):
        """Test that wrong user returns TASK_NOT_FOUND (function filters by user_id)."""
        from src.mcp.tools.update_task import update_task_handler

        # get_task_by_id filters by user_id, so wrong user gets None (not found)
        with patch("src.mcp.tools.update_task.get_task_by_id", return_value=None):
            with patch("src.mcp.tools.update_task.get_db_session") as mock_get_db:
                mock_session = MagicMock()
                mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                mock_get_db.return_value.__exit__ = Mock(return_value=False)

                input_data = UpdateTaskInput(
                    user_id="user123",
                    task_id="42",
                    title="New title",
                )
                response = update_task_handler(input_data)

                # Since function filters by user_id, different user gets TASK_NOT_FOUND
                assert response["success"] is False
                assert response["error"]["code"] == ErrorCode.TASK_NOT_FOUND.value
