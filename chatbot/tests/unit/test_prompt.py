"""
Unit tests for prompt builder (T027).

Tests layered prompt construction for the agent.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from chatbot.agent.prompt import (
    PromptBuilder,
    get_prompt_builder,
    build_agent_prompt,
    DEFAULT_SYSTEM_INSTRUCTIONS,
    RULES_LAYER,
)
from chatbot.agent.models import (
    ConfirmationState,
    ConfirmationStatus,
    ConversationContext,
    Message,
    MessageRole,
)
from chatbot.agent.models.context import TaskReference


class TestPromptBuilder:
    """Tests for PromptBuilder class."""

    def test_build_system_layer_default(self):
        """Should return default instructions when no file exists."""
        builder = PromptBuilder(instructions_path=Path("/nonexistent/path"))
        system_layer = builder.build_system_layer()

        assert "helpful AI assistant" in system_layer
        assert "todo list" in system_layer.lower()

    def test_build_system_layer_from_file(self, tmp_path):
        """Should load instructions from file."""
        instructions_file = tmp_path / "instructions.md"
        instructions_file.write_text("# Custom Instructions\nYou are a custom agent.")

        builder = PromptBuilder(instructions_path=instructions_file)
        system_layer = builder.build_system_layer()

        assert "Custom Instructions" in system_layer
        assert "custom agent" in system_layer

    def test_build_system_layer_caches_content(self, tmp_path):
        """Should cache loaded instructions."""
        instructions_file = tmp_path / "instructions.md"
        instructions_file.write_text("Original content")

        builder = PromptBuilder(instructions_path=instructions_file)
        first_load = builder.build_system_layer()

        # Modify file
        instructions_file.write_text("Modified content")
        second_load = builder.build_system_layer()

        # Should return cached content
        assert first_load == second_load
        assert "Original content" in second_load

    def test_build_context_layer_minimal(self):
        """Should build minimal context layer with just user ID."""
        builder = PromptBuilder()
        context_layer = builder.build_context_layer(user_id="user-123")

        assert "Session Context" in context_layer
        assert "user-123" in context_layer

    def test_build_context_layer_with_last_task(self):
        """Should include last mentioned task."""
        builder = PromptBuilder()
        context = ConversationContext()
        context.set_last_mentioned_task("task-abc", "buy groceries")

        context_layer = builder.build_context_layer(
            user_id="user-123",
            context=context,
        )

        assert "task-abc" in context_layer
        assert "buy groceries" in context_layer

    def test_build_context_layer_with_disambiguation(self):
        """Should include disambiguation candidates."""
        builder = PromptBuilder()
        context = ConversationContext()
        context.set_disambiguation_candidates([
            TaskReference(task_id="t1", title="Buy milk"),
            TaskReference(task_id="t2", title="Buy bread"),
        ])

        context_layer = builder.build_context_layer(
            user_id="user-123",
            context=context,
        )

        assert "selection" in context_layer.lower()
        assert "Buy milk" in context_layer
        assert "Buy bread" in context_layer

    def test_build_context_layer_with_long_history(self):
        """Should summarize long conversation history."""
        builder = PromptBuilder()
        context = ConversationContext()

        # Add more than 5 messages
        for i in range(10):
            context.add_user_message(f"Message {i}")

        context_layer = builder.build_context_layer(
            user_id="user-123",
            context=context,
        )

        assert "10 messages" in context_layer

    def test_build_state_layer_idle(self):
        """Should show no pending confirmations when idle."""
        builder = PromptBuilder()
        state_layer = builder.build_state_layer()

        assert "No pending confirmations" in state_layer

    def test_build_state_layer_awaiting_delete(self):
        """Should show pending delete confirmation."""
        builder = PromptBuilder()
        confirmation = ConfirmationState()
        confirmation.set_awaiting_delete(["task-123"], "Delete 'Buy groceries'")

        state_layer = builder.build_state_layer(confirmation_state=confirmation)

        assert "AWAITING DELETE" in state_layer
        assert "Delete 'Buy groceries'" in state_layer

    def test_build_state_layer_awaiting_plan(self):
        """Should show pending plan approval."""
        builder = PromptBuilder()
        confirmation = ConfirmationState()
        confirmation.set_awaiting_plan_approval("plan-1", "Create task and complete other")

        state_layer = builder.build_state_layer(confirmation_state=confirmation)

        assert "PLAN APPROVAL" in state_layer
        assert "Create task and complete other" in state_layer

    def test_build_rules_layer(self):
        """Should return rules layer content."""
        builder = PromptBuilder()
        rules_layer = builder.build_rules_layer()

        assert "Determinism" in rules_layer
        assert "Tool Usage" in rules_layer
        assert "Confirmation" in rules_layer
        assert rules_layer == RULES_LAYER

    def test_build_complete_prompt(self):
        """Should build complete layered prompt."""
        builder = PromptBuilder()
        context = ConversationContext()
        context.set_last_mentioned_task("task-1", "test task")

        confirmation = ConfirmationState()

        prompt = builder.build_prompt(
            user_id="user-123",
            context=context,
            confirmation_state=confirmation,
        )

        # Should contain all layers
        assert "user-123" in prompt  # Context layer
        assert "test task" in prompt  # Context layer with task
        assert "No pending" in prompt  # State layer
        assert "Determinism" in prompt  # Rules layer


class TestPromptBuilderSingleton:
    """Tests for prompt builder singleton."""

    def test_get_prompt_builder_returns_singleton(self):
        """Should return same instance."""
        from chatbot.agent import prompt

        # Reset singleton
        prompt._builder = None

        builder1 = get_prompt_builder()
        builder2 = get_prompt_builder()

        assert builder1 is builder2


class TestBuildAgentPrompt:
    """Tests for build_agent_prompt convenience function."""

    def test_builds_prompt_with_all_args(self):
        """Should build prompt using convenience function."""
        context = ConversationContext()
        confirmation = ConfirmationState()

        prompt = build_agent_prompt(
            user_id="user-123",
            context=context,
            confirmation_state=confirmation,
        )

        assert "user-123" in prompt
        assert "Determinism" in prompt

    def test_builds_prompt_with_minimal_args(self):
        """Should work with just user_id."""
        prompt = build_agent_prompt(user_id="user-456")

        assert "user-456" in prompt


class TestRulesLayerContent:
    """Tests for rules layer content."""

    def test_determinism_requirements(self):
        """Rules should include determinism requirements."""
        assert "identical tool selections" in RULES_LAYER
        assert "tomorrow" in RULES_LAYER
        assert "today" in RULES_LAYER

    def test_tool_usage_policy(self):
        """Rules should include tool usage policy."""
        assert "MCP tools" in RULES_LAYER
        assert "fabricate" in RULES_LAYER.lower() or "assume" in RULES_LAYER.lower()
        assert "30 second" in RULES_LAYER

    def test_confirmation_requirements(self):
        """Rules should include confirmation requirements."""
        assert "confirmation" in RULES_LAYER.lower()
        assert "yes" in RULES_LAYER.lower()
        assert "delete" in RULES_LAYER.lower()


class TestDefaultSystemInstructions:
    """Tests for default system instructions."""

    def test_includes_capabilities(self):
        """Default instructions should list capabilities."""
        assert "CAN help" in DEFAULT_SYSTEM_INSTRUCTIONS
        assert "Adding new tasks" in DEFAULT_SYSTEM_INSTRUCTIONS
        assert "Showing" in DEFAULT_SYSTEM_INSTRUCTIONS
        assert "Marking" in DEFAULT_SYSTEM_INSTRUCTIONS
        assert "Updating" in DEFAULT_SYSTEM_INSTRUCTIONS
        assert "Deleting" in DEFAULT_SYSTEM_INSTRUCTIONS

    def test_includes_limitations(self):
        """Default instructions should list limitations."""
        assert "CANNOT help" in DEFAULT_SYSTEM_INSTRUCTIONS
        assert "unrelated" in DEFAULT_SYSTEM_INSTRUCTIONS.lower()

    def test_includes_behavior_guidance(self):
        """Default instructions should guide behavior."""
        assert "helpful" in DEFAULT_SYSTEM_INSTRUCTIONS.lower()
        assert "concise" in DEFAULT_SYSTEM_INSTRUCTIONS.lower()
        assert "confirm" in DEFAULT_SYSTEM_INSTRUCTIONS.lower()
