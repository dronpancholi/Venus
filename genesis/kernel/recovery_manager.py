"""
Universal Kernel: RecoveryManager — Failure detection and recovery orchestration.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from genesis.kernel.types import RecoveryPlan


class RecoveryManager:
    """Detects failures and orchestrates recovery strategies."""

    def __init__(self):
        self._plans: dict[str, RecoveryPlan] = {}
        self._history: list[dict[str, Any]] = []

    def create_plan(self, capability_id: str, strategy: str = "restart",
                     checkpoint_id: str = "", max_attempts: int = 3) -> RecoveryPlan:
        plan = RecoveryPlan(
            capability_id=capability_id,
            strategy=strategy,
            checkpoint_id=checkpoint_id,
            max_attempts=max_attempts,
        )
        self._plans[plan.id] = plan
        self._history.append({
            "action": "create_plan",
            "plan_id": plan.id,
            "capability_id": capability_id,
            "strategy": strategy,
            "timestamp": time.time(),
        })
        return plan

    def get_plan(self, plan_id: str) -> RecoveryPlan | None:
        return self._plans.get(plan_id)

    def plans_for(self, capability_id: str) -> list[RecoveryPlan]:
        return [p for p in self._plans.values() if p.capability_id == capability_id]

    def execute(self, plan_id: str) -> bool:
        plan = self._plans.get(plan_id)
        if not plan or plan.status != "pending":
            return False
        plan.attempt += 1
        plan.executed_at = time.time()
        if plan.attempt > plan.max_attempts:
            plan.status = "exhausted"
            return False
        plan.status = "executing"
        self._history.append({
            "action": "execute",
            "plan_id": plan_id,
            "capability_id": plan.capability_id,
            "strategy": plan.strategy,
            "attempt": plan.attempt,
            "timestamp": time.time(),
        })
        if plan.strategy == "restart":
            plan.status = "completed"
            return True
        elif plan.strategy == "restore":
            if plan.checkpoint_id:
                plan.status = "completed"
                return True
            plan.status = "failed"
            return False
        elif plan.strategy == "failover":
            plan.status = "completed"
            return True
        elif plan.strategy == "degrade":
            plan.status = "completed"
            return True
        plan.status = "failed"
        return False

    def fail(self, plan_id: str, error: str = "") -> bool:
        plan = self._plans.get(plan_id)
        if not plan:
            return False
        plan.status = f"failed: {error}" if error else "failed"
        return True

    def pending_plans(self) -> list[RecoveryPlan]:
        return [p for p in self._plans.values() if p.status == "pending"]

    def active_plans(self) -> list[RecoveryPlan]:
        return [p for p in self._plans.values() if p.status in ("pending", "executing")]

    def cleanup(self, max_age_seconds: float = 86400) -> int:
        now = time.time()
        removed = 0
        for pid in list(self._plans.keys()):
            plan = self._plans[pid]
            if plan.status in ("completed", "exhausted", "failed"):
                if now - plan.executed_at > max_age_seconds:
                    self._plans.pop(pid)
                    removed += 1
        return removed

    def summary(self) -> dict[str, Any]:
        statuses: dict[str, int] = {}
        strategies: dict[str, int] = {}
        for p in self._plans.values():
            statuses[p.status] = statuses.get(p.status, 0) + 1
            strategies[p.strategy] = strategies.get(p.strategy, 0) + 1
        return {
            "total": len(self._plans),
            "by_status": statuses,
            "by_strategy": strategies,
            "active": len(self.active_plans()),
            "total_operations": len(self._history),
        }
