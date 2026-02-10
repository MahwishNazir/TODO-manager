"""
Entity extraction module for task information (T033).

Extracts task titles and descriptions from natural language input.
"""

import re
from typing import Optional, Tuple


# Patterns for extracting quoted content
QUOTED_PATTERNS = [
    r'"([^"]+)"',  # Double quotes
    r"'([^']+)'",  # Single quotes
    r"`([^`]+)`",  # Backticks
]

# Patterns indicating task title follows
TITLE_PREFIXES = [
    r"create\s+(?:a\s+)?task\s+(?:to\s+|for\s+|called\s+)?",
    r"add\s+(?:a\s+)?task\s*:?\s*",
    r"add\s+",
    r"new\s+task\s*:?\s*",
    r"task\s*:?\s*",
    r"todo\s*:?\s*",
    r"remind\s+me\s+to\s+",
    r"i\s+need\s+to\s+",
    r"don't\s+(?:let\s+me\s+)?forget\s+to\s+",
    r"i\s+should\s+",
    r"i\s+want\s+to\s+",
]

# Patterns indicating description follows
DESCRIPTION_MARKERS = [
    r"\s+with\s+description\s*:?\s*",
    r"\s+-\s+",
    r"\s+:\s+",
    r"\s+description\s*:?\s*",
    r"\s+details\s*:?\s*",
]


def extract_task_title(text: str) -> Optional[str]:
    """
    Extract task title from natural language input.

    Handles various patterns:
    - Quoted titles: Create task "Buy groceries"
    - Prefixed: Create task to buy groceries
    - Direct: Add buy groceries to my list

    Args:
        text: User input text

    Returns:
        Extracted title or None
    """
    if not text:
        return None

    # Try to extract quoted content first
    for pattern in QUOTED_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    # Try prefix patterns
    text_lower = text.lower()
    for prefix in TITLE_PREFIXES:
        match = re.search(prefix, text_lower, re.IGNORECASE)
        if match:
            # Get everything after the prefix
            remaining = text[match.end():].strip()
            # Extract title (stop at description markers or end)
            title = _extract_until_marker(remaining)
            if title:
                return title

    # If no pattern matches, try to extract the main content
    # Remove common question words and return the rest
    cleaned = re.sub(
        r"^(can\s+you\s+|please\s+|could\s+you\s+|would\s+you\s+)",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    if cleaned and len(cleaned) > 2:
        return _extract_until_marker(cleaned)

    return None


def _extract_until_marker(text: str) -> Optional[str]:
    """
    Extract text until a description marker or end.

    Args:
        text: Text to extract from

    Returns:
        Extracted title
    """
    if not text:
        return None

    # Find the earliest description marker
    earliest_pos = len(text)
    for marker in DESCRIPTION_MARKERS:
        match = re.search(marker, text, re.IGNORECASE)
        if match and match.start() < earliest_pos:
            earliest_pos = match.start()

    title = text[:earliest_pos].strip()

    # Clean up the title
    title = re.sub(r"\s+", " ", title)  # Normalize whitespace
    title = re.sub(r"[.!?]+$", "", title)  # Remove trailing punctuation
    title = title.strip()

    # Validate title length
    if title and 1 <= len(title) <= 500:
        return title

    return None


def extract_task_description(text: str) -> Optional[str]:
    """
    Extract task description from natural language input.

    Handles various patterns:
    - Explicit: with description "Get milk and bread"
    - Implicit: Create task "Buy groceries" - need for breakfast

    Args:
        text: User input text

    Returns:
        Extracted description or None
    """
    if not text:
        return None

    # Try to find description after markers
    for marker in DESCRIPTION_MARKERS:
        match = re.search(marker, text, re.IGNORECASE)
        if match:
            description = text[match.end():].strip()
            # Try to extract quoted content first
            for pattern in QUOTED_PATTERNS:
                quoted_match = re.search(pattern, description)
                if quoted_match:
                    return quoted_match.group(1).strip()
            # Otherwise return the rest
            if description:
                return description[:5000]  # Max description length

    # Check for sentence after title
    # If there's a second sentence, it might be the description
    sentences = re.split(r"[.!?]\s+", text)
    if len(sentences) > 1:
        # Skip the first sentence (likely the title)
        potential_desc = " ".join(sentences[1:]).strip()
        if potential_desc and len(potential_desc) >= 10:
            return potential_desc[:5000]

    return None


def extract_task_info(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract both title and description from natural language input.

    Args:
        text: User input text

    Returns:
        Tuple of (title, description)
    """
    title = extract_task_title(text)
    description = extract_task_description(text)
    return title, description


def clean_task_title(title: str) -> str:
    """
    Clean and normalize a task title.

    Args:
        title: Raw title

    Returns:
        Cleaned title
    """
    if not title:
        return ""

    # Remove quotes if wrapped
    title = re.sub(r'^["\']|["\']$', "", title)

    # Normalize whitespace
    title = re.sub(r"\s+", " ", title).strip()

    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]

    return title
