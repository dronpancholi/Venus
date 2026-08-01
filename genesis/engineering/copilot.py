from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering.object import EngineeringObject, EngineeringObjectType
from genesis.engineering.registry import get_registry


@dataclass
class CopilotContext:
    screen_id: str = ""
    screen_name: str = ""
    selected_object_id: str = ""
    selected_object_type: str = ""
    active_session_id: str = ""
    recent_events_count: int = 0
    total_objects: int = 0
    total_services: int = 0
    total_agents: int = 0
    total_tasks: int = 0
    total_conversations: int = 0
    total_reports: int = 0
    knowledge_items: int = 0
    uptime_seconds: float = 0.0
    kernel_state: str = ""


@dataclass
class CopilotResponse:
    query: str = ""
    answer: str = ""
    context: CopilotContext = field(default_factory=CopilotContext)
    suggestions: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    duration_ms: float = 0.0


class CopilotEngine:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()

    def _get_context(self, screen_id: str = "", selected_id: str = "") -> CopilotContext:
        ctx = CopilotContext(
            screen_id=screen_id or "",
            selected_object_id=selected_id or "",
            total_objects=self._registry.count(),
            total_services=len(self._registry.get_by_type(EngineeringObjectType.SERVICE)),
            total_agents=len(self._registry.get_by_type(EngineeringObjectType.AGENT)),
            total_tasks=len(self._registry.get_by_type(EngineeringObjectType.TASK)),
            total_conversations=len(self._registry.get_by_type(EngineeringObjectType.CONVERSATION)),
        )
        if self._kernel:
            try:
                health = self._kernel.health()
                ctx.uptime_seconds = health.uptime_seconds
                ctx.kernel_state = health.status
            except Exception:
                pass
            try:
                ctx.recent_events_count = self._kernel.event_store.count()
            except Exception:
                pass
            try:
                ke = self._kernel.knowledge
                ks = ke.summary()
                ctx.knowledge_items = ks.get("knowledge_items", 0)
                ctx.total_reports = ks.get("reports_indexed", 0)
            except Exception:
                pass
            try:
                if self._kernel._agent_runtime:
                    ctx.total_agents = len(self._kernel._agent_runtime.list_agents())
            except Exception:
                pass
        if selected_id:
            obj = self._registry.get(selected_id)
            if obj:
                ctx.selected_object_type = obj.object_type.value
                ctx.selected_object_id = obj.id
                ctx.selected_object_id = obj.id
        return ctx

    def _context_summary(self, ctx: CopilotContext) -> str:
        parts = [f"Current screen: {ctx.screen_name or ctx.screen_id or 'unknown'}"]
        if ctx.selected_object_id:
            parts.append(f"Selected: {ctx.selected_object_type} ({ctx.selected_object_id[:16]}...)")
        parts.append(f"Kernel: {ctx.kernel_state} (uptime: {ctx.uptime_seconds:.0f}s)")
        parts.append(f"Objects: {ctx.total_objects} total")
        counts = []
        if ctx.total_services:
            counts.append(f"{ctx.total_services} services")
        if ctx.total_agents:
            counts.append(f"{ctx.total_agents} agents")
        if ctx.total_tasks:
            counts.append(f"{ctx.total_tasks} tasks")
        if ctx.total_conversations:
            counts.append(f"{ctx.total_conversations} conversations")
        if ctx.total_reports:
            counts.append(f"{ctx.total_reports} reports")
        if counts:
            parts.append(f"Registry: {', '.join(counts)}")
        if ctx.knowledge_items:
            parts.append(f"Knowledge: {ctx.knowledge_items} items")
        if ctx.recent_events_count:
            parts.append(f"Events: {ctx.recent_events_count} in store")
        return " | ".join(parts)

    def ask(self, query: str, screen_id: str = "",
            selected_id: str = "") -> CopilotResponse:
        start = time.time()
        ctx = self._get_context(screen_id, selected_id)
        q = query.lower().strip()
        answer = ""
        suggestions = []
        references = []

        if not q:
            answer = f"I see you're on **{ctx.screen_name or ctx.screen_id or 'an unknown screen'}**.\n\n"
            answer += self._context_summary(ctx)
            suggestions = [
                "What's the current fragility analysis?",
                "Show me recent decisions from reports",
                "What engineering objects exist?",
                "Analyze architecture debt",
            ]
        elif "who" in q or "what" in q and any(w in q for w in ["here", "this", "screen", "current"]):
            answer = self._context_summary(ctx)
            if ctx.selected_object_id:
                obj = self._registry.get(ctx.selected_object_id)
                if obj:
                    links = f"{len(obj.links)} links, " if obj.links else ""
                    rels = f"{len(obj.relationships)} relationships, " if obj.relationships else ""
                    answer += f"\n\nSelected object: **{obj.name}** ({obj.object_type.value}) — {links}{rels}created {time.ctime(obj.created_at)}"
                    suggestions = [
                        f"Show relationships for {obj.name}",
                        f"Find related objects to {obj.name}",
                        "Analyze this object's health",
                    ]
            else:
                suggestions = [
                    "Analyze current engineering state",
                    "Show recent events and activity",
                    "What should I work on next?",
                ]
        elif "fragil" in q or "health" in q:
            try:
                result = self._kernel.reasoning.comprehensive_analysis()
                answer = result.summary
                for f in result.findings[:5]:
                    answer += f"\n- [{f.severity}] {f.title}"
                    if f.evidence:
                        answer += f" ({f.evidence[0][:100]})"
                suggestions = ["Show me architecture analysis", "Check for duplication issues", "Run debt analysis"]
            except Exception as e:
                answer = f"Reasoning engine unavailable: {e}"
        elif "decision" in q or "recommend" in q:
            try:
                ke = self._kernel.knowledge
                decisions = ke.get_decisions(limit=5)
                if decisions:
                    answer = "Recent engineering decisions:\n"
                    for d in decisions:
                        answer += f"\n- {d.content[:200]}"
                    suggestions = ["Show recommendations", "List all risks", "Find architecture patterns"]
                else:
                    answer = "No decisions extracted yet. Try indexing recent reports."
                    suggestions = ["Index reports now", "Show me available reports"]
            except Exception as e:
                answer = f"Knowledge engine unavailable: {e}"
        elif "report" in q:
            try:
                ke = self._kernel.knowledge
                keyword = q.replace("report", "").replace("search", "").replace("find", "").strip()
                if keyword:
                    reports = ke.search_reports(query=keyword, limit=5)
                else:
                    reports = ke.search_reports(query="", limit=5)
                if reports:
                    answer = f"Found {len(reports)} reports:\n"
                    for r in reports:
                        answer += f"\n- Cycle {r.cycle}: {r.title} ({r.word_count} words)"
                    suggestions = [
                        "Show decisions from these reports",
                        "Find me recommendations",
                        "What risks are documented?",
                    ]
                else:
                    answer = f"No reports found matching '{keyword}'."
            except Exception as e:
                answer = f"Cannot search reports: {e}"
        elif "object" in q or "registry" in q:
            stats = self._registry.stats()
            answer = f"Engineering Registry: **{stats['total']}** objects\n"
            for t, c in sorted(stats.get("by_type", {}).items()):
                answer += f"\n- {t}: {c}"
            suggestions = [
                "Show me the latest objects",
                "Find objects by tag",
                "Analyze object distribution",
            ]
        elif "analyze" in q or "review" in q:
            try:
                result = self._kernel.reasoning.comprehensive_analysis()
                answer = result.summary
                for f in result.findings[:10]:
                    answer += f"\n- [{f.severity}] **{f.title}**: {f.description[:120]}"
                suggestions = [
                    "Focus on critical findings",
                    "Show me recommended actions",
                    "Compare with previous analysis",
                ]
            except Exception as e:
                answer = f"Analysis failed: {e}"
        else:
            # Generic search across registry + knowledge
            results = self._registry.search(query, limit=10)
            if results:
                answer = f"Found {len(results)} matching objects:\n"
                for obj in results[:10]:
                    answer += f"\n- **{obj.name}** (`{obj.object_type.value}`, {obj.id[:16]}...)"
                suggestions = [
                    "Narrow the search",
                    "Show me objects by type",
                    "Analyze what was found",
                ]
            else:
                answer = f"I searched for '{query}' but found no matches.\n\nCurrent context:\n{self._context_summary(ctx)}"
                suggestions = [
                    "Show me what's available",
                    "Analyze current engineering state",
                    "What can you help me with?",
                ]

        return CopilotResponse(
            query=query,
            answer=answer,
            context=ctx,
            suggestions=suggestions,
            references=references,
            duration_ms=(time.time() - start) * 1000,
        )
