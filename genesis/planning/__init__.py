"""
Autonomous Planning System — Hierarchical 7-Level Planner (GENESIS IX Phase 3).

Level hierarchy:
  1. Strategic Planner      — Long-term vision, mission, epoch goals
  2. Architectural Planner  — System design, module boundaries, interfaces
  3. Research Planner       — Knowledge gaps, experiments, investigations
  4. Implementation Planner — Code changes, refactoring, feature work
  5. Execution Planner      — Task scheduling, resource allocation, sequencing
  6. Validation Planner     — Tests, verification, compliance, review
  7. Publication Planner    — Documentation, changelogs, release notes

Rules:
  - Plans decompose top-down (strategic → architectural → ... → publication)
  - Levels negotiate priorities via priority arbitration
  - Plans become executable DAGs of PlanSteps
  - Plans persist through the Engineering Brain
  - Plans survive runtime restarts
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.brain import EngineeringBrain, BrainEntity
from genesis.utils.identity import generate_id


# ── Plan Primitives ──


class PlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class PlannerLevel(str, Enum):
    STRATEGIC = "strategic"
    ARCHITECTURAL = "architectural"
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    EXECUTION = "execution"
    VALIDATION = "validation"
    PUBLICATION = "publication"


LEVEL_ORDER = [
    PlannerLevel.STRATEGIC,
    PlannerLevel.ARCHITECTURAL,
    PlannerLevel.RESEARCH,
    PlannerLevel.IMPLEMENTATION,
    PlannerLevel.EXECUTION,
    PlannerLevel.VALIDATION,
    PlannerLevel.PUBLICATION,
]


@dataclass
class PlanStep:
    """An atomic step in a plan."""
    id: str = ""
    action: str = ""
    description: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    estimated_effort: float = 1.0
    required_resources: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("step", 12)
        if not self.created_at:
            self.created_at = time.time()

    def to_brain_entity(self, plan_id: str) -> BrainEntity:
        entity = BrainEntity(
            label=self.action[:64],
            entity_type="plan_step",
            source_system="planning",
            source_id=self.id,
        )
        entity.attributes["plan_id"] = plan_id
        entity.attributes["action"] = self.action
        entity.attributes["description"] = self.description
        entity.attributes["estimated_effort"] = self.estimated_effort
        entity.attributes["status"] = self.status.value
        entity.attributes["dependencies"] = list(self.dependencies)
        return entity


@dataclass
class Plan:
    """A complete plan at one level of the hierarchy."""
    id: str = ""
    level: str = "strategic"
    title: str = ""
    goal: str = ""
    parent_plan_id: str = ""
    sub_plan_ids: list[str] = field(default_factory=list)
    steps: list[PlanStep] = field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    priority: float = 0.5
    owner: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id(self.level[:4], 12)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @property
    def is_terminal(self) -> bool:
        return not self.sub_plan_ids

    @property
    def progress(self) -> float:
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        return completed / len(self.steps)

    def add_step(self, action: str, description: str = "",
                 dependencies: list[str] | None = None,
                 estimated_effort: float = 1.0,
                 **params) -> PlanStep:
        step = PlanStep(
            action=action,
            description=description,
            dependencies=dependencies or [],
            estimated_effort=estimated_effort,
            params=params,
        )
        self.steps.append(step)
        self.updated_at = time.time()
        return step

    def next_steps(self) -> list[PlanStep]:
        """Return steps that are ready to execute."""
        completed_ids = {
            s.id for s in self.steps
            if s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED)
        }
        ready = []
        for s in self.steps:
            if s.status != StepStatus.PENDING:
                continue
            if all(dep in completed_ids for dep in s.dependencies):
                ready.append(s)
        return ready

    def to_brain_entity(self) -> BrainEntity:
        entity = BrainEntity(
            label=self.title or self.goal[:64],
            entity_type="plan",
            source_system="planning",
            source_id=self.id,
            description=self.goal[:500],
        )
        entity.attributes["level"] = self.level
        entity.attributes["status"] = self.status.value
        entity.attributes["priority"] = self.priority
        entity.attributes["parent_plan_id"] = self.parent_plan_id
        entity.attributes["sub_plan_count"] = len(self.sub_plan_ids)
        entity.attributes["step_count"] = len(self.steps)
        entity.attributes["progress"] = self.progress
        return entity

    def summary(self) -> dict[str, Any]:
        by_status: dict[str, int] = {}
        for s in self.steps:
            by_status[s.status.value] = by_status.get(s.status.value, 0) + 1
        return {
            "id": self.id,
            "level": self.level,
            "title": self.title or self.goal[:48],
            "status": self.status.value,
            "priority": self.priority,
            "steps_total": len(self.steps),
            "steps_by_status": by_status,
            "progress": round(self.progress, 3),
            "sub_plans": len(self.sub_plan_ids),
            "parent": self.parent_plan_id or None,
        }


# ── Planner Base ──


class Planner:
    """Base class for all hierarchical planners."""

    def __init__(self, level: str, brain: EngineeringBrain | None = None):
        self.level = level
        self.brain = brain
        self.plans: dict[str, Plan] = {}

    def create_plan(self, goal: str, title: str = "",
                    parent_plan_id: str = "",
                    priority: float = 0.5) -> Plan:
        plan = Plan(
            level=self.level,
            title=title or goal[:64],
            goal=goal,
            parent_plan_id=parent_plan_id,
            priority=priority,
        )
        self.plans[plan.id] = plan
        if self.brain:
            self.brain.register(plan.to_brain_entity())
            for step in plan.steps:
                self.brain.register(step.to_brain_entity(plan.id))
        return plan

    def get_plan(self, plan_id: str) -> Plan | None:
        return self.plans.get(plan_id)

    def update_status(self, plan_id: str, status: PlanStatus) -> bool:
        plan = self.plans.get(plan_id)
        if plan is None:
            return False
        plan.status = status
        plan.updated_at = time.time()
        if self.brain:
            entity = self.brain.find_by_source("planning", plan_id)
            if entity:
                entity.attributes["status"] = status.value
                self.brain.register(entity)
        return True

    def all_plans(self) -> list[Plan]:
        return list(self.plans.values())

    def active_plans(self) -> list[Plan]:
        return [p for p in self.plans.values() if p.status == PlanStatus.ACTIVE]

    def summary(self) -> dict[str, Any]:
        by_status: dict[str, int] = {}
        for p in self.plans.values():
            by_status[p.status.value] = by_status.get(p.status.value, 0) + 1
        return {
            "level": self.level,
            "total_plans": len(self.plans),
            "by_status": by_status,
            "active_count": len(self.active_plans()),
        }


# ── Specialized Planners ──


class StrategicPlanner(Planner):
    """Level 1: Long-term vision, mission, epoch goals."""

    def __init__(self, brain: EngineeringBrain | None = None):
        super().__init__("strategic", brain)

    def plan_epoch(self, vision: str, duration_days: int = 365,
                   objectives: list[str] | None = None) -> Plan:
        plan = self.create_plan(
            goal=vision,
            title=f"Epoch: {vision[:48]}",
            priority=1.0,
        )
        for obj in (objectives or []):
            plan.add_step(
                action=f"achieve:{obj[:48]}",
                description=obj[:200],
                estimated_effort=float(duration_days) / max(len(objectives or [1]), 1),
            )
        plan.status = PlanStatus.ACTIVE
        return plan


class ArchitecturalPlanner(Planner):
    """Level 2: System design, module boundaries, interfaces."""

    def __init__(self, brain: EngineeringBrain | None = None):
        super().__init__("architectural", brain)

    def plan_design(self, component: str, requirements: list[str],
                    parent_plan_id: str = "") -> Plan:
        plan = self.create_plan(
            goal=f"Design {component}",
            title=f"Architecture: {component}",
            parent_plan_id=parent_plan_id,
            priority=0.8,
        )
        for req in requirements:
            plan.add_step(
                action=f"design:{component}",
                description=req[:200],
                estimated_effort=2.0,
                requirement=req,
            )
        return plan


class ResearchPlanner(Planner):
    """Level 3: Knowledge gaps, experiments, investigations."""

    def __init__(self, brain: EngineeringBrain | None = None):
        super().__init__("research", brain)

    def plan_investigation(self, question: str, hypotheses: list[str],
                           parent_plan_id: str = "") -> Plan:
        plan = self.create_plan(
            goal=question,
            title=f"Research: {question[:48]}",
            parent_plan_id=parent_plan_id,
            priority=0.6,
        )
        for h in hypotheses:
            plan.add_step(
                action=f"investigate:{h[:48]}",
                description=f"Test hypothesis: {h[:200]}",
                estimated_effort=3.0,
            )
        return plan


class ImplementationPlanner(Planner):
    """Level 4: Code changes, refactoring, feature work."""

    def __init__(self, brain: EngineeringBrain | None = None):
        super().__init__("implementation", brain)

    def plan_feature(self, feature: str, tasks: list[str],
                     parent_plan_id: str = "") -> Plan:
        plan = self.create_plan(
            goal=f"Implement {feature}",
            title=f"Feature: {feature}",
            parent_plan_id=parent_plan_id,
            priority=0.5,
        )
        for i, task in enumerate(tasks):
            step = plan.add_step(
                action=f"implement:{task[:48]}",
                description=task[:200],
                estimated_effort=2.0,
            )
            if i > 0:
                step.dependencies = [plan.steps[i - 1].id]
        return plan


class ExecutionPlanner(Planner):
    """Level 5: Task scheduling, resource allocation, sequencing."""

    def __init__(self, brain: EngineeringBrain | None = None):
        super().__init__("execution", brain)

    def schedule_plan(self, plan_to_execute: Plan,
                      available_resources: list[str] | None = None,
                      parent_plan_id: str = "") -> Plan:
        plan = self.create_plan(
            goal=f"Execute {plan_to_execute.title or plan_to_execute.id}",
            title=f"Execution: {plan_to_execute.title[:48]}" if plan_to_execute.title else f"Execution: {plan_to_execute.id[:16]}",
            parent_plan_id=parent_plan_id,
            priority=0.4,
        )
        for step in plan_to_execute.steps:
            plan.add_step(
                action=step.action,
                description=step.description,
                dependencies=list(step.dependencies),
                estimated_effort=step.estimated_effort,
                resources=available_resources or [],
            )
        return plan


class ValidationPlanner(Planner):
    """Level 6: Tests, verification, compliance, review."""

    def __init__(self, brain: EngineeringBrain | None = None):
        super().__init__("validation", brain)

    def plan_validation(self, target: str, checks: list[str],
                        parent_plan_id: str = "") -> Plan:
        plan = self.create_plan(
            goal=f"Validate {target}",
            title=f"Validation: {target}",
            parent_plan_id=parent_plan_id,
            priority=0.3,
        )
        for check in checks:
            plan.add_step(
                action=f"validate:{check[:48]}",
                description=check[:200],
                estimated_effort=1.0,
            )
        return plan


class PublicationPlanner(Planner):
    """Level 7: Documentation, changelogs, release notes."""

    def __init__(self, brain: EngineeringBrain | None = None):
        super().__init__("publication", brain)

    def plan_publication(self, artifact: str, audiences: list[str] | None = None,
                         parent_plan_id: str = "") -> Plan:
        plan = self.create_plan(
            goal=f"Publish {artifact}",
            title=f"Publication: {artifact}",
            parent_plan_id=parent_plan_id,
            priority=0.2,
        )
        plan.add_step(
            action="write_documentation",
            description=f"Write documentation for {artifact}",
            estimated_effort=1.0,
        )
        plan.add_step(
            action="generate_changelog",
            description="Generate changelog entries",
            estimated_effort=0.5,
            dependencies=[plan.steps[0].id] if plan.steps else [],
        )
        plan.add_step(
            action="prepare_release",
            description="Prepare release notes",
            estimated_effort=0.5,
            dependencies=[plan.steps[-1].id] if len(plan.steps) > 1 else [],
        )
        for audience in (audiences or []):
            plan.add_step(
                action=f"communicate:{audience}",
                description=f"Communicate release to {audience}",
                estimated_effort=0.5,
            )
        return plan


# ── Planning Orchestrator ──


class PlanningSystem:
    """
    Orchestrates the 7-level hierarchical planning system.

    Manages:
      - All 7 planners
      - Plan decomposition across levels
      - Priority negotiation
      - Plan graph persistence via Engineering Brain
      - Runtime restart recovery
    """

    def __init__(self, brain: EngineeringBrain | None = None):
        self.brain = brain
        self.strategic = StrategicPlanner(brain)
        self.architectural = ArchitecturalPlanner(brain)
        self.research = ResearchPlanner(brain)
        self.implementation = ImplementationPlanner(brain)
        self.execution = ExecutionPlanner(brain)
        self.validation = ValidationPlanner(brain)
        self.publication = PublicationPlanner(brain)

        self._planners: dict[str, Planner] = {
            "strategic": self.strategic,
            "architectural": self.architectural,
            "research": self.research,
            "implementation": self.implementation,
            "execution": self.execution,
            "validation": self.validation,
            "publication": self.publication,
        }

    def get_planner(self, level: str) -> Planner | None:
        return self._planners.get(level)

    # ─── Decomposition ──

    def decompose(self, top_plan: Plan) -> list[Plan]:
        """
        Decompose a plan by passing sub-goals to the next level down.

        Returns all child plans created.
        """
        level_idx = LEVEL_ORDER_MAP.get(top_plan.level)
        if level_idx is None or level_idx >= len(LEVEL_ORDER) - 1:
            return []

        next_level = LEVEL_ORDER[level_idx + 1].value
        next_planner = self._planners.get(next_level)
        if next_planner is None:
            return []

        children: list[Plan] = []
        for step in top_plan.steps:
            child = next_planner.create_plan(
                goal=f"{top_plan.goal}: {step.action}",
                title=f"{next_level}: {step.action[:48]}",
                parent_plan_id=top_plan.id,
                priority=top_plan.priority * 0.9,
            )
            children.append(child)
            top_plan.sub_plan_ids.append(child.id)

        top_plan.updated_at = time.time()
        return children

    def decompose_full(self, vision: str, objectives: list[str] | None = None) -> Plan:
        """
        Create a complete 7-level plan hierarchy from a strategic vision.

        Recursively decomposes plans from strategic all the way to publication.
        """
        strategic_plan = self.strategic.plan_epoch(vision, objectives=objectives)
        self._decompose_recursive(strategic_plan, max_depth=7)
        return strategic_plan

    def _decompose_recursive(self, plan: Plan, depth: int = 0, max_depth: int = 7) -> None:
        if depth >= max_depth - 1:
            return
        children = self.decompose(plan)
        for child in children:
            self._decompose_recursive(child, depth + 1, max_depth)

    # ─── Priority Negotiation ──

    def negotiate_priorities(self) -> list[dict[str, Any]]:
        """
        Let each level's active plans negotiate priority.
        Higher-level plans can override lower-level priorities.
        """
        all_plans = self.all_plans()
        if not all_plans:
            return []

        conflicts: list[dict[str, Any]] = []
        for p in all_plans:
            if p.status != PlanStatus.ACTIVE:
                continue
            for child_id in p.sub_plan_ids:
                child = self._find_plan(child_id)
                if child and child.priority > p.priority:
                    child.priority = p.priority * 0.95
                    conflicts.append({
                        "plan_id": child.id,
                        "old_priority": round(child.priority / 0.95, 4),
                        "new_priority": round(child.priority, 4),
                        "reason": f"Overridden by parent {p.id} (priority {p.priority})",
                    })
        return conflicts

    def _find_plan(self, plan_id: str) -> Plan | None:
        for planner in self._planners.values():
            p = planner.get_plan(plan_id)
            if p:
                return p
        return None

    # ─── Status & Reporting ──

    def all_plans(self) -> list[Plan]:
        plans: list[Plan] = []
        for planner in self._planners.values():
            plans.extend(planner.all_plans())
        return plans

    def active_plans(self) -> list[Plan]:
        plans: list[Plan] = []
        for planner in self._planners.values():
            plans.extend(planner.active_plans())
        return plans

    def plan_graph(self) -> dict[str, Any]:
        """Return the full plan dependency graph."""
        all_plans = self.all_plans()
        nodes = [p.summary() for p in all_plans]
        edges = []
        for p in all_plans:
            for child_id in p.sub_plan_ids:
                edges.append({"source": p.id, "target": child_id, "relation": "decomposes_to"})
            if p.parent_plan_id:
                edges.append({"source": p.parent_plan_id, "target": p.id, "relation": "parent_of"})
        return {"nodes": nodes, "edges": edges}

    def summary(self) -> dict[str, Any]:
        by_level: dict[str, Any] = {}
        for name, planner in self._planners.items():
            by_level[name] = planner.summary()
        all_active = self.active_plans()
        return {
            "planners": by_level,
            "total_plans": sum(s["total_plans"] for s in by_level.values()),
            "total_active": len(all_active),
            "levels": list(self._planners.keys()),
        }


LEVEL_ORDER_MAP: dict[str, int] = {
    level.value: idx for idx, level in enumerate(LEVEL_ORDER)
}
