from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    APPROVAL_NEEDED = "approval_needed"


class WorkflowStage(Enum):
    INIT = "init"
    PREPARE = "prepare"
    EXECUTE = "execute"
    VALIDATE = "validate"
    COMPLETE = "complete"
    ROLLBACK = "rollback"


@dataclass
class WorkflowGoal:
    description: str
    success_criteria: list[str] = field(default_factory=list)
    measured_by: str = ""


@dataclass
class WorkflowCondition:
    check: Callable[[dict[str, Any]], bool] | None = None
    description: str = ""
    required: bool = True


@dataclass
class WorkflowApproval:
    required: bool = False
    approver: str = ""
    prompt: str = ""
    approved: bool = False
