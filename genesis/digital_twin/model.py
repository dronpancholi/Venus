"""
Repository Digital Twin — primary representation of the entire codebase.

Every node carries 14 dimensions of metadata:
  syntax, semantics, ownership, contracts, dependencies,
  lifecycle, persistence, runtime, architectural_role,
  spec_mapping, tests, evolution, confidence, cross_refs

Never reason directly over source code. Reason over the Digital Twin.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class TwinNode:
    id: str
    kind: str

    # ——— identity ———
    label: str = ""
    module: str = ""
    file_path: str = ""

    # 1. syntax
    source_text: str | None = None
    ast_json: dict[str, Any] | None = None
    first_line: int = 0
    last_line: int = 0

    # 2. semantics
    docstring: str | None = None
    purpose: str | None = None
    tags: list[str] = field(default_factory=list)

    # 3. ownership
    subsystem: str | None = None
    layer: int | None = None
    layer_name: str | None = None
    owner: str | None = None

    # 4. contracts
    interfaces: list[str] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)
    base_classes: list[str] = field(default_factory=list)
    abstract_methods: list[str] = field(default_factory=list)

    # 5. dependencies
    imports: list[str] = field(default_factory=list)
    imports_from: list[dict[str, Any]] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    depended_by: list[str] = field(default_factory=list)
    dependency_kinds: dict[str, str] = field(default_factory=dict)

    # 6. lifecycle
    created_at: str | None = None
    modified_at: str | None = None
    version: str | None = None
    change_frequency: int = 0

    # 7. persistence
    persistence_kind: str | None = None
    store_name: str | None = None
    store_table: str | None = None

    # 8. runtime
    service_name: str | None = None
    event_emissions: list[str] = field(default_factory=list)
    event_subscriptions: list[str] = field(default_factory=list)

    # 9. architectural role
    role: str | None = None
    pattern: str | None = None
    documented: bool = False
    verified: bool = False

    # 10. spec mapping
    spec_refs: list[str] = field(default_factory=list)
    adr_refs: list[str] = field(default_factory=list)

    # 11. tests
    test_file: str | None = None
    test_count: int = 0
    test_coverage: float | None = None

    # 12. evolution
    version_history: list[dict[str, Any]] = field(default_factory=list)
    refactor_count: int = 0

    # 13. confidence
    confidence: float = 1.0
    confidence_breakdown: dict[str, float] = field(default_factory=dict)

    # 14. cross_refs
    cross_refs: dict[str, list[str]] = field(default_factory=dict)

    # ——— graph edges ———
    edges_out: dict[str, list[tuple[str, str]]] = field(default_factory=dict)

    def add_edge(self, target_id: str, kind: str, label: str = ""):
        self.edges_out.setdefault(kind, []).append((target_id, label))

    def add_cross_ref(self, namespace: str, ref_id: str):
        self.cross_refs.setdefault(namespace, []).append(ref_id)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("ast_json", None)
        d.pop("source_text", None)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TwinNode:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def __hash__(self):
        return hash(self.id)


class DigitalTwin:
    """Complete repository digital twin.

    Primary representation. All analysis, reasoning, and evolution
    operates on this object, never on raw source code directly.
    """

    def __init__(self):
        self._nodes: dict[str, TwinNode] = {}
        self._edges_by_kind: dict[str, list[tuple[str, str, str]]] = {}
        self._indexes: dict[str, dict[str, list[str]]] = {}
        self.metadata: dict[str, Any] = {}
        self.built_at: float = 0.0
        self.metrics: dict[str, float] = {}

    # ——— node management ———

    def _update_index(self, node: TwinNode):
        for idx_name in ("kind", "layer_name", "role", "service_name", "subsystem", "layer"):
            val = getattr(node, idx_name, None)
            if val is not None:
                self._indexes.setdefault(idx_name, {}).setdefault(str(val), []).append(node.id)

    def add_node(self, node: TwinNode) -> TwinNode:
        existing = self._nodes.get(node.id)
        if existing:
            if existing.confidence > node.confidence:
                return existing
            old_kind = existing.kind
            if existing.kind == "class" and node.kind not in ("class", ""):
                existing.kind = node.kind
            for field_name in ("persistence_kind", "store_name", "role", "service_name"):
                new_val = getattr(node, field_name, None)
                if new_val is not None and not getattr(existing, field_name, None):
                    setattr(existing, field_name, new_val)
            if node.purpose and not existing.purpose:
                existing.purpose = node.purpose
            if node.tags:
                existing.tags = list(set(existing.tags + node.tags))
            if node.spec_refs:
                existing.spec_refs = list(set(existing.spec_refs + node.spec_refs))
            if node.adr_refs:
                existing.adr_refs = list(set(existing.adr_refs + node.adr_refs))
            if existing.kind != old_kind:
                self._indexes.get("kind", {}).get(old_kind, []).remove(node.id)
                self._update_index(existing)
            self._nodes[node.id] = existing
            return existing
        self._nodes[node.id] = node
        self._update_index(node)
        return node

    def get_node(self, node_id: str) -> TwinNode | None:
        return self._nodes.get(node_id)

    def find_nodes(self, kind: str | None = None, **attrs) -> list[TwinNode]:
        if kind:
            ids = self._indexes.get("kind", {}).get(kind, [])
            candidates = [self._nodes[i] for i in ids if i in self._nodes]
        else:
            candidates = list(self._nodes.values())

        if not attrs:
            return candidates

        result = []
        for n in candidates:
            match = True
            for k, v in attrs.items():
                if getattr(n, k, None) != v:
                    match = False
                    break
            if match:
                result.append(n)
        return result

    @property
    def nodes(self) -> list[TwinNode]:
        return list(self._nodes.values())

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    def count_by_kind(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for n in self._nodes.values():
            counts[n.kind] = counts.get(n.kind, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    # ——— edge management ———

    def add_edge(self, source_id: str, target_id: str, kind: str, label: str = ""):
        self._edges_by_kind.setdefault(kind, []).append((source_id, target_id, label))
        src = self._nodes.get(source_id)
        if src:
            src.add_edge(target_id, kind, label)

    def find_edges(self, kind: str | None = None) -> list[tuple[str, str, str]]:
        if kind:
            return self._edges_by_kind.get(kind, [])
        all_edges: list[tuple[str, str, str]] = []
        for edges in self._edges_by_kind.values():
            all_edges.extend(edges)
        return all_edges

    def edges_from(self, node_id: str) -> list[tuple[str, str, str]]:
        node = self._nodes.get(node_id)
        if not node:
            return []
        result = []
        for kind, targets in node.edges_out.items():
            for tid, label in targets:
                result.append((node_id, tid, kind, label))
        return result

    @property
    def edge_count(self) -> int:
        return sum(len(e) for e in self._edges_by_kind.values())

    # ——— serialization ———

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata,
            "built_at": self.built_at,
            "nodes": {nid: node.to_dict() for nid, node in self._nodes.items()},
            "edges": self._edges_by_kind,
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DigitalTwin:
        twin = cls()
        twin.metadata = d.get("metadata", {})
        twin.built_at = d.get("built_at", 0.0)
        twin.metrics = d.get("metrics", {})
        for nid, nd in d.get("nodes", {}).items():
            twin.add_node(TwinNode.from_dict(nd))
        for kind, edges in d.get("edges", {}).items():
            for sid, tid, label in edges:
                twin.add_edge(sid, tid, kind, label)
        return twin

    def save(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> DigitalTwin:
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text())
        return cls.from_dict(data)

    # ——— summary ———

    def summary(self) -> dict[str, Any]:
        kinds = self.count_by_kind()
        return {
            "total_nodes": self.node_count,
            "total_edges": self.edge_count,
            "node_kinds": kinds,
            "edge_kinds": list(self._edges_by_kind.keys()),
            "metrics": self.metrics,
        }
