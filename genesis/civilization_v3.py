"""
GENESIS-IX Phase 9: Software Civilization V3.

18 institutes: AI, Security, Runtime, OS, Compilers, Languages, Architecture,
Physics, Formal Methods, Verification, Knowledge, Simulation, Distributed
Systems, Networking, Databases, Human Factors, Economics, Governance.

Each institute conducts research, generates hypotheses, runs experiments,
publishes papers, mentors agents, proposes standards, participates in governance.
"""

from __future__ import annotations

import warnings
warnings.warn(
    f"{__name__} is deprecated. Use genesis.digital_civilization.DigitalCivilization instead.",
    DeprecationWarning,
    stacklevel=2,
)

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.utils.identity import generate_id


class InstituteType(Enum):
    AI = "ai"
    SECURITY = "security"
    RUNTIME = "runtime"
    OPERATING_SYSTEMS = "operating_systems"
    COMPILERS = "compilers"
    LANGUAGES = "languages"
    ARCHITECTURE = "architecture"
    PHYSICS = "physics"
    FORMAL_METHODS = "formal_methods"
    VERIFICATION = "verification"
    KNOWLEDGE = "knowledge"
    SIMULATION = "simulation"
    DISTRIBUTED_SYSTEMS = "distributed_systems"
    NETWORKING = "networking"
    DATABASES = "databases"
    HUMAN_FACTORS = "human_factors"
    ECONOMICS = "economics"
    GOVERNANCE = "governance"


@dataclass
class ResearchProject:
    id: str = ""
    name: str = ""
    description: str = ""
    institute_id: str = ""
    lead_researcher: str = ""
    status: str = "proposed"
    publications: list[str] = field(default_factory=list)
    experiments: list[str] = field(default_factory=list)
    hypotheses: list[str] = field(default_factory=list)
    standards_proposed: list[str] = field(default_factory=list)
    created_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("rp", 10)
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class Institute:
    id: str = ""
    name: str = ""
    institute_type: InstituteType = InstituteType.AI
    parent_id: str = ""
    child_ids: list[str] = field(default_factory=list)
    members: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    publications: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("inst", 8)
        if not self.created_at:
            self.created_at = time.time()


