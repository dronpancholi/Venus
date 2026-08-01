"""
Observatory Graph — cross-repository knowledge graph.

Merges USIR graphs from multiple repositories into a unified graph
that enables cross-repository queries:
  - Which repos use this protocol/interface/pattern?
  - How does architectural entropy compare across repos?
  - What are the common coupling patterns across the observed universe?
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from genesis.usir import USIRGraph


@dataclass
class ObservedNode:
    """A node from any repository in the observatory."""
    id: str
    kind: str
    name: str
    repo_id: str
    language: str = ""
    file_path: str = ""
    line_start: int = 0
    complexity: float = 0.0
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossRepoEdge:
    """An edge connecting nodes across repositories."""
    source_node: str
    target_node: str
    source_repo: str
    target_repo: str
    kind: str  # "import", "protocol_match", "pattern_match", "interface_match"
    weight: float = 1.0
    evidence: str = ""


@dataclass
class ObservatorySnapshot:
    """A snapshot of the observatory at a point in time."""
    timestamp: float
    repo_count: int
    node_count: int
    edge_count: int
    cross_repo_edges: int
    languages: dict[str, int]
    ris_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservatoryGraph:
    """Cross-repository knowledge graph for the Global Repository Observatory."""

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "observatory_graph"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._node_map: dict[str, ObservedNode] = {}
        self.edges: list[CrossRepoEdge] = []
        self.repo_index: dict[str, list[str]] = defaultdict(list)
        self.language_index: defaultdict[str, list[str]] = defaultdict(list)
        self.kind_index: defaultdict[str, list[str]] = defaultdict(list)
        self.snapshots: list[ObservatorySnapshot] = []

    # — Mutation —

    def add_repo_graph(self, repo_id: str, language: str, usir: USIRGraph):
        """Merge a USIR graph into the observatory."""
        added = 0
        for node in usir.nodes:
            on = ObservedNode(
                id=f"{repo_id}::{node.id}",
                kind=node.kind.name.lower() if hasattr(node.kind, 'name') else str(node.kind).lower(),
                name=node.name,
                repo_id=repo_id,
                language=language,
                file_path=node.source_file or "",
                line_start=node.source_line or 0,
                complexity=getattr(node, 'complexity', 0.0) or 0.0,
                dependencies=[d.target_id for d in node.dependencies] if hasattr(node, 'dependencies') else [],
            )
            self._node_map[on.id] = on
            self.repo_index[repo_id].append(on.id)
            self.language_index[language].append(on.id)
            self.kind_index[on.kind].append(on.id)
            added += 1

        for kind, edge_list in usir._edges.items():
            for triple in edge_list:
                u, v = triple[0], triple[1]
            src = f"{repo_id}::{u}"
            tgt = f"{repo_id}::{v}"
            if src in self._node_map and tgt in self._node_map:
                self.edges.append(CrossRepoEdge(
                    source_node=src, target_node=tgt,
                    source_repo=repo_id, target_repo=repo_id,
                    kind="dependency", weight=1.0,
                ))

        return added

    def add_cross_repo_edge(self, source_node: str, target_node: str,
                            kind: str, weight: float = 1.0, evidence: str = ""):
        src_repo = source_node.split("::", 1)[0] if "::" in source_node else ""
        tgt_repo = target_node.split("::", 1)[0] if "::" in target_node else ""
        self.edges.append(CrossRepoEdge(
            source_node=source_node, target_node=target_node,
            source_repo=src_repo, target_repo=tgt_repo,
            kind=kind, weight=weight, evidence=evidence,
        ))

    # — Query —

    def find_by_name(self, name: str, kind: str | None = None) -> list[ObservedNode]:
        results = []
        for n in self._node_map.values():
            if n.name == name and (kind is None or n.kind == kind):
                results.append(n)
        return results

    def find_by_kind(self, kind: str) -> list[ObservedNode]:
        return [self._node_map[nid] for nid in self.kind_index.get(kind, [])]

    def find_by_repo(self, repo_id: str) -> list[ObservedNode]:
        return [self._node_map[nid] for nid in self.repo_index.get(repo_id, [])]

    def find_by_language(self, language: str) -> list[ObservedNode]:
        return [self._node_map[nid] for nid in self.language_index.get(language, [])]

    def find_similar(self, node_id: str, threshold: float = 0.5) -> list[tuple[str, float]]:
        """Find similar nodes across repos based on name and kind."""
        node = self._node_map.get(node_id)
        if not node:
            return []
        similar = []
        for other_id, other in self._node_map.items():
            if other_id == node_id:
                continue
            if other.repo_id == node.repo_id:
                continue
            score = 0.0
            if other.name == node.name:
                score += 0.6
            if other.kind == node.kind:
                score += 0.3
            if other.name.lower() == node.name.lower():
                score += 0.1
            if score >= threshold:
                similar.append((other_id, score))
        return sorted(similar, key=lambda x: -x[1])

    def common_patterns(self) -> dict[str, list[dict[str, Any]]]:
        """Find architectural patterns that appear across multiple repos."""
        # — name+kind combos that appear in >1 repo —
        pattern_counts: dict[tuple[str, str], set[str]] = defaultdict(set)
        for n in self._node_map.values():
            pattern_counts[(n.name, n.kind)].add(n.repo_id)

        patterns = []
        for (name, kind), repos in sorted(pattern_counts.items(), key=lambda x: -len(x[1])):
            if len(repos) >= 2:
                patterns.append({
                    "name": name,
                    "kind": kind,
                    "repos": len(repos),
                    "repo_list": sorted(repos),
                })
        return {"patterns": patterns, "total": len(patterns)}

    def cross_repo_dependencies(self, min_weight: float = 0.0) -> list[CrossRepoEdge]:
        return [
            e for e in self.edges
            if e.source_repo != e.target_repo and e.weight >= min_weight
        ]

    def summary(self) -> dict[str, Any]:
        languages = defaultdict(int)
        for lang, nodes in self.language_index.items():
            languages[lang] = len(nodes)

        cross = len(self.cross_repo_dependencies())

        return {
            "repositories": len(self.repo_index),
            "nodes": len(self._node_map),
            "edges": len(self.edges),
            "cross_repo_edges": cross,
            "languages": dict(languages),
            "patterns_available": len(self.common_patterns()["patterns"]),
        }

    # — Persistence —

    def save(self, name: str = "latest"):
        path = self.storage_path / f"{name}.json"
        data = {
            "nodes": {
                nid: {
                    "id": n.id,
                    "kind": n.kind,
                    "name": n.name,
                    "repo_id": n.repo_id,
                    "language": n.language,
                    "file_path": n.file_path,
                    "line_start": n.line_start,
                    "complexity": n.complexity,
                    "dependencies": n.dependencies,
                }
                for nid, n in self._node_map.items()
            },
            "edges": [
                {
                    "source_node": e.source_node,
                    "target_node": e.target_node,
                    "source_repo": e.source_repo,
                    "target_repo": e.target_repo,
                    "kind": e.kind,
                    "weight": e.weight,
                    "evidence": e.evidence,
                }
                for e in self.edges
            ],
        }
        path.write_text(json.dumps(data, indent=2))

    def load(self, name: str = "latest"):
        path = self.storage_path / f"{name}.json"
        if not path.exists():
            return
        data = json.loads(path.read_text())
        self._node_map.clear()
        self.edges.clear()
        self.repo_index.clear()
        self.language_index.clear()
        self.kind_index.clear()

        for nid, ndata in data.get("nodes", {}).items():
            n = ObservedNode(**ndata)
            self._node_map[nid] = n
            self.repo_index[n.repo_id].append(nid)
            self.language_index[n.language].append(nid)
            self.kind_index[n.kind].append(nid)

        for edata in data.get("edges", []):
            self.edges.append(CrossRepoEdge(**edata))

    def snapshot(self, ris_score: float = 0.0) -> ObservatorySnapshot:
        s = ObservatorySnapshot(
            timestamp=time.time(),
            repo_count=len(self.repo_index),
            node_count=len(self._node_map),
            edge_count=len(self.edges),
            cross_repo_edges=len(self.cross_repo_dependencies()),
            languages={k: len(v) for k, v in self.language_index.items()},
            ris_score=ris_score,
        )
        self.snapshots.append(s)
        return s
