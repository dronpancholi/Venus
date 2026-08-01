"""
CORE-13: Studio Backend

Prepare backend APIs for Venus Studio.
Workspace, Projects, Compiler, Validation, Knowledge Graph,
Memory, Runtime, Search, Ontology, Capability Explorer,
Prompt Explorer, Plugin Explorer
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from genesis.compiler.compiler import Compiler
from genesis.validation.engine import ValidationEngine
from genesis.graph.engine import KnowledgeGraphEngine
from genesis.capability.registry import capability_registry
from genesis.core.types import type_registry
from genesis.utils.identity import generate_id


class Workspace:
    """A user workspace with projects."""

    def __init__(self, name: str, root: str | Path):
        self.name = name
        self.root = Path(root)
        self.projects: dict[str, dict[str, Any]] = {}
        self.created_at = datetime.now(timezone.utc).isoformat()

    def create_project(self, name: str, description: str = "") -> dict[str, Any]:
        project = {
            "id": generate_id("proj", 12),
            "name": name,
            "description": description,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "artifact_count": 0,
        }
        self.projects[name] = project
        return project

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "root": str(self.root),
            "projects": self.projects,
        }


class StudioBackend:
    """Backend APIs for Venus Studio."""

    def __init__(self):
        self.compiler = Compiler()
        self.validator = ValidationEngine()
        self.graph = KnowledgeGraphEngine()
        self.workspace = Workspace("default", Path("."))
        self._enabled = True

    # Workspace APIs
    def get_workspace(self) -> dict[str, Any]:
        return self.workspace.to_dict()

    def create_project(self, name: str, description: str = "") -> dict[str, Any]:
        return self.workspace.create_project(name, description)

    def list_projects(self) -> list[dict[str, Any]]:
        return list(self.workspace.projects.values())

    # Compiler APIs
    def compile_file(self, path: str) -> dict[str, Any]:
        cu = self.compiler.compile(path)
        return {
            "source": path,
            "ast_nodes": len(cu.ast.nodes),
            "dependencies": len(cu.dependencies.edges),
            "passes": cu.passes_applied,
        }

    # Validation APIs
    def validate_file(self, path: str) -> dict[str, Any]:
        results = self.validator.validate_path(path)
        return self.validator.summary(results)

    # Graph APIs
    def get_graph_summary(self) -> dict[str, Any]:
        return self.graph.summary()

    def query_graph(self, node_type: str | None = None, label: str = "") -> list[dict[str, Any]]:
        nodes = self.graph.find_nodes(node_type=node_type, label_contains=label)
        return [n.to_dict() for n in nodes]

    # Ontology APIs
    def get_ontology_types(self) -> list[dict[str, Any]]:
        return [t.to_dict() for t in type_registry.all_types()]

    def get_ontology_type(self, name: str) -> dict[str, Any] | None:
        t = type_registry.get(name)
        return t.to_dict() if t else None

    # Capability APIs
    def get_capabilities(self) -> list[dict[str, Any]]:
        return [c.to_dict() for c in capability_registry.all()]

    def get_capability(self, name: str) -> dict[str, Any] | None:
        c = capability_registry.get(name)
        return c.to_dict() if c else None

    # Explorer APIs
    def explore_prompts(self) -> list[dict[str, Any]]:
        return self.graph.find_nodes(node_type="prompt")

    def explore_plugins(self) -> list[dict[str, Any]]:
        return self.graph.find_nodes(node_type="plugin")

    # Search
    def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        nodes = self.graph.find_nodes(label_contains=query)[:max_results]
        return [n.to_dict() for n in nodes]

    # Health
    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._enabled else "disabled",
            "compiler": "ready",
            "validator": f"{len(self.validator.all_validators())} validators",
            "graph": f"{self.graph.summary()['total_nodes']} nodes",
            "ontology": f"{len(type_registry.all_types())} types",
            "capabilities": f"{len(capability_registry.all())} capabilities",
        }
