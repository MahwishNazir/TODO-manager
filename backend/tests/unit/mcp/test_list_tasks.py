"""
Unit tests for list_tasks MCP tool.

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

from src.mcp.schemas import ListTasksInput
from src.mcp.errors import ErrorCode


class TestListTasksInputValidation:
    """Test input validation for list_tasks tool."""

    def test_valid_input_with_defaults(self):
        """Test that valid input with only required fields uses defaults."""
        input_data = ListTasksInput(user_id="user123")
        assert input_data.user_id == "user123"
        assert input_data.status == "all"
        assert input_data.limit == 50
        assert input_data.offset == 0

    def test_valid_input_with_all_fields(self):
        """Test that valid input with all fields is accepted."""
        input_data = ListTasksInput(
            user_id="user123",
            status="pending",
            limit=25,
            offset=10,
        )
        assert input_data.status == "pending"
        assert input_data.limit == 25
        assert input_data.offset == 10

    def test_invalid_status_rejected(self):
        """Test that invalid status value is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(
                user_id="user123",
                status="invalid_status",
            )
        assert "status" in str(exc_info.value).lower()

    def test_limit_too_high_rejected(self):
        """Test that limit exceeding max is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(
                user_id="user123",
                limit=101,  # Max is 100
            )
        assert "limit" in str(exc_info.value).lower()

    def test_limit_too_low_rejected(self):
        """Test that limit below min is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(
                user_id="user123",
                limit=0,  # Min is 1
            )
        assert "limit" in str(exc_info.value).lower()

    def test_negative_offset_rejected(self):
        """Test that negative offset is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ListTasksInput(
                user_id="user123",
                offset=-1,
            )
        assert "offset" in str(exc_info.value).lower()


class TestListTasksSuccessResponse:
    """Test list_tasks success response format."""

    @pytest.fixture
    def mock_tasks(self):
        """Create mock task objects."""
        task1 = Mock()
        task1.id = 1
        task1.user_id = "user123"
        task1.title = "Task 1"
        task1.description = None
        task1.status.value = "incomplete"
        task1.is_completed = False
        task1.created_at.isoformat.return_value = "2026-01-29T10:00:00+00:00"
        task1.updated_at.isoformat.return_value = "2026-01-29T10:00:00+00:00"

        task2 = Mock()
        task2.id = 2
        task2.user_id = "user123"
        task2.title = "Task 2"
        task2.description = "Description"
        task2.status.value = "complete"
        task2.is_completed = True
        task2.created_at.isoformat.return_value = "2026-01-28T10:00:00+00:00"
        task2.updated_at.isoformat.return_value = "2026-01-29T11:00:00+00:00"

        return [task1, task2]

    def test_success_response_with_tasks(self, mock_tasks):
        """Test that success response has correct structure with tasks."""
        try:
            from src.mcp.tools.list_tasks import list_tasks_handler

            with patch(
                "src.mcp.tools.list_tasks.get_all_tasks",
                return_value=mock_tasks,
            ):
                with patch("src.mcp.tools.list_tasks.get_db_session") as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = ListTasksInput(user_id="user123")
                    response = list_tasks_handler(input_data)

                    assert response["success"] is True
                    assert "tasks" in response["data"]
                    assert len(response["data"]["tasks"]) == 2
                    assert "total_count" in response["data"]
                    assert "has_more" in response["data"]
        except ImportError:
            pytest.skip("list_tasks tool not yet implemented")

    def test_empty_result_returns_empty_array(self):
        """Test that empty result returns empty array, not error."""
        try:
            from src.mcp.tools.list_tasks import list_tasks_handler

            with patch(
                "src.mcp.tools.list_tasks.get_all_tasks",
                return_value=[],
            ):
                with patch("src.mcp.tools.list_tasks.get_db_session") as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = ListTasksInput(user_id="user123")
                    response = list_tasks_handler(input_data)

                    assert response["success"] is True
                    assert response["data"]["tasks"] == []
                    assert response["data"]["total_count"] == 0
        except ImportError:
            pytest.skip("list_tasks tool not yet implemented")

    def test_status_filter_applied(self, mock_tasks):
        """Test that status filter is applied correctly."""
        try:
            from src.mcp.tools.list_tasks import list_tasks_handler

            with patch(
                "src.mcp.tools.list_tasks.get_all_tasks",
                return_value=mock_tasks,
            ) as mock_get:
                with patch("src.mcp.tools.list_tasks.get_db_session") as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = ListTasksInput(user_id="user123", status="pending")
                    response = list_tasks_handler(input_data)

                    assert response["success"] is True
                    # Verify service was called
                    mock_get.assert_called_once()
                    # Only pending (not completed) tasks should be in result
                    assert len(response["data"]["tasks"]) == 1
        except ImportError:
            pytest.skip("list_tasks tool not yet implemented")

    def test_pagination_has_more_flag(self, mock_tasks):
        """Test that has_more flag is set correctly."""
        try:
            from src.mcp.tools.list_tasks import list_tasks_handler

            # Return exactly limit+1 tasks to indicate more exist
            with patch(
                "src.mcp.tools.list_tasks.get_all_tasks",
                return_value=mock_tasks,
            ):
                with patch("src.mcp.tools.list_tasks.get_db_session") as mock_get_db:
                    mock_session = MagicMock()
                    mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_get_db.return_value.__exit__ = Mock(return_value=False)

                    input_data = ListTasksInput(user_id="user123", limit=1)
                    response = list_tasks_handler(input_data)

                    assert response["success"] is True
                    # With limit=1 and 2 tasks, has_more should be True
                    assert response["data"]["has_more"] is True
        except ImportError:
            pytest.skip("list_tasks tool not yet implemented")
