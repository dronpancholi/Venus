"""
GENESIS-VIII Program 8: Software Civilization V2.

Institutes, Universities, Departments, Laboratories, Research groups,
Review boards, Engineering councils, Standards committees, Evolution committee,
Architecture council, Language institute, OS institute, Compiler institute,
AI institute, Formal methods institute, Physics institute, Knowledge institute.

Each performs autonomous work.
"""

from __future__ import annotations

import warnings
warnings.warn(
    f"{__name__} is deprecated. Use genesis.digital_civilization.DigitalCivilization instead.",
    DeprecationWarning,
    stacklevel=2,
)

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class InstituteType(Enum):
    UNIVERSITY = "university"
    DEPARTMENT = "department"
    LABORATORY = "laboratory"
    RESEARCH_GROUP = "research_group"
    REVIEW_BOARD = "review_board"
    ENGINEERING_COUNCIL = "engineering_council"
    STANDARDS_COMMITTEE = "standards_committee"
    EVOLUTION_COMMITTEE = "evolution_committee"
    ARCHITECTURE_COUNCIL = "architecture_council"
    LANGUAGE_INSTITUTE = "language_institute"
    OS_INSTITUTE = "os_institute"
    COMPILER_INSTITUTE = "compiler_institute"
    AI_INSTITUTE = "ai_institute"
    FORMAL_METHODS_INSTITUTE = "formal_methods_institute"
    PHYSICS_INSTITUTE = "physics_institute"
    KNOWLEDGE_INSTITUTE = "knowledge_institute"


class WorkProduct(Enum):
    RESEARCH_PAPER = "research_paper"
    STANDARD = "standard"
    PROTOCOL = "protocol"
    SPECIFICATION = "specification"
    REVIEW = "review"
    ARCHITECTURE_DECISION = "architecture_decision"
    IMPLEMENTATION = "implementation"
    BENCHMARK = "benchmark"
    EXPERIMENT = "experiment"
    PUBLICATION = "publication"
    REPORT = "report"
    RECOMMENDATION = "recommendation"


@dataclass
class Institute:
    id: str = ""
    name: str = ""
    institution_type: InstituteType = InstituteType.LABORATORY
    parent_id: str = ""
    child_ids: list[str] = field(default_factory=list)
    members: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    work_history: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: float = 0.0
    active: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("inst", 8)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class Project:
    id: str = ""
    name: str = ""
    description: str = ""
    lead_institute_id: str = ""
    participating_institutes: list[str] = field(default_factory=list)
    work_products: list[str] = field(default_factory=list)
    status: str = "proposed"  # proposed, active, completed, cancelled
    priority: int = 5
    created_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("proj", 8)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class Deliverable:
    id: str = ""
    title: str = ""
    product_type: WorkProduct = WorkProduct.REPORT
    content: Any = None
    institute_id: str = ""
    project_id: str = ""
    status: str = "draft"  # draft, review, approved, published
    quality_score: float = 0.0
    created_at: float = 0.0
    published_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("del", 10)
        if not self.created_at:
            self.created_at = time.time()


