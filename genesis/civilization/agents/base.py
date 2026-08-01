"""
Research Agent — base class for all persistent research agents.

Every agent maintains:
  - long-term memory (findings, publications, confidence history)
  - research agenda (active questions, hypotheses)
  - publication record (peer-reviewed findings)
  - debate transcripts
  - citation graph
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class ResearchFinding:
    """A finding produced by a research agent."""
    id: str = ""
    agent_id: str = ""
    title: str = ""
    description: str = ""
    evidence: str = ""
    confidence: float = 0.0
    impact: float = 0.0  # -1 to 1
    timestamp: float = 0.0
    tags: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    peer_reviewed: bool = False
    review_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ResearchFinding:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ResearchQuestion:
    """An open research question the agent is investigating."""
    question: str = ""
    hypothesis: str = ""
    priority: float = 0.0
    status: str = "open"  # open, investigating, answered, abandoned
    created_at: float = 0.0
    resolved_at: float = 0.0
    findings: list[str] = field(default_factory=list)


@dataclass
class AgentMemory:
    """Persistent memory for a research agent."""
    agent_id: str = ""
    findings: dict[str, ResearchFinding] = field(default_factory=dict)
    questions: list[ResearchQuestion] = field(default_factory=list)
    publications: list[str] = field(default_factory=list)
    confidence_history: list[tuple[float, float]] = field(default_factory=list)
    citations: dict[str, list[str]] = field(default_factory=dict)
    debate_history: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    @property
    def active_questions(self) -> list[ResearchQuestion]:
        return [q for q in self.questions if q.status == "open"]

    @property
    def average_confidence(self) -> float:
        if not self.findings:
            return 0.0
        return sum(f.confidence for f in self.findings.values()) / len(self.findings)

    def add_finding(self, finding: ResearchFinding):
        self.findings[finding.id] = finding
        self.confidence_history.append((time.time(), finding.confidence))

    def add_question(self, question: ResearchQuestion):
        self.questions.append(question)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "findings": {k: v.to_dict() for k, v in self.findings.items()},
            "questions": [q.__dict__ for q in self.questions],
            "publications": self.publications,
            "confidence_history": self.confidence_history,
            "finding_count": self.finding_count,
            "average_confidence": self.average_confidence,
        }


class ResearchAgent(ABC):
    """Base class for persistent research agents."""

    def __init__(self, agent_id: str = "", name: str = "",
                 storage_path: str | Path = ""):
        self.agent_id = agent_id or generate_id("agent", 8)
        self.name = name or self.__class__.__name__
        self.memory = AgentMemory(agent_id=self.agent_id)

        if not storage_path:
            storage_path = Path.home() / ".venus" / "agents"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._load_memory()

    @abstractmethod
    def research_domain(self) -> str:
        """Return the research domain name."""
        ...

    @abstractmethod
    def investigate(self, context: dict[str, Any]) -> list[ResearchFinding]:
        """Perform research and return new findings."""
        ...

    @abstractmethod
    def generate_questions(self, context: dict[str, Any]) -> list[ResearchQuestion]:
        """Generate new research questions based on current knowledge."""
        ...

    # — Research Lifecycle —

    def research_cycle(self, context: dict[str, Any]) -> list[ResearchFinding]:
        """Execute one research cycle: generate questions → investigate → publish."""
        # Generate new questions
        new_questions = self.generate_questions(context)
        for q in new_questions:
            self.memory.add_question(q)

        # Investigate active questions
        findings = self.investigate(context)

        # Store findings
        for f in findings:
            f.agent_id = self.agent_id
            if not f.id:
                f.id = generate_id("finding", 12)
            if not f.timestamp:
                f.timestamp = time.time()
            self.memory.add_finding(f)

        self._save_memory()
        return findings

    def get_answers_for(self, question: str) -> list[ResearchFinding]:
        """Find findings relevant to a question."""
        qlower = question.lower()
        relevant = []
        for f in self.memory.findings.values():
            if qlower in f.title.lower() or qlower in f.description.lower():
                relevant.append(f)
            for t in f.tags:
                if qlower in t.lower():
                    relevant.append(f)
        return relevant

    def confidence_in(self, topic: str) -> float:
        """Return confidence level for a topic."""
        relevant = self.get_answers_for(topic)
        if not relevant:
            return 0.0
        return sum(f.confidence for f in relevant) / len(relevant)

    def summary(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "domain": self.research_domain(),
            "findings": self.memory.finding_count,
            "active_questions": len(self.memory.active_questions),
            "total_questions": len(self.memory.questions),
            "publications": len(self.memory.publications),
            "average_confidence": self.memory.average_confidence,
            "debates": len(self.memory.debate_history),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "domain": self.research_domain(),
            "memory": self.memory.to_dict(),
        }

    # — Persistence —

    def _memory_path(self) -> Path:
        return self.storage_path / f"{self.agent_id}.json"

    def _save_memory(self):
        path = self._memory_path()
        path.write_text(json.dumps(self.to_dict(), indent=2))

    def _load_memory(self):
        path = self._memory_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if "memory" in data:
                    mem = data["memory"]
                    self.memory.agent_id = mem.get("agent_id", self.agent_id)
                    for fid, fd in mem.get("findings", {}).items():
                        self.memory.findings[fid] = ResearchFinding.from_dict(fd)
                    for qd in mem.get("questions", []):
                        self.memory.questions.append(ResearchQuestion(**qd))
                    self.memory.publications = mem.get("publications", [])
                    self.memory.confidence_history = [tuple(x) for x in mem.get("confidence_history", [])]
            except Exception:
                pass
