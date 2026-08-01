from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state import get_state


@dataclass
class ProactiveSuggestion:
    title: str
    explanation: str
    evidence: str = ""
    expected_impact: str = ""
    suggested_solution: str = ""
    rollback: str = ""
    confidence: float = 0.5
    category: str = "general"
    urgency: str = "info"
    timestamp: float = 0.0


class ProactiveCopilot:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._state = get_state()
        self._suggestions: list[ProactiveSuggestion] = []
        self._max_suggestions = 100
        self._lock = threading.RLock()
        self._pc_obj: EngineeringObject | None = None
        self._booted = False
        self._watch_thread: threading.Thread | None = None
        self._stop = threading.Event()

    def boot(self):
        if self._booted:
            return
        self._booted = True
        self._pc_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="ProactiveCopilot",
            description="Continuously watches engineering activity and proactively suggests improvements",
            tags=["copilot", "proactive", "assistant"],
        )
        self._registry.register(self._pc_obj)
        self._state.set("proactive_copilot", "status", "watching")
        self._state.set("proactive_copilot", "suggestions", 0)
        self._start_watcher()

    def _start_watcher(self):
        self._stop.clear()
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True, name="proactive-copilot")
        self._watch_thread.start()

    def _watch_loop(self):
        while not self._stop.is_set():
            try:
                self._check_conditions()
            except Exception:
                pass
            self._stop.wait(30.0)

    def _check_conditions(self):
        k = self._kernel
        if not k:
            return

        try:
            dt = k.twin
            if dt and dt.model.total_lines > 50000:
                ratio = dt.model.total_functions / max(dt.model.total_classes, 1)
                if ratio > 15:
                    self._suggest(
                        title="High Function-to-Class Ratio",
                        explanation=f"Repository has {dt.model.total_functions} functions but only "
                                    f"{dt.model.total_classes} classes (ratio {ratio:.1f}:1). "
                                    f"Consider encapsulating related functions.",
                        evidence=f"Twin: {dt.model.total_classes} classes, {dt.model.total_functions} functions",
                        expected_impact="Improved maintainability and discoverability",
                        suggested_solution="Group related functions into classes by domain",
                        category="architecture",
                        urgency="warning",
                    )
        except Exception:
            pass

        try:
            findings = {}
            if hasattr(k.reasoning, 'comprehensive_analysis'):
                findings = k.reasoning.comprehensive_analysis()
            if isinstance(findings, dict):
                for ftype, fdata in findings.items():
                    if isinstance(fdata, dict):
                        risk = fdata.get("risk", fdata.get("score", 0))
                        if isinstance(risk, (int, float)) and risk > 0.7:
                            self._suggest(
                                title=f"Critical {ftype.replace('_', ' ').title()}",
                                explanation=fdata.get("summary", f"High risk ({risk:.2f}) detected in {ftype}"),
                                evidence=f"ReasoningEngine: {ftype} analyzer",
                                expected_impact="Reducing technical debt and improving stability",
                                category=ftype,
                                urgency="critical",
                            )
        except Exception:
            pass

        try:
            if hasattr(k, 'knowledge_organizer') and k._knowledge_organizer:
                stats = k.knowledge_organizer.stats() if hasattr(k.knowledge_organizer, 'stats') else {}
                if isinstance(stats, dict) and stats.get("clusters", 0) > 50 and not self._recently_suggested("consolidate_knowledge"):
                    self._suggest(
                        title="Knowledge Consolidation Recommended",
                        explanation=f"Knowledge base has {stats.get('clusters', 0)} clusters. "
                                    f"Running consolidation may merge related topics.",
                        category="knowledge",
                        urgency="info",
                    )
        except Exception:
            pass

    def _recently_suggested(self, title_key: str, within: float = 300) -> bool:
        for s in self._suggestions[-20:]:
            if title_key in s.title.lower() and time.time() - s.timestamp < within:
                return True
        return False

    def _suggest(self, title: str, explanation: str,
                 evidence: str = "", expected_impact: str = "",
                 suggested_solution: str = "", rollback: str = "",
                 confidence: float = 0.6, category: str = "general",
                 urgency: str = "info"):
        suggestion = ProactiveSuggestion(
            title=title, explanation=explanation, evidence=evidence,
            expected_impact=expected_impact, suggested_solution=suggested_solution,
            rollback=rollback, confidence=confidence, category=category,
            urgency=urgency, timestamp=time.time(),
        )
        with self._lock:
            self._suggestions.append(suggestion)
            if len(self._suggestions) > self._max_suggestions:
                self._suggestions = self._suggestions[-self._max_suggestions:]
        self._state.set("proactive_copilot", "suggestions", len(self._suggestions))
        if self._kernel:
            self._kernel.emit("copilot.suggestion", {
                "title": title, "category": category, "urgency": urgency,
            }, origin="proactive_copilot", tags=["copilot", "proactive"])

    def suggestions(self, category: str | None = None,
                    min_urgency: str = "info",
                    limit: int = 20) -> list[ProactiveSuggestion]:
        urgency_order = {"critical": 4, "warning": 3, "info": 2, "debug": 1}
        min_ord = urgency_order.get(min_urgency, 0)
        results = []
        for s in reversed(self._suggestions):
            if category and s.category != category:
                continue
            if urgency_order.get(s.urgency, 0) < min_ord:
                continue
            results.append(s)
            if len(results) >= limit:
                break
        return results

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total_suggestions": len(self._suggestions),
                "watching": self._watch_thread is not None and self._watch_thread.is_alive(),
            }
