"""
Task reference resolution module (T052, T053).

Resolves natural language task references to task IDs.
Handles exact matches, partial matches, pronouns, and disambiguation.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from chatbot.agent.models import ConversationContext


class TaskResolutionStatus(str, Enum):
    """Status of task resolution attempt."""

    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"


class TaskResolutionResult(BaseModel):
    """Result of attempting to resolve a task reference."""

    status: TaskResolutionStatus = Field(
        ...,
        description="Resolution status"
    )
    task_id: Optional[str] = Field(
        default=None,
        description="Resolved task ID (if RESOLVED)"
    )
    task: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Full task data (if RESOLVED)"
    )
    candidates: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Candidate tasks (if AMBIGUOUS)"
    )
    confidence: float = Field(
        default=0.0,
        description="Confidence score (0.0 to 1.0)"
    )
    reference_text: Optional[str] = Field(
        default=None,
        description="Original reference text"
    )

    def is_resolved(self) -> bool:
        """Check if task was successfully resolved."""
        return self.status == TaskResolutionStatus.RESOLVED

    def is_ambiguous(self) -> bool:
        """Check if reference was ambiguous."""
        return self.status == TaskResolutionStatus.AMBIGUOUS


# Patterns that indicate pronoun/context reference
PRONOUN_PATTERNS = [
    r"^(it|that|this)$",
    r"^that\s+(one|task)$",
    r"^the\s+task$",
    r"^(my\s+)?last\s+(one|task)$",
    r"^the\s+same\s+(one|task)$",
]


def resolve_task_reference(
    reference: str,
    tasks: List[Dict[str, Any]],
    context: Optional[ConversationContext] = None,
) -> TaskResolutionResult:
    """
    Resolve a natural language task reference to a task ID.

    Resolution strategy:
    1. Check if reference is a pronoun -> use context
    2. Try exact title match
    3. Try partial title match
    4. Try description match
    5. Return ambiguous if multiple matches
    6. Return not found if no matches

    Args:
        reference: Natural language reference text
        tasks: List of user's tasks
        context: Conversation context for pronoun resolution

    Returns:
        TaskResolutionResult with status and resolved task or candidates
    """
    if not reference or not tasks:
        return TaskResolutionResult(
            status=TaskResolutionStatus.NOT_FOUND,
            reference_text=reference,
        )

    reference_lower = reference.lower().strip()

    # Step 1: Check for pronoun reference
    if _is_pronoun_reference(reference_lower):
        return _resolve_from_context(reference, tasks, context)

    # Step 2: Try exact title match
    exact_match = _find_exact_match(reference_lower, tasks)
    if exact_match:
        return TaskResolutionResult(
            status=TaskResolutionStatus.RESOLVED,
            task_id=exact_match["id"],
            task=exact_match,
            confidence=1.0,
            reference_text=reference,
        )

    # Step 3-4: Find all matching tasks
    matches = find_matching_tasks(reference, tasks)

    if len(matches) == 1:
        # Single match - resolved
        return TaskResolutionResult(
            status=TaskResolutionStatus.RESOLVED,
            task_id=matches[0]["id"],
            task=matches[0],
            confidence=0.8,
            reference_text=reference,
        )

    if len(matches) > 1:
        # Multiple matches - ambiguous
        return TaskResolutionResult(
            status=TaskResolutionStatus.AMBIGUOUS,
            candidates=matches,
            reference_text=reference,
        )

    # No matches found
    return TaskResolutionResult(
        status=TaskResolutionStatus.NOT_FOUND,
        reference_text=reference,
    )


def _is_pronoun_reference(text: str) -> bool:
    """Check if text is a pronoun reference."""
    for pattern in PRONOUN_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    return False


def _resolve_from_context(
    reference: str,
    tasks: List[Dict[str, Any]],
    context: Optional[ConversationContext],
) -> TaskResolutionResult:
    """Resolve pronoun reference from conversation context."""
    if not context or not context.last_mentioned_task_id:
        return TaskResolutionResult(
            status=TaskResolutionStatus.NOT_FOUND,
            reference_text=reference,
        )

    # Find the task by ID
    task_id = context.last_mentioned_task_id
    for task in tasks:
        if task.get("id") == task_id:
            return TaskResolutionResult(
                status=TaskResolutionStatus.RESOLVED,
                task_id=task_id,
                task=task,
                confidence=0.9,  # Slightly lower for context-based
                reference_text=reference,
            )

    # Task ID in context but not in current list (deleted?)
    return TaskResolutionResult(
        status=TaskResolutionStatus.NOT_FOUND,
        reference_text=reference,
    )


def _find_exact_match(
    reference_lower: str,
    tasks: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Find task with exact title match."""
    for task in tasks:
        title = task.get("title", "").lower()
        if title == reference_lower:
            return task
    return None


def find_matching_tasks(
    reference: str,
    tasks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Find all tasks matching the reference.

    Searches in title and description with word boundary awareness.

    Args:
        reference: Search reference
        tasks: List of tasks to search

    Returns:
        List of matching tasks
    """
    if not reference or not tasks:
        return []

    reference_lower = reference.lower().strip()
    matches = []

    # Create word boundary pattern
    # Escape special regex chars and add word boundaries
    escaped = re.escape(reference_lower)
    pattern = rf"\b{escaped}\b"

    for task in tasks:
        title = task.get("title", "").lower()
        description = (task.get("description") or "").lower()

        # Check title first (higher priority)
        if re.search(pattern, title, re.IGNORECASE):
            matches.append(task)
        # Check description if not already matched
        elif re.search(pattern, description, re.IGNORECASE):
            matches.append(task)

    return matches


def format_disambiguation_prompt(candidates: List[Dict[str, Any]]) -> str:
    """
    Format a prompt asking user to choose from candidates.

    Args:
        candidates: List of matching tasks

    Returns:
        Formatted disambiguation prompt
    """
    lines = [f"I found {len(candidates)} tasks that might match:\n"]

    for i, task in enumerate(candidates, 1):
        title = task.get("title", "Untitled")
        lines.append(f"{i}. {title}")

    lines.append("\nWhich one did you mean? (say the number or be more specific)")

    return "\n".join(lines)


def extract_task_id_from_selection(
    user_input: str,
    candidates: List[Dict[str, Any]],
) -> Optional[str]:
    """
    Extract task ID from user's selection.

    Handles numeric selection (e.g., "1", "the first one") or
    title clarification.

    Args:
        user_input: User's response to disambiguation
        candidates: Candidate tasks

    Returns:
        Selected task ID or None
    """
    if not user_input or not candidates:
        return None

    user_input_lower = user_input.lower().strip()

    # Try numeric selection
    number_match = re.match(r"^(\d+)$", user_input_lower)
    if number_match:
        index = int(number_match.group(1)) - 1
        if 0 <= index < len(candidates):
            return candidates[index].get("id")

    # Try ordinal selection
    ordinals = {
        "first": 0, "1st": 0,
        "second": 1, "2nd": 1,
        "third": 2, "3rd": 2,
        "fourth": 3, "4th": 3,
        "fifth": 4, "5th": 4,
    }
    for word, index in ordinals.items():
        if word in user_input_lower and index < len(candidates):
            return candidates[index].get("id")

    # Try title matching
    for task in candidates:
        title = task.get("title", "").lower()
        if user_input_lower in title or title in user_input_lower:
            return task.get("id")

    return None
