from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class PlanItem:
    title: str
    description: str = ""
    priority: str = "medium"
    effort: str = "medium"
    status: str = "pending"
    source: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class EngineeringPlan:
    name: str
    items: list[PlanItem] = field(default_factory=list)
    repository: str = ""
    created_at: float = 0.0
    total_items: int = 0
    completed_items: int = 0


class EngineeringPlanner:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._plans: dict[str, EngineeringPlan] = {}
        self._planner_obj: EngineeringObject | None = None

    def boot(self):
        self._planner_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="EngineeringPlanner",
            description="Autonomous engineering plan generator based on repository analysis",
            tags=["planner", "planning"],
        )
        self._registry.register(self._planner_obj)

    def generate_plan(self, name: str = "") -> EngineeringPlan:
        items: list[PlanItem] = []
        repo = ""
        if self._kernel:
            dt = self._kernel.twin
            if dt:
                repo = str(dt.root)
                s = dt.summary()
                if s["total_files"] > 200:
                    items.append(PlanItem(
                        title="Refactor large modules",
                        description=f"Repository has {s['total_modules']} modules and {s['total_lines']} lines. Identify and break down modules exceeding 500 lines.",
                        priority="high", effort="large", source="digital_twin",
                        tags=["refactoring", "tech_debt"],
                    ))
                if s["total_classes"] > 0 and s["total_functions"] > 0:
                    ratio = s["total_functions"] / max(s["total_classes"], 1)
                    if ratio > 10:
                        items.append(PlanItem(
                            title="Improve class utilization",
                            description=f"Function-to-class ratio is {ratio:.1f}:1. Consider encapsulating related functions into classes.",
                            priority="medium", effort="medium", source="digital_twin",
                            tags=["design", "refactoring"],
                        ))
            if self._kernel.reasoning:
                findings = self._kernel.reasoning.comprehensive_analysis()
                if isinstance(findings, dict):
                    for ftype, fdata in findings.items():
                        if isinstance(fdata, dict):
                            risk = fdata.get("risk", fdata.get("score", fdata.get("confidence", 0)))
                            if isinstance(risk, (int, float)) and risk > 0.5:
                                items.append(PlanItem(
                                    title=f"Address {ftype} risk",
                                    description=fdata.get("summary", f"Risk score: {risk:.2f}"),
                                    priority="high", effort="medium", source="reasoning",
                                    tags=[ftype, "risk"],
                                ))
            if self._kernel.knowledge:
                decisions = self._kernel.knowledge.get_decisions(limit=5)
                for d in decisions:
                    items.append(PlanItem(
                        title=f"Follow up on decision: {d.get('content', '?')[:60]}",
                        description=d.get("content", ""),
                        priority="medium", effort="small", source="knowledge",
                        tags=["decision", "follow_up"],
                    ))

        plan = EngineeringPlan(
            name=name or f"Plan {time.strftime('%Y-%m-%d %H:%M')}",
            items=items,
            repository=repo,
            created_at=time.time(),
            total_items=len(items),
        )
        self._plans[plan.name] = plan
        plan_obj = EngineeringObject(
            object_type=EngineeringObjectType.PLAN,
            name=plan.name,
            description=f"Engineering plan with {len(items)} items",
            tags=["plan", "generated"],
            metadata={"repository": repo, "items": len(items)},
        )
        self._registry.register(plan_obj)
        return plan

    def list_plans(self) -> list[dict[str, Any]]:
        return [
            {
                "name": p.name,
                "items": p.total_items,
                "completed": p.completed_items,
                "created": p.created_at,
                "repository": p.repository,
            }
            for p in self._plans.values()
        ]

    def get_plan(self, name: str) -> EngineeringPlan | None:
        return self._plans.get(name)
