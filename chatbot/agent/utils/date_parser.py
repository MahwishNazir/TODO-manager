"""
Natural language date parsing module (T032).

Parses relative date expressions like "tomorrow", "next week" into datetime objects.
Implements FR-060 determinism requirements.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


# Supported relative date expressions (case-insensitive)
RELATIVE_DATE_PATTERNS = {
    "today": 0,
    "tomorrow": 1,
    "day after tomorrow": 2,
    "next week": 7,
    "in a week": 7,
    "next monday": None,  # Special handling
    "next tuesday": None,
    "next wednesday": None,
    "next thursday": None,
    "next friday": None,
    "next saturday": None,
    "next sunday": None,
}

# Day name to weekday number (Monday = 0)
DAY_NAME_TO_WEEKDAY = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse_relative_date(expression: str, reference_date: Optional[datetime] = None) -> Optional[datetime]:
    """
    Parse a relative date expression into a datetime.

    Implements deterministic date parsing (FR-060):
    - "tomorrow" always means the next calendar day
    - "today" always means the current calendar day
    - "next week" always means 7 days from now

    Args:
        expression: Natural language date expression
        reference_date: Reference date for relative calculations (default: now)

    Returns:
        Parsed datetime or None if not a recognized expression
    """
    if not expression:
        return None

    # Use current time as reference if not provided
    ref = reference_date or datetime.now(timezone.utc)
    ref_date = ref.replace(hour=0, minute=0, second=0, microsecond=0)

    # Normalize expression
    expr_lower = expression.lower().strip()

    # Check for simple relative dates
    if expr_lower == "today":
        return ref_date

    if expr_lower == "tomorrow":
        return ref_date + timedelta(days=1)

    if expr_lower == "day after tomorrow":
        return ref_date + timedelta(days=2)

    if expr_lower in ("next week", "in a week"):
        return ref_date + timedelta(days=7)

    # Check for "next <day>" pattern
    next_day_match = re.match(r"next\s+(\w+)", expr_lower)
    if next_day_match:
        day_name = next_day_match.group(1)
        if day_name in DAY_NAME_TO_WEEKDAY:
            return _get_next_weekday(ref_date, DAY_NAME_TO_WEEKDAY[day_name])

    # Check for "in X days" pattern
    in_days_match = re.match(r"in\s+(\d+)\s+days?", expr_lower)
    if in_days_match:
        days = int(in_days_match.group(1))
        return ref_date + timedelta(days=days)

    # Check for just day name (e.g., "monday")
    if expr_lower in DAY_NAME_TO_WEEKDAY:
        return _get_next_weekday(ref_date, DAY_NAME_TO_WEEKDAY[expr_lower])

    return None


def _get_next_weekday(ref_date: datetime, target_weekday: int) -> datetime:
    """
    Get the next occurrence of a weekday.

    If today is the target weekday, returns next week's occurrence.

    Args:
        ref_date: Reference date
        target_weekday: Target weekday (0=Monday, 6=Sunday)

    Returns:
        Next occurrence of the target weekday
    """
    current_weekday = ref_date.weekday()
    days_ahead = target_weekday - current_weekday

    # If the target day is today or earlier this week, go to next week
    if days_ahead <= 0:
        days_ahead += 7

    return ref_date + timedelta(days=days_ahead)


def parse_date_expression(text: str, reference_date: Optional[datetime] = None) -> Tuple[Optional[datetime], str]:
    """
    Extract and parse a date expression from text.

    Scans text for date expressions and returns the parsed date
    along with the remaining text.

    Args:
        text: Text potentially containing a date expression
        reference_date: Reference date for relative calculations

    Returns:
        Tuple of (parsed_date, text_without_date)
    """
    if not text:
        return None, text

    text_lower = text.lower()

    # Check for common patterns
    date_patterns = [
        (r"\b(tomorrow)\b", "tomorrow"),
        (r"\b(today)\b", "today"),
        (r"\b(next week)\b", "next week"),
        (r"\b(in a week)\b", "in a week"),
        (r"\b(day after tomorrow)\b", "day after tomorrow"),
        (r"\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", None),
        (r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", None),
        (r"\bin\s+(\d+)\s+days?\b", None),
    ]

    for pattern, simple_expr in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            matched_text = match.group(0)
            expr = simple_expr or matched_text
            parsed = parse_relative_date(expr, reference_date)
            if parsed:
                # Remove the date expression from text
                cleaned_text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                # Clean up extra whitespace
                cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
                return parsed, cleaned_text

    return None, text


def format_date_for_display(dt: datetime) -> str:
    """
    Format a datetime for user-friendly display.

    Args:
        dt: Datetime to format

    Returns:
        Human-readable date string
    """
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    diff = (dt.replace(hour=0, minute=0, second=0, microsecond=0) - today).days

    if diff == 0:
        return "today"
    elif diff == 1:
        return "tomorrow"
    elif diff == -1:
        return "yesterday"
    elif 0 < diff <= 7:
        return dt.strftime("%A")  # Day name
    else:
        return dt.strftime("%B %d, %Y")  # Month Day, Year
