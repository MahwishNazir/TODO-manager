"""
Confirmation flow management module (T062-T066).

Handles confirmation requests for destructive operations like delete.
Implements FR-042, FR-043 confirmation requirements.
"""

import re
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from chatbot.agent.config import get_settings
from chatbot.agent.models import ConfirmationState, ConfirmationStatus
from chatbot.agent.formatters import (
    format_delete_confirmation_request,
    format_bulk_operation_confirmation,
)


class ConfirmationResponse(str, Enum):
    """Parsed confirmation response type."""

    YES = "YES"
    NO = "NO"
    UNCLEAR = "UNCLEAR"


# Patterns for parsing confirmation responses
YES_PATTERNS = [
    r"^y(es)?$",
    r"^yeah?$",
    r"^yep$",
    r"^sure$",
    r"^ok(ay)?$",
    r"^confirm$",
    r"^proceed$",
    r"^go\s*ahead$",
    r"^do\s*it$",
    r"^execute$",
    r"^affirmative$",
]

NO_PATTERNS = [
    r"^n(o)?$",
    r"^nope$",
    r"^nah$",
    r"^cancel$",
    r"^abort$",
    r"^stop$",
    r"^don'?t$",
    r"^never\s*mind$",
    r"^negative$",
]


def parse_confirmation_response(text: str) -> ConfirmationResponse:
    """
    Parse user response to confirmation request (FR-042, FR-043).

    Recognizes variations of yes/no responses including:
    - Explicit: "yes", "no", "y", "n"
    - Colloquial: "yeah", "nope", "sure", "nah"
    - Commands: "proceed", "cancel", "abort"

    Args:
        text: User's response text

    Returns:
        ConfirmationResponse enum value
    """
    if not text:
        return ConfirmationResponse.UNCLEAR

    text_lower = text.lower().strip()

    # Check yes patterns
    for pattern in YES_PATTERNS:
        if re.match(pattern, text_lower):
            return ConfirmationResponse.YES

    # Check no patterns
    for pattern in NO_PATTERNS:
        if re.match(pattern, text_lower):
            return ConfirmationResponse.NO

    return ConfirmationResponse.UNCLEAR


