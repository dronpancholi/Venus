"""
GENESIS Ω² — Civilization II, Phase 6: Engineering Planner.

Hierarchical planning: Vision → Mission → Program → Portfolio → Roadmap →
Milestone → Project → Epic → Capability → Feature → Task → Action.

Every node owns dependencies, economics, risks, confidence, evidence,
expected ROI, and simulation. Integrates with UEM, ExecutionGraph, Economics.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id
from genesis.ontology import UniversalEntity, EntityDefinition, EntityRegistry


class PlannerLevel(Enum):
    VISION = "vision"
    MISSION = "mission"
    PROGRAM = "program"
    PORTFOLIO = "portfolio"
    ROADMAP = "roadmap"
    MILESTONE = "milestone"
    PROJECT = "project"
    EPIC = "epic"
    CAPABILITY = "capability"
    FEATURE = "feature"
    TASK = "task"
    ACTION = "action"


LEVEL_ORDER = [
    PlannerLevel.VISION, PlannerLevel.MISSION, PlannerLevel.PROGRAM,
    PlannerLevel.PORTFOLIO, PlannerLevel.ROADMAP, PlannerLevel.MILESTONE,
    PlannerLevel.PROJECT, PlannerLevel.EPIC, PlannerLevel.CAPABILITY,
    PlannerLevel.FEATURE, PlannerLevel.TASK, PlannerLevel.ACTION,
]


@dataclass
class PlanNode:
    id: str = ""
    name: str = ""
    level: PlannerLevel = PlannerLevel.TASK
    parent_id: str = ""
    description: str = ""
    status: str = "draft"
    confidence: float = 0.5
    priority: int = 0
    effort_hours: float = 0.0
    expected_roi: float = 0.0
    risk: float = 0.0
    dependencies: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    entity_id: str = ""  # Link to UniversalEntity
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("plan", 12)
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @property
    def level_index(self) -> int:
        try:
            return LEVEL_ORDER.index(self.level)
        except ValueError:
            return 99

    @property
    def is_leaf(self) -> bool:
        return self.level in (PlannerLevel.TASK, PlannerLevel.ACTION)


@dataclass
class SimulationResult:
    node_id: str = ""
    predicted_duration_hours: float = 0.0
    predicted_cost: float = 0.0
    predicted_roi: float = 0.0
    confidence: float = 0.5
    risks: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


class EngineeringPlanner:
    """Hierarchical engineering planner — from vision to action."""

    def __init__(self, entity_registry: EntityRegistry | None = None):
        self._nodes: dict[str, PlanNode] = {}
        self._simulations: dict[str, list[SimulationResult]] = defaultdict(list)
        self._registry = entity_registry or EntityRegistry()

    def create(self, name: str, level: PlannerLevel, parent_id: str = "",
               description: str = "", priority: int = 0,
               effort_hours: float = 0.0, expected_roi: float = 0.0,
               risk: float = 0.0, confidence: float = 0.5,
               dependencies: list[str] | None = None,
               tags: list[str] | None = None) -> PlanNode:
        node = PlanNode(
            name=name,
            level=level,
            parent_id=parent_id,
            description=description,
            priority=priority,
            effort_hours=effort_hours,
            expected_roi=expected_roi,
            risk=risk,
            confidence=confidence,
            dependencies=dependencies or [],
            tags=tags or [],
        )
        self._nodes[node.id] = node

        if self._registry:
            entity = UniversalEntity(
                type_name=f"plan_{level.value}",
                identity=node.id,
                maturity=1.0 - risk,
                confidence=confidence,
                attributes={
                    "name": name,
                    "level": level.value,
                    "status": "draft",
                    "effort_hours": effort_hours,
                    "expected_roi": expected_roi,
                    "priority": priority,
                    "parent_id": parent_id,
                },
                dependencies=list(dependencies or []),
            )
            self._registry.add(entity)
            node.entity_id = entity.id

        return node

    def get(self, node_id: str) -> PlanNode | None:
        return self._nodes.get(node_id)

    def children_of(self, parent_id: str) -> list[PlanNode]:
        return [n for n in self._nodes.values() if n.parent_id == parent_id]

    def ancestors(self, node_id: str) -> list[PlanNode]:
        result: list[PlanNode] = []
        current = self._nodes.get(node_id)
        while current and current.parent_id:
            parent = self._nodes.get(current.parent_id)
            if parent:
                result.append(parent)
                current = parent
            else:
                break
        return result

    def descendants(self, node_id: str) -> list[PlanNode]:
        result: list[PlanNode] = []
        children = self.children_of(node_id)
        for child in children:
            result.append(child)
            result.extend(self.descendants(child.id))
        return result

    def by_level(self, level: PlannerLevel) -> list[PlanNode]:
        return [n for n in self._nodes.values() if n.level == level]

    def by_status(self, status: str) -> list[PlanNode]:
        return [n for n in self._nodes.values() if n.status == status]

    def by_tag(self, tag: str) -> list[PlanNode]:
        return [n for n in self._nodes.values() if tag in n.tags]

    def update_status(self, node_id: str, status: str):
        node = self._nodes.get(node_id)
        if node:
            node.status = status
            node.updated_at = datetime.now(timezone.utc).isoformat()

    def add_evidence(self, node_id: str, evidence: str):
        node = self._nodes.get(node_id)
        if node:
            node.evidence.append(evidence)
            node.updated_at = datetime.now(timezone.utc).isoformat()

    def set_entity_link(self, node_id: str, entity_id: str):
        node = self._nodes.get(node_id)
        if node:
            node.entity_id = entity_id

    def simulate(self, node_id: str, **params: Any) -> SimulationResult:
        node = self._nodes.get(node_id)
        if not node:
            raise ValueError(f"Unknown node: {node_id}")

        base_duration = node.effort_hours
        risk_factor = 1.0 + node.risk * 0.5
        predicted_duration = base_duration * risk_factor
        predicted_cost = predicted_duration * 100.0
        predicted_roi = node.expected_roi * node.confidence

        result = SimulationResult(
            node_id=node_id,
            predicted_duration_hours=predicted_duration,
            predicted_cost=predicted_cost,
            predicted_roi=predicted_roi,
            confidence=node.confidence,
            risks=[f"Risk factor: {node.risk:.2f}"] if node.risk > 0.3 else [],
            assumptions=[f"Base effort: {base_duration}h", f"Confidence: {node.confidence:.2f}"],
        )
        self._simulations[node_id].append(result)
        return result

    def root_nodes(self) -> list[PlanNode]:
        return [n for n in self._nodes.values() if not n.parent_id]

    def plan_tree(self) -> list[dict[str, Any]]:
        def _build(node_id: str) -> dict[str, Any]:
            node = self._nodes[node_id]
            children = [_build(c.id) for c in self.children_of(node_id)]
            sims = self._simulations.get(node_id, [])
            return {
                "id": node.id,
                "name": node.name,
                "level": node.level.value,
                "status": node.status,
                "effort_hours": node.effort_hours,
                "expected_roi": node.expected_roi,
                "risk": node.risk,
                "confidence": node.confidence,
                "dependencies": node.dependencies,
                "children": children,
                "simulations": [asdict(s) for s in sims[-1:]] if sims else [],
            }

        return [_build(n.id) for n in self.root_nodes()]

    def summary(self) -> dict[str, Any]:
        by_level = {l: 0 for l in PlannerLevel}
        by_status: dict[str, int] = {}
        total_effort = 0.0
        for node in self._nodes.values():
            by_level[node.level] = by_level.get(node.level, 0) + 1
            by_status[node.status] = by_status.get(node.status, 0) + 1
            total_effort += node.effort_hours

        total_roi = sum(n.expected_roi * n.confidence for n in self._nodes.values())
        avg_risk = sum(n.risk for n in self._nodes.values()) / max(len(self._nodes), 1)

        return {
            "total_nodes": len(self._nodes),
            "by_level": {k.value: v for k, v in by_level.items() if v > 0},
            "by_status": by_status,
            "total_effort_hours": round(total_effort, 1),
            "total_weighted_roi": round(total_roi, 2),
            "average_risk": round(avg_risk, 2),
            "simulations": sum(len(v) for v in self._simulations.values()),
        }

    def save(self, path: str):
        data = {
            "summary": self.summary(),
            "plan_tree": self.plan_tree(),
            "nodes": [asdict(n) for n in self._nodes.values()],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def build_vision(self, name: str, description: str = "") -> PlanNode:
        return self.create(name, PlannerLevel.VISION, description=description)

    def build_mission(self, name: str, vision_id: str, description: str = "") -> PlanNode:
        return self.create(name, PlannerLevel.MISSION, parent_id=vision_id, description=description)

    def build_roadmap(self, name: str, mission_id: str, milestones: list[tuple[str, str, float]] | None = None) -> tuple[PlanNode, list[PlanNode]]:
        roadmap = self.create(name, PlannerLevel.ROADMAP, parent_id=mission_id)
        milestone_nodes = []
        for m_name, m_desc, m_effort in (milestones or []):
            ms = self.create(m_name, PlannerLevel.MILESTONE, parent_id=roadmap.id,
                             description=m_desc, effort_hours=m_effort)
            milestone_nodes.append(ms)
        return roadmap, milestone_nodes

    def build_project(self, name: str, milestone_id: str, description: str = "",
                      effort_hours: float = 0.0, roi: float = 0.0) -> PlanNode:
        return self.create(name, PlannerLevel.PROJECT, parent_id=milestone_id,
                           description=description, effort_hours=effort_hours, expected_roi=roi)

    def build_epic(self, name: str, project_id: str, description: str = "",
                   effort_hours: float = 0.0) -> PlanNode:
        return self.create(name, PlannerLevel.EPIC, parent_id=project_id,
                           description=description, effort_hours=effort_hours)

    def build_feature(self, name: str, epic_id: str, description: str = "",
                      effort_hours: float = 0.0) -> PlanNode:
        return self.create(name, PlannerLevel.FEATURE, parent_id=epic_id,
                           description=description, effort_hours=effort_hours)

    def build_task(self, name: str, feature_id: str, description: str = "",
                   effort_hours: float = 0.0, dependencies: list[str] | None = None) -> PlanNode:
        return self.create(name, PlannerLevel.TASK, parent_id=feature_id,
                           description=description, effort_hours=effort_hours,
                           dependencies=dependencies)
