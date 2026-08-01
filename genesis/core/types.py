"""
CORE-05: Type System

Semantic type registry for classifying all Venus entities.
"""

import json
from pathlib import Path
from typing import Any


class SemanticType:
    """A type in the Venus ontology."""

    def __init__(
        self,
        name: str,
        parent: str | None = None,
        description: str = "",
        abstract: bool = False,
    ):
        self.name = name
        self.parent = parent
        self.description = description
        self.abstract = abstract
        self.constraints: list[TypeConstraint] = []
        self.required_fields: list[str] = []
        self.allowed_edges: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "parent": self.parent,
            "description": self.description,
            "abstract": self.abstract,
            "constraints": [c.to_dict() for c in self.constraints],
            "required_fields": list(self.required_fields),
            "allowed_edges": list(self.allowed_edges),
        }


class TypeConstraint:
    """Constraint on a type definition."""

    def __init__(self, field: str, rule: str, value: Any = None):
        self.field = field
        self.rule = rule
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        return {"field": self.field, "rule": self.rule, "value": self.value}


class TypeRegistry:
    """Registry of all semantic types with inheritance resolution."""

    def __init__(self):
        self._types: dict[str, SemanticType] = {}
        self._load_builtins()

    def _load_builtins(self):
        builtins = [
            SemanticType("entity", None, "Root of all types", abstract=True),
            SemanticType("base_entity", "entity", "Concrete base", abstract=True),
            SemanticType("capability", "base_entity", "Platform capability"),
            SemanticType("artifact", "base_entity", "Produced/consumed artifact"),
            SemanticType("operating_system", "artifact", "A Venus OS"),
            SemanticType("part", "artifact", "OS component part"),
            SemanticType("engine", "artifact", "Execution engine"),
            SemanticType("template", "artifact", "Documentation template"),
            SemanticType("schema", "artifact", "JSON Schema definition"),
            SemanticType("workflow", "artifact", "Executable workflow"),
            SemanticType("prompt", "artifact", "LLM prompt template"),
            SemanticType("tool", "artifact", "Executable tool"),
            SemanticType("agent", "artifact", "Autonomous agent"),
            SemanticType("runtime", "artifact", "Runtime component"),
            SemanticType("graph", "artifact", "Graph definition"),
            SemanticType("compiler_pass", "artifact", "Compiler optimization pass"),
            SemanticType("validator", "artifact", "Validation plugin"),
            SemanticType("certificate", "artifact", "Certification record"),
            SemanticType("memory_object", "artifact", "Memory store entry"),
            SemanticType("project", "artifact", "Project definition"),
            SemanticType("task", "artifact", "Workflow task"),
            SemanticType("knowledge_node", "artifact", "Graph knowledge node"),
            SemanticType("plugin", "artifact", "Installable plugin"),
            SemanticType("policy", "artifact", "Policy definition"),
            SemanticType("interface", "artifact", "API interface definition"),
            SemanticType("ontology_type", "artifact", "Ontology type definition"),
            SemanticType("decision", "artifact", "Architectural decision"),
            SemanticType("configuration", "artifact", "Configuration document"),
        ]
        for t in builtins:
            self.register(t)

    def register(self, stype: SemanticType):
        self._types[stype.name] = stype

    def get(self, name: str) -> SemanticType | None:
        return self._types.get(name)

    def resolve_hierarchy(self, name: str) -> list[SemanticType]:
        """Resolve full inheritance chain from type to root."""
        chain = []
        current = name
        while current and current in self._types:
            chain.append(self._types[current])
            current = self._types[current].parent
        return chain

    def is_subtype_of(self, child: str, parent: str) -> bool:
        ancestors = {t.name for t in self.resolve_hierarchy(child)}
        return parent in ancestors

    def all_types(self) -> list[SemanticType]:
        return list(self._types.values())

    def load_from_file(self, path: str | Path):
        data = json.loads(Path(path).read_text())
        for entry in data:
            st = SemanticType(
                name=entry["name"],
                parent=entry.get("parent"),
                description=entry.get("description", ""),
                abstract=entry.get("abstract", False),
            )
            st.required_fields = entry.get("required_fields", [])
            st.allowed_edges = entry.get("allowed_edges", [])
            self.register(st)

    def to_dict(self) -> dict[str, Any]:
        return {name: t.to_dict() for name, t in self._types.items()}


# Global registry
type_registry = TypeRegistry()
