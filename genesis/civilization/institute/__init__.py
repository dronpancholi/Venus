"""
Research Institute (Program C) — departments, PIs, researchers, projects, agendas.

Organizes the 12+ research agents into a functioning academic institute.
Each department has a research agenda, active projects, publication pipeline.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id


class ResearcherRole(Enum):
    PRINCIPAL_INVESTIGATOR = "principal_investigator"
    SENIOR_RESEARCHER = "senior_researcher"
    RESEARCHER = "researcher"
    GRADUATE_STUDENT = "graduate_student"
    POSTDOC = "postdoc"
    VISITING_SCHOLAR = "visiting_scholar"


class ProjectStatus(Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FUNDED = "funded"


@dataclass
class Researcher:
    """A researcher in the institute."""
    id: str = ""
    name: str = ""
    role: ResearcherRole = ResearcherRole.RESEARCHER
    department: str = ""
    expertise: list[str] = field(default_factory=list)
    agent_id: str = ""
    publications: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    students: list[str] = field(default_factory=list)
    mentor_id: str = ""
    h_index: int = 0
    total_publications: int = 0
    total_citations: int = 0
    joined_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "department": self.department,
            "expertise": self.expertise[:5],
            "agent_id": self.agent_id,
            "publication_count": len(self.publications),
            "project_count": len(self.projects),
            "student_count": len(self.students),
            "mentor_id": self.mentor_id,
            "h_index": self.h_index,
            "total_publications": self.total_publications,
            "total_citations": self.total_citations,
            "joined_at": self.joined_at,
        }


@dataclass
class ResearchProject:
    """A research project within a department."""
    id: str = ""
    title: str = ""
    description: str = ""
    department: str = ""
    pi_id: str = ""
    researcher_ids: list[str] = field(default_factory=list)
    status: ProjectStatus = ProjectStatus.PROPOSED
    priority: float = 0.5
    hypotheses: list[str] = field(default_factory=list)
    experiments: list[str] = field(default_factory=list)
    publications: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    funding: float = 0.0
    start_date: float = 0.0
    end_date: float = 0.0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "department": self.department,
            "pi_id": self.pi_id,
            "researcher_count": len(self.researcher_ids),
            "status": self.status.value,
            "priority": self.priority,
            "experiment_count": len(self.experiments),
            "publication_count": len(self.publications),
            "funding": self.funding,
        }


@dataclass
class Department:
    """A research department within the institute."""
    id: str = ""
    name: str = ""
    domain: str = ""
    description: str = ""
    head_id: str = ""
    researcher_ids: list[str] = field(default_factory=list)
    project_ids: list[str] = field(default_factory=list)
    research_agenda: list[str] = field(default_factory=list)
    publication_ids: list[str] = field(default_factory=list)
    created_at: float = 0.0
    budget: float = 0.0
    metrics: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "head_id": self.head_id,
            "researcher_count": len(self.researcher_ids),
            "active_projects": len(self.project_ids),
            "publication_count": len(self.publication_ids),
            "budget": self.budget,
        }


class ResearchInstitute:
    """
    Complete research institute (Program C).

    Organizes agents into departments with PIs, students, projects.
    Integrates with KnowledgeBase, PeerReviewSystem, Agents, Runtime.
    """

    DEPARTMENTS = [
        ("software_architecture", "Software Architecture"),
        ("programming_languages", "Programming Languages"),
        ("distributed_systems", "Distributed Systems"),
        ("security", "Security"),
        ("databases", "Databases"),
        ("ai_systems", "AI Systems"),
        ("devops", "DevOps"),
        ("formal_methods", "Formal Methods"),
        ("networking", "Networking"),
        ("operating_systems", "Operating Systems"),
        ("human_factors", "Human Factors"),
        ("performance_engineering", "Performance Engineering"),
    ]

    def __init__(self, storage_path: str | Path = "",
                 knowledge_base=None, review_system=None):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "institute"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.departments: dict[str, Department] = {}
        self.researchers: dict[str, Researcher] = {}
        self.projects: dict[str, ResearchProject] = {}
        self.knowledge = knowledge_base
        self.review_system = review_system

        self._agent_map: dict[str, str] = {}
        self._load()

    def initialize_default_departments(self):
        for domain, name in self.DEPARTMENTS:
            if not any(d.domain == domain for d in self.departments.values()):
                self.create_department(domain, name)

    def create_department(self, domain: str, name: str) -> Department:
        dept = Department(
            id=generate_id("dept", 8),
            name=name,
            domain=domain,
            created_at=time.time(),
            research_agenda=self._default_agenda(domain),
        )
        self.departments[dept.id] = dept
        self._save()
        return dept

    def _default_agenda(self, domain: str) -> list[str]:
        agendas = {
            "software_architecture": [
                "Discover architectural patterns in open-source repositories",
                "Quantify the relationship between coupling and maintainability",
                "Develop automated architecture recovery techniques",
            ],
            "programming_languages": [
                "Analyze type system adoption across ecosystems",
                "Study the evolution of language features over time",
                "Build cross-language migration strategies",
            ],
            "distributed_systems": [
                "Identify consensus protocol usage patterns",
                "Study failure modes in production distributed systems",
                "Develop self-healing distributed architectures",
            ],
            "security": [
                "Automated vulnerability discovery in open-source code",
                "Security pattern adoption analysis",
                "Supply chain security risk modeling",
            ],
            "databases": [
                "Schema evolution patterns in long-lived projects",
                "Query optimization pattern discovery",
                "Database migration strategy analysis",
            ],
            "ai_systems": [
                "ML pipeline architecture patterns",
                "Training infrastructure scalability analysis",
                "Model deployment and serving patterns",
            ],
            "devops": [
                "CI/CD pipeline evolution patterns",
                "Infrastructure as code best practices",
                "Deployment strategy effectiveness analysis",
            ],
            "formal_methods": [
                "Invariant discovery in real-world codebases",
                "Architecture constraint verification patterns",
                "Automated theorem proving for software correctness",
            ],
            "networking": [
                "Protocol implementation correctness analysis",
                "Network performance pattern discovery",
                "API evolution and backward compatibility",
            ],
            "operating_systems": [
                "System call interface evolution",
                "OS-level security mechanism analysis",
                "Container and virtualization pattern study",
            ],
            "human_factors": [
                "Developer productivity measurement",
                "Code review effectiveness analysis",
                "Documentation quality impact on maintainability",
            ],
            "performance_engineering": [
                "Performance regression pattern detection",
                "Scalability bottleneck identification",
                "Caching and optimization strategy analysis",
            ],
        }
        return agendas.get(domain, [f"Investigate {domain} patterns"])

    def add_researcher(self, name: str, role: ResearcherRole,
                       department_id: str, expertise: list[str] | None = None,
                       agent_id: str = "") -> Researcher:
        researcher = Researcher(
            id=generate_id("res", 10),
            name=name, role=role,
            department=department_id,
            expertise=expertise or [],
            agent_id=agent_id,
            joined_at=time.time(),
        )
        self.researchers[researcher.id] = researcher

        dept = self.departments.get(department_id)
        if dept and researcher.id not in dept.researcher_ids:
            dept.researcher_ids.append(researcher.id)

        if agent_id:
            self._agent_map[agent_id] = researcher.id

        self._save()
        return researcher

    def get_researcher(self, researcher_id: str) -> Researcher | None:
        return self.researchers.get(researcher_id)

    def find_by_agent(self, agent_id: str) -> Researcher | None:
        rid = self._agent_map.get(agent_id)
        return self.researchers.get(rid) if rid else None

    def create_project(self, title: str, description: str,
                        department_id: str, pi_id: str,
                        hypotheses: list[str] | None = None,
                        priority: float = 0.5) -> ResearchProject:
        project = ResearchProject(
            id=generate_id("proj", 10),
            title=title, description=description,
            department=department_id, pi_id=pi_id,
            hypotheses=hypotheses or [],
            priority=priority,
            status=ProjectStatus.PROPOSED,
            start_date=time.time(),
        )
        self.projects[project.id] = project

        dept = self.departments.get(department_id)
        if dept and project.id not in dept.project_ids:
            dept.project_ids.append(project.id)

        pi = self.researchers.get(pi_id)
        if pi and project.id not in pi.projects:
            pi.projects.append(project.id)

        self._save()
        return project

    def get_project(self, project_id: str) -> ResearchProject | None:
        return self.projects.get(project_id)

    def assign_to_project(self, project_id: str, researcher_id: str):
        project = self.projects.get(project_id)
        researcher = self.researchers.get(researcher_id)
        if project and researcher:
            if researcher_id not in project.researcher_ids:
                project.researcher_ids.append(researcher_id)
            if project.id not in researcher.projects:
                researcher.projects.append(project.id)
            self._save()

    def set_mentor(self, student_id: str, mentor_id: str):
        student = self.researchers.get(student_id)
        mentor = self.researchers.get(mentor_id)
        if student and mentor:
            student.mentor_id = mentor_id
            if student.id not in mentor.students:
                mentor.students.append(student.id)
            self._save()

    def record_publication(self, researcher_id: str, artifact_id: str):
        researcher = self.researchers.get(researcher_id)
        if researcher:
            if artifact_id not in researcher.publications:
                researcher.publications.append(artifact_id)
                researcher.total_publications += 1
            self._save()

    def update_h_index(self, researcher_id: str):
        researcher = self.researchers.get(researcher_id)
        if not researcher or not self.knowledge:
            return
        citations = []
        for pid in researcher.publications:
            artifact = self.knowledge.get(pid)
            if artifact:
                citations.append(len(artifact.citations))
        citations.sort(reverse=True)
        h = 0
        for i, c in enumerate(citations, 1):
            if c >= i:
                h = i
            else:
                break
        researcher.h_index = h
        researcher.total_citations = sum(citations)
        self._save()

    def department_summary(self, dept_id: str) -> dict[str, Any]:
        dept = self.departments.get(dept_id)
        if not dept:
            return {}
        researchers = [self.researchers[rid] for rid in dept.researcher_ids
                       if rid in self.researchers]
        projects = [self.projects[pid] for pid in dept.project_ids
                    if pid in self.projects]
        return {
            "name": dept.name,
            "domain": dept.domain,
            "head_id": dept.head_id,
            "researchers": len(researchers),
            "projects": len(projects),
            "active_projects": sum(1 for p in projects if p.status == ProjectStatus.ACTIVE),
            "publications": len(dept.publication_ids),
            "budget": dept.budget,
            "agenda": dept.research_agenda[:3],
            "avg_h_index": (
                statistics.mean([r.h_index for r in researchers])
                if researchers else 0.0
            ) if researchers else 0.0,
        }

    def institute_summary(self) -> dict[str, Any]:
        role_counts: dict[str, int] = {}
        for role in ResearcherRole:
            role_counts[role.value] = sum(
                1 for r in self.researchers.values() if r.role == role
            )
        status_counts: dict[str, int] = {}
        for status in ProjectStatus:
            status_counts[status.value] = sum(
                1 for p in self.projects.values() if p.status == status
            )
        return {
            "departments": len(self.departments),
            "researchers": len(self.researchers),
            "projects": len(self.projects),
            "by_role": role_counts,
            "by_status": status_counts,
            "total_publications": sum(
                len(r.publications) for r in self.researchers.values()
            ),
            "total_students": sum(
                len(r.students) for r in self.researchers.values()
            ),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "institute.json"

    def _save(self):
        data = {
            "departments": {did: d.to_dict() for did, d in self.departments.items()},
            "researchers": {rid: r.to_dict() for rid, r in self.researchers.items()},
            "projects": {pid: p.to_dict() for pid, p in self.projects.items()},
        }
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text())
            for did, dd in data.get("departments", {}).items():
                self.departments[did] = Department(
                    id=did, name=dd.get("name", ""),
                    domain=dd.get("domain", ""),
                    description=dd.get("description", ""),
                    head_id=dd.get("head_id", ""),
                    researcher_ids=dd.get("researcher_ids", []),
                    project_ids=dd.get("project_ids", []),
                    research_agenda=dd.get("research_agenda", []),
                    publication_ids=dd.get("publication_ids", []),
                    created_at=dd.get("created_at", 0.0),
                    budget=dd.get("budget", 0.0),
                )
            for rid, rd in data.get("researchers", {}).items():
                self.researchers[rid] = Researcher(
                    id=rid, name=rd.get("name", ""),
                    role=ResearcherRole(rd.get("role", "researcher")),
                    department=rd.get("department", ""),
                    expertise=rd.get("expertise", []),
                    agent_id=rd.get("agent_id", ""),
                    publications=rd.get("publications", []),
                    projects=rd.get("projects", []),
                    students=rd.get("students", []),
                    mentor_id=rd.get("mentor_id", ""),
                    h_index=rd.get("h_index", 0),
                    total_publications=rd.get("total_publications", 0),
                    total_citations=rd.get("total_citations", 0),
                    joined_at=rd.get("joined_at", 0.0),
                )
                if rd.get("agent_id"):
                    self._agent_map[rd["agent_id"]] = rid
            for pid, pd in data.get("projects", {}).items():
                self.projects[pid] = ResearchProject(
                    id=pid, title=pd.get("title", ""),
                    description=pd.get("description", ""),
                    department=pd.get("department", ""),
                    pi_id=pd.get("pi_id", ""),
                    researcher_ids=pd.get("researcher_ids", []),
                    status=ProjectStatus(pd.get("status", "proposed")),
                    priority=pd.get("priority", 0.5),
                    hypotheses=pd.get("hypotheses", []),
                    experiments=pd.get("experiments", []),
                    publications=pd.get("publications", []),
                    findings=pd.get("findings", []),
                    funding=pd.get("funding", 0.0),
                    start_date=pd.get("start_date", 0.0),
                    end_date=pd.get("end_date", 0.0),
                    tags=pd.get("tags", []),
                )
        except Exception:
            pass


import statistics  # noqa: E402 (needed for department_summary)
