"""
GENESIS-VIII Program 5: Scientific Discovery Engine.

Complete scientific method automation:
Observe → Hypotheses → Literature review → Design experiments →
Execute experiments → Collect evidence → Statistical validation →
Reject/accept hypotheses → Publish → Peer review → Update world model → Repeat.
"""

from __future__ import annotations

import warnings
warnings.warn(
    f"{__name__} is deprecated. Use genesis.repository_scientist.RepositoryScientist instead.",
    DeprecationWarning,
    stacklevel=2,
)

import math
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class HypothesisStatus(Enum):
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    EXPERIMENTING = "experimenting"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    PUBLISHED = "published"


class EvidenceStrength(Enum):
    ANECDOTAL = "anecdotal"
    PRELIMINARY = "preliminary"
    SUBSTANTIAL = "substantial"
    STRONG = "strong"
    CONCLUSIVE = "conclusive"


@dataclass
class Observation:
    id: str = ""
    description: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    source: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("obs", 12)
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class Hypothesis:
    id: str = ""
    statement: str = ""
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence: float = 0.5
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    predictions: list[str] = field(default_factory=list)
    related_literature: list[str] = field(default_factory=list)
    created_at: float = 0.0
    last_tested: float = 0.0
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("hyp", 10)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def evidence_ratio(self) -> float:
        support = len(self.supporting_evidence)
        contra = len(self.contradicting_evidence)
        total = support + contra
        if total == 0:
            return 0.5
        return support / total

    def update_confidence(self):
        ratio = self.evidence_ratio
        prior = self.confidence
        evidence_strength = abs(ratio - 0.5) * 2
        self.confidence = prior * 0.7 + evidence_strength * 0.3


@dataclass
class Experiment:
    id: str = ""
    hypothesis_id: str = ""
    design: dict[str, Any] = field(default_factory=dict)
    procedure: list[str] = field(default_factory=list)
    expected_outcome: str = ""
    actual_outcome: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    statistical_significance: float = 0.0
    confounders: list[str] = field(default_factory=list)
    status: str = "designed"
    run_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("exp", 12)


@dataclass
class Publication:
    id: str = ""
    title: str = ""
    hypothesis_id: str = ""
    experiment_ids: list[str] = field(default_factory=list)
    findings: str = ""
    conclusions: str = ""
    peer_reviews: list[dict[str, Any]] = field(default_factory=list)
    status: str = "draft"  # draft, submitted, under_review, accepted, rejected, published
    created_at: float = 0.0
    published_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("pub", 10)


class HypothesisGenerator:
    """Generates hypotheses from observations."""

    def generate(self, observation: Observation, patterns: list[str] | None = None) -> list[Hypothesis]:
        pattern_templates = patterns or [
            f"{observation.description} is caused by a hidden factor",
            f"Changes in {observation.description} follow a periodic pattern",
            f"{observation.description} correlates with system complexity",
            f"Reducing {observation.description} improves overall quality",
        ]
        return [
            Hypothesis(
                statement=t,
                tags=observation.tags + ["generated"],
                related_literature=[],
            )
            for t in pattern_templates
        ]

    def from_data(self, data: dict[str, Any], correlations: list[tuple[str, str, float]]) -> list[Hypothesis]:
        hyps = []
        for v1, v2, corr in correlations:
            if abs(corr) > 0.5:
                direction = "positively" if corr > 0 else "negatively"
                hyps.append(Hypothesis(
                    statement=f"{v1} and {v2} are {direction} correlated (r={corr:.2f})",
                    confidence=abs(corr),
                    tags=["data_driven", v1, v2],
                ))
        return hyps


class ExperimentDesigner:
    """Designs experiments to test hypotheses."""

    def design(self, hypothesis: Hypothesis,
               available_tools: list[str] | None = None) -> Experiment:
        tools = available_tools or ["analysis", "simulation", "validation"]
        return Experiment(
            hypothesis_id=hypothesis.id,
            design={"type": "controlled", "variables": self._extract_variables(hypothesis.statement)},
            procedure=[
                f"Set up test environment",
                f"Apply {tools[0] if tools else 'analysis'} to measure baseline",
                f"Apply treatment based on hypothesis",
                f"Measure outcome and compare to baseline",
                f"Statistical significance test",
            ],
            expected_outcome=f"Hypothesis '{hypothesis.statement}' is supported",
            status="designed",
        )

    @staticmethod
    def _extract_variables(statement: str) -> list[str]:
        return [w for w in statement.split() if w.startswith(("X", "Y", "Z"))] or ["independent_var", "dependent_var"]


