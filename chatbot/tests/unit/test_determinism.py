"""
Unit tests for determinism verification (T106).

Tests that same input produces same tool selection (FR-060 to FR-063).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from chatbot.agent.core import create_agent, get_agent, reset_agent
from chatbot.agent.config import get_settings


class TestAgentDeterminism:
    """Tests for agent determinism requirements."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    def test_temperature_is_zero(self):
        """Agent should be configured with temperature=0 (FR-060)."""
        settings = get_settings()

        assert settings.agent_temperature == 0.0

    def test_agent_created_with_temperature_zero(self):
        """Agent should be created with temperature=0."""
        agent = create_agent()

        # Verify model settings include temperature=0
        assert agent.model_settings.get("temperature") == 0

    def test_same_input_same_agent_config(self):
        """Same agent config should be used across invocations."""
        agent1 = get_agent()
        agent2 = get_agent()

        # Should be same singleton instance
        assert agent1 is agent2

    def test_custom_temperature_override(self):
        """Custom temperature should be respected when explicitly set."""
        # Note: This is for testing purposes; production should always use 0
        agent = create_agent(temperature=0.5)

        assert agent.model_settings.get("temperature") == 0.5


class TestToolSelectionDeterminism:
    """Tests for deterministic tool selection."""

    ADD_TASK_INPUTS = [
        "Create a task to buy groceries",
        "Add a task: buy groceries",
        "New task: buy groceries",
    ]

    LIST_TASKS_INPUTS = [
        "Show my tasks",
        "What are my tasks?",
        "List my todos",
    ]

    def test_add_inputs_recognized_consistently(self):
        """ADD task inputs should be consistently recognized."""
        from chatbot.agent.execution import detect_intents, IntentType

        for input_text in self.ADD_TASK_INPUTS:
            intents = detect_intents(input_text)
            # Should detect ADD intent
            has_add = any(i.type == IntentType.ADD for i in intents)
            assert has_add, f"ADD intent not detected for: {input_text}"

    def test_list_inputs_recognized_consistently(self):
        """LIST task inputs should be consistently recognized."""
        from chatbot.agent.execution import detect_intents, IntentType

        for input_text in self.LIST_TASKS_INPUTS:
            intents = detect_intents(input_text)
            # Should detect LIST intent
            has_list = any(i.type == IntentType.LIST for i in intents)
            assert has_list, f"LIST intent not detected for: {input_text}"

    def test_repeated_calls_same_result(self):
        """Repeated calls with same input should produce same result."""
        from chatbot.agent.execution import detect_intents

        input_text = "Create a task to buy groceries"

        results = [detect_intents(input_text) for _ in range(5)]

        # All results should have same structure
        first_types = [i.type for i in results[0]]
        for result in results[1:]:
            result_types = [i.type for i in result]
            assert result_types == first_types


class TestPromptDeterminism:
    """Tests for deterministic prompt generation."""

    def test_same_context_same_prompt(self):
        """Same context should produce same prompt."""
        from chatbot.agent.prompt import build_agent_prompt
        from chatbot.agent.models import ConversationContext, ConfirmationState

        context = ConversationContext()
        context.add_user_message("Hello")
        confirmation = ConfirmationState()

        prompt1 = build_agent_prompt(
            user_id="user-123",
            context=context,
            confirmation_state=confirmation,
        )

        prompt2 = build_agent_prompt(
            user_id="user-123",
            context=context,
            confirmation_state=confirmation,
        )

        assert prompt1 == prompt2

    def test_rules_layer_consistent(self):
        """Rules layer should be consistent."""
        from chatbot.agent.prompt import RULES_LAYER

        # Should contain determinism requirements
        assert "temperature" in RULES_LAYER.lower() or "determinism" in RULES_LAYER.lower()


class TestConfigurationDeterminism:
    """Tests for configuration consistency."""

    def test_settings_singleton(self):
        """Settings should be singleton."""
        from chatbot.agent.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_default_model_consistent(self):
        """Default model should be consistent."""
        settings = get_settings()

        assert settings.agent_model == "gpt-4"

    def test_timeout_consistent(self):
        """Timeout should be consistent (FR-024)."""
        settings = get_settings()

        assert settings.mcp_timeout_seconds == 30
