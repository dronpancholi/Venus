"""
Peer Review System — quality-controlled scientific review pipeline.

Manages the complete review lifecycle:
  submission → assignment → review → rebuttal → decision → publication

Integrates with KnowledgeBase, Institute, and PaperFactory.
"""

from __future__ import annotations

import json
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


class ReviewDecision(Enum):
    DESK_REJECT = "desk_reject"
    REJECT = "reject"
    MAJOR_REVISION = "major_revision"
    MINOR_REVISION = "minor_revision"
    ACCEPT = "accept"


class ReviewStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CONFLICTED = "conflicted"


@dataclass
class ReviewCriteria:
    methodology: float = 0.0
    evidence: float = 0.0
    clarity: float = 0.0
    novelty: float = 0.0
    reproducibility: float = 0.0
    relevance: float = 0.0
    overall: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "methodology": round(self.methodology, 3),
            "evidence": round(self.evidence, 3),
            "clarity": round(self.clarity, 3),
            "novelty": round(self.novelty, 3),
            "reproducibility": round(self.reproducibility, 3),
            "relevance": round(self.relevance, 3),
            "overall": round(self.overall, 3),
        }


@dataclass
class Review:
    """A completed peer review."""
    id: str = ""
    artifact_id: str = ""
    reviewer_id: str = ""
    reviewer_name: str = ""
    decision: ReviewDecision = ReviewDecision.REJECT
    criteria: ReviewCriteria = field(default_factory=ReviewCriteria)
    summary: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    status: ReviewStatus = ReviewStatus.PENDING
    confidence: float = 0.0
    assigned_at: float = 0.0
    completed_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "artifact_id": self.artifact_id,
            "reviewer_id": self.reviewer_id,
            "reviewer_name": self.reviewer_name,
            "decision": self.decision.value,
            "criteria": self.criteria.to_dict(),
            "summary": self.summary[:200],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses[:3],
            "status": self.status.value,
            "confidence": self.confidence,
            "assigned_at": self.assigned_at,
        }


@dataclass
class Rebuttal:
    """Author response to a review."""
    id: str = ""
    review_id: str = ""
    artifact_id: str = ""
    author_id: str = ""
    response: str = ""
    changes_made: list[str] = field(default_factory=list)
    timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "review_id": self.review_id,
            "author_id": self.author_id,
            "changes_made": self.changes_made,
            "timestamp": self.timestamp,
        }


@dataclass
class ReviewBoard:
    """A group of reviewers for a specific domain."""
    id: str = ""
    name: str = ""
    domain: str = ""
    members: list[str] = field(default_factory=list)
    expertise: dict[str, list[str]] = field(default_factory=dict)
    created_at: float = 0.0

    def add_member(self, reviewer_id: str, expertise: list[str] | None = None):
        if reviewer_id not in self.members:
            self.members.append(reviewer_id)
            if expertise:
                self.expertise[reviewer_id] = expertise

    def find_reviewers(self, artifact_domain: str,
                       min_expertise: int = 1) -> list[str]:
        candidates = []
        for member in self.members:
            expertise = self.expertise.get(member, [])
            if any(artifact_domain.lower() in e.lower() for e in expertise):
                candidates.append(member)
            elif not expertise:
                candidates.append(member)
        return candidates[:3]


