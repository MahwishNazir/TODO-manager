"""
Stateless Agent Runner (Phase III Part 5).

Wraps the OpenAI Agents SDK for stateless operation where all context
is provided in each request and no state is maintained between calls.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from agents import Agent, Runner, ModelSettings

from chatbot.agent.config import get_settings
from chatbot.agent.tools import AGENT_TOOLS
from chatbot.agent.tool_collector import ToolCallCollector


class StatelessAgentRunner:
    """
    Stateless agent runner that processes messages without maintaining state.

    Each call to run() is completely independent - no context is stored
    between invocations. This enables horizontal scaling and eliminates
    session affinity requirements.
    """

    def __init__(self):
        """Initialize the stateless runner with agent configuration."""
        self._settings = get_settings()
        self._agent: Optional[Agent] = None

    def _get_agent(self) -> Agent:
        """Get or create the singleton agent instance."""
        if self._agent is None:
            self._agent = Agent(
                name="todo-agent-stateless",
                model=self._settings.agent_model,
                model_settings=ModelSettings(
                    temperature=self._settings.agent_temperature,
                    max_tokens=self._settings.agent_max_tokens,
                ),
                instructions=self._build_system_instructions(),
                tools=AGENT_TOOLS,
            )
        return self._agent

    def _build_system_instructions(self) -> str:
        """Build system instructions for the agent."""
        return """You are a helpful AI assistant for managing todo tasks.
You have access to tools for creating, listing, updating, completing, and deleting tasks.

IMPORTANT: Always use the appropriate tool when the user wants to manage their tasks.
- For creating tasks: use add_task
- For listing tasks: use list_tasks
- For updating tasks: use update_task
- For completing tasks: use complete_task
- For deleting tasks: use delete_task (requires confirmation)

Be concise and helpful in your responses. Confirm actions taken clearly."""

    def _convert_messages_to_agent_format(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Convert input messages to agent-compatible format.

        Args:
            messages: List of message dicts with role and content

        Returns:
            Messages in format expected by Runner
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]

    async def run(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process messages through the agent statelessly.

        This method creates a fresh context for each invocation.
        No state is stored or retrieved from previous calls.

        Args:
            messages: Conversation history from client
            user_id: User ID for tool operations

        Returns:
            Dict containing:
                - response: MessageOutput data (message_id, role, content, timestamp)
                - tool_calls: List of ToolCallOutput data
                - usage: TokenUsage data
                - pending_confirmation: Optional PendingConfirmation data
        """
        # Create fresh tool collector for this request (stateless)
        tool_collector = ToolCallCollector(user_id=user_id)

        # Get agent (singleton, but stateless per-request)
        agent = self._get_agent()

        # Convert messages to agent format
        agent_messages = self._convert_messages_to_agent_format(messages)

        try:
            # Set tool collector context for this request
            tool_collector.start_collection()

            # Execute agent via Runner class method (no stored context)
            result = await Runner.run(
                starting_agent=agent,
                input=agent_messages,
            )

            # Stop collection and get tool calls
            tool_calls = tool_collector.stop_collection()

            # Extract response text from RunResult.new_items
            response_text = self._extract_response_text(result)

            # Extract token usage (if available from result)
            usage = self._extract_usage(result)

            # Check for pending confirmation (destructive actions)
            pending_confirmation = self._check_pending_confirmation(
                response_text, tool_calls, user_id
            )

            # Build response
            return {
                "response": {
                    "message_id": str(uuid4()),
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                "tool_calls": tool_calls,
                "usage": usage,
                "pending_confirmation": pending_confirmation,
            }

        except Exception as e:
            # Return error response
            return {
                "response": {
                    "message_id": str(uuid4()),
                    "role": "assistant",
                    "content": f"I encountered an error processing your request: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                "tool_calls": [],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "pending_confirmation": None,
                "error": str(e),
            }

    def _extract_response_text(self, result: Any) -> str:
        """
        Extract assistant response text from RunResult.new_items.

        Iterates through new_items in reverse to find the last
        MessageOutputItem and extracts text from its raw_item.content.

        Args:
            result: RunResult from Runner.run()

        Returns:
            The assistant's response text, or empty string if not found
        """
        from agents.items import MessageOutputItem

        for item in reversed(result.new_items):
            if isinstance(item, MessageOutputItem):
                # raw_item is ResponseOutputMessage with .content list
                for content_part in item.raw_item.content:
                    if hasattr(content_part, "text"):
                        return content_part.text
        return ""

    def _extract_usage(self, result: Any) -> Dict[str, int]:
        """
        Extract token usage from agent result.

        Aggregates usage from all raw_responses in the RunResult.
        The SDK uses input_tokens/output_tokens naming, which we map
        to prompt_tokens/completion_tokens for our API schema.

        Args:
            result: RunResult from Runner.run()

        Returns:
            TokenUsage dict with prompt_tokens, completion_tokens, total_tokens
        """
        total_input = 0
        total_output = 0
        total_tokens = 0

        for raw_response in getattr(result, "raw_responses", []):
            usage = getattr(raw_response, "usage", None)
            if usage:
                total_input += getattr(usage, "input_tokens", 0)
                total_output += getattr(usage, "output_tokens", 0)
                total_tokens += getattr(usage, "total_tokens", 0)

        return {
            "prompt_tokens": total_input,
            "completion_tokens": total_output,
            "total_tokens": total_tokens,
        }

    def _check_pending_confirmation(
        self,
        response_text: str,
        tool_calls: List[Dict[str, Any]],
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Check if response requires confirmation for destructive action.

        Args:
            response_text: Agent's response
            tool_calls: Tool calls made during this request
            user_id: User ID for token generation

        Returns:
            PendingConfirmation dict if confirmation needed, else None
        """
        # Check if any tool call was for delete_task
        for call in tool_calls:
            if call.get("tool_name") == "delete_task":
                # Import here to avoid circular dependency
                from chatbot.agent.confirmation_token import ConfirmationTokenService

                token_service = ConfirmationTokenService()
                return token_service.generate_token(
                    action="delete_task",
                    user_id=user_id,
                    description=f"Delete task",
                    task_id=call.get("parameters", {}).get("task_id"),
                )

        return None


# Singleton instance for reuse
_runner: Optional[StatelessAgentRunner] = None


def get_stateless_runner() -> StatelessAgentRunner:
    """Get the singleton stateless runner instance."""
    global _runner
    if _runner is None:
        _runner = StatelessAgentRunner()
    return _runner
