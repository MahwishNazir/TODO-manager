"""
Agent core module.

Provides agent initialization and runner wrapper following OpenAI Agents SDK patterns.
Implements research.md R2 (determinism) and R4 (context management).
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from agents import Agent, Runner

from chatbot.agent.config import get_settings
from chatbot.agent.models import (
    AgentSession,
    ConfirmationState,
    ConversationContext,
)
from chatbot.agent.prompt import build_agent_prompt
from chatbot.agent.tools import (
    AGENT_TOOLS,
    set_tool_context,
    clear_tool_context,
)


# Agent instance (singleton per process)
_agent: Optional[Agent] = None


def create_agent(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    instructions: Optional[str] = None,
) -> Agent:
    """
    Create and configure the todo agent.

    Args:
        model: Model name override (default from settings)
        temperature: Temperature override (default 0.0 for determinism)
        instructions: System instructions override

    Returns:
        Configured Agent instance
    """
    settings = get_settings()

    # Use defaults from settings unless overridden
    model_name = model or settings.agent_model
    temp = temperature if temperature is not None else settings.agent_temperature

    # Default instructions if not provided
    default_instructions = """
You are a helpful AI assistant designed to help users manage their todo list.
You have access to tools for creating, listing, updating, completing, and deleting tasks.
Always use the appropriate tool when the user wants to manage their tasks.
Be concise and helpful in your responses.
"""
    agent_instructions = instructions or default_instructions

    # Create agent with deterministic settings (FR-060)
    agent = Agent(
        name="todo-agent",
        model=model_name,
        model_settings={"temperature": temp},
        instructions=agent_instructions,
        tools=AGENT_TOOLS,
    )

    return agent


def get_agent() -> Agent:
    """
    Get the singleton agent instance.

    Creates the agent on first call with default settings.

    Returns:
        The configured Agent instance
    """
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent


def reset_agent() -> None:
    """Reset the agent singleton (useful for testing)."""
    global _agent
    _agent = None


class AgentRunner:
    """
    Runner wrapper for handling agent invocations with context.

    Manages conversation context, confirmation state, and tool context
    across agent turns.
    """

    def __init__(
        self,
        agent: Optional[Agent] = None,
        session: Optional[AgentSession] = None,
    ):
        """
        Initialize the agent runner.

        Args:
            agent: Agent instance (uses singleton if not provided)
            session: Session for context (creates empty context if not provided)
        """
        self._agent = agent or get_agent()
        self._session = session
        self._context: Optional[ConversationContext] = None
        self._confirmation_state: Optional[ConfirmationState] = None

    def set_context(self, context: ConversationContext) -> None:
        """Set the conversation context."""
        self._context = context

    def get_context(self) -> Optional[ConversationContext]:
        """Get the current conversation context."""
        return self._context

    def set_confirmation_state(self, state: ConfirmationState) -> None:
        """Set the confirmation state."""
        self._confirmation_state = state

    def get_confirmation_state(self) -> Optional[ConfirmationState]:
        """Get the current confirmation state."""
        return self._confirmation_state

    def _build_messages(self, user_message: str) -> List[Dict[str, str]]:
        """
        Build messages list for agent from context and new message.

        Args:
            user_message: New user message

        Returns:
            List of message dicts for agent
        """
        messages = []

        # Add conversation history from context
        if self._context:
            for msg in self._context.messages:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })

        # Add new user message
        messages.append({
            "role": "user",
            "content": user_message,
        })

        return messages

    async def run(
        self,
        user_message: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Run the agent with a user message.

        Handles context management, tool context setup, and response processing.

        Args:
            user_message: The user's message
            user_id: User ID for tool invocations

        Returns:
            Dict with response, updated context, and any confirmation state
        """
        # Build system prompt with current state
        system_prompt = build_agent_prompt(
            user_id=user_id,
            context=self._context,
            confirmation_state=self._confirmation_state,
        )

        # Update agent instructions with dynamic prompt
        self._agent.instructions = system_prompt

        # Set tool context for audit
        session_id = self._session.session_id if self._session else None
        set_tool_context(session_id=session_id, user_id=user_id)

        try:
            # Build messages including history
            messages = self._build_messages(user_message)

            # Create runner and execute
            runner = Runner(agent=self._agent)
            result = await runner.run(messages=messages)

            # Extract response
            response_text = ""
            if result.messages:
                # Get the last assistant message
                for msg in reversed(result.messages):
                    if msg.get("role") == "assistant":
                        response_text = msg.get("content", "")
                        break

            # Update context with new messages
            if self._context is None:
                self._context = ConversationContext()

            # Add user message to context
            self._context.add_user_message(user_message)

            # Add assistant response to context
            if response_text:
                self._context.add_assistant_message(response_text)

            return {
                "success": True,
                "response": response_text,
                "context": self._context,
                "confirmation_state": self._confirmation_state,
            }

        except Exception as e:
            # Return error response
            return {
                "success": False,
                "error": str(e),
                "context": self._context,
                "confirmation_state": self._confirmation_state,
            }

        finally:
            # Clear tool context
            clear_tool_context()


async def process_message(
    user_message: str,
    user_id: str,
    session: Optional[AgentSession] = None,
    context: Optional[ConversationContext] = None,
    confirmation_state: Optional[ConfirmationState] = None,
) -> Dict[str, Any]:
    """
    Process a user message through the agent.

    Convenience function for single-turn processing.

    Args:
        user_message: The user's message
        user_id: User ID for tool invocations and auth
        session: Optional session for audit context
        context: Optional conversation context
        confirmation_state: Optional confirmation state

    Returns:
        Dict with response and updated state
    """
    runner = AgentRunner(session=session)

    if context:
        runner.set_context(context)

    if confirmation_state:
        runner.set_confirmation_state(confirmation_state)

    return await runner.run(user_message=user_message, user_id=user_id)
