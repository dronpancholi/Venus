from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state import get_state


@dataclass
class Insight:
    title: str
    summary: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.5
    category: str = "general"
    severity: str = "info"
    affected_objects: list[str] = field(default_factory=list)
    architecture_impact: str = ""
    knowledge_refs: list[str] = field(default_factory=list)
    timeline_refs: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    estimated_effort: str = "medium"
    estimated_value: str = "medium"
    risks: list[str] = field(default_factory=list)
    related_reports: list[str] = field(default_factory=list)
    related_decisions: list[str] = field(default_factory=list)
    related_plans: list[str] = field(default_factory=list)
    timestamp: float = 0.0
    source: str = ""


class EngineeringInsightEngine:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._state = get_state()
        self._insights: list[Insight] = []
        self._max_insights = 1000
        self._lock = threading.RLock()
        self._insight_obj: EngineeringObject | None = None
        self._booted = False

    def boot(self):
        if self._booted:
            return
        self._booted = True
        self._insight_obj = EngineeringObject(
            object_type=EngineeringObjectType.RECOMMENDATION,
            name="EngineeringInsightEngine",
            description="Evidence-backed engineering insights with root cause, impact, and suggested actions",
            tags=["insight", "intelligence"],
        )
        self._registry.register(self._insight_obj)
        self._auto_generate()

    def _auto_generate(self):
        try:
            if self._kernel and self._kernel.reasoning:
                findings = self._kernel.reasoning.comprehensive_analysis()
                if isinstance(findings, dict):
                    for ftype, fdata in findings.items():
                        if isinstance(fdata, dict):
                            risk = fdata.get("risk", fdata.get("score", 0))
                            if isinstance(risk, (int, float)) and risk > 0.3:
                                self.create(
                                    title=f"{ftype.replace('_', ' ').title()} Risk Detected",
                                    summary=fdata.get("summary", f"Risk score: {risk:.2f}"),
                                    evidence=[f"Analyzer: {ftype}", f"Risk: {risk:.2f}"],
                                    confidence=min(risk + 0.2, 1.0),
                                    category=ftype,
                                    severity="warning" if risk > 0.6 else "info",
                                    affected_objects=fdata.get("object_ids", []),
                                    estimated_effort="medium",
                                    estimated_value="high",
                                    source="reasoning",
                                )
        except Exception:
            pass

    def create(self, title: str, summary: str,
               evidence: list[str] | None = None,
               confidence: float = 0.5,
               category: str = "general",
               severity: str = "info",
               affected_objects: list[str] | None = None,
               architecture_impact: str = "",
               knowledge_refs: list[str] | None = None,
               timeline_refs: list[str] | None = None,
               suggested_actions: list[str] | None = None,
               estimated_effort: str = "medium",
               estimated_value: str = "medium",
               risks: list[str] | None = None,
               related_reports: list[str] | None = None,
               related_decisions: list[str] | None = None,
               related_plans: list[str] | None = None,
               source: str = "") -> Insight:
        insight = Insight(
            title=title,
            summary=summary,
            evidence=evidence or [],
            confidence=confidence,
            category=category,
            severity=severity,
            affected_objects=affected_objects or [],
            architecture_impact=architecture_impact,
            knowledge_refs=knowledge_refs or [],
            timeline_refs=timeline_refs or [],
            suggested_actions=suggested_actions or [],
            estimated_effort=estimated_effort,
            estimated_value=estimated_value,
            risks=risks or [],
            related_reports=related_reports or [],
            related_decisions=related_decisions or [],
            related_plans=related_plans or [],
            timestamp=time.time(),
            source=source or "insight_engine",
        )
        with self._lock:
            self._insights.append(insight)
            if len(self._insights) > self._max_insights:
                self._insights = self._insights[-self._max_insights:]
        self._state.set("insights", "total", len(self._insights))
        self._state.set("insights", f"latest.{len(self._insights)}", {
            "title": title, "category": category, "confidence": confidence,
        })
        obj = EngineeringObject(
            object_type=EngineeringObjectType.RECOMMENDATION,
            name=f"Insight: {title[:40]}...",
            description=summary[:200],
            tags=["insight", category, severity],
            metadata={
                "confidence": confidence,
                "category": category,
                "effort": estimated_effort,
                "value": estimated_value,
                "actions": len(suggested_actions or []),
            },
        )
        self._registry.register(obj)
        if self._kernel:
            self._kernel.emit("insight.created", {
                "title": title, "category": category,
                "confidence": confidence, "severity": severity,
            }, origin="insight", tags=["insight"])
        return insight

    def list(self, category: str | None = None,
             severity: str | None = None,
             min_confidence: float = 0.0,
             limit: int = 50) -> list[Insight]:
        results = []
        for ins in reversed(self._insights):
            if category and ins.category != category:
                continue
            if severity and ins.severity != severity:
                continue
            if ins.confidence < min_confidence:
                continue
            results.append(ins)
            if len(results) >= limit:
                break
        return results

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total": len(self._insights),
                "by_category": self._count_by("category"),
                "by_severity": self._count_by("severity"),
                "avg_confidence": sum(i.confidence for i in self._insights) / max(len(self._insights), 1),
            }

    def _count_by(self, field: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for ins in self._insights:
            val = getattr(ins, field, "unknown")
            counts[val] = counts.get(val, 0) + 1
        return counts