class SoftwareCivilization:
    """Software civilization with autonomous institutes."""

    def __init__(self):
        self._institutes: dict[str, Institute] = {}
        self._projects: dict[str, Project] = {}
        self._deliverables: dict[str, Deliverable] = {}

    # ── Institute Management ──

    def create_institute(self, name: str,
                          institution_type: InstituteType,
                          parent_id: str = "",
                          capabilities: list[str] | None = None,
                          focus_areas: list[str] | None = None) -> Institute:
        inst = Institute(
            name=name, institution_type=institution_type,
            parent_id=parent_id, capabilities=capabilities or [],
            focus_areas=focus_areas or [],
        )
        self._institutes[inst.id] = inst
        if parent_id and parent_id in self._institutes:
            self._institutes[parent_id].child_ids.append(inst.id)
        return inst

    def get_institute(self, institute_id: str) -> Institute | None:
        return self._institutes.get(institute_id)

    def find_institutes(self, institution_type: InstituteType | None = None,
                         capability: str = "",
                         focus_area: str = "") -> list[Institute]:
        results = list(self._institutes.values())
        if institution_type:
            results = [i for i in results if i.institution_type == institution_type]
        if capability:
            results = [i for i in results if capability in i.capabilities]
        if focus_area:
            results = [i for i in results if focus_area in i.focus_areas]
        return results

    def add_member(self, institute_id: str, member_id: str) -> bool:
        inst = self._institutes.get(institute_id)
        if not inst:
            return False
        if member_id not in inst.members:
            inst.members.append(member_id)
        return True

    # ── Project Management ──

    def create_project(self, name: str, description: str,
                        lead_institute_id: str,
                        participating_institutes: list[str] | None = None,
                        priority: int = 5) -> Project:
        proj = Project(
            name=name, description=description,
            lead_institute_id=lead_institute_id,
            participating_institutes=participating_institutes or [],
            priority=priority,
        )
        self._projects[proj.id] = proj
        return proj

    def get_project(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)

    def active_projects(self) -> list[Project]:
        return [p for p in self._projects.values() if p.status == "active"]

    def complete_project(self, project_id: str) -> bool:
        proj = self._projects.get(project_id)
        if not proj:
            return False
        proj.status = "completed"
        proj.completed_at = time.time()
        return True

    # ── Deliverable Management ──

    def create_deliverable(self, title: str, product_type: WorkProduct,
                            institute_id: str, project_id: str = "",
                            content: Any = None) -> Deliverable:
        d = Deliverable(
            title=title, product_type=product_type,
            institute_id=institute_id, project_id=project_id,
            content=content,
        )
        self._deliverables[d.id] = d
        inst = self._institutes.get(institute_id)
        if inst:
            inst.work_history.append(d.id)
            inst.metrics["deliverables"] = inst.metrics.get("deliverables", 0) + 1
        proj = self._projects.get(project_id)
        if proj:
            proj.work_products.append(d.id)
        return d

    def publish_deliverable(self, deliverable_id: str) -> bool:
        d = self._deliverables.get(deliverable_id)
        if not d:
            return False
        d.status = "published"
        d.published_at = time.time()
        d.quality_score = 0.8  # Baseline quality
        return True

    # ── Autonomous Work Cycle ──

    def work_cycle(self, capacity: int = 10) -> list[Deliverable]:
        """Simulate one work cycle: each active institute produces deliverables."""
        produced = []
        active_institutes = [i for i in self._institutes.values() if i.active]
        for inst in active_institutes[:capacity]:
            if not inst.focus_areas:
                continue
            focus = inst.focus_areas[0]
            d = self.create_deliverable(
                title=f"{inst.name}: Report on {focus}",
                product_type=WorkProduct.REPORT,
                institute_id=inst.id,
                content={"focus": focus, "findings": f"Analysis of {focus} complete"},
            )
            produced.append(d)
        return produced

    def institute_hierarchy(self) -> dict[str, Any]:
        def build_tree(inst_id: str) -> dict[str, Any]:
            inst = self._institutes.get(inst_id)
            if not inst:
                return {}
            return {
                "id": inst.id,
                "name": inst.name,
                "type": inst.institution_type.value,
                "children": [build_tree(cid) for cid in inst.child_ids],
            }
        roots = [i for i in self._institutes.values() if not i.parent_id]
        return {"roots": [build_tree(r.id) for r in roots]}

    def summary(self) -> dict[str, Any]:
        return {
            "institutes": {
                "total": len(self._institutes),
                "by_type": {t.value: len(self.find_institutes(institution_type=t))
                           for t in InstituteType},
            },
            "projects": {
                "total": len(self._projects),
                "active": len(self.active_projects()),
            },
            "deliverables": {
                "total": len(self._deliverables),
                "published": len([d for d in self._deliverables.values() if d.status == "published"]),
            },
        }
