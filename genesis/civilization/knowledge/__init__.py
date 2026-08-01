"""
Global Scientific Knowledge Base (Program D) — persistent, queryable corpus.

Stores papers, findings, experiments, datasets, reviews, citations, lineage.
Integrates with Knowledge Graph for graph queries and Memory for fast retrieval.
"""

from __future__ import annotations

import gzip
import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


# ── Knowledge Artifact Types ──


@dataclass
class KnowledgeAuthor:
    id: str = ""
    name: str = ""
    department: str = ""
    affiliations: list[str] = field(default_factory=list)
    orcid: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> KnowledgeAuthor:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class KnowledgeArtifact:
    """Base artifact stored in the knowledge base."""
    id: str = ""
    artifact_type: str = ""  # paper, finding, experiment, dataset, review, specification, benchmark
    title: str = ""
    description: str = ""
    authors: list[KnowledgeAuthor] = field(default_factory=list)
    domain: str = ""
    tags: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    content: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    quality_score: float = 0.0
    novelty_score: float = 0.0
    reproducibility_score: float = 0.0
    status: str = "draft"
    version: int = 1
    created_at: float = 0.0
    updated_at: float = 0.0
    source: str = ""  # genesis, external, literature, experiment
    lineage: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "description": self.description,
            "authors": [a.to_dict() for a in self.authors],
            "domain": self.domain,
            "tags": self.tags,
            "references": self.references,
            "citation_count": len(self.citations),
            "evidence": self.evidence[:5],
            "confidence": self.confidence,
            "quality_score": self.quality_score,
            "novelty_score": self.novelty_score,
            "reproducibility_score": self.reproducibility_score,
            "status": self.status,
            "version": self.version,
            "created_at": self.created_at,
            "source": self.source,
            "lineage": self.lineage[:10],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> KnowledgeArtifact:
        authors = [KnowledgeAuthor(**a) if isinstance(a, dict) else a for a in d.get("authors", [])]
        return cls(
            id=d["id"],
            artifact_type=d.get("artifact_type", "paper"),
            title=d.get("title", ""),
            description=d.get("description", ""),
            authors=authors,
            domain=d.get("domain", ""),
            tags=d.get("tags", []),
            references=d.get("references", []),
            citations=d.get("citations", []),
            evidence=d.get("evidence", []),
            content=d.get("content", {}),
            confidence=d.get("confidence", 0.0),
            quality_score=d.get("quality_score", 0.0),
            novelty_score=d.get("novelty_score", 0.0),
            reproducibility_score=d.get("reproducibility_score", 0.0),
            status=d.get("status", "draft"),
            version=d.get("version", 1),
            created_at=d.get("created_at", 0.0),
            updated_at=d.get("updated_at", 0.0),
            source=d.get("source", ""),
            lineage=d.get("lineage", []),
            provenance=d.get("provenance", {}),
        )


# ── Lineage Graph ──


@dataclass
class LineageEdge:
    source_id: str = ""
    target_id: str = ""
    relation: str = ""  # derives_from, extends, contradicts, replicates, supersedes
    weight: float = 1.0
    timestamp: float = 0.0
    evidence: str = ""