class SoftwareCivilizationV3:
    """18-institute civilization with autonomous research, publication, and governance."""

    def __init__(self):
        self._institutes: dict[str, Institute] = {}
        self._projects: dict[str, ResearchProject] = {}
        self._governance_log: list[dict[str, Any]] = []

        # Create all 18 institutes
        for it in InstituteType:
            self._create_default_institute(it)

    def _create_default_institute(self, it: InstituteType):
        names = {
            InstituteType.AI: ("AI Institute", ["machine_learning", "reasoning", "planning"]),
            InstituteType.SECURITY: ("Security Institute", ["vulnerability", "auth", "crypto"]),
            InstituteType.RUNTIME: ("Runtime Institute", ["execution", "scheduling", "concurrency"]),
            InstituteType.OPERATING_SYSTEMS: ("Operating Systems Institute", ["kernel", "processes", "memory"]),
            InstituteType.COMPILERS: ("Compiler Institute", ["codegen", "optimization", "parsing"]),
            InstituteType.LANGUAGES: ("Languages Institute", ["type_systems", "syntax", "semantics"]),
            InstituteType.ARCHITECTURE: ("Architecture Council", ["patterns", "design", "coupling"]),
            InstituteType.PHYSICS: ("Physics Institute", ["thermodynamics", "entropy", "gravity"]),
            InstituteType.FORMAL_METHODS: ("Formal Methods Institute", ["verification", "proofs", "logic"]),
            InstituteType.VERIFICATION: ("Verification Institute", ["testing", "validation", "model_checking"]),
            InstituteType.KNOWLEDGE: ("Knowledge Institute", ["graphs", "ontologies", "reasoning"]),
            InstituteType.SIMULATION: ("Simulation Institute", ["prediction", "monte_carlo", "modeling"]),
            InstituteType.DISTRIBUTED_SYSTEMS: ("Distributed Systems Institute", ["consensus", "replication", "sharding"]),
            InstituteType.NETWORKING: ("Networking Institute", ["protocols", "latency", "routing"]),
            InstituteType.DATABASES: ("Databases Institute", ["storage", "query", "indexing"]),
            InstituteType.HUMAN_FACTORS: ("Human Factors Institute", ["ux", "productivity", "cognition"]),
            InstituteType.ECONOMICS: ("Economics Institute", ["cost", "value", "incentives"]),
            InstituteType.GOVERNANCE: ("Governance Council", ["standards", "policy", "oversight"]),
        }
        name, caps = names.get(it, (it.value.replace("_", " ").title(), []))
        inst = Institute(
            name=name, institute_type=it, capabilities=caps,
            focus_areas=[it.value],
        )
        self._institutes[inst.id] = inst

    def get_institute(self, institute_id: str) -> Institute | None:
        return self._institutes.get(institute_id)

    def find_institutes(self, institute_type: InstituteType | None = None,
                         capability: str = "") -> list[Institute]:
        results = list(self._institutes.values())
        if institute_type:
            results = [i for i in results if i.institute_type == institute_type]
        if capability:
            results = [i for i in results if capability in i.capabilities]
        return results

    def add_member(self, institute_id: str, member_id: str) -> bool:
        inst = self._institutes.get(institute_id)
        if not inst or member_id in inst.members:
            return False
        inst.members.append(member_id)
        return True

    def start_research(self, institute_id: str, name: str,
                        description: str) -> ResearchProject:
        proj = ResearchProject(
            name=name, description=description,
            institute_id=institute_id, status="active",
        )
        self._projects[proj.id] = proj
        inst = self._institutes.get(institute_id)
        if inst:
            inst.projects.append(proj.id)
            inst.metrics["projects"] = inst.metrics.get("projects", 0) + 1
        return proj

    def publish_paper(self, project_id: str, title: str,
                       findings: str) -> str:
        pub_id = generate_id("pub", 10)
        proj = self._projects.get(project_id)
        if proj:
            proj.publications.append(pub_id)
            proj.status = "published"
            inst = self._institutes.get(proj.institute_id)
            if inst:
                inst.publications.append(pub_id)
                inst.metrics["publications"] = inst.metrics.get("publications", 0) + 1
        return pub_id

    def propose_standard(self, institute_id: str, name: str,
                          description: str) -> str:
        std_id = generate_id("std", 8)
        inst = self._institutes.get(institute_id)
        if inst:
            inst.standards.append(std_id)
            inst.metrics["standards"] = inst.metrics.get("standards", 0) + 1
        self._governance_log.append({
            "type": "standard_proposed",
            "institute_id": institute_id,
            "name": name, "timestamp": time.time(),
        })
        return std_id

    def governance_action(self, action: str, proposer_id: str,
                            description: str) -> dict[str, Any]:
        record = {
            "action": action, "proposer_id": proposer_id,
            "description": description, "timestamp": time.time(),
            "approved": True,
        }
        self._governance_log.append(record)
        return record

    def research_cycle(self) -> list[ResearchProject]:
        new_projects = []
        for inst in self._institutes.values():
            if inst.focus_areas:
                area = inst.focus_areas[0]
                proj = self.start_research(
                    inst.id,
                    f"{inst.name}: Investigating {area}",
                    f"Research project on {area} led by {inst.name}",
                )
                pub_id = self.publish_paper(
                    proj.id,
                    f"Findings in {area}",
                    f"New insights about {area} discovered",
                )
                new_projects.append(proj)
        return new_projects

    def hierarchy(self) -> dict[str, Any]:
        roots = [i for i in self._institutes.values() if not i.parent_id]
        return {
            "roots": [
                {"id": r.id, "name": r.name, "type": r.institute_type.value}
                for r in roots
            ]
        }

    def summary(self) -> dict[str, Any]:
        type_counts = defaultdict(int)
        total_pubs = 0
        total_standards = 0
        for inst in self._institutes.values():
            type_counts[inst.institute_type.value] += 1
            total_pubs += len(inst.publications)
            total_standards += len(inst.standards)
        return {
            "institutes": len(self._institutes),
            "by_type": dict(type_counts),
            "projects": len(self._projects),
            "publications": total_pubs,
            "standards": total_standards,
            "governance_actions": len(self._governance_log),
            "total_members": sum(len(i.members) for i in self._institutes.values()),
        }