class PeerReviewSystem:
    """
    Complete peer review management (Program C, G).

    Lifecycle:
      submit → assign_reviewers → review → rebut → decide → publish

    Quality scoring across 6 criteria with statistical aggregation.
    """

    def __init__(self, storage_path: str | Path = "", knowledge_base=None):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "review"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.reviews: dict[str, Review] = {}
        self.rebuttals: dict[str, Rebuttal] = {}
        self.boards: dict[str, ReviewBoard] = {}
        self.knowledge = knowledge_base
        self._decisions: dict[str, list[ReviewDecision]] = defaultdict(list)
        self._load()

    def create_board(self, name: str, domain: str) -> ReviewBoard:
        board = ReviewBoard(
            id=generate_id("board", 8),
            name=name, domain=domain,
            created_at=time.time(),
        )
        self.boards[board.id] = board
        self._save()
        return board

    def get_board(self, board_id: str) -> ReviewBoard | None:
        return self.boards.get(board_id)

    def assign_reviewers(self, artifact_id: str, board_id: str,
                         num_reviewers: int = 3) -> list[Review]:
        artifact = None
        if self.knowledge:
            artifact = self.knowledge.get(artifact_id)
        domain = artifact.domain if artifact else "general"

        board = self.boards.get(board_id)
        if not board:
            return []

        candidates = board.find_reviewers(domain)
        selected = candidates[:num_reviewers]
        assigned = []
        for reviewer_id in selected:
            review = Review(
                id=generate_id("review", 12),
                artifact_id=artifact_id,
                reviewer_id=reviewer_id,
                status=ReviewStatus.ASSIGNED,
                assigned_at=time.time(),
            )
            self.reviews[review.id] = review
            self._decisions[artifact_id].append(ReviewDecision.REJECT)
            assigned.append(review)
        self._save()
        return assigned

    def submit_review(self, review_id: str, criteria: ReviewCriteria,
                      decision: ReviewDecision, summary: str = "",
                      strengths: list[str] | None = None,
                      weaknesses: list[str] | None = None,
                      suggestions: list[str] | None = None,
                      confidence: float = 0.0) -> Review | None:
        review = self.reviews.get(review_id)
        if not review:
            return None
        review.criteria = criteria
        review.decision = decision
        review.summary = summary
        review.strengths = strengths or []
        review.weaknesses = weaknesses or []
        review.suggestions = suggestions or []
        review.confidence = confidence
        review.status = ReviewStatus.COMPLETED
        review.completed_at = time.time()

        self._decisions[review.artifact_id].append(decision)
        self._evaluate_artifact(review.artifact_id)
        self._save()
        return review

    def submit_rebuttal(self, review_id: str, author_id: str,
                        response: str, changes: list[str] | None = None) -> Rebuttal | None:
        review = self.reviews.get(review_id)
        if not review:
            return None
        rebuttal = Rebuttal(
            id=generate_id("rebut", 10),
            review_id=review_id,
            artifact_id=review.artifact_id,
            author_id=author_id,
            response=response,
            changes_made=changes or [],
            timestamp=time.time(),
        )
        self.rebuttals[rebuttal.id] = rebuttal
        self._save()
        return rebuttal

    def reviews_for_artifact(self, artifact_id: str) -> list[Review]:
        return [r for r in self.reviews.values() if r.artifact_id == artifact_id]

    def review_statistics(self, artifact_id: str) -> dict[str, Any]:
        reviews = self.reviews_for_artifact(artifact_id)
        if not reviews:
            return {}
        scores = {
            "methodology": [],
            "evidence": [],
            "clarity": [],
            "novelty": [],
            "reproducibility": [],
            "relevance": [],
            "overall": [],
        }
        decisions = []
        for r in reviews:
            if r.status == ReviewStatus.COMPLETED:
                for key in scores:
                    val = getattr(r.criteria, key, None)
                    if val is not None:
                        scores[key].append(val)
                decisions.append(r.decision.value)

        stats = {}
        for key, vals in scores.items():
            if vals:
                stats[f"avg_{key}"] = round(statistics.mean(vals), 3)
                stats[f"std_{key}"] = round(statistics.stdev(vals), 3) if len(vals) > 1 else 0.0
            else:
                stats[f"avg_{key}"] = 0.0
                stats[f"std_{key}"] = 0.0

        decision_counts = defaultdict(int)
        for d in decisions:
            decision_counts[d] += 1
        stats["decision_distribution"] = dict(decision_counts)
        stats["total_reviews"] = len(reviews)
        stats["completed_reviews"] = len([r for r in reviews if r.status == ReviewStatus.COMPLETED])
        return stats

    def _evaluate_artifact(self, artifact_id: str):
        reviews = [r for r in self.reviews.values()
                   if r.artifact_id == artifact_id and r.status == ReviewStatus.COMPLETED]
        if len(reviews) < 2:
            return

        avg_overall = statistics.mean(r.criteria.overall for r in reviews)
        decisions = [r.decision for r in reviews]
        accept_count = sum(1 for d in decisions if d == ReviewDecision.ACCEPT)
        revision_count = sum(1 for d in decisions if d in (
            ReviewDecision.MAJOR_REVISION, ReviewDecision.MINOR_REVISION
        ))

        if self.knowledge:
            artifact = self.knowledge.get(artifact_id)
            if artifact:
                artifact.quality_score = avg_overall
                artifact.reproducibility_score = statistics.mean(
                    r.criteria.reproducibility for r in reviews
                )
                artifact.novelty_score = statistics.mean(
                    r.criteria.novelty for r in reviews
                )
                if accept_count >= 2:
                    artifact.status = "accepted"
                elif accept_count == 1 and revision_count >= 1:
                    artifact.status = "minor_revision"
                elif all(d == ReviewDecision.REJECT for d in decisions):
                    artifact.status = "rejected"

    def reviewer_metrics(self, reviewer_id: str) -> dict[str, Any]:
        reviews = [r for r in self.reviews.values() if r.reviewer_id == reviewer_id]
        if not reviews:
            return {"total_reviews": 0}
        completed = [r for r in reviews if r.status == ReviewStatus.COMPLETED]
        return {
            "total_reviews": len(reviews),
            "completed": len(completed),
            "avg_confidence": (
                statistics.mean(r.confidence for r in completed) if completed else 0.0
            ),
            "avg_overall_score": (
                statistics.mean(r.criteria.overall for r in completed) if completed else 0.0
            ),
        }

    def summary(self) -> dict[str, Any]:
        statuses = defaultdict(int)
        decisions = defaultdict(int)
        for r in self.reviews.values():
            statuses[r.status.value] += 1
            decisions[r.decision.value] += 1
        return {
            "total_reviews": len(self.reviews),
            "total_rebuttals": len(self.rebuttals),
            "review_boards": len(self.boards),
            "status_distribution": dict(statuses),
            "decision_distribution": dict(decisions),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "review_system.json"

    def _save(self):
        data = {
            "reviews": {rid: r.to_dict() for rid, r in self.reviews.items()},
            "rebuttals": {rid: r.to_dict() for rid, r in self.rebuttals.items()},
            "boards": {bid: {
                "id": b.id, "name": b.name, "domain": b.domain,
                "members": b.members, "expertise": b.expertise,
                "created_at": b.created_at,
            } for bid, b in self.boards.items()},
        }
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text())
            for rid, rd in data.get("reviews", {}).items():
                review = Review(id=rid)
                review.artifact_id = rd.get("artifact_id", "")
                review.reviewer_id = rd.get("reviewer_id", "")
                review.reviewer_name = rd.get("reviewer_name", "")
                review.decision = ReviewDecision(rd.get("decision", "reject"))
                if "criteria" in rd:
                    review.criteria = ReviewCriteria(**rd["criteria"])
                review.summary = rd.get("summary", "")
                review.strengths = rd.get("strengths", [])
                review.weaknesses = rd.get("weaknesses", [])
                review.suggestions = rd.get("suggestions", [])
                review.status = ReviewStatus(rd.get("status", "pending"))
                review.confidence = rd.get("confidence", 0.0)
                review.assigned_at = rd.get("assigned_at", 0.0)
                review.completed_at = rd.get("completed_at", 0.0)
                self.reviews[rid] = review
            for rid, rd in data.get("rebuttals", {}).items():
                self.rebuttals[rid] = Rebuttal(**rd)
            for bid, bd in data.get("boards", {}).items():
                board = ReviewBoard(
                    id=bid, name=bd.get("name", ""),
                    domain=bd.get("domain", ""),
                    members=bd.get("members", []),
                    expertise=bd.get("expertise", {}),
                    created_at=bd.get("created_at", 0.0),
                )
                self.boards[bid] = board
        except Exception:
            pass
