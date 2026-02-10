"""
Unit tests for ToolCallCollector (Phase III Part 5).

TDD: These tests are written FIRST and should FAIL until implementation.
Tests T028-T030 for User Story 3.
"""

import pytest
import time
from unittest.mock import MagicMock


# =============================================================================
# User Story 3: Tool Call Reporting (T028-T030)
# =============================================================================

class TestToolCallCollector:
    """Unit tests for User Story 3."""

    def test_captures_tool_invocation(self):
        """T028: ToolCallCollector captures tool_name and parameters."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        # Record a tool call
        collector.record_call(
            tool_name="add_task",
            parameters={"title": "Buy milk", "priority": "high"},
            status="success",
            result={"task_id": "task-123"},
            execution_time_ms=50,
        )

        tool_calls = collector.stop_collection()

        # Verify capture
        assert len(tool_calls) == 1
        call = tool_calls[0]

        assert call["tool_name"] == "add_task"
        assert call["parameters"]["title"] == "Buy milk"
        assert call["parameters"]["priority"] == "high"
        assert call["status"] == "success"
        assert call["result"]["task_id"] == "task-123"

    def test_captures_execution_time(self):
        """T029: ToolCallCollector captures execution_time_ms."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        # Record call with specific execution time
        collector.record_call(
            tool_name="list_tasks",
            parameters={"filter": "all"},
            status="success",
            result={"tasks": []},
            execution_time_ms=125,
        )

        tool_calls = collector.stop_collection()

        assert len(tool_calls) == 1
        call = tool_calls[0]

        assert "execution_time_ms" in call
        assert isinstance(call["execution_time_ms"], int)
        assert call["execution_time_ms"] == 125
        assert call["execution_time_ms"] >= 0

    def test_captures_error_on_failure(self):
        """T030: ToolCallCollector captures error on failure."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        # Record a failed tool call
        collector.record_call(
            tool_name="delete_task",
            parameters={"task_id": "nonexistent-task"},
            status="error",
            error="Task not found",
            execution_time_ms=10,
        )

        tool_calls = collector.stop_collection()

        assert len(tool_calls) == 1
        call = tool_calls[0]

        assert call["tool_name"] == "delete_task"
        assert call["status"] == "error"
        assert call["error"] == "Task not found"
        assert call["result"] is None


class TestToolCallCollectorTracking:
    """Additional tests for tool call tracking."""

    def test_track_call_context_manager(self):
        """Context manager should capture timing automatically."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        with collector.track_call("test_tool", {"param": "value"}) as tracker:
            # Simulate some work
            time.sleep(0.01)  # 10ms
            tracker.set_result({"success": True})

        tool_calls = collector.stop_collection()

        assert len(tool_calls) == 1
        call = tool_calls[0]

        assert call["tool_name"] == "test_tool"
        assert call["execution_time_ms"] >= 10  # At least 10ms

    def test_track_call_captures_exception(self):
        """Context manager should capture exceptions as errors."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        with pytest.raises(ValueError):
            with collector.track_call("failing_tool", {"x": 1}) as tracker:
                raise ValueError("Something went wrong")

        tool_calls = collector.stop_collection()

        assert len(tool_calls) == 1
        call = tool_calls[0]

        assert call["status"] == "error"
        assert "Something went wrong" in call["error"]

    def test_multiple_tool_calls(self):
        """Should capture multiple tool calls in order."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        collector.record_call("tool_1", {"a": 1}, "success", execution_time_ms=10)
        collector.record_call("tool_2", {"b": 2}, "success", execution_time_ms=20)
        collector.record_call("tool_3", {"c": 3}, "error", error="Failed", execution_time_ms=5)

        tool_calls = collector.stop_collection()

        assert len(tool_calls) == 3
        assert tool_calls[0]["tool_name"] == "tool_1"
        assert tool_calls[1]["tool_name"] == "tool_2"
        assert tool_calls[2]["tool_name"] == "tool_3"

    def test_inactive_collector_ignores_calls(self):
        """Calls recorded when inactive should be ignored."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")

        # Record before starting collection
        collector.record_call("ignored_tool", {}, "success", execution_time_ms=10)

        collector.start_collection()
        collector.record_call("captured_tool", {}, "success", execution_time_ms=10)

        tool_calls = collector.stop_collection()

        assert len(tool_calls) == 1
        assert tool_calls[0]["tool_name"] == "captured_tool"


class TestSanitization:
    """Tests for parameter and result sanitization."""

    def test_sanitizes_sensitive_parameters(self):
        """Sensitive parameters should be redacted."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        collector.record_call(
            tool_name="auth_tool",
            parameters={
                "username": "john",
                "password": "secret123",
                "token": "bearer-xyz",
                "api_key": "key-abc",
                "Authorization": "Bearer xyz",
            },
            status="success",
            execution_time_ms=10,
        )

        tool_calls = collector.stop_collection()

        params = tool_calls[0]["parameters"]

        # Non-sensitive should be preserved
        assert params["username"] == "john"

        # Sensitive should be redacted
        assert params["password"] == "[REDACTED]"
        assert params["token"] == "[REDACTED]"
        assert params["api_key"] == "[REDACTED]"

    def test_sanitizes_result_dict(self):
        """Sensitive values in result dict should be redacted."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        collector.record_call(
            tool_name="get_credentials",
            parameters={},
            status="success",
            result={
                "user": "john",
                "password": "secret",
                "secret": "data",
            },
            execution_time_ms=10,
        )

        tool_calls = collector.stop_collection()

        result = tool_calls[0]["result"]

        assert result["user"] == "john"
        assert result["password"] == "[REDACTED]"
        assert result["secret"] == "[REDACTED]"


class TestActiveCollector:
    """Tests for active collector thread-local storage."""

    def test_get_active_returns_none_when_inactive(self):
        """Should return None when no collector is active."""
        from chatbot.agent.tool_collector import ToolCallCollector

        # Clear any existing active collector
        ToolCallCollector._local.active_collector = None

        assert ToolCallCollector.get_active() is None

    def test_get_active_returns_current(self):
        """Should return the currently active collector."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()

        active = ToolCallCollector.get_active()

        assert active is collector

        collector.stop_collection()

    def test_stop_clears_active(self):
        """Stopping collection should clear active collector."""
        from chatbot.agent.tool_collector import ToolCallCollector

        collector = ToolCallCollector(user_id="test-user-123")
        collector.start_collection()
        collector.stop_collection()

        assert ToolCallCollector.get_active() is None