class ConfirmationManager:
    """
    Manages confirmation flow for destructive operations.

    Handles state transitions, timeout expiry, and response parsing.
    """

    def __init__(
        self,
        state: Optional[ConfirmationState] = None,
        timeout_seconds: Optional[int] = None,
    ):
        """
        Initialize confirmation manager.

        Args:
            state: Existing state to manage (creates new if None)
            timeout_seconds: Confirmation timeout (default from settings)
        """
        self.state = state or ConfirmationState()
        settings = get_settings()
        self.timeout_seconds = timeout_seconds or settings.confirmation_timeout_seconds

    def request_delete_confirmation(
        self,
        task: Dict[str, Any],
    ) -> str:
        """
        Request confirmation for task deletion.

        Sets state to AWAITING_DELETE and returns confirmation message.

        Args:
            task: Task to be deleted

        Returns:
            Formatted confirmation request message
        """
        task_id = task.get("id", "")
        title = task.get("title", "Untitled")

        self.state.set_awaiting_delete(
            task_ids=[task_id],
            description=f"Delete '{title}'"
        )

        return format_delete_confirmation_request(task)

    def request_bulk_confirmation(
        self,
        operation: str,
        tasks: List[Dict[str, Any]],
    ) -> str:
        """
        Request confirmation for bulk operation.

        Args:
            operation: Operation type (e.g., "delete", "complete")
            tasks: Tasks affected by the operation

        Returns:
            Formatted confirmation request message
        """
        task_ids = [t.get("id", "") for t in tasks]

        self.state.set_awaiting_bulk(
            action=operation,
            task_ids=task_ids,
            description=f"{operation.capitalize()} {len(tasks)} tasks"
        )

        return format_bulk_operation_confirmation(operation, tasks)

    def request_plan_approval(
        self,
        plan_id: str,
        description: str,
    ) -> None:
        """
        Request approval for multi-step plan.

        Args:
            plan_id: Plan identifier
            description: Plan description
        """
        self.state.set_awaiting_plan_approval(plan_id, description)

    def has_pending_confirmation(self) -> bool:
        """
        Check if there's a pending confirmation.

        Also handles auto-expiration of stale confirmations.

        Returns:
            True if confirmation is pending and not expired
        """
        if self.state.is_idle():
            return False

        # Check for expiration
        if self.state.is_expired(self.timeout_seconds):
            self._expire()
            return False

        return True

    def get_pending_action(self) -> Optional[str]:
        """Get the pending action type, if any."""
        if not self.has_pending_confirmation():
            return None
        return self.state.pending_action

    def get_affected_ids(self) -> List[str]:
        """Get IDs affected by pending action."""
        if not self.has_pending_confirmation():
            return []
        return self.state.affected_ids

    def process_response(self, response: str) -> Dict[str, Any]:
        """
        Process user's confirmation response.

        Args:
            response: User's response text

        Returns:
            Dict with:
                - confirmed: bool (True if confirmed)
                - cancelled: bool (True if cancelled)
                - unclear: bool (True if response was unclear)
                - action: str (pending action type)
                - affected_ids: List[str] (affected task IDs)
        """
        if not self.has_pending_confirmation():
            return {
                "confirmed": False,
                "cancelled": False,
                "unclear": False,
                "action": None,
                "affected_ids": [],
                "message": "No pending confirmation.",
            }

        parsed = parse_confirmation_response(response)
        action = self.state.pending_action
        affected_ids = self.state.affected_ids.copy()

        if parsed == ConfirmationResponse.YES:
            self.confirm()
            return {
                "confirmed": True,
                "cancelled": False,
                "unclear": False,
                "action": action,
                "affected_ids": affected_ids,
                "message": "Confirmed.",
            }

        if parsed == ConfirmationResponse.NO:
            self.cancel()
            return {
                "confirmed": False,
                "cancelled": True,
                "unclear": False,
                "action": action,
                "affected_ids": affected_ids,
                "message": "Cancelled.",
            }

        # Unclear response
        return {
            "confirmed": False,
            "cancelled": False,
            "unclear": True,
            "action": action,
            "affected_ids": affected_ids,
            "message": "I didn't understand. Please reply 'yes' to confirm or 'no' to cancel.",
        }

    def confirm(self) -> bool:
        """
        Confirm the pending action.

        Returns:
            True if there was a pending action to confirm
        """
        if self.state.is_idle():
            return False

        self.state.reset()
        return True

    def cancel(self) -> bool:
        """
        Cancel the pending action.

        Returns:
            True if there was a pending action to cancel
        """
        if self.state.is_idle():
            return False

        self.state.reset()
        return True

    def _expire(self) -> None:
        """Handle expiration of pending confirmation."""
        self.state.reset()

    def get_expiration_message(self) -> str:
        """Get message for expired confirmation."""
        return (
            "The previous confirmation request has expired. "
            "Please try your request again."
        )


def check_requires_confirmation(action: str, count: int = 1) -> bool:
    """
    Check if an action requires confirmation.

    Args:
        action: Action type (delete, bulk_complete, etc.)
        count: Number of items affected

    Returns:
        True if confirmation is required
    """
    # Delete always requires confirmation (FR-042)
    if action == "delete":
        return True

    # Bulk operations (3+ items) require confirmation
    if count >= 3:
        return True

    return False


def format_confirmation_expired_message() -> str:
    """Get message when confirmation has expired."""
    return (
        "That confirmation request has expired. "
        "Please try your request again if you'd still like to proceed."
    )


def format_confirmation_cancelled_message(action: str) -> str:
    """Get message when user cancels confirmation."""
    return f"Okay, I've cancelled the {action}. Your tasks are unchanged."
