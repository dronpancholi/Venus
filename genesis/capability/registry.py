"""
CORE-04: Capability Registry

Every capability becomes an object.
Decision Engine, Research Engine, Security Validator, Compiler,
Runtime, Planner, Scheduler, Memory, Ontology, etc.

Each includes:
  UUID, Semantic Type, Dependencies, Interfaces,
  Inputs, Outputs, Contracts, Policies, Permissions,
  Version, Owner, Validation Rules, Certification State.
"""

from datetime import datetime, timezone
from typing import Any

from genesis.events.bus import EventBus
from genesis.utils.graph_algorithms import find_cycles as _find_cycles
from genesis.utils.identity import generate_id


class CapabilityDefinition:
    """A registered capability in the Venus platform."""

    def __init__(
        self,
        name: str,
        description: str = "",
        version: str = "0.1.0",
        owner: str = "genesis",
    ):
        self.capability_id = generate_id("cap", 8)
        self.name = name
        self.description = description
        self.version = version
        self.owner = owner
        self.semantic_type: str = "capability"
        self.dependencies: list[str] = []
        self.interfaces: list[dict[str, Any]] = []
        self.inputs: list[dict[str, Any]] = []
        self.outputs: list[dict[str, Any]] = []
        self.contracts: list[dict[str, Any]] = []
        self.policies: list[str] = []
        self.permissions: list[str] = []
        self.validation_rules: list[str] = []
        self.certification_state: str = "uncertified"
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.enabled: bool = True
        self.metadata: dict[str, Any] = {}

    def add_interface(self, name: str, method: str = "", path: str = "", schema: str = ""):
        self.interfaces.append({
            "name": name,
            "method": method,
            "path": path,
            "schema": schema,
        })

    def add_contract(self, name: str, description: str, condition: str = ""):
        self.contracts.append({
            "name": name,
            "description": description,
            "condition": condition,
        })

    def add_dependency(self, capability_name: str):
        if capability_name not in self.dependencies:
            self.dependencies.append(capability_name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "owner": self.owner,
            "semantic_type": self.semantic_type,
            "dependencies": list(self.dependencies),
            "interfaces": list(self.interfaces),
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "contracts": list(self.contracts),
            "policies": list(self.policies),
            "permissions": list(self.permissions),
            "validation_rules": list(self.validation_rules),
            "certification_state": self.certification_state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
        }

    def to_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent)


