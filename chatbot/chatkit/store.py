"""
ChatKit Store Implementation (T001).

In-memory store for ChatKit threads and items.
Implements the ChatKit Store interface for thread persistence.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


@dataclass
class Thread:
    """ChatKit thread (conversation)."""

    id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ThreadItem:
    """Single item in a thread."""

    id: str
    thread_id: str
    type: str  # user_message, assistant_message, tool_call, tool_result
    content: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ItemsPage:
    """Paginated result for thread items."""

    data: list[ThreadItem]
    has_more: bool = False


class MemoryStore:
    """
    In-memory store for ChatKit threads and items.

    Implements the ChatKit Store interface pattern.
    Thread data is stored in memory and cleared when the server restarts.

    This is appropriate for stateless operation where conversation
    context is provided in each request.
    """

    def __init__(self):
        """Initialize empty store."""
        self._threads: dict[str, Thread] = {}
        self._items: dict[str, list[ThreadItem]] = {}

    async def load_thread(self, thread_id: str) -> Optional[Thread]:
        """
        Load a thread by ID.

        Args:
            thread_id: Unique thread identifier

        Returns:
            Thread object or None if not found
        """
        return self._threads.get(thread_id)

    async def save_thread(self, thread: Thread) -> None:
        """
        Save or update a thread.

        Args:
            thread: Thread object to save
        """
        thread.updated_at = datetime.now(timezone.utc)
        self._threads[thread.id] = thread

    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str] = None,
        limit: int = 20,
        order: str = "asc",
        context: Optional[dict] = None,
    ) -> ItemsPage:
        """
        Load items for a thread with pagination.

        Args:
            thread_id: Thread to load items for
            after: Item ID to start after (for pagination)
            limit: Maximum items to return
            order: Sort order ("asc" or "desc")
            context: Optional request context

        Returns:
            ItemsPage with data and pagination info
        """
        items = self._items.get(thread_id, [])

        # Apply ordering
        if order == "desc":
            items = list(reversed(items))

        # Apply after filter
        if after:
            start_idx = 0
            for i, item in enumerate(items):
                if item.id == after:
                    start_idx = i + 1
                    break
            items = items[start_idx:]

        # Apply limit
        has_more = len(items) > limit
        items = items[:limit]

        return ItemsPage(data=items, has_more=has_more)

    async def add_thread_item(self, thread_id: str, item: ThreadItem) -> None:
        """
        Add an item to a thread.

        Args:
            thread_id: Thread to add item to
            item: ThreadItem to add
        """
        if thread_id not in self._items:
            self._items[thread_id] = []
        self._items[thread_id].append(item)

    async def save_item(self, item: ThreadItem) -> None:
        """
        Update an existing item.

        Args:
            item: ThreadItem to update
        """
        if item.thread_id in self._items:
            for i, existing in enumerate(self._items[item.thread_id]):
                if existing.id == item.id:
                    self._items[item.thread_id][i] = item
                    break

    async def delete_thread(self, thread_id: str) -> None:
        """
        Delete a thread and all its items.

        Args:
            thread_id: Thread to delete
        """
        self._threads.pop(thread_id, None)
        self._items.pop(thread_id, None)

    def generate_id(self) -> str:
        """
        Generate a unique ID for threads or items.

        Returns:
            Unique string ID
        """
        return str(uuid4())

    def clear(self) -> None:
        """Clear all stored data (for testing)."""
        self._threads.clear()
        self._items.clear()
