from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any

from genesis.autonomous.analyzer import AnalysisFinding, AnalysisReport
from genesis.utils.identity import generate_id


class PlanType(Enum):
    REFACTOR = "refactor"
    CLEANUP = "cleanup"
    OPTIMIZE = "optimize"
    FIX = "fix"
    FEATURE = "feature"
    TEST = "test"


class PlanStatus(Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ImprovementStep:
    action: str = ""
    file: str = ""
    description: str = ""
    estimated_effort: float = 1.0


@dataclass
class ImprovementPlan:
    id: str = ""
    plan_type: PlanType = PlanType.REFACTOR
    title: str = ""
    description: str = ""
    priority: float = 0.0
    status: PlanStatus = PlanStatus.DRAFT
    steps: list[ImprovementStep] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    estimated_effort: float = 0.0
    created_at: float = 0.0
    completed_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("plan", 14)
        if not self.created_at:
            self.created_at = time.time()
        if self.steps and not self.estimated_effort:
            self.estimated_effort = sum(s.estimated_effort for s in self.steps)


@dataclass
class PlanningSession:
    id: str = ""
    started_at: float = 0.0
    completed_at: float = 0.0
    report: AnalysisReport | None = None
    plans: list[ImprovementPlan] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("plan_session", 14)
        if not self.started_at:
            self.started_at = time.time()


SEVERITY_WEIGHTS = {
    "critical": 100,
    "error": 50,
    "warning": 20,
    "info": 5,
}

CATEGORY_PLAN_MAP: dict[str, PlanType] = {
    "complexity": PlanType.REFACTOR,
    "duplication": PlanType.REFACTOR,
    "bug_prone": PlanType.FIX,
    "todo": PlanType.CLEANUP,
    "style": PlanType.CLEANUP,
    "imports": PlanType.CLEANUP,
}


class ImprovementPlanner:
    def __init__(self):
        self._history: list[PlanningSession] = []
        self._lock = RLock()

    def plan(self, report: AnalysisReport) -> PlanningSession:
        session = PlanningSession(report=report)

        by_category: dict[str, list[AnalysisFinding]] = {}
        for f in report.findings:
            by_category.setdefault(f.category, []).append(f)

        for category, findings in by_category.items():
            plan_type = CATEGORY_PLAN_MAP.get(category, PlanType.FEATURE)
            title = f"{plan_type.value.title()}: {category} issues"
            steps: list[ImprovementStep] = []
            total_priority = 0.0

            for finding in findings:
                weight = SEVERITY_WEIGHTS.get(finding.severity, 5)
                total_priority += weight * (finding.metric if finding.metric > 0 else 1.0)
                steps.append(ImprovementStep(
                    action=f"{finding.suggestion or 'Investigate'}",
                    file=finding.file,
                    description=finding.message,
                    estimated_effort=max(0.5, weight / 20),
                ))

            plan = ImprovementPlan(
                plan_type=plan_type,
                title=title,
                description=f"Address {len(findings)} {category} issues across {len(set(s.file for s in steps))} files",
                priority=total_priority / max(1, len(findings)),
                steps=steps[:10],
                findings=[f.message for f in findings],
            )
            session.plans.append(plan)

        session.plans.sort(key=lambda p: -p.priority)
        session.completed_at = time.time()
        session.metrics = {
            "total_plans": len(session.plans),
            "total_steps": sum(len(p.steps) for p in session.plans),
            "estimated_effort": sum(p.estimated_effort for p in session.plans),
            "highest_priority": session.plans[0].priority if session.plans else 0,
        }

        with self._lock:
            self._history.append(session)
        return session

    def approve(self, plan_id: str) -> bool:
        with self._lock:
            for session in self._history:
                for plan in session.plans:
                    if plan.id == plan_id:
                        if plan.status == PlanStatus.DRAFT:
                            plan.status = PlanStatus.APPROVED
                            return True
                        return False
            return False

    def complete(self, plan_id: str) -> bool:
        with self._lock:
            for session in self._history:
                for plan in session.plans:
                    if plan.id == plan_id:
                        plan.status = PlanStatus.COMPLETED
                        plan.completed_at = time.time()
                        return True
            return False

    def history(self, limit: int = 10) -> list[PlanningSession]:
        with self._lock:
            return list(self._history[-limit:])

    def summary(self) -> dict[str, Any]:
        with self._lock:
            total_plans = sum(len(s.plans) for s in self._history)
            total_completed = sum(
                1 for s in self._history for p in s.plans if p.status == PlanStatus.COMPLETED
            )
            return {
                "sessions": len(self._history),
                "total_plans": total_plans,
                "completed": total_completed,
                "in_progress": total_plans - total_completed,
            }