class LineageGraph:
    """Tracks the intellectual lineage of all knowledge artifacts."""

    def __init__(self):
        self.edges: list[LineageEdge] = []

    def add_edge(self, source: str, target: str, relation: str,
                 weight: float = 1.0, evidence: str = ""):
        self.edges.append(LineageEdge(
            source_id=source, target_id=target, relation=relation,
            weight=weight, timestamp=time.time(), evidence=evidence,
        ))

    def ancestors(self, artifact_id: str) -> list[LineageEdge]:
        return [e for e in self.edges if e.target_id == artifact_id]

    def descendants(self, artifact_id: str) -> list[LineageEdge]:
        return [e for e in self.edges if e.source_id == artifact_id]

    def timeline(self, artifact_id: str) -> list[LineageEdge]:
        visited: set[str] = set()
        result: list[LineageEdge] = []
        queue = [artifact_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for edge in self.ancestors(current):
                result.append(edge)
                queue.append(edge.source_id)
        result.sort(key=lambda e: e.timestamp)
        return result

    def evolution_path(self, from_id: str, to_id: str) -> list[LineageEdge]:
        """Find the path of intellectual lineage between two artifacts."""
        parent_map: dict[str, LineageEdge] = {}
        visited: set[str] = set()
        queue = [from_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for edge in self.descendants(current):
                parent_map[edge.target_id] = edge
                queue.append(edge.target_id)
        path: list[LineageEdge] = []
        current = to_id
        while current in parent_map and current != from_id:
            edge = parent_map[current]
            path.append(edge)
            current = edge.source_id
        path.reverse()
        return path

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_edges": len(self.edges),
            "relations": dict(defaultdict(int, {
                e.relation: sum(1 for x in self.edges if x.relation == e.relation)
                for e in self.edges
            })),
        }


# ── Knowledge Base ──


class KnowledgeBase:
    """
    Persistent, queryable scientific corpus (Program D).

    Stores all artifacts (papers, findings, experiments, datasets, reviews)
    with full lineage tracking, citation graph, and multi-dimensional search.

    Integrates with:
      - PersistentGraphDB for graph queries
      - MemoryManager for fast retrieval
      - Runtime for automatic indexing
    """

    def __init__(self, storage_path: str | Path = "",
                 graph_db=None, memory_manager=None):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "knowledge"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.artifacts: dict[str, KnowledgeArtifact] = {}
        self.lineage = LineageGraph()
        self.graph_db = graph_db
        self.memory = memory_manager

        self._domain_index: dict[str, list[str]] = defaultdict(list)
        self._type_index: dict[str, list[str]] = defaultdict(list)
        self._tag_index: dict[str, list[str]] = defaultdict(list)
        self._author_index: dict[str, list[str]] = defaultdict(list)
        self._status_index: dict[str, list[str]] = defaultdict(list)

        self._load()

    def store(self, artifact: KnowledgeArtifact) -> str:
        if not artifact.id:
            artifact.id = generate_id("ka", 16)
        if not artifact.created_at:
            artifact.created_at = time.time()
        artifact.updated_at = time.time()

        self.artifacts[artifact.id] = artifact
        self._index(artifact)
        self._sync_graph(artifact)
        self._sync_memory(artifact)
        self._save()
        return artifact.id

    def get(self, artifact_id: str) -> KnowledgeArtifact | None:
        return self.artifacts.get(artifact_id)

    def delete(self, artifact_id: str):
        artifact = self.artifacts.pop(artifact_id, None)
        if artifact:
            self._deindex(artifact)
            self._save()

    def search(self, query: str = "", domain: str = "",
               artifact_type: str = "", tags: list[str] | None = None,
               author: str = "", status: str = "",
               min_confidence: float = 0.0, max_results: int = 100,
               sort_by: str = "-created_at") -> list[KnowledgeArtifact]:
        ids = self._search_ids(query, domain, artifact_type, tags,
                                author, status, min_confidence)
        results = [self.artifacts[i] for i in ids if i in self.artifacts]
        results = self._sort(results, sort_by)
        return results[:max_results]

    def _search_ids(self, query: str = "", domain: str = "",
                    artifact_type: str = "", tags: list[str] | None = None,
                    author: str = "", status: str = "",
                    min_confidence: float = 0.0) -> set[str]:
        result: set[str] | None = None
        if domain:
            result = self._and(result, set(self._domain_index.get(domain, [])))
        if artifact_type:
            result = self._and(result, set(self._type_index.get(artifact_type, [])))
        if tags:
            for tag in tags:
                result = self._and(result, set(self._tag_index.get(tag, [])))
        if author:
            result = self._and(result, set(self._author_index.get(author.lower(), [])))
        if status:
            result = self._and(result, set(self._status_index.get(status, [])))
        if result is None:
            result = set(self.artifacts.keys())
        if query:
            ql = query.lower()
            result = {i for i in result
                      if i in self.artifacts and
                      (ql in self.artifacts[i].title.lower() or
                       ql in self.artifacts[i].description.lower() or
                       any(ql in t.lower() for t in self.artifacts[i].tags))}
        if min_confidence > 0:
            result = {i for i in result
                      if i in self.artifacts and
                      self.artifacts[i].confidence >= min_confidence}
        return result

    def _and(self, a: set[str] | None, b: set[str]) -> set[str]:
        return a & b if a is not None else b

    def _sort(self, results: list[KnowledgeArtifact],
              sort_by: str) -> list[KnowledgeArtifact]:
        reverse = sort_by.startswith("-")
        key = sort_by.lstrip("-")
        def sort_key(a: KnowledgeArtifact) -> float:
            val = getattr(a, key, 0)
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str):
                return -float(time.time()) if val == "draft" else float(time.time())
            return float(time.time())
        return sorted(results, key=sort_key, reverse=reverse)

    def add_citation(self, source_id: str, target_id: str):
        source = self.artifacts.get(source_id)
        target = self.artifacts.get(target_id)
        if source and target:
            if target_id not in source.citations:
                source.citations.append(target_id)
            self.lineage.add_edge(source_id, target_id, "cites")
            self._save()

    def add_lineage(self, source_id: str, target_id: str, relation: str,
                    evidence: str = ""):
        child = self.artifacts.get(source_id)
        parent = self.artifacts.get(target_id)
        if parent and child:
            self.lineage.add_edge(parent.id, child.id, relation, evidence=evidence)
            if relation == "derives_from":
                child.lineage.append(parent.id)
            self._save()

    def by_author(self, author_name: str) -> list[KnowledgeArtifact]:
        ids = self._author_index.get(author_name.lower(), [])
        return [self.artifacts[i] for i in ids if i in self.artifacts]

    def by_domain(self, domain: str) -> list[KnowledgeArtifact]:
        ids = self._domain_index.get(domain, [])
        return [self.artifacts[i] for i in ids if i in self.artifacts]

    def by_type(self, artifact_type: str) -> list[KnowledgeArtifact]:
        ids = self._type_index.get(artifact_type, [])
        return [self.artifacts[i] for i in ids if i in self.artifacts]

    def by_tag(self, tag: str) -> list[KnowledgeArtifact]:
        ids = self._tag_index.get(tag, [])
        return [self.artifacts[i] for i in ids if i in self.artifacts]

    def most_cited(self, n: int = 10) -> list[tuple[str, str, int]]:
        cited_by: dict[str, int] = {}
        for a in self.artifacts.values():
            for target_id in a.citations:
                cited_by[target_id] = cited_by.get(target_id, 0) + 1
        result = [(aid, self.artifacts[aid].title, cited_by.get(aid, 0))
                  for aid in self.artifacts]
        return sorted(result, key=lambda x: -x[2])[:n]

    def discovery_timeline(self, domain: str = "",
                           start_time: float = 0) -> list[KnowledgeArtifact]:
        artifacts = self.by_domain(domain) if domain else list(self.artifacts.values())
        filtered = [a for a in artifacts if a.created_at >= start_time]
        return sorted(filtered, key=lambda a: a.created_at)

    def statistics(self) -> dict[str, Any]:
        types: dict[str, int] = defaultdict(int)
        domains: dict[str, int] = defaultdict(int)
        statuses: dict[str, int] = defaultdict(int)
        for a in self.artifacts.values():
            types[a.artifact_type] += 1
            domains[a.domain] += 1
            statuses[a.status] += 1
        return {
            "total_artifacts": len(self.artifacts),
            "type_distribution": dict(types),
            "domain_distribution": dict(domains),
            "status_distribution": dict(statuses),
            "total_citations": sum(len(a.citations) for a in self.artifacts.values()),
            "lineage_edges": len(self.lineage.edges),
            "avg_confidence": (
                sum(a.confidence for a in self.artifacts.values()) / max(len(self.artifacts), 1)
            ),
        }

    def export_json(self, path: str | Path, compress: bool = False) -> str:
        out = Path(path)
        data = {
            "artifacts": {aid: a.to_dict() for aid, a in self.artifacts.items()},
            "lineage": [e.__dict__ for e in self.lineage.edges],
            "statistics": self.statistics(),
            "exported_at": time.time(),
        }
        content = json.dumps(data, indent=2, default=str)
        if compress:
            out = out.with_suffix(out.suffix + ".gz")
            gzip.compress(content.encode()).write(out)
        else:
            out.write_text(content)
        return str(out)

    def import_json(self, path: str | Path) -> int:
        p = Path(path)
        if p.suffix == ".gz":
            data = json.loads(gzip.decompress(p.read_bytes()).decode())
        else:
            data = json.loads(p.read_text())
        count = 0
        for aid, ad in data.get("artifacts", {}).items():
            if aid not in self.artifacts:
                self.artifacts[aid] = KnowledgeArtifact.from_dict(ad)
                self._index(self.artifacts[aid])
                count += 1
        for ed in data.get("lineage", []):
            self.lineage.edges.append(LineageEdge(**ed))
        self._save()
        return count

    def _index(self, artifact: KnowledgeArtifact):
        self._domain_index[artifact.domain].append(artifact.id)
        self._type_index[artifact.artifact_type].append(artifact.id)
        self._status_index[artifact.status].append(artifact.id)
        for tag in artifact.tags:
            self._tag_index[tag].append(artifact.id)
        for author in artifact.authors:
            self._author_index[author.name.lower()].append(artifact.id)

    def _deindex(self, artifact: KnowledgeArtifact):
        for idx in [self._domain_index, self._type_index, self._status_index]:
            lst = idx.get(artifact.domain if idx is self._domain_index
                          else artifact.artifact_type if idx is self._type_index
                          else artifact.status)
            if lst and artifact.id in lst:
                lst.remove(artifact.id)
        for tag in artifact.tags:
            if artifact.id in self._tag_index.get(tag, []):
                self._tag_index[tag].remove(artifact.id)
        for author in artifact.authors:
            if artifact.id in self._author_index.get(author.name.lower(), []):
                self._author_index[author.name.lower()].remove(artifact.id)

    def _sync_graph(self, artifact: KnowledgeArtifact):
        if self.graph_db is None:
            return
        try:
            from genesis.graphdb import Node
            node = Node(
                uid=f"knowledge:{artifact.id}",
                name=artifact.title,
                node_type=f"knowledge_{artifact.artifact_type}",
                description=artifact.description[:500],
                attributes=json.dumps({
                    "artifact_type": artifact.artifact_type,
                    "domain": artifact.domain,
                    "confidence": artifact.confidence,
                    "quality_score": artifact.quality_score,
                    "status": artifact.status,
                }),
                source="knowledge_base",
                confidence=artifact.confidence,
                tags=artifact.tags,
                created_at=artifact.created_at,
                updated_at=artifact.updated_at,
            )
            self.graph_db.add_node(node)
        except Exception:
            pass

    def _sync_memory(self, artifact: KnowledgeArtifact):
        if self.memory is None:
            return
        try:
            self.memory.store(
                f"knowledge:{artifact.id}",
                artifact.to_dict(),
                tier="long_term",
                tags=artifact.tags + [artifact.domain, artifact.artifact_type],
            )
        except Exception:
            pass

    def _state_path(self) -> Path:
        return self.storage_path / "knowledge_base.json"

    def _save(self):
        data = {
            "artifacts": {aid: {
                k: ([x.to_dict() for x in v] if k == "authors" else v)
                for k, v in a.__dict__.items()
            } for aid, a in self.artifacts.items()},
            "lineage": [e.__dict__ for e in self.lineage.edges],
            "indexes": {
                "domain": dict(self._domain_index),
                "type": dict(self._type_index),
                "tag": {k: v for k, v in self._tag_index.items()},
                "author": dict(self._author_index),
                "status": dict(self._status_index),
            },
        }
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text())
            for aid, ad in data.get("artifacts", {}).items():
                authors = [KnowledgeAuthor(**a) for a in ad.get("authors", [])]
                ad["authors"] = authors
                self.artifacts[aid] = KnowledgeArtifact.from_dict(ad)
                self._index(self.artifacts[aid])
            for ed in data.get("lineage", []):
                self.lineage.edges.append(LineageEdge(**ed))
            idx = data.get("indexes", {})
            self._domain_index = defaultdict(list, idx.get("domain", {}))
            self._type_index = defaultdict(list, idx.get("type", {}))
            self._tag_index = defaultdict(list, idx.get("tag", {}))
            self._author_index = defaultdict(list, idx.get("author", {}))
            self._status_index = defaultdict(list, idx.get("status", {}))
        except Exception:
            pass
