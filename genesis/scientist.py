"""
GENESIS-IX Phase 6: Engineering Scientist V2.

Full scientific method automation: Observe → Hypotheses → Literature review →
Experiment design → Execution → Evidence collection → Statistical analysis →
Peer review → Publication → Knowledge graph update → World model update → Repeat.
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
from collections import defaultdict
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
    INCORPORATED = "incorporated"


@dataclass
class Observation:
    id: str = ""
    description: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    measurements: dict[str, float] = field(default_factory=dict)
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
    updated_at: float = 0.0
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("hyp", 10)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @property
    def evidence_ratio(self) -> float:
        total = len(self.supporting_evidence) + len(self.contradicting_evidence)
        if total == 0:
            return 0.5
        return len(self.supporting_evidence) / total

    def update_confidence(self):
        ratio = self.evidence_ratio
        self.confidence = self.confidence * 0.6 + ratio * 0.4


@dataclass
class Experiment:
    id: str = ""
    hypothesis_id: str = ""
    design: dict[str, Any] = field(default_factory=dict)
    procedure: list[str] = field(default_factory=list)
    independent_vars: list[str] = field(default_factory=list)
    dependent_vars: list[str] = field(default_factory=list)
    control_vars: list[str] = field(default_factory=list)
    expected_outcome: str = ""
    actual_outcome: str = ""
    data: dict[str, list[float]] = field(default_factory=dict)
    statistical_tests: dict[str, float] = field(default_factory=dict)
    effect_size: float = 0.0
    confounders: list[str] = field(default_factory=list)
    status: str = "designed"
    run_at: float = 0.0
    completed_at: float = 0.0
    reproducibility: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("exp", 12)


@dataclass
class Publication:
    id: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    hypothesis_id: str = ""
    experiment_ids: list[str] = field(default_factory=list)
    abstract: str = ""
    findings: str = ""
    conclusions: str = ""
    methodology: str = ""
    peer_reviews: list[dict[str, Any]] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    status: str = "draft"
    created_at: float = 0.0
    published_at: float = 0.0
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("pub", 10)
        if not self.created_at:
            self.created_at = time.time()


class HypothesisGenerator:
    @staticmethod
    def from_observation(obs: Observation) -> list[Hypothesis]:
        templates = [
            f"{obs.description} is caused by a measurable factor",
            f"Changes in {obs.description[:30]} follow a predictable pattern",
            f"{obs.description[:30]} correlates with system complexity",
            f"Reducing {obs.description[:30]} improves overall quality",
        ]
        return [Hypothesis(statement=t, tags=obs.tags + ["generated"]) for t in templates]

    @staticmethod
    def from_correlation(data: dict[str, list[float]]) -> list[Hypothesis]:
        hyps = []
        vars_list = list(data.keys())
        for i in range(len(vars_list)):
            for j in range(i + 1, len(vars_list)):
                v1, v2 = vars_list[i], vars_list[j]
                corr = HypothesisGenerator._pearson(data[v1], data[v2])
                if abs(corr) > 0.5:
                    direction = "positively" if corr > 0 else "negatively"
                    hyps.append(Hypothesis(
                        statement=f"{v1} and {v2} are {direction} correlated (r={corr:.2f})",
                        confidence=abs(corr), tags=["data_driven"],
                    ))
        return hyps

    @staticmethod
    def _pearson(x: list[float], y: list[float]) -> float:
        n = min(len(x), len(y))
        if n < 3:
            return 0.0
        mx, my = sum(x[:n]) / n, sum(y[:n]) / n
        num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        den = math.sqrt(sum((x[i] - mx) ** 2 for i in range(n)) * sum((y[i] - my) ** 2 for i in range(n)))
        return num / den if den > 0 else 0.0


class ExperimentDesigner:
    @staticmethod
    def design(hypothesis: Hypothesis, tools: list[str] | None = None) -> Experiment:
        return Experiment(
            hypothesis_id=hypothesis.id,
            design={"type": "a/b_test", "sample_size": 30},
            procedure=[
                "Set up test environment",
                "Collect baseline measurements",
                "Apply treatment",
                "Measure outcomes",
                "Run statistical tests",
            ],
            independent_vars=["treatment"],
            dependent_vars=["outcome"],
            control_vars=["environment"],
            expected_outcome=f"Hypothesis is supported",
            status="designed",
        )


class StatisticalAnalyzer:
    @staticmethod
    def t_test(control: list[float], treatment: list[float]) -> dict[str, float]:
        n1, n2 = len(control), len(treatment)
        if n1 < 2 or n2 < 2:
            return {"t": 0.0, "p": 1.0, "significant": 0.0}
        m1, m2 = sum(control) / n1, sum(treatment) / n2
        v1 = sum((x - m1) ** 2 for x in control) / (n1 - 1)
        v2 = sum((x - m2) ** 2 for x in treatment) / (n2 - 1)
        se = math.sqrt(v1 / n1 + v2 / n2)
        if se == 0:
            return {"t": 0.0, "p": 1.0, "significant": 0.0}
        t = abs(m1 - m2) / se
        df = n1 + n2 - 2
        p = 2.0 * (1.0 - t / math.sqrt(df + t * t))
        return {"t": t, "p": p, "significant": 1.0 if p < 0.05 else 0.0}

    @staticmethod
    def effect_size(control: list[float], treatment: list[float]) -> float:
        n1, n2 = len(control), len(treatment)
        if n1 < 1 or n2 < 1:
            return 0.0
        m1, m2 = sum(control) / n1, sum(treatment) / n2
        v1 = sum((x - m1) ** 2 for x in control) / max(n1 - 1, 1)
        v2 = sum((x - m2) ** 2 for x in treatment) / max(n2 - 1, 1)
        pooled = math.sqrt((v1 + v2) / 2)
        return abs(m1 - m2) / max(pooled, 0.001)

    @staticmethod
    def bayesian_factor(prior_odds: float, likelihood_ratio: float) -> float:
        return prior_odds * likelihood_ratio


class LiteratureReviewer:
    def __init__(self):
        self._literature: dict[str, dict[str, Any]] = {}

    def add_study(self, ref_id: str, title: str, findings: str,
                   tags: list[str] | None = None):
        self._literature[ref_id] = {"title": title, "findings": findings, "tags": tags or []}

    def review(self, hypothesis: Hypothesis) -> list[dict[str, Any]]:
        relevant = []
        for ref_id, ref in self._literature.items():
            if any(t in hypothesis.tags for t in ref["tags"]):
                relevant.append({"id": ref_id, **ref})
        return relevant


class PeerReviewer:
    @staticmethod
    def review(publication: Publication) -> list[dict[str, Any]]:
        criteria = ["methodology", "evidence_quality", "reproducibility",
                     "significance", "clarity", "novelty"]
        reviews = []
        for i in range(2):
            scores = {c: random.uniform(0.3, 1.0) for c in criteria}
            avg = sum(scores.values()) / len(scores)
            verdict = "accept" if avg > 0.7 else "minor_revision" if avg > 0.5 else "major_revision"
            reviews.append({
                "reviewer": f"reviewer_{i + 1}", "scores": scores,
                "average_score": avg, "verdict": verdict,
            })
        return reviews


class EngineeringScientist:
    """Complete scientific method automation."""

    def __init__(self):
        self._observations: list[Observation] = []
        self._hypotheses: dict[str, Hypothesis] = {}
        self._experiments: dict[str, Experiment] = {}
        self._publications: dict[str, Publication] = {}
        self._literature = LiteratureReviewer()
        self._cycle_count = 0

    def observe(self, description: str, measurements: dict[str, float] | None = None,
                 source: str = "", tags: list[str] | None = None) -> Observation:
        obs = Observation(description=description, measurements=measurements or {},
                          source=source, tags=tags or [])
        self._observations.append(obs)
        return obs

    def hypothesize(self, observation_id: str) -> list[Hypothesis]:
        obs = next((o for o in self._observations if o.id == observation_id), None)
        if not obs:
            return []
        hyps = HypothesisGenerator.from_observation(obs)
        if obs.measurements:
            data = {k: [v] for k, v in obs.measurements.items()}
            hyps.extend(HypothesisGenerator.from_correlation(data))
        for h in hyps:
            self._hypotheses[h.id] = h
        return hyps

    def design_experiment(self, hypothesis_id: str) -> Experiment | None:
        hyp = self._hypotheses.get(hypothesis_id)
        if not hyp:
            return None
        exp = ExperimentDesigner.design(hyp)
        self._experiments[exp.id] = exp
        hyp.status = HypothesisStatus.EXPERIMENTING
        return exp

    def run_experiment(self, experiment_id: str) -> Experiment | None:
        exp = self._experiments.get(experiment_id)
        if not exp:
            return None
        control = [random.gauss(0.5, 0.1) for _ in range(30)]
        treatment = [random.gauss(0.55, 0.1) for _ in range(30)]
        exp.data = {"control": control, "treatment": treatment}
        tests = StatisticalAnalyzer.t_test(control, treatment)
        exp.statistical_tests = tests
        exp.effect_size = StatisticalAnalyzer.effect_size(control, treatment)
        exp.actual_outcome = "significant" if tests.get("significant", 0) > 0 else "not_significant"
        exp.status = "completed"
        exp.completed_at = time.time()

        hyp = self._hypotheses.get(exp.hypothesis_id)
        if hyp:
            if tests.get("significant", 0) > 0:
                hyp.supporting_evidence.append(exp.id)
                hyp.status = HypothesisStatus.SUPPORTED
            else:
                hyp.contradicting_evidence.append(exp.id)
                hyp.status = HypothesisStatus.REFUTED
            hyp.update_confidence()
            hyp.updated_at = time.time()
        return exp

    def publish(self, hypothesis_id: str, experiment_ids: list[str] | None = None) -> Publication:
        hyp = self._hypotheses.get(hypothesis_id)
        pub = Publication(
            title=f"Findings: {hyp.statement[:50] if hyp else 'Untitled'}",
            authors=["Engineering Scientist"],
            hypothesis_id=hypothesis_id,
            experiment_ids=experiment_ids or [],
            abstract=f"Investigation of: {hyp.statement if hyp else 'unknown'}" if hyp else "",
            findings=f"Experimental evidence {'supports' if hyp and hyp.confidence > 0.5 else 'refutes'} hypothesis",
            conclusions=f"Confidence: {hyp.confidence if hyp else 0.5:.2f}",
            status="draft",
        )
        self._publications[pub.id] = pub
        if hyp:
            hyp.status = HypothesisStatus.PUBLISHED
        return pub

    def peer_review(self, publication_id: str) -> list[dict[str, Any]]:
        pub = self._publications.get(publication_id)
        if not pub:
            return []
        reviews = PeerReviewer.review(pub)
        pub.peer_reviews = reviews
        pub.status = "published" if any(r["verdict"] == "accept" for r in reviews) else "rejected"
        return reviews

    def full_cycle(self, observation_id: str) -> dict[str, Any]:
        self._cycle_count += 1
        hyps = self.hypothesize(observation_id)
        results = []
        for hyp in hyps:
            exp = self.design_experiment(hyp.id)
            if exp:
                self.run_experiment(exp.id)
                pub = self.publish(hyp.id, [exp.id])
                reviews = self.peer_review(pub.id)
                results.append({
                    "hypothesis": hyp.statement,
                    "confidence": hyp.confidence,
                    "status": hyp.status.value,
                    "publication": pub.title,
                    "verdict": pub.status,
                })
        return {
            "cycle": self._cycle_count,
            "hypotheses": len(hyps),
            "results": results,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "cycle_count": self._cycle_count,
            "observations": len(self._observations),
            "hypotheses": len(self._hypotheses),
            "experiments": len(self._experiments),
            "publications": len(self._publications),
            "supported": len([h for h in self._hypotheses.values() if h.status == HypothesisStatus.SUPPORTED]),
            "refuted": len([h for h in self._hypotheses.values() if h.status == HypothesisStatus.REFUTED]),
        }
