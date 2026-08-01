from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class EngineeringContext:
    query: str = ""
    workspace: dict[str, Any] = field(default_factory=dict)
    project: dict[str, Any] = field(default_factory=dict)
    repository: dict[str, Any] = field(default_factory=dict)
    architecture: dict[str, Any] = field(default_factory=dict)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    knowledge: list[dict[str, Any]] = field(default_factory=list)
    memory: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    plans: list[dict[str, Any]] = field(default_factory=list)
    workflows: list[dict[str, Any]] = field(default_factory=list)
    ai: dict[str, Any] = field(default_factory=dict)
    agents: list[dict[str, Any]] = field(default_factory=list)
    insights: list[dict[str, Any]] = field(default_factory=list)
    recent_events: list[dict[str, Any]] = field(default_factory=list)
    related_objects: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    timestamp: float = 0.0


class ContextEngine:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._ctx_obj: EngineeringObject | None = None

    def boot(self):
        self._ctx_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="ContextEngine",
            description="Automatic context assembly for every interaction — no manual context building",
            tags=["context", "assistant"],
        )
        self._registry.register(self._ctx_obj)

    def build(self, query: str = "", project: str = "",
              object_id: str = "", depth: int = 3) -> EngineeringContext:
        ctx = EngineeringContext(query=query, timestamp=time.time())
        k = self._kernel
        if not k:
            return ctx

        try:
            dt = k.twin
            if dt:
                ctx.repository = {
                    "modules": dt.model.total_files,
                    "lines": dt.model.total_lines,
                    "classes": dt.model.total_classes,
                    "functions": dt.model.total_functions,
                    "packages": len(dt.model.packages),
                }
        except Exception as e:
            ctx.errors.append(f"twin: {e}")

        try:
            ke = k.knowledge
            if hasattr(ke, 'search') and query:
                ctx.knowledge = ke.search(query, limit=5)
        except Exception:
            pass

        try:
            mem = k.memory_v2
            if hasattr(mem, 'search') and query:
                ctx.memory = [{"key": e.key, "content": e.content[:100], "layer": e.layer.value}
                              for e in mem.search(query, limit=5)]
        except Exception:
            pass

        try:
            tl = k.timeline
            if hasattr(tl, 'query'):
                ctx.timeline = tl.query(limit=10)
        except Exception:
            pass

        try:
            if k.task_graph:
                s = k.task_graph.summary()
                ctx.workflows.append({"task_graph": {"total": s.get("total_nodes", 0)}})
        except Exception:
            pass

        try:
            ai_engine = k.ai
            if hasattr(ai_engine, 'summarize'):
                ctx.ai = ai_engine.summarize()
        except Exception:
            pass

        try:
            if k.agent_runtime:
                agents = k.agent_runtime.list_agents()
                ctx.agents = [{"name": a.to_dict().get("name", "?"), "role": a.to_dict().get("role", "?")}
                              for a in agents[:5]]
        except Exception:
            pass

        try:
            reg = k.engineering
            stats = reg.stats()
            ctx.related_objects = [{"type": t, "count": c} for t, c in stats.get("by_type", {}).items()]
        except Exception:
            pass

        try:
            events = k.query_events(limit=10)
            ctx.recent_events = [
                {"type": e.type, "origin": e.origin, "age": time.time() - e.timestamp}
                for e in events
            ]
        except Exception:
            pass

        return ctx

    def summarize(self, ctx: EngineeringContext, max_lines: int = 30) -> list[str]:
        lines = []
        if ctx.repository:
            lines.append(f"Repository: {ctx.repository.get('modules', 0)} modules, {ctx.repository.get('lines', 0)} lines")
        if ctx.knowledge:
            lines.append(f"Knowledge: {len(ctx.knowledge)} items")
        if ctx.memory:
            lines.append(f"Memory: {len(ctx.memory)} items")
        if ctx.timeline:
            lines.append(f"Timeline: {len(ctx.timeline)} entries")
        if ctx.ai:
            lines.append(f"AI: {ctx.ai.get('total', 0)} providers")
        if ctx.agents:
            lines.append(f"Agents: {len(ctx.agents)} active")
        if ctx.recent_events:
            lines.append(f"Recent events: {len(ctx.recent_events)}")
        if ctx.errors:
            lines.append(f"Errors: {len(ctx.errors)}")
        return lines[:max_lines]
