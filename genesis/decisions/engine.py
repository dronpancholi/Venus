from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state import get_state


@dataclass
class DecisionRecord:
    id: str
    title: str
    problem: str = ""
    context: str = ""
    alternatives: list[str] = field(default_factory=list)
    reasoning: str = ""
    supporting_evidence: list[str] = field(default_factory=list)
    counterarguments: list[str] = field(default_factory=list)
    affected_objects: list[str] = field(default_factory=list)
    reports: list[str] = field(default_factory=list)
    implementation: str = ""
    validation: str = ""
    outcome: str = ""
    lessons_learned: list[str] = field(default_factory=list)
    status: str = "proposed"
    created_at: float = 0.0
    decided_at: float = 0.0
    tags: list[str] = field(default_factory=list)


class EngineeringDecisionIntelligence:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._state = get_state()
        self._decisions: dict[str, DecisionRecord] = {}
        self._lock = threading.RLock()
        self._di_obj: EngineeringObject | None = None

    def boot(self):
        self._di_obj = EngineeringObject(
            object_type=EngineeringObjectType.DECISION,
            name="EngineeringDecisionIntelligence",
            description="Operational engineering decisions with full context, alternatives, and outcomes",
            tags=["decisions", "intelligence"],
        )
        self._registry.register(self._di_obj)
        self._state.set("decisions", "total", 0)

    def propose(self, title: str, problem: str = "",
                context: str = "", alternatives: list[str] | None = None,
                reasoning: str = "", tags: list[str] | None = None) -> DecisionRecord:
        from genesis.utils.identity import generate_id
        rec = DecisionRecord(
            id=generate_id("dec", 12),
            title=title,
            problem=problem,
            context=context,
            alternatives=alternatives or [],
            reasoning=reasoning,
            status="proposed",
            created_at=time.time(),
            tags=tags or [],
        )
        with self._lock:
            self._decisions[rec.id] = rec
        self._state.set("decisions", "total", len(self._decisions))
        obj = EngineeringObject(
            object_type=EngineeringObjectType.DECISION,
            name=f"Decision: {title[:40]}",
            description=f"Proposed: {problem[:100]}" if problem else title[:100],
            tags=["decision"] + (tags or []),
            metadata={"status": "proposed", "alternatives": len(alternatives or [])},
        )
        self._registry.register(obj)
        if self._kernel:
            self._kernel.emit("decision.proposed", {
                "id": rec.id, "title": title, "alternatives": len(alternatives or []),
            }, origin="decisions", tags=["decision"])
        return rec

    def decide(self, decision_id: str, reasoning: str = "",
               outcome: str = "", implementation: str = "",
               validation: str = ""):
        with self._lock:
            rec = self._decisions.get(decision_id)
            if not rec:
                raise ValueError(f"Decision not found: {decision_id}")
            rec.status = "decided"
            rec.reasoning = reasoning or rec.reasoning
            rec.outcome = outcome
            rec.implementation = implementation
            rec.validation = validation
            rec.decided_at = time.time()
        self._state.set("decisions", f"{decision_id}.status", "decided")
        if self._kernel:
            self._kernel.emit("decision.made", {
                "id": decision_id, "title": rec.title, "outcome": outcome,
            }, origin="decisions", tags=["decision"])

    def get(self, decision_id: str) -> DecisionRecord | None:
        return self._decisions.get(decision_id)

    def search(self, query: str = "", status: str | None = None,
               limit: int = 20) -> list[DecisionRecord]:
        q = query.lower()
        results = []
        for rec in self._decisions.values():
            if status and rec.status != status:
                continue
            if q and q not in rec.title.lower() and q not in rec.problem.lower() and q not in rec.context.lower():
                continue
            results.append(rec)
        results.sort(key=lambda r: -r.created_at)
        return results[:limit]

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total": len(self._decisions),
                "proposed": sum(1 for d in self._decisions.values() if d.status == "proposed"),
                "decided": sum(1 for d in self._decisions.values() if d.status == "decided"),
                "implemented": sum(1 for d in self._decisions.values() if d.status == "implemented"),
            }
