"""
USIR — Universal Software Intermediate Representation.

A language-independent canonical representation for all software constructs.
Any language → AST → USIR → DigitalTwin enrichment.

Capable of representing:
  modules, packages, classes, interfaces, traits, protocols,
  functions, methods, fields, annotations, decorators, imports,
  dependencies, inheritance, generic types, async execution,
  events, data flow, control flow
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class USIRKind(Enum):
    MODULE = auto()
    PACKAGE = auto()
    IMPORT = auto()
    CLASS = auto()
    INTERFACE = auto()
    TRAIT = auto()
    PROTOCOL = auto()
    STRUCT = auto()
    ENUM = auto()
    UNION = auto()
    RECORD = auto()
    FUNCTION = auto()
    METHOD = auto()
    CONSTRUCTOR = auto()
    LAMBDA = auto()
    FIELD = auto()
    PROPERTY = auto()
    CONSTANT = auto()
    ENUM_VARIANT = auto()
    PARAMETER = auto()
    TYPE_PARAMETER = auto()
    TYPE_CONSTRAINT = auto()
    ANNOTATION = auto()
    DECORATOR = auto()
    INHERITANCE = auto()
    IMPLEMENTS = auto()
    MIXIN = auto()
    VARIABLE = auto()
    EXPRESSION = auto()
    STATEMENT = auto()
    CONTROL_FLOW = auto()
    LOOP = auto()
    MATCH = auto()
    ASYNC = auto()
    AWAIT = auto()
    EVENT_EMIT = auto()
    EVENT_HANDLE = auto()
    PROMISE = auto()
    FUTURE = auto()
    OBSERVABLE = auto()
    ERROR = auto()
    RESULT = auto()
    OPTION = auto()
    NAMESPACE = auto()
    ALIAS = auto()
    MACRO = auto()
    ATTRIBUTE = auto()
    CONFIG = auto()
    TEST = auto()
    DOC = auto()


VISIBILITY_PUBLIC = "public"
VISIBILITY_PRIVATE = "private"
VISIBILITY_PROTECTED = "protected"
VISIBILITY_INTERNAL = "internal"
VISIBILITY_PACKAGE = "package"


class Mutability(Enum):
    IMMUTABLE = auto()
    MUTABLE = auto()
    CONST = auto()


@dataclass
class USIRNode:
    """A single node in the USIR graph."""

    id: str
    kind: USIRKind
    name: str = ""
    qualified_name: str = ""

    # — language metadata —
    language: str = ""
    source_file: str = ""
    source_line: int = 0
    source_column: int = 0

    # — type system —
    type_ref: str | None = None
    type_parameters: list[str] = field(default_factory=list)
    type_constraints: list[dict[str, str]] = field(default_factory=list)
    return_type: str | None = None
    is_async: bool = False
    is_generator: bool = False

    # — visibility & mutability —
    visibility: str = VISIBILITY_PUBLIC
    mutability: Mutability = Mutability.IMMUTABLE
    is_static: bool = False
    is_abstract: bool = False
    is_virtual: bool = False
    is_override: bool = False
    is_final: bool = False

    # — inheritance —
    base_types: list[str] = field(default_factory=list)
    implemented_interfaces: list[str] = field(default_factory=list)
    mixed_in_traits: list[str] = field(default_factory=list)

    # — annotations —
    annotations: list[dict[str, Any]] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)

    # — children —
    children: list[str] = field(default_factory=list)

    # — dependencies —
    imports: list[dict[str, str]] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    depended_by: list[str] = field(default_factory=list)

    # — events —
    events_emitted: list[str] = field(default_factory=list)
    events_handled: list[str] = field(default_factory=list)

    # — metadata —
    docstring: str | None = None
    complexity: int = 0
    lines_of_code: int = 0

    def to_dict(self) -> dict[str, Any]:
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Enum):
                d[k] = v.name.lower()
            elif k == "children" and not v:
                d[k] = []
            else:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> USIRNode:
        if "kind" in d and isinstance(d["kind"], str):
            d["kind"] = USIRKind[d["kind"].upper()]
        if "mutability" in d and isinstance(d["mutability"], str):
            d["mutability"] = Mutability[d["mutability"].upper()]
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def __hash__(self):
        return hash(self.id)


class USIRGraph:
    """A complete USIR graph — the language-independent software representation."""

    def __init__(self):
        self._nodes: dict[str, USIRNode] = {}
        self._edges: dict[str, list[tuple[str, str]]] = {}

    def add_node(self, node: USIRNode) -> USIRNode:
        self._nodes[node.id] = node
        return node

    def add_edge(self, source: str, target: str, kind: str, label: str = ""):
        if source not in self._nodes and target not in self._nodes:
            return
        self._edges.setdefault(kind, []).append((source, target, label))

    def get_node(self, node_id: str) -> USIRNode | None:
        return self._nodes.get(node_id)

    def find_nodes(self, kind: USIRKind | None = None, **attrs) -> list[USIRNode]:
        candidates = list(self._nodes.values())
        if kind:
            candidates = [n for n in candidates if n.kind == kind]
        for k, v in attrs.items():
            candidates = [n for n in candidates if getattr(n, k, None) == v]
        return candidates

    @property
    def nodes(self) -> list[USIRNode]:
        return list(self._nodes.values())

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    def count_by_kind(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for n in self._nodes.values():
            kind = n.kind.name.lower()
            counts[kind] = counts.get(kind, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {nid: n.to_dict() for nid, n in self._nodes.items()},
            "edges": {k: v for k, v in self._edges.items()},
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> USIRGraph:
        g = cls()
        for nid, nd in d.get("nodes", {}).items():
            g.add_node(USIRNode.from_dict(nd))
        for kind, edges in d.get("edges", {}).items():
            for src, tgt, lbl in edges:
                g.add_edge(src, tgt, kind, lbl)
        return g
