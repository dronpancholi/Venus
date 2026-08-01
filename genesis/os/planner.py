"""
PersistentPlanner — decomposes high-level goals into executable task plans.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class PlanStep:
    """A single step in a plan."""
    id: str = ""
    action: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    resources: list[str] = field(default_factory=list)
    timeout: float = 0.0
    status: str = "pending"  # pending, running, success, failed, skipped


@dataclass
class Plan:
    """A complete plan to achieve a goal."""
    id: str = ""
    goal: str = ""
    steps: list[PlanStep] = field(default_factory=list)
    created_at: float = 0.0
    status: str = "active"  # active, completed, failed, cancelled
    priority: float = 0.5
    owner: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class PersistentPlanner:
    """
    Decomposes high-level goals into executable plans.

    Plans are persisted and can be resumed after restart.
    Uses a simple decomposition strategy (can be extended with LLM).
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "planner"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.plans: dict[str, Plan] = {}
        self._decomposers: dict[str, Callable] = {}
        self._load()

    def register_decomposer(self, goal_pattern: str, decomposer: Callable):
        """Register a function that decomposes a goal type into plan steps."""
        self._decomposers[goal_pattern] = decomposer

    def create_plan(self, goal: str, context: dict[str, Any] | None = None) -> Plan:
        """Create a plan for a given goal."""
        plan = Plan(
            id=generate_id("plan", 10),
            goal=goal,
            created_at=time.time(),
        )

        # Find matching decomposer
        decomposer = self._find_decomposer(goal)
        if decomposer:
            steps = decomposer(goal, context or {})
            plan.steps = steps
        else:
            # Default: single-step plan
            plan.steps = [
                PlanStep(
                    id=generate_id("step", 8),
                    action=goal,
                    status="pending",
                )
            ]

        self.plans[plan.id] = plan
        self._save()
        return plan

    def _find_decomposer(self, goal: str) -> Callable | None:
        goal_lower = goal.lower()
        for pattern, decomposer in self._decomposers.items():
            if pattern.lower() in goal_lower:
                return decomposer
        return None

    def get_plan(self, plan_id: str) -> Plan | None:
        return self.plans.get(plan_id)

    def get_next_step(self, plan_id: str) -> PlanStep | None:
        """Get the next executable step (all deps satisfied, not yet run)."""
        plan = self.plans.get(plan_id)
        if not plan or plan.status != "active":
            return None

        for step in plan.steps:
            if step.status != "pending":
                continue
            deps_satisfied = all(
                self._step_status(plan, dep) in ("success", "skipped")
                for dep in step.dependencies
            )
            if deps_satisfied:
                return step
        return None

    def update_step(self, plan_id: str, step_id: str, status: str,
                     result: Any = None):
        plan = self.plans.get(plan_id)
        if not plan:
            return
        for step in plan.steps:
            if step.id == step_id:
                step.status = status
                if result is not None:
                    step.params["_result"] = result
                break

        # Check if all steps complete
        all_done = all(s.status in ("success", "skipped", "failed") for s in plan.steps)
        if all_done:
            plan.status = "completed" if all(s.status == "success" for s in plan.steps) else "failed"

        self._save()

    def cancel_plan(self, plan_id: str):
        plan = self.plans.get(plan_id)
        if plan:
            plan.status = "cancelled"
            self._save()

    def _step_status(self, plan: Plan, step_id: str) -> str:
        for s in plan.steps:
            if s.id == step_id:
                return s.status
        return "unknown"

    def list_plans(self, status: str = "") -> list[Plan]:
        if status:
            return [p for p in self.plans.values() if p.status == status]
        return list(self.plans.values())

    def summary(self) -> dict[str, Any]:
        statuses = {}
        for p in self.plans.values():
            statuses[p.status] = statuses.get(p.status, 0) + 1
        return {
            "total_plans": len(self.plans),
            "total_steps": sum(len(p.steps) for p in self.plans.values()),
            "status_distribution": statuses,
            "decomposers_registered": len(self._decomposers),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "planner_state.json"

    def _save(self):
        data = {
            pid: {
                "id": p.id, "goal": p.goal, "status": p.status,
                "priority": p.priority, "owner": p.owner,
                "created_at": p.created_at, "metadata": p.metadata,
                "steps": [s.__dict__ for s in p.steps],
            }
            for pid, p in self.plans.items()
        }
        (self._state_path()).write_text(json.dumps(data, indent=2))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for pid, pd in data.items():
                    plan = Plan(
                        id=pd["id"], goal=pd["goal"],
                        status=pd.get("status", "active"),
                        priority=pd.get("priority", 0.5),
                        owner=pd.get("owner", ""),
                        created_at=pd.get("created_at", 0),
                        metadata=pd.get("metadata", {}),
                    )
                    for sd in pd.get("steps", []):
                        plan.steps.append(PlanStep(**sd))
                    self.plans[pid] = plan
            except Exception:
                pass