class CapabilityRegistry:
    """Registry of all capabilities in the platform."""

    def __init__(self, event_bus: EventBus | None = None):
        self._capabilities: dict[str, CapabilityDefinition] = {}
        self._bus = event_bus
        self._register_core_capabilities()

    def _register_core_capabilities(self):
        core_caps = [
            ("compiler", "Multi-source compiler framework", "1.0.0"),
            ("parser", "Multi-format source parser", "1.0.0"),
            ("validator", "Universal validation engine", "1.0.0"),
            ("knowledge_graph", "Knowledge graph engine", "1.0.0"),
            ("metadata_engine", "Automatic metadata management", "1.0.0"),
            ("type_registry", "Semantic type registry", "1.0.0"),
            ("plugin_manager", "Plugin installation and lifecycle", "1.0.0"),
            ("capability_registry", "Capability registration and discovery", "1.0.0"),
            ("repository_indexer", "Repository scanning and indexing", "1.0.0"),
            ("execution_engine", "DAG-based workflow execution", "1.0.0"),
            ("package_manager", "VenusPM package management", "1.0.0"),
            ("studio_backend", "Venus Studio backend APIs", "1.0.0"),
            ("diagnostics", "Self-diagnostics and health checks", "1.0.0"),
            ("memory_engine", "Institutional memory management", "1.0.0"),
            ("graph_exporter", "Graph export to Neo4j and other formats", "1.0.0"),
            ("project_manager", "Project management and lifecycle", "1.0.0"),
            ("certification", "Artifact certification", "1.0.0"),
            ("security", "Security validation and policies", "1.0.0"),
        ]
        for name, desc, ver in core_caps:
            cap = CapabilityDefinition(name, desc, ver)
            self.register(cap)

        # Define dependency edges between capabilities
        # Derived from VPS §9.3 Capability Resolution and import analysis
        self.get("compiler").add_dependency("parser")
        self.get("graph_exporter").add_dependency("knowledge_graph")
        self.get("package_manager").add_dependency("plugin_manager")
        self.get("certification").add_dependency("metadata_engine")
        self.get("diagnostics").add_dependency("capability_registry")
        self.get("diagnostics").add_dependency("type_registry")
        self.get("diagnostics").add_dependency("knowledge_graph")
        self.get("studio_backend").add_dependency("capability_registry")
        self.get("studio_backend").add_dependency("compiler")
        self.get("studio_backend").add_dependency("type_registry")
        self.get("studio_backend").add_dependency("knowledge_graph")
        self.get("studio_backend").add_dependency("validator")
        self.get("project_manager").add_dependency("capability_registry")
        self.get("project_manager").add_dependency("compiler")
        self.get("project_manager").add_dependency("type_registry")
        self.get("project_manager").add_dependency("knowledge_graph")
        self.get("project_manager").add_dependency("validator")
        self.get("memory_engine").add_dependency("knowledge_graph")

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def register(self, capability: CapabilityDefinition):
        self._capabilities[capability.name] = capability
        self._emit("capability.registered", {"name": capability.name, "version": capability.version})

    def get(self, name: str) -> CapabilityDefinition | None:
        return self._capabilities.get(name)

    def all(self) -> list[CapabilityDefinition]:
        return list(self._capabilities.values())

    def find_by_interface(self, method: str, path: str) -> list[CapabilityDefinition]:
        results = []
        for cap in self._capabilities.values():
            for iface in cap.interfaces:
                if iface.get("method") == method and iface.get("path") == path:
                    results.append(cap)
        return results

    def dependency_chain(self, name: str) -> list[str]:
        """Resolve full dependency chain for a capability.

        Uses shared find_cycles for cycle detection.
        Returns empty list if cycles are detected.
        """
        # Build edge list from current dependency graph
        edges = []
        for cap_name, cap in self._capabilities.items():
            for dep in cap.dependencies:
                edges.append((cap_name, dep))

        cycles = _find_cycles(edges)
        if cycles:
            return []

        chain = []
        visited = set()

        def resolve(cap_name: str):
            if cap_name in visited:
                return
            visited.add(cap_name)
            cap = self._capabilities.get(cap_name)
            if cap:
                for dep in cap.dependencies:
                    resolve(dep)
                chain.append(cap_name)

        resolve(name)
        return chain

    def clear(self):
        self._capabilities.clear()
        self._emit("capability.registry.cleared", {})

    def validate_all(self) -> list[dict[str, Any]]:
        """Validate all registered capabilities.

        Checks:
          - Interfaces defined
          - All dependencies resolve to registered capabilities
          - No circular dependencies
        """
        errors = []

        # Build full edge list for cycle detection
        edges = []
        for cap in self._capabilities.values():
            for dep in cap.dependencies:
                edges.append((cap.name, dep))

        cycles = _find_cycles(edges)
        if cycles:
            errors.append({
                "error": "circular capability dependencies detected",
                "cycles": cycles,
            })

        for cap in self._capabilities.values():
            if not cap.interfaces:
                errors.append({
                    "capability": cap.name,
                    "error": "no interfaces defined",
                })
            if not cap.validation_rules:
                errors.append({
                    "capability": cap.name,
                    "warning": "no validation rules defined",
                })
            for dep in cap.dependencies:
                if dep not in self._capabilities:
                    errors.append({
                        "capability": cap.name,
                        "error": f"dependency '{dep}' not registered",
                    })

        self._emit("capability.validation.completed", {
            "errors": len([e for e in errors if "error" in e.get("error", "")]),
            "warnings": len([e for e in errors if "warning" in e.get("error", "")]),
        })
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            name: cap.to_dict() for name, cap in self._capabilities.items()
        }

    def to_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent)


# Global registry
capability_registry = CapabilityRegistry()
