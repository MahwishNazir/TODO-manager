"""
Multi-step execution module (T072-T078).

Handles multi-intent detection, plan building, and sequential execution.
Implements FR-030 through FR-034.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from chatbot.agent.models import (
    ExecutionPlan,
    PlanStep,
    StepResult,
    PlanStatus,
    ActionType,
)
from chatbot.agent.formatters import format_plan_preview, format_plan_result


class IntentType(str, Enum):
    """Types of user intents."""

    ADD = "ADD"
    LIST = "LIST"
    UPDATE = "UPDATE"
    COMPLETE = "COMPLETE"
    DELETE = "DELETE"
    UNKNOWN = "UNKNOWN"


class Intent(BaseModel):
    """Detected user intent from message."""

    type: IntentType = Field(..., description="Intent type")
    reference: Optional[str] = Field(
        default=None,
        description="Task reference (title, ID, or pronoun)"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters"
    )
    raw_text: Optional[str] = Field(
        default=None,
        description="Original text segment"
    )


# Intent detection patterns
INTENT_PATTERNS = {
    IntentType.ADD: [
        r"create\s+(?:a\s+)?task",
        r"add\s+(?:a\s+)?task",
        r"add\s+(?:a\s+)?(?:new\s+)?todo",
        r"remind\s+me\s+to",
        r"new\s+task",
        r"make\s+a\s+task",
    ],
    IntentType.LIST: [
        r"show\s+(?:my\s+)?tasks",
        r"list\s+(?:my\s+)?tasks",
        r"what\s+are\s+my\s+tasks",
        r"what\s+do\s+i\s+(?:have|need)\s+to\s+do",
        r"show\s+(?:me\s+)?(?:my\s+)?(?:todo|list)",
        r"display\s+tasks",
    ],
    IntentType.UPDATE: [
        r"update\s+(?:the\s+)?task",
        r"change\s+(?:the\s+)?task",
        r"edit\s+(?:the\s+)?task",
        r"modify\s+(?:the\s+)?task",
        r"rename\s+(?:the\s+)?task",
    ],
    IntentType.COMPLETE: [
        r"mark\s+.+\s+(?:as\s+)?(?:done|complete|finished)",
        r"complete\s+(?:the\s+)?(?:task)?",
        r"finish\s+(?:the\s+)?(?:task)?",
        r"check\s+off",
        r"i\s+(?:finished|completed|done)",
        r"done\s+with",
    ],
    IntentType.DELETE: [
        r"delete\s+(?:the\s+)?(?:task)?",
        r"remove\s+(?:the\s+)?(?:task)?",
        r"cancel\s+(?:the\s+)?(?:task)?",
        r"get\s+rid\s+of",
    ],
}

# Standard execution order (FR-031)
EXECUTION_ORDER = [
    IntentType.ADD,
    IntentType.UPDATE,
    IntentType.COMPLETE,
    IntentType.DELETE,
    IntentType.LIST,
]


def detect_intents(text: str) -> List[Intent]:
    """
    Detect intents from user message.

    Handles messages with multiple intents like:
    "Create a task and mark groceries as done"

    Args:
        text: User message text

    Returns:
        List of detected intents
    """
    if not text:
        return []

    text_lower = text.lower()
    intents = []
    matched_positions: List[Tuple[int, int, IntentType]] = []

    # Find all pattern matches
    for intent_type, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text_lower):
                matched_positions.append((match.start(), match.end(), intent_type))

    # Sort by position and deduplicate overlapping
    matched_positions.sort(key=lambda x: x[0])

    last_end = -1
    for start, end, intent_type in matched_positions:
        if start >= last_end:  # Non-overlapping
            # Extract reference text after the pattern
            remaining = text[end:].strip()
            reference = _extract_reference(remaining, intent_type)

            intents.append(Intent(
                type=intent_type,
                reference=reference,
                raw_text=text[start:end],
            ))
            last_end = end

    return intents


def _extract_reference(text: str, intent_type: IntentType) -> Optional[str]:
    """Extract task reference from text following an intent pattern."""
    if not text:
        return None

    # Clean up text
    text = text.strip()

    # Stop at common conjunctions
    for stop_word in [" and ", " then ", " after that ", " also "]:
        if stop_word in text.lower():
            text = text[:text.lower().index(stop_word)]

    # Extract quoted content
    quoted_match = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted_match:
        return quoted_match.group(1)

    # Extract "called X" or "named X"
    called_match = re.search(r"(?:called|named)\s+['\"]?([^'\"]+)['\"]?", text, re.IGNORECASE)
    if called_match:
        return called_match.group(1).strip()

    # For simple cases, take first few words
    words = text.split()[:5]
    if words:
        return " ".join(words).rstrip(".,!?")

    return None


def build_execution_plan(
    intents: List[Intent],
    user_id: str,
) -> ExecutionPlan:
    """
    Build an execution plan from detected intents (FR-030).

    Orders intents according to standard execution order:
    ADD → UPDATE → COMPLETE → DELETE → LIST

    Args:
        intents: Detected intents
        user_id: User ID for the plan

    Returns:
        ExecutionPlan with ordered steps
    """
    plan = ExecutionPlan(user_id=user_id)

    # Sort intents by execution order
    ordered_intents = sorted(
        intents,
        key=lambda i: EXECUTION_ORDER.index(i.type) if i.type in EXECUTION_ORDER else 99
    )

    for intent in ordered_intents:
        action_type = _intent_to_action(intent.type)
        params = {
            "reference": intent.reference,
            **intent.params,
        }
        plan.add_step(action_type, params)

    return plan


def _intent_to_action(intent_type: IntentType) -> ActionType:
    """Convert intent type to action type."""
    mapping = {
        IntentType.ADD: ActionType.ADD,
        IntentType.LIST: ActionType.LIST,
        IntentType.UPDATE: ActionType.UPDATE,
        IntentType.COMPLETE: ActionType.COMPLETE,
        IntentType.DELETE: ActionType.DELETE,
    }
    return mapping.get(intent_type, ActionType.LIST)


def format_plan_for_approval(plan: ExecutionPlan) -> str:
    """
    Format execution plan for user approval (FR-030).

    Args:
        plan: Execution plan to format

    Returns:
        Formatted plan preview string
    """
    steps = []
    for step in plan.steps:
        description = _describe_step(step)
        steps.append({
            "action": step.action.value,
            "description": description,
        })

    return format_plan_preview(steps)


def _describe_step(step: PlanStep) -> str:
    """Generate human-readable description of a step."""
    action = step.action
    params = step.params
    reference = params.get("reference", "")

    descriptions = {
        ActionType.ADD: f"Create task '{reference}'" if reference else "Create a new task",
        ActionType.LIST: "Show your tasks",
        ActionType.UPDATE: f"Update '{reference}'" if reference else "Update a task",
        ActionType.COMPLETE: f"Mark '{reference}' as complete" if reference else "Complete a task",
        ActionType.DELETE: f"Delete '{reference}'" if reference else "Delete a task",
    }

    return descriptions.get(action, f"{action.value} task")


async def execute_plan_step(
    step: PlanStep,
    user_id: str,
    tools: Dict[str, Any],
) -> StepResult:
    """
    Execute a single plan step (FR-031).

    Args:
        step: Step to execute
        user_id: User ID
        tools: Tool functions dict

    Returns:
        StepResult with execution outcome
    """
    action = step.action
    params = step.params

    try:
        tool_name = action.value.lower() + "_task"
        if tool_name == "list_task":
            tool_name = "list_tasks"

        if tool_name not in tools:
            return StepResult(
                order=step.order,
                success=False,
                error=f"Unknown action: {action.value}",
            )

        tool_fn = tools[tool_name]
        result = await tool_fn(user_id=user_id, **params)

        if result.get("success"):
            return StepResult(
                order=step.order,
                success=True,
                result=result.get("data"),
            )
        else:
            return StepResult(
                order=step.order,
                success=False,
                error=result.get("error", {}).get("message", "Unknown error"),
            )

    except Exception as e:
        return StepResult(
            order=step.order,
            success=False,
            error=str(e),
        )


async def execute_plan(
    plan: ExecutionPlan,
    user_id: str,
    tools: Dict[str, Any],
    halt_on_failure: bool = True,
) -> Tuple[bool, List[StepResult]]:
    """
    Execute all steps in a plan sequentially (FR-031, FR-032, FR-033).

    Args:
        plan: Execution plan
        user_id: User ID
        tools: Tool functions dict
        halt_on_failure: Stop on first failure (FR-033)

    Returns:
        Tuple of (all_success, list of results)
    """
    results = []
    all_success = True

    for step in plan.steps:
        result = await execute_plan_step(step, user_id, tools)
        results.append(result)
        plan.record_step_result(step.order, result.success, result.result or {"error": result.error})

        if not result.success:
            all_success = False
            if halt_on_failure:
                break  # FR-033: Halt on failure

    return all_success, results


def format_execution_results(
    plan: ExecutionPlan,
    results: List[StepResult],
) -> str:
    """
    Format execution results for user (FR-032).

    Args:
        plan: Executed plan
        results: Execution results

    Returns:
        Formatted result string
    """
    steps = [
        {"action": step.action.value, "description": _describe_step(step)}
        for step in plan.steps
    ]

    result_dicts = [
        {"success": r.success, "error": r.error}
        for r in results
    ]

    return format_plan_result(steps, result_dicts)


def should_require_plan_approval(intents: List[Intent]) -> bool:
    """
    Check if plan approval is required (FR-030).

    Plan approval required when 2+ tool calls will be made.

    Args:
        intents: Detected intents

    Returns:
        True if plan approval should be requested
    """
    # Count intents that result in tool calls
    tool_call_intents = [
        i for i in intents
        if i.type in [IntentType.ADD, IntentType.UPDATE, IntentType.COMPLETE, IntentType.DELETE]
    ]

    return len(tool_call_intents) >= 2
