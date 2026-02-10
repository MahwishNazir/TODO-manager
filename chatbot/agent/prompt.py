"""
Prompt construction module.

Builds layered prompts for the agent with system, context, state, and rules layers.
Implements the prompt construction strategy from plan.md D4.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from chatbot.agent.models.confirmation import ConfirmationState, ConfirmationStatus
from chatbot.agent.models.context import ConversationContext


# Default system instructions if instructions.md is not found
DEFAULT_SYSTEM_INSTRUCTIONS = """
You are a helpful AI assistant designed to help users manage their todo list through natural conversation.

You CAN help with:
- Adding new tasks to the user's todo list
- Showing the user's tasks (all or filtered)
- Marking tasks as complete
- Updating task details (title, description)
- Deleting tasks (with confirmation)

You CANNOT help with:
- Questions unrelated to task management
- Creating accounts or managing authentication
- Accessing other users' tasks

Be helpful, concise, and confirm destructive actions before executing them.
"""

# Rules layer for determinism and tool usage policies
RULES_LAYER = """
## Determinism Requirements

You MUST:
- Produce identical tool selections for identical inputs
- Interpret "tomorrow" as the next calendar day
- Interpret "today" as the current calendar day
- Interpret "next week" as 7 days from now

## Tool Usage Policy

You MUST:
- Only use the registered MCP tools for data operations
- Never fabricate or assume parameter values
- Validate required parameters before tool invocation
- Handle tool timeouts gracefully (30 second limit)

## Confirmation Requirements

You MUST:
- Require explicit confirmation ("yes", "confirm", "proceed", "do it") before delete operations
- Treat ambiguous responses as non-confirmation and re-ask
- Show task details before confirming deletion
"""


class PromptBuilder:
    """
    Builds layered prompts for the agent.

    Layers:
    1. System Layer: Agent identity and capabilities from instructions.md
    2. Context Layer: User session info, conversation history summary
    3. State Layer: Current confirmation state, last mentioned task
    4. Rules Layer: Determinism requirements, tool usage policies
    """

    def __init__(
        self,
        instructions_path: Optional[Path] = None,
    ):
        """
        Initialize the prompt builder.

        Args:
            instructions_path: Path to instructions.md file
        """
        self._instructions_path = instructions_path
        self._system_instructions: Optional[str] = None

    def _load_instructions(self) -> str:
        """Load system instructions from instructions.md."""
        if self._system_instructions is not None:
            return self._system_instructions

        # Try to find instructions.md
        if self._instructions_path and self._instructions_path.exists():
            path = self._instructions_path
        else:
            # Try default location
            default_path = Path(__file__).parent / "instructions.md"
            if default_path.exists():
                path = default_path
            else:
                self._system_instructions = DEFAULT_SYSTEM_INSTRUCTIONS
                return self._system_instructions

        try:
            self._system_instructions = path.read_text(encoding="utf-8")
        except Exception:
            self._system_instructions = DEFAULT_SYSTEM_INSTRUCTIONS

        return self._system_instructions

    def build_system_layer(self) -> str:
        """Build the system layer from instructions.md."""
        return self._load_instructions()

    def build_context_layer(
        self,
        user_id: str,
        context: Optional[ConversationContext] = None,
    ) -> str:
        """
        Build the context layer with session info.

        Args:
            user_id: Current user's ID
            context: Conversation context

        Returns:
            Context layer string
        """
        lines = [
            "## Current Session Context",
            f"- User ID: {user_id}",
        ]

        if context:
            # Add last mentioned task if any
            if context.last_mentioned_task_id:
                lines.append(
                    f"- Last mentioned task: {context.last_mentioned_task_ref} "
                    f"(ID: {context.last_mentioned_task_id})"
                )

            # Add disambiguation candidates if any
            if context.disambiguation_candidates:
                lines.append("- Awaiting task selection from:")
                for i, task in enumerate(context.disambiguation_candidates):
                    lines.append(f"  {i + 1}. {task.title}")

            # Summarize conversation if long
            if len(context.messages) > 5:
                lines.append(
                    f"- Conversation has {len(context.messages)} messages"
                )

        return "\n".join(lines)

    def build_state_layer(
        self,
        confirmation_state: Optional[ConfirmationState] = None,
    ) -> str:
        """
        Build the state layer with confirmation status.

        Args:
            confirmation_state: Current confirmation state

        Returns:
            State layer string
        """
        if not confirmation_state or confirmation_state.is_idle():
            return "## Current State\n- No pending confirmations"

        lines = ["## Current State"]

        if confirmation_state.state == ConfirmationStatus.AWAITING_DELETE:
            lines.append("- AWAITING DELETE CONFIRMATION")
            lines.append(f"- Action: {confirmation_state.action_description}")
            lines.append(
                "- Respond to user's confirmation (yes/no) before any other action"
            )
        elif confirmation_state.state == ConfirmationStatus.AWAITING_PLAN_APPROVAL:
            lines.append("- AWAITING PLAN APPROVAL")
            lines.append(f"- Plan: {confirmation_state.action_description}")
            lines.append(
                "- Wait for user to approve or reject the plan before executing"
            )
        else:
            lines.append(f"- Awaiting confirmation: {confirmation_state.state.value}")
            if confirmation_state.action_description:
                lines.append(f"- Action: {confirmation_state.action_description}")

        return "\n".join(lines)

    def build_rules_layer(self) -> str:
        """Build the rules layer with determinism and policy requirements."""
        return RULES_LAYER

    def build_prompt(
        self,
        user_id: str,
        context: Optional[ConversationContext] = None,
        confirmation_state: Optional[ConfirmationState] = None,
    ) -> str:
        """
        Build the complete layered prompt.

        Args:
            user_id: Current user's ID
            context: Conversation context
            confirmation_state: Confirmation state

        Returns:
            Complete system prompt
        """
        layers = [
            self.build_system_layer(),
            self.build_context_layer(user_id, context),
            self.build_state_layer(confirmation_state),
            self.build_rules_layer(),
        ]

        return "\n\n".join(layers)


# Singleton instance
_builder: Optional[PromptBuilder] = None


def get_prompt_builder() -> PromptBuilder:
    """Get the prompt builder singleton."""
    global _builder
    if _builder is None:
        _builder = PromptBuilder()
    return _builder


def build_agent_prompt(
    user_id: str,
    context: Optional[ConversationContext] = None,
    confirmation_state: Optional[ConfirmationState] = None,
) -> str:
    """
    Build the complete agent prompt.

    Convenience function using the singleton builder.

    Args:
        user_id: Current user's ID
        context: Conversation context
        confirmation_state: Confirmation state

    Returns:
        Complete system prompt
    """
    return get_prompt_builder().build_prompt(
        user_id=user_id,
        context=context,
        confirmation_state=confirmation_state,
    )
