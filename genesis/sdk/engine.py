from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from genesis.state import get_state


@dataclass
class SDKCapability:
    name: str
    description: str
    methods: list[str] = field(default_factory=list)
    version: str = "1.0.0"


class GenesisSDK:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._state = get_state()
        self._capabilities: dict[str, SDKCapability] = {}

    def boot(self):
        self._register_capabilities()

    def _register_capabilities(self):
        caps = [
            SDKCapability("engineering_objects", "Create, read, search EngineeringObjects", ["get", "search", "register", "get_by_type", "get_by_tag", "latest", "stats"]),
            SDKCapability("knowledge", "Query engineering knowledge", ["search", "get_decisions", "get_recommendations", "get_entities", "summary"]),
            SDKCapability("twin", "Repository digital twin access", ["summary", "query", "scan"]),
            SDKCapability("reasoning", "Code analysis and reasoning", ["analyze_fragility", "analyze_coupling", "analyze_debt", "analyze_duplication", "analyze_architecture_decay", "comprehensive_analysis"]),
            SDKCapability("timeline", "Universal timeline queries", ["query", "add"]),
            SDKCapability("search", "Unified multi-source search", ["search"]),
            SDKCapability("ai", "AI provider orchestration", ["chat", "stream_chat", "embeddings", "tool_call", "list_providers", "routing_decision"]),
            SDKCapability("automation", "Event-driven workflow management", ["list_workflows", "get_workflow", "stats"]),
            SDKCapability("workflows", "Executable engineering workflows", ["register", "run", "get_execution", "list_executions", "list_defs"]),
            SDKCapability("insights", "Engineering insight engine", ["list", "create", "stats"]),
            SDKCapability("decisions", "Decision intelligence", ["propose", "decide", "get", "search", "stats"]),
            SDKCapability("memory", "Multi-layer memory", ["store", "recall", "search", "promote", "stats"]),
            SDKCapability("projects", "Multi-project management", ["register_project", "scan_project", "list_projects", "compare"]),
            SDKCapability("architecture", "Live architecture model", ["scan", "summary", "get_dependents", "get_dependencies"]),
            SDKCapability("observatory", "Historical analytics", ["record", "trend", "snapshot"]),
            SDKCapability("explorer", "Relationship navigation", ["explore", "explore_by_type", "find_path"]),
            SDKCapability("planner", "Plan generation", ["generate_plan", "list_plans", "get_plan"]),
            SDKCapability("copilot", "Proactive copilot", ["suggestions", "stats"]),
            SDKCapability("playbooks", "Engineering playbooks", ["get", "list", "search", "stats"]),
            SDKCapability("agentos", "AgentOS foundation", ["list_capabilities", "check_readiness", "get_capability"]),
            SDKCapability("state", "Engineering state engine", ["get", "set", "get_domain", "snapshot", "domains", "transitions"]),
        ]
        for cap in caps:
            self._capabilities[cap.name] = cap

    def capabilities(self) -> list[dict[str, Any]]:
        return [
            {"name": c.name, "description": c.description,
             "methods": c.methods, "version": c.version}
            for c in self._capabilities.values()
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": "GenesisSDK",
            "version": "1.0.0",
            "capabilities": self.capabilities(),
            "access": "kernel.<capability>.<method>()",
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
