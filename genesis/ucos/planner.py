"""
UCOS: CapabilityPlanner — Plans capability execution order and resource allocation.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.ucos.capability import Capability, CapabilityDefinition, CapabilityState
from genesis.utils.identity import generate_id


@dataclass
class ExecutionPlan:
    id: str = ""
    capability_id: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    estimated_duration: float = 0.0
    resource_requirements: dict[str, float] = field(default_factory=dict)
    parallel_groups: list[list[str]] = field(default_factory=list)
    risk: float = 0.0
    status: str = "draft"
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = generate_id("plan", 12)
        if not self.created_at:
            self.created_at = now


class CapabilityPlanner:
    """Plans execution of capabilities based on dependencies and resources."""

    def __init__(self, registry, resolver=None):
        self._registry = registry
        self._resolver = resolver
        self._plans: dict[str, ExecutionPlan] = {}
        self._plan_history: list[ExecutionPlan] = []

    def create_plan(self, capability_id: str) -> ExecutionPlan | None:
        cap = self._registry.get(capability_id)
        if not cap:
            return None
        deps = self._registry.resolve_dependencies(capability_id)
        steps = []
        parallel_groups: list[list[str]] = []
        current_group: list[str] = []
        for dep in deps:
            if not dep.definition.dependencies:
                current_group.append(dep.id)
            else:
                if current_group:
                    parallel_groups.append(list(current_group))
                    current_group = []
                steps.append({
                    "capability_id": dep.id,
                    "name": dep.name,
                    "action": "execute",
                    "estimated_duration": dep.avg_execution_time if dep.execution_count > 0 else 1.0,
                })
        if current_group:
            parallel_groups.append(list(current_group))
        steps.append({
            "capability_id": cap.id,
            "name": cap.name,
            "action": "execute",
            "estimated_duration": cap.avg_execution_time if cap.execution_count > 0 else 1.0,
        })
        est_duration = sum(s.get("estimated_duration", 1.0) for s in steps)
        plan = ExecutionPlan(
            capability_id=capability_id,
            steps=steps,
            estimated_duration=est_duration,
            risk=0.1 * len(deps) / max(len(steps), 1),
            parallel_groups=parallel_groups,
        )
        self._plans[plan.id] = plan
        return plan

    def get_plan(self, plan_id: str) -> ExecutionPlan | None:
        return self._plans.get(plan_id)

    def estimate_resources(self, capability_id: str) -> dict[str, float]:
        cap = self._registry.get(capability_id)
        if not cap:
            return {}
        deps = self._registry.resolve_dependencies(capability_id)
        resources: dict[str, float] = defaultdict(float)
        for dep in [cap] + deps:
            for k, v in dep.definition.execution_policy.get("resources", {}).items():
                resources[k] += v
        return dict(resources)

    def optimize_order(self, capability_ids: list[str]) -> list[str]:
        scored = []
        for cid in capability_ids:
            cap = self._registry.get(cid)
            if not cap:
                continue
            deps_count = len(cap.definition.dependencies)
            consumers_count = len(cap.definition.consumers)
            depth = self._resolver.dependency_depth(cid) if self._resolver else 0
            score = consumers_count * 2 + depth * 1.5 - deps_count * 0.5
            scored.append((score, cid))
        scored.sort(reverse=True)
        return [cid for _, cid in scored]

    def mark_started(self, plan_id: str):
        plan = self._plans.get(plan_id)
        if plan:
            plan.status = "running"
            plan.started_at = time.time()

    def mark_completed(self, plan_id: str):
        plan = self._plans.get(plan_id)
        if plan:
            plan.status = "completed"
            plan.completed_at = time.time()
            self._plan_history.append(plan)

    def mark_failed(self, plan_id: str, reason: str = ""):
        plan = self._plans.get(plan_id)
        if plan:
            plan.status = f"failed: {reason}" if reason else "failed"
            plan.completed_at = time.time()