class StatisticalValidator:
    """Performs statistical tests on experimental data."""

    @staticmethod
    def t_test(sample_a: list[float], sample_b: list[float]) -> float:
        n1, n2 = len(sample_a), len(sample_b)
        if n1 < 2 or n2 < 2:
            return 0.5
        m1, m2 = sum(sample_a) / n1, sum(sample_b) / n2
        v1 = sum((x - m1) ** 2 for x in sample_a) / (n1 - 1)
        v2 = sum((x - m2) ** 2 for x in sample_b) / (n2 - 1)
        se = math.sqrt(v1 / n1 + v2 / n2)
        if se == 0:
            return 1.0
        t = abs(m1 - m2) / se
        df = n1 + n2 - 2
        return min(1.0, t / math.sqrt(df + t * t))

    @staticmethod
    def effect_size(sample_a: list[float], sample_b: list[float]) -> float:
        n1, n2 = len(sample_a), len(sample_b)
        if n1 < 1 or n2 < 1:
            return 0.0
        m1, m2 = sum(sample_a) / n1, sum(sample_b) / n2
        v1 = sum((x - m1) ** 2 for x in sample_a) / max(n1 - 1, 1)
        v2 = sum((x - m2) ** 2 for x in sample_b) / max(n2 - 1, 1)
        pooled = math.sqrt((v1 + v2) / 2)
        return abs(m1 - m2) / max(pooled, 0.001)

    @staticmethod
    def p_value(t_statistic: float, df: int) -> float:
        return min(1.0, 2.0 * (1.0 - t_statistic / math.sqrt(df + t_statistic * t_statistic)))


class LiteratureReviewer:
    """Reviews existing literature related to hypotheses."""

    def __init__(self):
        self._literature: dict[str, dict[str, Any]] = {}

    def add_reference(self, ref_id: str, title: str, findings: str,
                       relevant_tags: list[str] | None = None):
        self._literature[ref_id] = {
            "title": title, "findings": findings,
            "tags": relevant_tags or [],
        }

    def review(self, hypothesis: Hypothesis) -> list[str]:
        relevant = []
        for ref_id, ref in self._literature.items():
            if any(t in hypothesis.tags for t in ref["tags"]):
                relevant.append(ref_id)
        return relevant


class PeerReviewer:
    """Simulates peer review of publications."""

    @staticmethod
    def review(publication: Publication) -> list[dict[str, Any]]:
        reviews = []
        criteria = ["methodology", "evidence_quality", "reproducibility",
                     "significance", "clarity"]
        for i in range(2):
            scores = {c: random.uniform(0.4, 1.0) for c in criteria}
            avg = sum(scores.values()) / len(scores)
            verdict = "accept" if avg > 0.7 else "minor_revision" if avg > 0.5 else "major_revision"
            reviews.append({
                "reviewer": f"reviewer_{i + 1}",
                "scores": scores,
                "average_score": avg,
                "verdict": verdict,
                "comments": f"Evidence quality: {scores['evidence_quality']:.2f}",
            })
        return reviews


