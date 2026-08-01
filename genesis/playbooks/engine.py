from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state import get_state


@dataclass
class Playbook:
    name: str
    description: str
    prerequisites: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    validation: list[str] = field(default_factory=list)
    rollback: list[str] = field(default_factory=list)
    expected_outputs: list[str] = field(default_factory=list)
    common_mistakes: list[str] = field(default_factory=list)
    historical_examples: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0


class EngineeringPlaybooks:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._state = get_state()
        self._playbooks: dict[str, Playbook] = {}
        self._pb_obj: EngineeringObject | None = None

    def boot(self):
        self._pb_obj = EngineeringObject(
            object_type=EngineeringObjectType.PLAYBOOK,
            name="EngineeringPlaybooks",
            description="Reusable institutional playbooks capturing 19 cycles of engineering learning",
            tags=["playbooks", "knowledge"],
        )
        self._registry.register(self._pb_obj)
        self._register_builtins()
        self._state.set("playbooks", "total", len(self._playbooks))

    def _register_builtins(self):
        self._register(Playbook(
            name="large_refactoring",
            description="Safely refactor a large module or package across the repository",
            prerequisites=["DigitalTwin scan completed", "ReasoningEngine analysis available",
                           "Test suite passing", "Git working tree clean"],
            tools=["kernel.twin", "kernel.reasoning", "kernel.workflow_engine",
                   "Git", "pytest"],
            steps=["1. Scan the repository with DigitalTwin to understand module structure",
                   "2. Run ReasoningEngine to identify high-risk coupling points",
                   "3. Create a refactoring workflow via kernel.workflow_engine",
                   "4. Create backup of all affected modules",
                   "5. Execute refactoring in stages with validation after each",
                   "6. Run full test suite",
                   "7. Generate before/after architecture comparison",
                   "8. Record engineering decision with DecisionIntelligence"],
            validation=["All tests pass", "Architecture delta shows improvement",
                        "No new coupling introduced", "Performance regression < 5%"],
            rollback=["Revert to last known good state via backup",
                       "Restore backed-up modules", "Re-run test suite"],
            expected_outputs=["Refactored module", "Architecture delta report",
                               "Engineering decision record"],
            common_mistakes=["Refactoring without understanding all call sites",
                              "Not running tests between each stage",
                              "Missing edge case imports"],
            historical_examples=["Cycle 017 M133: DigitalTwin was extracted from monolithic watch module"],
            tags=["refactoring", "architecture"],
        ))
        self._register(Playbook(
            name="ai_provider_integration",
            description="Register and deploy a new AI provider into the platform",
            prerequisites=["AI provider endpoint available", "API key configured",
                           "Model supports chat completion"],
            tools=["kernel.ai", "ProviderRegistry", "AIRouter"],
            steps=["1. Add provider class in genesis/ai/providers/",
                   "2. Implement AIProvider interface (chat, stream_chat, embeddings, tool_call)",
                   "3. Provider auto-registers on next boot",
                   "4. Run benchmark via kernel.ai.routing_decision()",
                   "5. Verify routing includes new provider in fallback chain"],
            validation=["Provider appears in kernel.ai.list_providers()",
                        "Routing decision includes provider in healthy list"],
            rollback=["Remove provider file", "Restart kernel"],
            expected_outputs=["New AI provider registered", "Benchmarked and routed"],
            common_mistakes=["Missing required methods", "Incorrect model IDs",
                              "Not handling authentication errors"],
            historical_examples=["Cycle 018 M141: Three providers auto-discovered"],
            tags=["ai", "providers"],
        ))
        self._register(Playbook(
            name="knowledge_consolidation",
            description="Consolidate and optimize the knowledge base",
            prerequisites=["KnowledgeEngine booted", "SelfOrganizingKnowledge active"],
            tools=["kernel.knowledge", "kernel.knowledge_organizer"],
            steps=["1. Run SelfOrganizingKnowledge.consolidate()",
                   "2. Review cluster merges",
                   "3. Archive low-access concepts",
                   "4. Verify search still returns relevant results"],
            validation=["Knowledge clusters reduced", "Search precision maintained"],
            rollback=["Restore from previous knowledge snapshot"],
            expected_outputs=["Consolidated knowledge base", "Consolidation report"],
            common_mistakes=["Over-merging distinct concepts", "Archiving recently added items"],
            historical_examples=["Cycle 019 M152: Self-organizing knowledge introduced"],
            tags=["knowledge", "optimization"],
        ))

    def _register(self, playbook: Playbook):
        self._playbooks[playbook.name] = playbook
        obj = EngineeringObject(
            object_type=EngineeringObjectType.PLAYBOOK,
            name=playbook.name,
            description=playbook.description[:200],
            tags=["playbook"] + playbook.tags,
            metadata={"steps": len(playbook.steps), "tools": len(playbook.tools)},
        )
        self._registry.register(obj)

    def get(self, name: str) -> Playbook | None:
        return self._playbooks.get(name)

    def list(self) -> list[dict[str, Any]]:
        return [
            {"name": p.name, "description": p.description[:80],
             "steps": len(p.steps), "tools": len(p.tools), "tags": p.tags}
            for p in self._playbooks.values()
        ]

    def search(self, query: str) -> list[Playbook]:
        q = query.lower()
        return [p for p in self._playbooks.values()
                if q in p.name.lower() or q in p.description.lower() or
                any(q in t.lower() for t in p.tags)]

    def stats(self) -> dict[str, Any]:
        return {"total": len(self._playbooks)}
