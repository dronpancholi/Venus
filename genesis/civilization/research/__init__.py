"""
Research Publication System — paper model, peer review, debate, citation graph.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


# ── Research Publication ──


@dataclass
class ResearchPaper:
    """A research paper published by an agent or the system."""
    id: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    body: str = ""
    domain: str = ""
    findings: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    status: str = "draft"  # draft, submitted, under_review, accepted, rejected, published
    reviews: list[PeerReview] = field(default_factory=list)
    timestamp: float = 0.0
    version: int = 1
    tags: list[str] = field(default_factory=list)

    @property
    def average_review_score(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(r.overall_score for r in self.reviews) / len(self.reviews)

    @property
    def accepted(self) -> bool:
        return self.status == "accepted" or self.status == "published"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract[:200],
            "domain": self.domain,
            "finding_count": len(self.findings),
            "citation_count": len(self.citations),
            "confidence": self.confidence,
            "status": self.status,
            "reviews": [r.to_dict() for r in self.reviews],
            "avg_review_score": self.average_review_score,
            "accepted": self.accepted,
            "version": self.version,
        }


# ── Peer Review ──


@dataclass
class PeerReview:
    """A peer review of a research paper."""
    id: str = ""
    paper_id: str = ""
    reviewer_id: str = ""
    reviewer_name: str = ""
    overall_score: float = 0.0
    methodology_score: float = 0.0
    evidence_score: float = 0.0
    clarity_score: float = 0.0
    comments: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    recommendation: str = "reject"  # reject, major_revision, minor_revision, accept
    timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


# ── Debate ──


@dataclass
class DebateStatement:
    agent_id: str = ""
    agent_name: str = ""
    statement: str = ""
    position: str = ""  # for, against, neutral
    evidence: str = ""
    timestamp: float = 0.0


@dataclass
class DebateTranscript:
    """A multi-agent debate transcript."""
    id: str = ""
    topic: str = ""
    participants: list[str] = field(default_factory=list)
    statements: list[DebateStatement] = field(default_factory=list)
    conclusion: str = ""
    consensus: float = 0.0  # 0 = no consensus, 1 = perfect consensus
    timestamp: float = 0.0
    duration: float = 0.0

    def add_statement(self, agent_id: str, agent_name: str, statement: str,
                       position: str = "", evidence: str = ""):
        self.statements.append(DebateStatement(
            agent_id=agent_id, agent_name=agent_name,
            statement=statement, position=position,
            evidence=evidence, timestamp=time.time(),
        ))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "participants": self.participants,
            "statements": [s.__dict__ for s in self.statements],
            "conclusion": self.conclusion,
            "consensus": self.consensus,
        }


# ── Citation Graph ──


@dataclass
class CitationNode:
    paper_id: str = ""
    title: str = ""
    citations: list[str] = field(default_factory=list)
    cited_by: list[str] = field(default_factory=list)


class CitationGraph:
    """Track citations between research papers."""

    def __init__(self):
        self.papers: dict[str, CitationNode] = {}

    def add_paper(self, paper_id: str, title: str = ""):
        if paper_id not in self.papers:
            self.papers[paper_id] = CitationNode(paper_id=paper_id, title=title)

    def add_citation(self, source: str, target: str):
        self.add_paper(source)
        self.add_paper(target)
        if target not in self.papers[source].citations:
            self.papers[source].citations.append(target)
        if source not in self.papers[target].cited_by:
            self.papers[target].cited_by.append(source)

    def citation_count(self, paper_id: str) -> int:
        node = self.papers.get(paper_id)
        return len(node.cited_by) if node else 0

    def most_cited(self, n: int = 10) -> list[tuple[str, str, int]]:
        counts = [(pid, n.title, len(n.cited_by))
                  for pid, n in self.papers.items()]
        return sorted(counts, key=lambda x: -x[2])[:n]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_papers": len(self.papers),
            "most_cited": self.most_cited(5),
        }


# ── Research Library ──


class ResearchLibrary:
    """Central repository for all research publications."""

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "research_library"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.papers: dict[str, ResearchPaper] = {}
        self.debates: dict[str, DebateTranscript] = {}
        self.citations = CitationGraph()
        self._load()

    def submit_paper(self, paper: ResearchPaper) -> str:
        if not paper.id:
            paper.id = generate_id("paper", 12)
        paper.timestamp = time.time()
        paper.status = "submitted"
        self.papers[paper.id] = paper
        self.citations.add_paper(paper.id, paper.title)
        self._save()
        return paper.id

    def review_paper(self, paper_id: str, review: PeerReview) -> ResearchPaper | None:
        paper = self.papers.get(paper_id)
        if not paper:
            return None
        paper.reviews.append(review)
        # Auto-decide based on review scores
        avg = paper.average_review_score
        if avg >= 0.8 and len(paper.reviews) >= 2:
            paper.status = "accepted"
        elif avg < 0.4 and len(paper.reviews) >= 2:
            paper.status = "rejected"
        else:
            paper.status = "under_review"
        self._save()
        return paper

    def publish(self, paper_id: str) -> ResearchPaper | None:
        paper = self.papers.get(paper_id)
        if paper and paper.accepted:
            paper.status = "published"
            paper.version += 1
            self._save()
        return paper

    def record_debate(self, transcript: DebateTranscript) -> str:
        if not transcript.id:
            transcript.id = generate_id("debate", 10)
        self.debates[transcript.id] = transcript
        self._save()
        return transcript.id

    def search(self, query: str, domain: str = "") -> list[ResearchPaper]:
        qlower = query.lower()
        results = []
        for p in self.papers.values():
            if domain and p.domain != domain:
                continue
            if (qlower in p.title.lower() or qlower in p.abstract.lower() or
                any(qlower in t.lower() for t in p.tags)):
                results.append(p)
        return sorted(results, key=lambda p: -p.confidence)

    def summary(self) -> dict[str, Any]:
        accepted = sum(1 for p in self.papers.values() if p.accepted)
        return {
            "total_papers": len(self.papers),
            "accepted": accepted,
            "under_review": sum(1 for p in self.papers.values() if p.status == "under_review"),
            "published": sum(1 for p in self.papers.values() if p.status == "published"),
            "debates": len(self.debates),
            "citations": self.citations.to_dict(),
        }

    def _save(self):
        data = {
            "papers": {pid: p.to_dict() for pid, p in self.papers.items()},
            "debates": {did: d.to_dict() for did, d in self.debates.items()},
        }
        (self.storage_path / "library.json").write_text(json.dumps(data, indent=2))

    def _load(self):
        path = self.storage_path / "library.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for pid, pd in data.get("papers", {}).items():
                    paper = ResearchPaper(id=pid, title=pd.get("title", ""))
                    paper.authors = pd.get("authors", [])
                    paper.abstract = pd.get("abstract", "")
                    paper.domain = pd.get("domain", "")
                    paper.status = pd.get("status", "draft")
                    paper.confidence = pd.get("confidence", 0.0)
                    for rd in pd.get("reviews", []):
                        paper.reviews.append(PeerReview(**rd))
                    self.papers[pid] = paper
                    self.citations.add_paper(pid, paper.title)
            except Exception:
                pass
