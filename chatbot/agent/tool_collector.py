"""
Tool Call Collector (Phase III Part 5 - T006).

Captures MCP tool invocations with timing information for
transparency in the stateless chat response.
"""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from threading import local


@dataclass
class ToolCallRecord:
    """Record of a single tool invocation."""

    tool_name: str
    parameters: Dict[str, Any]
    status: str  # "success" or "error"
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: int = 0


class ToolCallCollector:
    """
    Collects tool call information during agent execution.

    This collector is designed for stateless operation - each request
    gets a fresh collector instance that captures all tool invocations
    for that single request.

    Usage:
        collector = ToolCallCollector(user_id="user-123")
        collector.start_collection()
        # ... agent executes tools ...
        tool_calls = collector.stop_collection()
    """

    # Thread-local storage for active collector
    _local = local()

    def __init__(self, user_id: str):
        """
        Initialize collector for a specific user.

        Args:
            user_id: User ID for context (used for logging/filtering)
        """
        self._user_id = user_id
        self._calls: List[ToolCallRecord] = []
        self._active = False

    @property
    def user_id(self) -> str:
        """Get the user ID this collector is tracking for."""
        return self._user_id

    @property
    def is_active(self) -> bool:
        """Check if collection is currently active."""
        return self._active

    def start_collection(self) -> None:
        """
        Start collecting tool calls.

        Sets this collector as the active collector in thread-local storage.
        """
        self._calls = []
        self._active = True
        ToolCallCollector._local.active_collector = self

    def stop_collection(self) -> List[Dict[str, Any]]:
        """
        Stop collecting and return all captured tool calls.

        Returns:
            List of tool call records as dictionaries
        """
        self._active = False
        ToolCallCollector._local.active_collector = None

        return [
            {
                "tool_name": call.tool_name,
                "parameters": self._sanitize_parameters(call.parameters),
                "status": call.status,
                "result": self._sanitize_result(call.result) if call.result else None,
                "error": call.error,
                "execution_time_ms": call.execution_time_ms,
            }
            for call in self._calls
        ]

    def record_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        status: str,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        execution_time_ms: int = 0,
    ) -> None:
        """
        Record a tool call.

        Args:
            tool_name: Name of the tool that was called
            parameters: Parameters passed to the tool
            status: "success" or "error"
            result: Return value from the tool (if success)
            error: Error message (if error)
            execution_time_ms: How long the call took in milliseconds
        """
        if not self._active:
            return

        self._calls.append(
            ToolCallRecord(
                tool_name=tool_name,
                parameters=parameters,
                status=status,
                result=result,
                error=error,
                execution_time_ms=execution_time_ms,
            )
        )

    @contextmanager
    def track_call(self, tool_name: str, parameters: Dict[str, Any]):
        """
        Context manager to track a tool call with automatic timing.

        Usage:
            with collector.track_call("add_task", {"title": "Buy milk"}) as tracker:
                result = actual_tool_function(...)
                tracker.set_result(result)

        Args:
            tool_name: Name of the tool being called
            parameters: Parameters being passed

        Yields:
            CallTracker object with set_result() and set_error() methods
        """
        tracker = CallTracker()
        start_time = time.perf_counter()

        try:
            yield tracker
        except Exception as e:
            tracker.set_error(str(e))
            raise
        finally:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            self.record_call(
                tool_name=tool_name,
                parameters=parameters,
                status=tracker.status,
                result=tracker.result,
                error=tracker.error,
                execution_time_ms=elapsed_ms,
            )

    def _sanitize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize parameters to exclude sensitive information.

        Args:
            params: Raw parameters dict

        Returns:
            Sanitized parameters safe for logging/response
        """
        sensitive_keys = {"password", "token", "secret", "api_key", "authorization"}
        sanitized = {}

        for key, value in params.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_result(self, result: Any) -> Any:
        """
        Sanitize result to exclude sensitive information.

        Args:
            result: Raw result from tool

        Returns:
            Sanitized result safe for response
        """
        if isinstance(result, dict):
            return self._sanitize_parameters(result)
        return result

    @classmethod
    def get_active(cls) -> Optional["ToolCallCollector"]:
        """
        Get the currently active collector (if any).

        Returns:
            Active ToolCallCollector or None
        """
        return getattr(cls._local, "active_collector", None)


class CallTracker:
    """Helper class for tracking individual call results."""

    def __init__(self):
        self.status = "success"
        self.result: Optional[Any] = None
        self.error: Optional[str] = None

    def set_result(self, result: Any) -> None:
        """Set successful result."""
        self.status = "success"
        self.result = result
        self.error = None

    def set_error(self, error: str) -> None:
        """Set error result."""
        self.status = "error"
        self.result = None
        self.error = error


def wrap_tool_with_collector(tool_func):
    """
    Decorator to wrap a tool function with automatic collection.

    This decorator automatically records tool calls to the active
    collector (if any).

    Args:
        tool_func: The tool function to wrap

    Returns:
        Wrapped function that records calls
    """
    import functools

    @functools.wraps(tool_func)
    async def wrapper(*args, **kwargs):
        collector = ToolCallCollector.get_active()
        tool_name = tool_func.__name__

        # Build parameters dict from kwargs
        parameters = dict(kwargs)

        if collector is None:
            # No active collector, just execute
            return await tool_func(*args, **kwargs)

        start_time = time.perf_counter()
        try:
            result = await tool_func(*args, **kwargs)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            collector.record_call(
                tool_name=tool_name,
                parameters=parameters,
                status="success",
                result=result,
                execution_time_ms=elapsed_ms,
            )
            return result
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            collector.record_call(
                tool_name=tool_name,
                parameters=parameters,
                status="error",
                error=str(e),
                execution_time_ms=elapsed_ms,
            )
            raise

    return wrapper
