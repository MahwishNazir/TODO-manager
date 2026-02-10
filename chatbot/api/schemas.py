"""
API response schemas for AI Agent API (T105).

Defines Pydantic models matching the OpenAPI specification.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Base response model
class APIResponse(BaseModel):
    """Base API response wrapper."""

    success: bool = Field(..., description="Whether the request succeeded")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error details if failed")


# Session schemas
class CreateSessionRequest(BaseModel):
    """Request to create a new session."""

    # No body required - user_id comes from JWT
    pass


class SessionResponse(BaseModel):
    """Session data in responses."""

    session_id: UUID = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User who owns the session")
    created_at: datetime = Field(..., description="When session was created")
    last_active: datetime = Field(..., description="Last activity timestamp")
    status: str = Field(..., description="Session status (ACTIVE/EXPIRED)")


class CreateSessionResponse(APIResponse):
    """Response for session creation."""

    data: Optional[Dict[str, SessionResponse]] = None


class GetSessionResponse(APIResponse):
    """Response for getting session details."""

    data: Optional[Dict[str, SessionResponse]] = None


# Message schemas
class SendMessageRequest(BaseModel):
    """Request to send a message to the agent."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message content"
    )


class MessageResponse(BaseModel):
    """Agent message response."""

    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When message was sent")


class SendMessageResponse(APIResponse):
    """Response for sending a message."""

    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contains 'response' (agent reply) and 'requires_confirmation' flag"
    )


class GetHistoryResponse(APIResponse):
    """Response for getting conversation history."""

    data: Optional[Dict[str, List[MessageResponse]]] = None


# Confirmation schemas
class ConfirmActionRequest(BaseModel):
    """Request to confirm or cancel a pending action."""

    response: str = Field(
        ...,
        description="User's response (yes/no/cancel)"
    )


class ConfirmActionResponse(APIResponse):
    """Response for confirmation action."""

    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contains 'confirmed', 'cancelled', or 'message'"
    )


# Plan schemas
class PlanStepSchema(BaseModel):
    """Execution plan step."""

    order: int = Field(..., description="Step order (0-indexed)")
    action: str = Field(..., description="Action type (ADD/UPDATE/COMPLETE/DELETE/LIST)")
    description: str = Field(..., description="Human-readable step description")
    status: str = Field(default="pending", description="Step status")


class PlanResponse(BaseModel):
    """Execution plan details."""

    plan_id: UUID = Field(..., description="Unique plan identifier")
    status: str = Field(..., description="Plan status (PENDING/EXECUTING/COMPLETED/FAILED)")
    steps: List[PlanStepSchema] = Field(..., description="Plan steps")
    current_step: Optional[int] = Field(default=None, description="Currently executing step")


class GetPlanResponse(APIResponse):
    """Response for getting plan details."""

    data: Optional[Dict[str, PlanResponse]] = None


class ApprovePlanRequest(BaseModel):
    """Request to approve a plan."""

    approve: bool = Field(..., description="Whether to approve the plan")


class ApprovePlanResponse(APIResponse):
    """Response for plan approval."""

    data: Optional[Dict[str, Any]] = None


# Error schemas
class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="User-friendly error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error context")


class ErrorResponse(BaseModel):
    """Error response structure."""

    success: bool = Field(default=False)
    error: ErrorDetail = Field(..., description="Error details")


# =============================================================================
# Stateless Chat API Schemas (Phase III Part 5)
# =============================================================================

class MessageInput(BaseModel):
    """Single message in conversation history (client → server)."""

    role: str = Field(
        ...,
        pattern="^(user|assistant)$",
        description="Who sent the message (user or assistant)"
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Message text content"
    )


class ConfirmationInput(BaseModel):
    """Client confirmation for pending destructive action."""

    token: str = Field(..., description="Confirmation token from previous response")
    confirmed: bool = Field(..., description="true to execute, false to cancel")


class StatelessChatRequest(BaseModel):
    """Request body for stateless chat endpoint."""

    messages: List[MessageInput] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Conversation history (1-50 messages)"
    )
    confirmation: Optional[ConfirmationInput] = Field(
        default=None,
        description="Optional confirmation for pending destructive action"
    )


class MessageOutput(BaseModel):
    """Agent's response message (server → client)."""

    message_id: UUID = Field(..., description="Unique message identifier")
    role: str = Field(default="assistant", description="Always 'assistant' for responses")
    content: str = Field(..., description="Agent's response text")
    timestamp: datetime = Field(..., description="When response was generated")


class ToolCallOutput(BaseModel):
    """Documentation of a single MCP tool invocation."""

    tool_name: str = Field(..., description="Name of MCP tool called")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to tool")
    status: str = Field(..., pattern="^(success|error)$", description="Execution outcome")
    result: Optional[Any] = Field(default=None, description="Tool return value (if success)")
    error: Optional[str] = Field(default=None, description="Error message (if error)")
    execution_time_ms: int = Field(..., ge=0, description="Execution duration in milliseconds")


class PendingConfirmation(BaseModel):
    """Request for user confirmation before destructive action."""

    token: str = Field(..., description="JWT confirmation token")
    action: str = Field(..., description="Action type (e.g., delete_task)")
    description: str = Field(..., description="Human-readable action description")
    expires_at: datetime = Field(..., description="Token expiration timestamp")


class TokenUsage(BaseModel):
    """Token consumption metrics for cost tracking."""

    prompt_tokens: int = Field(..., ge=0, description="Tokens in prompt/input")
    completion_tokens: int = Field(..., ge=0, description="Tokens in completion/output")
    total_tokens: int = Field(..., ge=0, description="Total tokens consumed")


class StatelessChatResponse(BaseModel):
    """Response body from stateless chat endpoint."""

    response: MessageOutput = Field(..., description="Agent's response message")
    tool_calls: List[ToolCallOutput] = Field(
        default_factory=list,
        description="All tool invocations (may be empty)"
    )
    pending_confirmation: Optional[PendingConfirmation] = Field(
        default=None,
        description="Present when destructive action requires confirmation"
    )
    usage: TokenUsage = Field(..., description="Token consumption metrics")
