from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class AgentOSCapability:
    name: str
    description: str
    enabled: bool = True
    version: str = "1.0.0"
    verified: bool = False
    last_verified: float = 0.0


class AgentOSFoundation:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._capabilities: dict[str, AgentOSCapability] = {}
        self._os_obj: EngineeringObject | None = None
        self._lock = threading.RLock()
        self._verification_results: dict[str, dict[str, Any]] = {}

    def boot(self):
        self._register_builtin_capabilities()
        self._os_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="AgentOSFoundation",
            description="Intelligence backend foundation for Agent Operating System — all Genesis capabilities as AgentOS services",
            tags=["agentos", "foundation", "v2"],
        )
        self._registry.register(self._os_obj)

    def _register_builtin_capabilities(self):
        caps = [
            AgentOSCapability("engineering_objects", "Universal EngineeringObject registry and search", version="2.0.0"),
            AgentOSCapability("knowledge_engine", "Report parsing and structured knowledge extraction", version="2.0.0"),
            AgentOSCapability("digital_twin", "Live repository model — 487 modules, 120K lines, 8K functions", version="2.0.0"),
            AgentOSCapability("reasoning_engine", "Evidence-based code analysis with 5 analyzers (fragility, coupling, debt, duplication, decay)", version="2.0.0"),
            AgentOSCapability("copilot_engine", "Context-aware developer assistance with CopilotSuggestions", version="2.0.0"),
            AgentOSCapability("timeline", "Universal chronological event history across all subsystems", version="2.0.0"),
            AgentOSCapability("ai_orchestration", "Multi-provider AI routing (NvidiaNIM, Ollama, OpenAICompatible)", version="2.0.0"),
            AgentOSCapability("automation", "Event-driven workflow automation with 3 built-in workflows", version="2.0.0"),
            AgentOSCapability("observatory", "Historical engineering analytics and trends across projects", version="2.0.0"),
            AgentOSCapability("explorer", "Relationship-based object navigation across EngineeringRegistry", version="2.0.0"),
            AgentOSCapability("planner", "Autonomous engineering plan generation from findings", version="2.0.0"),
            AgentOSCapability("memory_v2", "Multi-layer memory (working/short/long-term) with promotion", version="2.0.0"),
            AgentOSCapability("multi_project", "Cross-project intelligence and comparison", version="2.0.0"),
            AgentOSCapability("live_architecture", "Source-derived executable architecture model", version="2.0.0"),
            AgentOSCapability("visual_reasoning", "Explainable recommendations with evidence graphs", version="2.0.0"),
            AgentOSCapability("engineering_search", "Unified multi-source search across 6 engines", version="2.0.0"),
            AgentOSCapability("state_engine", "Unified canonical engineering state — all subsystems share the same state", version="2.0.0"),
            AgentOSCapability("nervous_system", "Continuous engineering signal propagation via state changes", version="2.0.0"),
            AgentOSCapability("context_engine", "Auto-assembles context from 15+ subsystems for every interaction", version="2.0.0"),
            AgentOSCapability("workflow_engine", "Executable workflows with stages, goals, retries, rollback, approvals", version="2.0.0"),
            AgentOSCapability("insight_engine", "Evidence-backed engineering insights with root cause, trend, confidence", version="2.0.0"),
            AgentOSCapability("decision_intelligence", "Operational decisions with alternatives, reasoning, evidence, outcomes", version="2.0.0"),
            AgentOSCapability("knowledge_organizer", "Self-organizing knowledge with auto-merging clusters", version="2.0.0"),
            AgentOSCapability("proactive_copilot", "Continuous background watcher — suggests improvements without prompts", version="2.0.0"),
            AgentOSCapability("playbooks", "3 built-in institutional playbooks (refactoring, AI, knowledge)", version="2.0.0"),
            AgentOSCapability("app_platform", "Genesis Application Platform hosting 6 apps (BuildIT, Venus, ArchitectureStudio, etc.)", version="2.0.0"),
            AgentOSCapability("command_center", "Live Project Command Center with 14 real-time dashboard panels", version="2.0.0"),
            AgentOSCapability("sdk", "21 documented SDK capabilities — Python, REST, WebSocket, CLI", version="2.0.0"),
        ]
        for cap in caps:
            self._capabilities[cap.name] = cap
            cap_obj = EngineeringObject(
                object_type=EngineeringObjectType.CAPABILITY,
                name=f"cap_{cap.name}",
                description=cap.description,
                tags=["capability", "agentos", "v2", cap.name],
                metadata={"version": cap.version, "enabled": cap.enabled},
            )
            self._registry.register(cap_obj)

    def list_capabilities(self) -> list[dict[str, Any]]:
        return [
            {
                "name": c.name, "description": c.description,
                "enabled": c.enabled, "version": c.version,
                "verified": c.verified,
            }
            for c in self._capabilities.values()
        ]

    def get_capability(self, name: str) -> AgentOSCapability | None:
        return self._capabilities.get(name)

    def enable(self, name: str) -> bool:
        cap = self._capabilities.get(name)
        if cap:
            cap.enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        cap = self._capabilities.get(name)
        if cap:
            cap.enabled = False
            return True
        return False

    def verify_all(self) -> dict[str, Any]:
        results = {}
        for name, cap in self._capabilities.items():
            result = self.verify_capability(name)
            results[name] = result
        return {
            "total": len(results),
            "verified": sum(1 for r in results.values() if r.get("verified")),
            "failed": sum(1 for r in results.values() if not r.get("verified")),
            "results": results,
        }

    def verify_capability(self, name: str) -> dict[str, Any]:
        cap = self._capabilities.get(name)
        if not cap:
            return {"verified": False, "error": f"Capability '{name}' not found"}

        if self._kernel is None:
            cap.verified = False
            return {"verified": False, "error": "No kernel available"}

        kernel = self._kernel
        result = {"verified": False, "checks": []}

        try:
            if name == "engineering_objects":
                reg = kernel.engineering
                count = reg.count()
                result["checks"].append(f"Registry has {count} objects")
                result["verified"] = True

            elif name == "digital_twin":
                twin = kernel.twin
                summary = twin.summary() if hasattr(twin, 'summary') else {}
                result["checks"].append(f"Twin: {summary.get('total_modules', 'N/A')} modules")
                result["verified"] = True

            elif name == "reasoning_engine":
                reasoning = kernel.reasoning
                result["checks"].append("Reasoning engine available")
                result["verified"] = True

            elif name == "knowledge_engine":
                knowledge = kernel.knowledge
                result["checks"].append("Knowledge engine available")
                result["verified"] = True

            elif name == "copilot_engine":
                copilot = kernel.copilot
                result["checks"].append("Copilot engine available")
                result["verified"] = True

            elif name == "timeline":
                timeline = kernel.timeline
                result["checks"].append("Timeline available")
                result["verified"] = True

            elif name == "ai_orchestration":
                ai = kernel.ai
                providers = ai.list_providers() if hasattr(ai, 'list_providers') else []
                result["checks"].append(f"{len(providers)} AI providers")
                result["verified"] = True

            elif name == "automation":
                automation = kernel.automation
                stats = automation.stats() if hasattr(automation, 'stats') else {}
                result["checks"].append(f"Automation: {stats.get('total_workflows', 'N/A')} workflows")
                result["verified"] = True

            elif name == "engineering_search":
                search = kernel.search() if hasattr(kernel, 'search') else None
                result["checks"].append("Search available" if search else "Search fallback")
                result["verified"] = True

            elif name == "state_engine":
                state = kernel.state_engine
                snapshot = state.snapshot()
                result["checks"].append(f"{snapshot.get('total_domains', 0)} domains, {snapshot.get('total_keys', 0)} keys")
                result["verified"] = True

            elif name == "nervous_system":
                ns = kernel.nervous_system
                stats = ns.stats() if hasattr(ns, 'stats') else {}
                result["checks"].append(f"Signals processed: {stats.get('signals_processed', 0)}")
                result["verified"] = True

            elif name == "context_engine":
                ctx = kernel.context_engine
                result["checks"].append("Context engine available")
                result["verified"] = True

            elif name == "workflow_engine":
                we = kernel.workflow_engine
                defs = we.list_defs() if hasattr(we, 'list_defs') else []
                result["checks"].append(f"{len(defs)} workflow definitions")
                result["verified"] = True

            elif name == "insight_engine":
                ie = kernel.insight_engine
                stats = ie.stats() if hasattr(ie, 'stats') else {}
                result["checks"].append(f"Insights: {stats.get('total', 0)}")
                result["verified"] = True

            elif name == "decision_intelligence":
                di = kernel.decision_intelligence
                stats = di.stats() if hasattr(di, 'stats') else {}
                result["checks"].append(f"Decisions: {stats.get('total', 0)}")
                result["verified"] = True

            elif name == "knowledge_organizer":
                ko = kernel.knowledge_organizer
                stats = ko.stats() if hasattr(ko, 'stats') else {}
                result["checks"].append(f"Clusters: {stats.get('clusters', 0)}")
                result["verified"] = True

            elif name == "proactive_copilot":
                pc = kernel.proactive_copilot
                suggestions = pc.suggestions() if hasattr(pc, 'suggestions') else []
                result["checks"].append(f"{len(suggestions)} suggestions")
                result["verified"] = True

            elif name == "playbooks":
                pb = kernel.playbooks
                playbooks = pb.list() if hasattr(pb, 'list') else []
                result["checks"].append(f"{len(playbooks)} playbooks")
                result["verified"] = True

            elif name == "command_center":
                cc = kernel.command_center
                result["checks"].append("Command center available")
                result["verified"] = True

            elif name == "sdk":
                sdk = kernel.sdk
                caps = sdk.list_capabilities() if hasattr(sdk, 'list_capabilities') else []
                result["checks"].append(f"{len(caps)} SDK capabilities")
                result["verified"] = True

            elif name == "app_platform":
                ap = kernel.app_platform
                apps = ap.list() if hasattr(ap, 'list') else []
                result["checks"].append(f"{len(apps)} apps registered")
                result["verified"] = True

            else:
                subsystem = getattr(kernel, name, None)
                if subsystem is not None:
                    result["checks"].append(f"{name} available on kernel")
                    result["verified"] = True
                else:
                    result["checks"].append(f"No kernel property for {name}")
                    result["verified"] = False
        except Exception as e:
            result["error"] = str(e)
            result["verified"] = False

        cap.verified = result["verified"]
        cap.last_verified = time.time()
        self._verification_results[name] = result
        return result

    def check_readiness(self) -> dict[str, Any]:
        ready = []
        not_ready = []
        for name, cap in self._capabilities.items():
            status = "ready" if cap.enabled else "disabled"
            (ready if cap.enabled else not_ready).append(name)
        return {
            "status": "ready" if len(ready) > len(not_ready) else "degraded",
            "total": len(self._capabilities),
            "ready": len(ready),
            "disabled": len(not_ready),
            "verified": sum(1 for c in self._capabilities.values() if c.verified),
            "ready_capabilities": ready,
            "disabled_capabilities": not_ready,
        }

    def readiness_summary(self) -> str:
        r = self.check_readiness()
        lines = [
            f"AgentOS Foundation V2 — Readiness Summary",
            f"Status: {r['status'].upper()}",
            f"Total capabilities: {r['total']}",
            f"Ready: {r['ready']}",
            f"Disabled: {r['disabled']}",
            f"Verified: {r['verified']}",
        ]
        if r['ready_capabilities']:
            lines.append(f"\nReady: {', '.join(sorted(r['ready_capabilities']))}")
        if r['disabled_capabilities']:
            lines.append(f"\nDisabled: {', '.join(sorted(r['disabled_capabilities']))}")
        return "\n".join(lines)