class DiscoveryEngine:
    """Unified scientific discovery engine."""

    def __init__(self):
        self._observations: list[Observation] = []
        self._hypotheses: dict[str, Hypothesis] = {}
        self._experiments: dict[str, Experiment] = {}
        self._publications: dict[str, Publication] = {}
        self._generator = HypothesisGenerator()
        self._designer = ExperimentDesigner()
        self._statistics = StatisticalValidator()
        self._literature = LiteratureReviewer()
        self._peer_review = PeerReviewer()

    def observe(self, description: str, context: dict[str, Any] | None = None,
                source: str = "", tags: list[str] | None = None) -> Observation:
        obs = Observation(description=description, context=context or {},
                          source=source, tags=tags or [])
        self._observations.append(obs)
        return obs

    def hypothesize(self, observation_id: str) -> list[Hypothesis]:
        obs = next((o for o in self._observations if o.id == observation_id), None)
        if not obs:
            return []
        hyps = self._generator.generate(obs)
        for h in hyps:
            self._hypotheses[h.id] = h
        return hyps

    def design_experiment(self, hypothesis_id: str) -> Experiment | None:
        hyp = self._hypotheses.get(hypothesis_id)
        if not hyp:
            return None
        exp = self._designer.design(hyp)
        self._experiments[exp.id] = exp
        hyp.status = HypothesisStatus.EXPERIMENTING
        return exp

    def run_experiment(self, experiment_id: str,
                       data_generator: Callable[[Experiment], dict[str, Any]] | None = None) -> Experiment | None:
        exp = self._experiments.get(experiment_id)
        if not exp:
            return None
        exp.status = "running"
        exp.run_at = time.time()
        if data_generator:
            exp.data = data_generator(exp)
        else:
            exp.data = {"control": [random.gauss(0.5, 0.1) for _ in range(30)],
                        "treatment": [random.gauss(0.55, 0.1) for _ in range(30)]}
        exp.actual_outcome = "treatment differs from control"
        control = exp.data.get("control", [])
        treatment = exp.data.get("treatment", [])
        exp.statistical_significance = self._statistics.t_test(control, treatment)
        exp.status = "completed"
        exp.completed_at = time.time()
        hyp = self._hypotheses.get(exp.hypothesis_id)
        if hyp:
            if exp.statistical_significance > 0.05:
                hyp.supporting_evidence.append(exp.id)
                hyp.status = HypothesisStatus.SUPPORTED
            else:
                hyp.contradicting_evidence.append(exp.id)
                hyp.status = HypothesisStatus.REFUTED
            hyp.last_tested = time.time()
            hyp.update_confidence()
        return exp

    def review_literature(self, hypothesis_id: str) -> list[str]:
        hyp = self._hypotheses.get(hypothesis_id)
        if not hyp:
            return []
        return self._literature.review(hyp)

    def publish(self, hypothesis_id: str,
                experiment_ids: list[str] | None = None) -> Publication:
        hyp = self._hypotheses.get(hypothesis_id)
        pub = Publication(
            title=f"Findings: {hyp.statement[:50] if hyp else hypothesis_id}",
            hypothesis_id=hypothesis_id,
            experiment_ids=experiment_ids or [],
            findings=f"Experimental evidence {'supports' if hyp and hyp.confidence > 0.5 else 'refutes'} hypothesis",
            conclusions=f"Confidence: {hyp.confidence if hyp else 0.5:.2f}",
        )
        self._publications[pub.id] = pub
        if hyp:
            hyp.status = HypothesisStatus.PUBLISHED
        return pub

    def peer_review(self, publication_id: str) -> list[dict[str, Any]]:
        pub = self._publications.get(publication_id)
        if not pub:
            return []
        reviews = self._peer_review.review(pub)
        pub.peer_reviews = reviews
        pub.status = "under_review"
        avg = sum(r["average_score"] for r in reviews) / len(reviews)
        pub.status = "published" if avg > 0.6 else "rejected"
        return reviews

    def scientific_method_cycle(self, observation_id: str) -> dict[str, Any]:
        hyps = self.hypothesize(observation_id)
        results = []
        for hyp in hyps:
            exp = self.design_experiment(hyp.id)
            if exp:
                self.run_experiment(exp.id)
                self.review_literature(hyp.id)
                pub = self.publish(hyp.id, [exp.id])
                reviews = self.peer_review(pub.id)
                results.append({
                    "hypothesis": hyp.statement,
                    "confidence": hyp.confidence,
                    "status": hyp.status.value,
                    "publication": pub.title,
                    "peer_review_verdict": pub.status,
                })
        return {
            "observation_id": observation_id,
            "hypotheses_generated": len(hyps),
            "results": results,
            "cycle_completed": True,
        }

    def summary(self) -> dict[str, Any]:
        status_counts: dict[str, int] = {}
        for h in self._hypotheses.values():
            status_counts[h.status.value] = status_counts.get(h.status.value, 0) + 1
        return {
            "observations": len(self._observations),
            "hypotheses": len(self._hypotheses),
            "experiments": len(self._experiments),
            "publications": len(self._publications),
            "hypothesis_statuses": status_counts,
            "average_confidence": sum(h.confidence for h in self._hypotheses.values()) / max(len(self._hypotheses), 1),
        }
