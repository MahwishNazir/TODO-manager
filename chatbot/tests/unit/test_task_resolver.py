"""
Unit tests for task reference resolution (T049).

Tests resolving task references like "that one", "the groceries task", etc.
"""

import pytest
from typing import List, Dict, Any

from chatbot.agent.utils.task_resolver import (
    resolve_task_reference,
    find_matching_tasks,
    TaskResolutionResult,
    TaskResolutionStatus,
)
from chatbot.agent.models import ConversationContext


class TestResolveTaskReference:
    """Tests for resolve_task_reference function."""

    @pytest.fixture
    def sample_tasks(self) -> List[Dict[str, Any]]:
        """Sample task list for testing."""
        return [
            {"id": "t1", "title": "Buy groceries", "description": "Get milk and bread"},
            {"id": "t2", "title": "Buy gifts", "description": "Birthday presents"},
            {"id": "t3", "title": "Call mom", "description": None},
            {"id": "t4", "title": "Finish report", "description": "Q1 summary"},
        ]

    def test_resolve_exact_title_match(self, sample_tasks):
        """Should resolve exact title match."""
        result = resolve_task_reference("Buy groceries", sample_tasks)

        assert result.status == TaskResolutionStatus.RESOLVED
        assert result.task_id == "t1"
        assert result.confidence == 1.0

    def test_resolve_partial_title_match(self, sample_tasks):
        """Should resolve partial title match."""
        result = resolve_task_reference("groceries", sample_tasks)

        assert result.status == TaskResolutionStatus.RESOLVED
        assert result.task_id == "t1"

    def test_resolve_case_insensitive(self, sample_tasks):
        """Should match case-insensitively."""
        result = resolve_task_reference("BUY GROCERIES", sample_tasks)

        assert result.status == TaskResolutionStatus.RESOLVED
        assert result.task_id == "t1"

    def test_ambiguous_match(self, sample_tasks):
        """Should return ambiguous when multiple tasks match."""
        result = resolve_task_reference("Buy", sample_tasks)

        assert result.status == TaskResolutionStatus.AMBIGUOUS
        assert len(result.candidates) == 2  # Buy groceries, Buy gifts

    def test_no_match(self, sample_tasks):
        """Should return not found when no tasks match."""
        result = resolve_task_reference("nonexistent task", sample_tasks)

        assert result.status == TaskResolutionStatus.NOT_FOUND
        assert result.task_id is None

    def test_resolve_from_context(self, sample_tasks):
        """Should resolve 'that one' from context."""
        context = ConversationContext()
        context.set_last_mentioned_task("t3", "call mom")

        result = resolve_task_reference("that one", sample_tasks, context)

        assert result.status == TaskResolutionStatus.RESOLVED
        assert result.task_id == "t3"

    def test_resolve_pronouns(self, sample_tasks):
        """Should resolve various pronouns from context."""
        context = ConversationContext()
        context.set_last_mentioned_task("t1", "buy groceries")

        pronouns = ["it", "that", "that one", "that task", "the task"]
        for pronoun in pronouns:
            result = resolve_task_reference(pronoun, sample_tasks, context)
            assert result.status == TaskResolutionStatus.RESOLVED
            assert result.task_id == "t1"

    def test_no_context_for_pronoun(self, sample_tasks):
        """Should fail when pronoun used without context."""
        result = resolve_task_reference("that one", sample_tasks, context=None)

        assert result.status == TaskResolutionStatus.NOT_FOUND

    def test_empty_task_list(self):
        """Should handle empty task list."""
        result = resolve_task_reference("any task", [])

        assert result.status == TaskResolutionStatus.NOT_FOUND


class TestFindMatchingTasks:
    """Tests for find_matching_tasks function."""

    @pytest.fixture
    def sample_tasks(self) -> List[Dict[str, Any]]:
        """Sample task list for testing."""
        return [
            {"id": "t1", "title": "Buy groceries", "description": "Get milk"},
            {"id": "t2", "title": "Buy presents", "description": "For birthday"},
            {"id": "t3", "title": "Call mom", "description": "About dinner"},
        ]

    def test_find_by_title(self, sample_tasks):
        """Should find tasks by title match."""
        matches = find_matching_tasks("groceries", sample_tasks)

        assert len(matches) == 1
        assert matches[0]["id"] == "t1"

    def test_find_multiple_matches(self, sample_tasks):
        """Should find all matching tasks."""
        matches = find_matching_tasks("Buy", sample_tasks)

        assert len(matches) == 2

    def test_find_by_description(self, sample_tasks):
        """Should find tasks by description match."""
        matches = find_matching_tasks("birthday", sample_tasks)

        assert len(matches) == 1
        assert matches[0]["id"] == "t2"

    def test_no_matches(self, sample_tasks):
        """Should return empty list when no matches."""
        matches = find_matching_tasks("nonexistent", sample_tasks)

        assert len(matches) == 0

    def test_word_boundary_matching(self, sample_tasks):
        """Should respect word boundaries."""
        # "mom" should match "Call mom" but not other words containing "mom"
        matches = find_matching_tasks("mom", sample_tasks)

        assert len(matches) == 1
        assert matches[0]["id"] == "t3"


class TestTaskResolutionResult:
    """Tests for TaskResolutionResult model."""

    def test_resolved_result(self):
        """Should create resolved result."""
        result = TaskResolutionResult(
            status=TaskResolutionStatus.RESOLVED,
            task_id="t1",
            confidence=1.0,
        )

        assert result.is_resolved()
        assert not result.is_ambiguous()
        assert result.task_id == "t1"

    def test_ambiguous_result(self):
        """Should create ambiguous result with candidates."""
        candidates = [
            {"id": "t1", "title": "Task 1"},
            {"id": "t2", "title": "Task 2"},
        ]
        result = TaskResolutionResult(
            status=TaskResolutionStatus.AMBIGUOUS,
            candidates=candidates,
        )

        assert result.is_ambiguous()
        assert not result.is_resolved()
        assert len(result.candidates) == 2

    def test_not_found_result(self):
        """Should create not found result."""
        result = TaskResolutionResult(
            status=TaskResolutionStatus.NOT_FOUND,
        )

        assert not result.is_resolved()
        assert not result.is_ambiguous()
        assert result.task_id is None
