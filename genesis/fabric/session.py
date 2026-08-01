from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.utils.identity import generate_id


class SessionStage(Enum):
    INIT = "init"
    OBSERVE = "observe"
    ACQUIRE = "acquire"
    COMPILE = "compile"
    BUILD_IR = "build_ir"
    BUILD_TWIN = "build_twin"
    UPDATE_GRAPH = "update_graph"
    UPDATE_BRAIN = "update_brain"
    REASON = "reason"
    HYPOTHESIS = "hypothesis"
    PLAN = "plan"
    SIMULATE = "simulate"
    GENERATE_PATCH = "generate_patch"
    VALIDATE = "validate"
    PUBLISH = "publish"
    LEARN = "learn"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class SessionStageResult:
    stage: SessionStage = SessionStage.INIT
    status: str = "pending"
    started_at: float = 0.0
    completed_at: float = 0.0
    output: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        end = self.completed_at or time.time()
        return (end - self.started_at) * 1000


class EngineeringSession:
    """An engineering session tracking a complete lifecycle through the autonomous cycle."""

    def __init__(self, session_type: str = "engineering",
                 metadata: dict[str, Any] | None = None):
        self.id = generate_id("sess", 16)
        self.type = session_type
        self.stage = SessionStage.INIT
        self.metadata: dict[str, Any] = metadata or {}
        self._stage_results: dict[SessionStage, SessionStageResult] = {}
        self._artifacts: dict[str, Any] = {}
        self._started_at = time.time()
        self._completed_at: float = 0.0
        self._status = "active"

    def transition(self, stage: SessionStage):
        if self.stage != SessionStage.COMPLETE and self.stage != SessionStage.FAILED:
            self.stage = stage
            result = SessionStageResult(stage=stage, started_at=time.time())
            self._stage_results[stage] = result

    def complete_stage(self, output: dict[str, Any] | None = None,
                       errors: list[str] | None = None):
        result = self._stage_results.get(self.stage)
        if result:
            result.completed_at = time.time()
            result.status = "failed" if errors else "completed"
            if output:
                result.output = output
            if errors:
                result.errors = errors

    def add_artifact(self, key: str, value: Any):
        self._artifacts[key] = value

    def get_artifact(self, key: str) -> Any | None:
        return self._artifacts.get(key)

    def complete(self):
        self._completed_at = time.time()
        self._status = "completed"
        self.stage = SessionStage.COMPLETE

    def fail(self, reason: str = ""):
        self._completed_at = time.time()
        self._status = "failed"
        self.metadata["failure_reason"] = reason
        self.stage = SessionStage.FAILED

    @property
    def duration_ms(self) -> float:
        end = self._completed_at or time.time()
        return (end - self._started_at) * 1000

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "stage": self.stage.value,
            "status": self._status,
            "duration_ms": self.duration_ms,
            "stages": {
                s.value: {
                    "status": r.status,
                    "duration_ms": r.duration_ms,
                }
                for s, r in self._stage_results.items()
            },
            "artifacts": len(self._artifacts),
        }
