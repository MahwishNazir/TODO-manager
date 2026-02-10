"""
TodoChatKitServer Implementation (T002).

Custom ChatKitServer that bridges ChatKit protocol to the existing
StatelessAgentRunner and OpenAI Agents SDK.
"""

from typing import Any, AsyncIterator, Optional

from agents import Agent, Runner, ModelSettings

from chatbot.agent.config import get_settings
from chatbot.agent.tools import AGENT_TOOLS
from chatbot.chatkit.store import MemoryStore, Thread, ThreadItem, ItemsPage


class AgentContext:
    """
    Context passed to agent execution.

    Contains thread metadata, store access, and request context.
    """

    def __init__(
        self,
        thread: Thread,
        store: MemoryStore,
        user_id: str,
        request_context: Optional[dict[str, Any]] = None,
    ):
        self.thread = thread
        self.store = store
        self.user_id = user_id
        self.request_context = request_context or {}


class TodoChatKitServer:
    """
    ChatKit server for TODO application.

    Bridges ChatKit protocol to OpenAI Agents SDK via the existing
    agent configuration and MCP tools.
    """

    def __init__(self, store: MemoryStore):
        """
        Initialize the ChatKit server.

        Args:
            store: MemoryStore instance for thread/item persistence
        """
        self._store = store
        self._settings = get_settings()
        self._agent: Optional[Agent] = None

    def get_agent(self, user_id: str = "") -> Agent:
        """Get or create the agent instance with user-specific instructions."""
        # Rebuild agent with current user_id in instructions
        self._agent = Agent(
            name="todo-agent-chatkit",
            model=self._settings.agent_model,
            model_settings=ModelSettings(
                temperature=self._settings.agent_temperature,
                max_tokens=self._settings.agent_max_tokens,
            ),
            instructions=self._build_instructions(user_id),
            tools=AGENT_TOOLS,
        )
        return self._agent

    def _build_instructions(self, user_id: str = "") -> str:
        """Build system instructions for the agent."""
        return f"""You are a helpful AI assistant for managing todo tasks.
You have access to tools for creating, listing, updating, completing, and deleting tasks.

IMPORTANT: The current user's ID is: {user_id}
You MUST pass this exact user_id when calling any tool.

Tool usage:
- For creating tasks: use add_task with user_id="{user_id}"
- For listing tasks: use list_tasks with user_id="{user_id}"
- For updating tasks: use update_task with user_id="{user_id}"
- For completing tasks: use complete_task with user_id="{user_id}"
- For deleting tasks: use delete_task with user_id="{user_id}" (requires confirmation)

Be concise and helpful in your responses. Confirm actions taken clearly.
When listing tasks, format them in a readable way.
When an action succeeds, provide a brief confirmation.
When an error occurs, explain what went wrong and suggest alternatives."""

    async def get_or_create_thread(
        self,
        thread_id: str,
        user_id: str,
    ) -> Thread:
        """
        Get existing thread or create a new one.

        Args:
            thread_id: Thread identifier
            user_id: User who owns the thread

        Returns:
            Thread object
        """
        thread = await self._store.load_thread(thread_id)
        if thread is None:
            thread = Thread(
                id=thread_id,
                metadata={"user_id": user_id},
            )
            await self._store.save_thread(thread)
        return thread

    def convert_items_to_agent_input(
        self,
        items: list[ThreadItem],
    ) -> list[dict[str, str]]:
        """
        Convert ChatKit thread items to agent input format.

        Args:
            items: List of ThreadItem objects

        Returns:
            List of message dicts with role and content
        """
        messages = []
        for item in items:
            if item.type == "user_message" and item.content:
                messages.append({"role": "user", "content": item.content})
            elif item.type == "assistant_message" and item.content:
                messages.append({"role": "assistant", "content": item.content})
        return messages

    async def respond(
        self,
        thread: Thread,
        input_user_message: Optional[ThreadItem],
        context: AgentContext,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Process user message and stream response events.

        This method orchestrates the agent interaction:
        1. Load conversation history from thread
        2. Convert to agent input format
        3. Execute agent with streaming
        4. Yield ChatKit-formatted events

        Args:
            thread: Thread metadata
            input_user_message: The user's input message (if any)
            context: Agent context with store and user info

        Yields:
            ChatKit stream events (text_delta, tool_call, tool_result, done)
        """
        # Load thread history
        items_page: ItemsPage = await self._store.load_thread_items(
            thread.id,
            after=None,
            limit=50,
            order="asc",
            context=context.request_context,
        )

        # Add current user message if provided
        if input_user_message and input_user_message.content:
            # Save user message to store
            await self._store.add_thread_item(thread.id, input_user_message)
            items_page.data.append(input_user_message)

        # Convert to agent input format
        agent_input = self.convert_items_to_agent_input(items_page.data)

        if not agent_input:
            # No messages to process
            yield {
                "event": "error",
                "data": {"code": "EMPTY_INPUT", "message": "No messages to process"},
            }
            yield {"event": "done", "data": {}}
            return

        try:
            # Execute agent with streaming
            agent = self.get_agent(user_id=context.user_id)
            result = Runner.run_streamed(
                agent,
                agent_input,
                context={"user_id": context.user_id},
            )

            # Stream response events
            response_text = ""
            async for event in result.stream_events():
                if event.type == "raw_response_event":
                    # Skip function call argument deltas — only process text deltas
                    event_type = getattr(event.data, "type", "")
                    if "function_call_arguments" in event_type:
                        continue

                    # Text delta from model
                    delta = getattr(event.data, "delta", None)
                    if delta:
                        # Responses API: delta is a string
                        if isinstance(delta, str):
                            response_text += delta
                            yield {
                                "event": "text_delta",
                                "data": {"text": delta},
                            }
                        else:
                            # Chat Completions API: delta is an object
                            content = getattr(delta, "content", None)
                            if content:
                                response_text += content
                                yield {
                                    "event": "text_delta",
                                    "data": {"text": content},
                                }

                elif event.type == "run_item_stream_event":
                    # Run item events for tool calls and results
                    item = getattr(event, "item", None)
                    if item:
                        item_type = getattr(item, "type", "")
                        if item_type == "tool_call_item":
                            yield {
                                "event": "tool_call",
                                "data": {
                                    "id": getattr(item, "call_id", ""),
                                    "name": getattr(item, "name", ""),
                                    "arguments": getattr(item, "arguments", ""),
                                },
                            }
                        elif item_type == "tool_call_output_item":
                            yield {
                                "event": "tool_result",
                                "data": {
                                    "tool_call_id": getattr(item, "call_id", ""),
                                    "status": "success",
                                    "result": getattr(item, "output", None),
                                },
                            }

            # Save assistant response to store
            if response_text:
                assistant_item = ThreadItem(
                    id=self._store.generate_id(),
                    thread_id=thread.id,
                    type="assistant_message",
                    content=response_text,
                )
                await self._store.add_thread_item(thread.id, assistant_item)

            # Signal completion
            yield {"event": "done", "data": {}}

        except Exception as e:
            # Handle errors gracefully
            yield {
                "event": "error",
                "data": {
                    "code": "AGENT_ERROR",
                    "message": str(e),
                },
            }
            yield {"event": "done", "data": {}}
