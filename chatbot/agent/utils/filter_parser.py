"""
Filter parsing module for task queries (T041, T042).

Parses status and date filters from natural language input.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Literal, Optional, Tuple, Any

from chatbot.agent.utils.date_parser import parse_relative_date


# Status filter patterns (case-insensitive)
STATUS_PATTERNS = {
    "pending": [
        r"\bpending\b",
        r"\bnot\s+done\b",
        r"\bincomplete\b",
        r"\bunfinished\b",
        r"\bopen\b",
        r"\bactive\b",
        r"\btodo\b",
        r"\bto\s+do\b",
        r"\bneed\s+to\s+do\b",
        r"\bhave\s+to\s+do\b",
    ],
    "completed": [
        r"\bcompleted?\b",
        r"\bdone\b",
        r"\bfinished\b",
        r"\bclosed\b",
        r"\bcheck(?:ed)?\s+off\b",
    ],
    "all": [
        r"\ball\b",
        r"\beverything\b",
        r"\bfull\s+list\b",
    ],
}

# Date filter patterns
DATE_FILTER_PATTERNS = [
    # Due today/tomorrow/etc
    (r"\bdue\s+(today|tomorrow|next\s+week)\b", "due_date"),
    (r"\bdue\s+on\s+(\w+)\b", "due_date"),
    # Overdue
    (r"\boverdue\b", "overdue"),
    (r"\bpast\s+due\b", "overdue"),
    (r"\blate\b", "overdue"),
    # Created today/this week
    (r"\bcreated\s+(today|this\s+week|yesterday)\b", "created_date"),
    (r"\bnew\b", "recent"),
    (r"\brecent(?:ly)?\b", "recent"),
]


def parse_status_filter(text: str) -> Literal["pending", "completed", "all"]:
    """
    Parse status filter from natural language.

    Args:
        text: User input text

    Returns:
        Status filter value
    """
    if not text:
        return "all"

    text_lower = text.lower()

    # Check each status category
    for status, patterns in STATUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return status  # type: ignore

    # Default to all if no filter detected
    return "all"


def parse_date_filter(text: str, reference_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Parse date filter from natural language.

    Args:
        text: User input text
        reference_date: Reference date for relative calculations

    Returns:
        Dict with filter type and value
    """
    if not text:
        return {}

    ref = reference_date or datetime.now(timezone.utc)
    text_lower = text.lower()

    # Check for overdue
    if re.search(r"\boverdue\b|\bpast\s+due\b|\blate\b", text_lower):
        return {
            "filter_type": "overdue",
            "due_before": ref,
        }

    # Check for due date patterns
    due_match = re.search(r"\bdue\s+(today|tomorrow|next\s+week)\b", text_lower)
    if due_match:
        date_expr = due_match.group(1)
        parsed_date = parse_relative_date(date_expr, ref)
        if parsed_date:
            return {
                "filter_type": "due_date",
                "due_date": parsed_date,
            }

    # Check for "due on <day>"
    due_on_match = re.search(r"\bdue\s+on\s+(\w+)\b", text_lower)
    if due_on_match:
        day_expr = due_on_match.group(1)
        parsed_date = parse_relative_date(day_expr, ref)
        if parsed_date:
            return {
                "filter_type": "due_date",
                "due_date": parsed_date,
            }

    # Check for recent/new
    if re.search(r"\bnew\b|\brecent(?:ly)?\b", text_lower):
        return {
            "filter_type": "recent",
            "created_after": ref - timedelta(days=7),
        }

    # Check for created today
    created_match = re.search(r"\bcreated\s+(today|this\s+week|yesterday)\b", text_lower)
    if created_match:
        expr = created_match.group(1)
        if expr == "today":
            return {
                "filter_type": "created_date",
                "created_after": ref.replace(hour=0, minute=0, second=0, microsecond=0),
            }
        elif expr == "yesterday":
            yesterday = ref - timedelta(days=1)
            return {
                "filter_type": "created_date",
                "created_after": yesterday.replace(hour=0, minute=0, second=0, microsecond=0),
                "created_before": ref.replace(hour=0, minute=0, second=0, microsecond=0),
            }
        elif expr == "this week":
            # Start of week (Monday)
            days_since_monday = ref.weekday()
            week_start = ref - timedelta(days=days_since_monday)
            return {
                "filter_type": "created_date",
                "created_after": week_start.replace(hour=0, minute=0, second=0, microsecond=0),
            }

    return {}


def parse_list_filters(text: str) -> Tuple[Literal["pending", "completed", "all"], Dict[str, Any]]:
    """
    Parse all filters from a list command.

    Args:
        text: User input text

    Returns:
        Tuple of (status_filter, date_filter_dict)
    """
    status = parse_status_filter(text)
    date_filter = parse_date_filter(text)
    return status, date_filter


def describe_filters(
    status: str,
    date_filter: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Generate human-readable filter description.

    Args:
        status: Status filter value
        date_filter: Date filter dict

    Returns:
        Human-readable description or None if no filters
    """
    parts = []

    if status != "all":
        parts.append(status)

    if date_filter:
        filter_type = date_filter.get("filter_type")
        if filter_type == "overdue":
            parts.append("overdue")
        elif filter_type == "due_date":
            due_date = date_filter.get("due_date")
            if due_date:
                parts.append(f"due {due_date.strftime('%b %d')}")
        elif filter_type == "recent":
            parts.append("recent")
        elif filter_type == "created_date":
            parts.append("recently created")

    if parts:
        return " ".join(parts)

    return None
