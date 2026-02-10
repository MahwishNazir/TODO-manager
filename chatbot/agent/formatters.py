"""
Response formatting module (T034).

Formats agent responses for task operations in a user-friendly way.
"""

from typing import Any, Dict, List, Optional


def format_task_created(task: Dict[str, Any]) -> str:
    """
    Format a confirmation message for task creation.

    Args:
        task: Created task data

    Returns:
        Formatted confirmation message
    """
    title = task.get("title", "Untitled task")
    description = task.get("description")

    message = f"I've created the task '{title}'"

    if description:
        # Truncate long descriptions
        desc_preview = description[:100] + "..." if len(description) > 100 else description
        message += f" with description: {desc_preview}"

    message += "."

    return message


def format_task_updated(task: Dict[str, Any], changes: Dict[str, Any]) -> str:
    """
    Format a confirmation message for task update.

    Shows before/after for changed fields (FR-041).

    Args:
        task: Updated task data
        changes: Dict of field name to (old_value, new_value) tuples

    Returns:
        Formatted confirmation message
    """
    title = task.get("title", "Untitled task")
    message = f"I've updated '{title}':\n"

    for field, (old_val, new_val) in changes.items():
        message += f"- {field}: '{old_val}' -> '{new_val}'\n"

    return message.strip()


def format_task_completed(task: Dict[str, Any]) -> str:
    """
    Format a confirmation message for task completion.

    Args:
        task: Completed task data

    Returns:
        Formatted confirmation message
    """
    title = task.get("title", "Untitled task")
    return f"Great! I've marked '{title}' as complete."


def format_task_deleted(task: Dict[str, Any]) -> str:
    """
    Format a confirmation message for task deletion.

    Args:
        task: Deleted task data

    Returns:
        Formatted confirmation message
    """
    title = task.get("title", "Untitled task")
    return f"Done! I've deleted '{title}'."


def format_task_list(
    tasks: List[Dict[str, Any]],
    total_count: int,
    filter_description: Optional[str] = None,
) -> str:
    """
    Format a list of tasks for display.

    Uses emoji status indicators for visual clarity.

    Args:
        tasks: List of task data
        total_count: Total number of tasks (may differ from len(tasks) if paginated)
        filter_description: Description of any active filter

    Returns:
        Formatted task list
    """
    if not tasks:
        return _format_empty_task_list(filter_description)

    lines = []

    # Header with filter info
    if filter_description:
        lines.append(f"Here are your {filter_description} tasks ({total_count} total):\n")
    else:
        lines.append(f"Here are your tasks ({total_count} total):\n")

    # Format each task
    for i, task in enumerate(tasks, 1):
        status_emoji = _get_status_emoji(task.get("status", "pending"))
        title = task.get("title", "Untitled")
        task_line = f"{status_emoji} {i}. {title}"

        # Add due date if present
        due_date = task.get("due_date")
        if due_date:
            task_line += f" (due: {due_date})"

        lines.append(task_line)

    # Pagination note
    if len(tasks) < total_count:
        remaining = total_count - len(tasks)
        lines.append(f"\n...and {remaining} more. Say 'show more' to see additional tasks.")

    return "\n".join(lines)


def _format_empty_task_list(filter_description: Optional[str] = None) -> str:
    """Format message for empty task list with helpful suggestions."""
    if filter_description:
        if "pending" in filter_description.lower():
            return (
                "You don't have any pending tasks. Nice work!\n"
                "Say 'create a task' to add a new one."
            )
        elif "completed" in filter_description.lower():
            return (
                "You haven't completed any tasks yet.\n"
                "Say 'show my pending tasks' to see what needs to be done."
            )
        else:
            return f"No tasks found matching '{filter_description}'."

    return (
        "You don't have any tasks yet.\n"
        "Say something like 'Create a task to buy groceries' to get started!"
    )


def _get_status_emoji(status: str) -> str:
    """Get emoji indicator for task status."""
    status_emojis = {
        "pending": "[ ]",  # Using text for accessibility
        "completed": "[x]",
        "in_progress": "[>]",
        "cancelled": "[-]",
    }
    return status_emojis.get(status.lower(), "[ ]")


def format_delete_confirmation_request(task: Dict[str, Any]) -> str:
    """
    Format a delete confirmation request.

    Shows task details before asking for confirmation (FR-043).

    Args:
        task: Task to be deleted

    Returns:
        Formatted confirmation request
    """
    title = task.get("title", "Untitled task")
    description = task.get("description")
    status = task.get("status", "pending")

    lines = [f"Are you sure you want to delete this task?\n"]
    lines.append(f"- Title: {title}")
    lines.append(f"- Status: {status}")

    if description:
        desc_preview = description[:100] + "..." if len(description) > 100 else description
        lines.append(f"- Description: {desc_preview}")

    lines.append("\nReply 'yes' to confirm or 'no' to cancel.")

    return "\n".join(lines)


def format_bulk_operation_confirmation(
    operation: str,
    tasks: List[Dict[str, Any]],
) -> str:
    """
    Format a bulk operation confirmation request.

    Args:
        operation: Operation type (e.g., "complete", "delete")
        tasks: Tasks affected by the operation

    Returns:
        Formatted confirmation request
    """
    count = len(tasks)
    operation_verb = operation.lower()

    lines = [f"You're about to {operation_verb} {count} tasks:\n"]

    for task in tasks[:5]:  # Show first 5 tasks
        title = task.get("title", "Untitled")
        lines.append(f"- {title}")

    if count > 5:
        lines.append(f"- ...and {count - 5} more")

    lines.append(f"\nReply 'yes' to {operation_verb} all or 'no' to cancel.")

    return "\n".join(lines)


def format_plan_preview(steps: List[Dict[str, Any]]) -> str:
    """
    Format a multi-step plan preview (FR-030).

    Args:
        steps: List of planned steps

    Returns:
        Formatted plan preview
    """
    lines = ["I'll do the following:\n"]

    for i, step in enumerate(steps, 1):
        action = step.get("action", "unknown")
        description = step.get("description", "")
        lines.append(f"{i}. {action}: {description}")

    lines.append("\nReply 'proceed' to execute or 'cancel' to abort.")

    return "\n".join(lines)


def format_plan_result(
    steps: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
) -> str:
    """
    Format the result of a multi-step plan execution (FR-032).

    Args:
        steps: Executed steps
        results: Results for each step

    Returns:
        Formatted plan result
    """
    success_count = sum(1 for r in results if r.get("success"))
    total = len(results)

    if success_count == total:
        lines = [f"All {total} steps completed successfully:\n"]
    else:
        lines = [f"{success_count} of {total} steps completed:\n"]

    for i, (step, result) in enumerate(zip(steps, results), 1):
        action = step.get("action", "unknown")
        if result.get("success"):
            lines.append(f"[x] {i}. {action} - Done")
        else:
            error = result.get("error", "Failed")
            lines.append(f"[-] {i}. {action} - {error}")

    return "\n".join(lines)
