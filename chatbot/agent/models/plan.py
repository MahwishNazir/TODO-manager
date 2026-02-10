"""
ExecutionPlan model.

Represents a multi-step operation plan for complex requests.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Type of action in an execution plan step."""

    ADD = "ADD"
    LIST = "LIST"
    UPDATE = "UPDATE"
    COMPLETE = "COMPLETE"
    DELETE = "DELETE"


class PlanStatus(str, Enum):
    """Status of an execution plan."""

    PENDING = "PENDING"  # Plan created, awaiting approval
    APPROVED = "APPROVED"  # User approved, ready to execute
    EXECUTING = "EXECUTING"  # Currently running steps
    COMPLETED = "COMPLETED"  # All steps finished successfully
    FAILED = "FAILED"  # A step failed, execution halted
    CANCELLED = "CANCELLED"  # User aborted execution


class PlanStep(BaseModel):
    """A single step in an execution plan."""

    step_number: int = Field(
        ...,
        ge=1,
        description="Step number in execution order"
    )
    action: ActionType = Field(
        ...,
        description="Type of action to perform"
    )
    tool_name: str = Field(
        ...,
        description="MCP tool to invoke"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the tool"
    )
    description: str = Field(
        ...,
        description="Human-readable step description"
    )
    depends_on: Optional[List[int]] = Field(
        default=None,
        description="Step numbers this step depends on"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "step_number": 1,
                "action": "ADD",
                "tool_name": "add_task",
                "params": {"title": "Buy groceries"},
                "description": "Add task 'Buy groceries'",
                "depends_on": None,
            }
        }
    }


class StepResult(BaseModel):
    """Result of executing a plan step."""

    step_number: int = Field(
        ...,
        description="Step number that was executed"
    )
    status: str = Field(
        ...,
        description="Result status: SUCCESS, ERROR, or SKIPPED"
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Step result data"
    )
    error: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Error details if step failed"
    )
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When step completed (UTC)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "step_number": 1,
                "status": "SUCCESS",
                "result": {"task": {"id": "task-123"}},
                "error": None,
                "completed_at": "2026-01-31T12:00:01Z",
            }
        }
    }


class ExecutionPlan(BaseModel):
    """
    Represents a multi-step operation plan.

    Used when a user request requires multiple tool invocations.
    The plan is presented to the user for approval before execution.
    Steps are executed sequentially, capturing intermediate results.
    Execution halts if any step fails.
    """

    plan_id: UUID = Field(
        default_factory=uuid4,
        description="Unique plan identifier"
    )
    session_id: UUID = Field(
        ...,
        description="Parent session ID"
    )
    steps: List[PlanStep] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Ordered execution steps (max 10)"
    )
    status: PlanStatus = Field(
        default=PlanStatus.PENDING,
        description="Overall plan status"
    )
    current_step: Optional[int] = Field(
        default=None,
        description="Currently executing step (0-indexed)"
    )
    results: List[StepResult] = Field(
        default_factory=list,
        description="Results from completed steps"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When plan was created (UTC)"
    )
    approved_at: Optional[datetime] = Field(
        default=None,
        description="When user approved plan (UTC)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "plan_id": "550e8400-e29b-41d4-a716-446655440000",
                "session_id": "660e8400-e29b-41d4-a716-446655440001",
                "steps": [
                    {
                        "step_number": 1,
                        "action": "ADD",
                        "tool_name": "add_task",
                        "params": {"title": "Buy milk"},
                        "description": "Add task 'Buy milk'",
                    }
                ],
                "status": "PENDING",
                "current_step": None,
                "results": [],
            }
        }
    }

    def approve(self) -> None:
        """Mark plan as approved and ready for execution."""
        self.status = PlanStatus.APPROVED
        self.approved_at = datetime.now(timezone.utc)
        self.current_step = 0

    def start_execution(self) -> None:
        """Start plan execution."""
        if self.status != PlanStatus.APPROVED:
            raise ValueError("Plan must be approved before execution")
        self.status = PlanStatus.EXECUTING

    def record_step_success(
        self,
        step_number: int,
        result: Dict[str, Any]
    ) -> StepResult:
        """Record successful step completion."""
        step_result = StepResult(
            step_number=step_number,
            status="SUCCESS",
            result=result,
        )
        self.results.append(step_result)

        # Move to next step
        if self.current_step is not None:
            self.current_step += 1
            if self.current_step >= len(self.steps):
                self.status = PlanStatus.COMPLETED

        return step_result

    def record_step_failure(
        self,
        step_number: int,
        error: Dict[str, Any]
    ) -> StepResult:
        """Record step failure and halt execution."""
        step_result = StepResult(
            step_number=step_number,
            status="ERROR",
            error=error,
        )
        self.results.append(step_result)
        self.status = PlanStatus.FAILED
        return step_result

    def cancel(self) -> None:
        """Cancel plan execution."""
        self.status = PlanStatus.CANCELLED

    def get_current_step(self) -> Optional[PlanStep]:
        """Get the current step to execute."""
        if self.current_step is None or self.current_step >= len(self.steps):
            return None
        return self.steps[self.current_step]

    def is_complete(self) -> bool:
        """Check if plan execution is complete."""
        return self.status in [
            PlanStatus.COMPLETED,
            PlanStatus.FAILED,
            PlanStatus.CANCELLED,
        ]

    def format_for_display(self) -> str:
        """Format plan for user display (FR-030)."""
        lines = ["I'll do the following:"]
        for step in self.steps:
            lines.append(f"{step.step_number}. {step.description}")
        lines.append("\nProceed? (yes/no)")
        return "\n".join(lines)
