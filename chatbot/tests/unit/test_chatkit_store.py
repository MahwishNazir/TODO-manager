"""
Unit tests for ChatKit MemoryStore (T001).

Tests thread/item CRUD, pagination, ordering, and cleanup.
"""

import pytest
from chatbot.chatkit.store import MemoryStore, Thread, ThreadItem, ItemsPage


class TestMemoryStore:
    """Unit tests for MemoryStore."""

    @pytest.fixture
    def store(self):
        return MemoryStore()

    @pytest.mark.asyncio
    async def test_save_and_load_thread(self, store):
        thread = Thread(id="t1", metadata={"user": "test"})
        await store.save_thread(thread)
        loaded = await store.load_thread("t1")
        assert loaded is not None
        assert loaded.id == "t1"
        assert loaded.metadata == {"user": "test"}

    @pytest.mark.asyncio
    async def test_load_nonexistent_thread(self, store):
        result = await store.load_thread("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_save_thread_updates_timestamp(self, store):
        thread = Thread(id="t1", metadata={})
        await store.save_thread(thread)
        first_update = thread.updated_at
        await store.save_thread(thread)
        assert thread.updated_at >= first_update

    @pytest.mark.asyncio
    async def test_add_and_load_items(self, store):
        item = ThreadItem(id="i1", thread_id="t1", type="user_message", content="hello")
        await store.add_thread_item("t1", item)
        page = await store.load_thread_items("t1")
        assert len(page.data) == 1
        assert page.data[0].content == "hello"
        assert page.has_more is False

    @pytest.mark.asyncio
    async def test_load_items_pagination(self, store):
        for i in range(25):
            item = ThreadItem(id=f"i{i}", thread_id="t1", type="user_message", content=f"msg{i}")
            await store.add_thread_item("t1", item)
        page = await store.load_thread_items("t1", limit=20)
        assert len(page.data) == 20
        assert page.has_more is True

    @pytest.mark.asyncio
    async def test_load_items_after_cursor(self, store):
        for i in range(5):
            item = ThreadItem(id=f"i{i}", thread_id="t1", type="user_message", content=f"msg{i}")
            await store.add_thread_item("t1", item)
        page = await store.load_thread_items("t1", after="i2")
        assert len(page.data) == 2
        assert page.data[0].id == "i3"

    @pytest.mark.asyncio
    async def test_load_items_desc_order(self, store):
        for i in range(3):
            item = ThreadItem(id=f"i{i}", thread_id="t1", type="user_message", content=f"msg{i}")
            await store.add_thread_item("t1", item)
        page = await store.load_thread_items("t1", order="desc")
        assert page.data[0].id == "i2"
        assert page.data[-1].id == "i0"

    @pytest.mark.asyncio
    async def test_save_item_updates_existing(self, store):
        item = ThreadItem(id="i1", thread_id="t1", type="user_message", content="original")
        await store.add_thread_item("t1", item)
        updated = ThreadItem(id="i1", thread_id="t1", type="user_message", content="updated")
        await store.save_item(updated)
        page = await store.load_thread_items("t1")
        assert page.data[0].content == "updated"

    @pytest.mark.asyncio
    async def test_delete_thread(self, store):
        thread = Thread(id="t1", metadata={})
        await store.save_thread(thread)
        item = ThreadItem(id="i1", thread_id="t1", type="user_message", content="hello")
        await store.add_thread_item("t1", item)
        await store.delete_thread("t1")
        assert await store.load_thread("t1") is None
        page = await store.load_thread_items("t1")
        assert len(page.data) == 0

    def test_generate_id_unique(self, store):
        ids = {store.generate_id() for _ in range(100)}
        assert len(ids) == 100

    @pytest.mark.asyncio
    async def test_clear(self, store):
        thread = Thread(id="t1", metadata={})
        await store.save_thread(thread)
        store.clear()
        assert await store.load_thread("t1") is None

    @pytest.mark.asyncio
    async def test_load_items_empty_thread(self, store):
        page = await store.load_thread_items("nonexistent")
        assert len(page.data) == 0
        assert page.has_more is False

    @pytest.mark.asyncio
    async def test_multiple_threads_isolated(self, store):
        item1 = ThreadItem(id="i1", thread_id="t1", type="user_message", content="thread1")
        item2 = ThreadItem(id="i2", thread_id="t2", type="user_message", content="thread2")
        await store.add_thread_item("t1", item1)
        await store.add_thread_item("t2", item2)
        page1 = await store.load_thread_items("t1")
        page2 = await store.load_thread_items("t2")
        assert len(page1.data) == 1
        assert page1.data[0].content == "thread1"
        assert len(page2.data) == 1
        assert page2.data[0].content == "thread2"
