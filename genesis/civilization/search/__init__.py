"""
Engineering Search Engine (Program N) — multi-modal search.

Combines:
  - Graph traversal (observatory graph queries)
  - Vector similarity (via optional embedding integration)
  - Semantic matching (keyword + domain-aware)
  - Structural pattern matching (USIR subtree patterns)
  - Temporal queries (evolution over time)
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SearchResult:
    """A single search result."""
    id: str = ""
    title: str = ""
    snippet: str = ""
    score: float = 0.0
    source: str = ""  # graph, vector, semantic, structural, temporal
    domain: str = ""
    url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchQuery:
    """A parsed search query."""
    raw: str = ""
    tokens: list[str] = field(default_factory=list)
    domain_filter: str = ""
    source_filters: list[str] = field(default_factory=list)
    min_score: float = 0.0
    max_results: int = 20


class SearchEngine:
    """
    Multi-modal search across all engineering knowledge stores.

    Modes:
      - graph: traverse observatory graph nodes and edges
      - semantic: keyword matching with domain awareness
      - structural: USIR pattern matching (AST subtree patterns)
      - temporal: time-series queries over genome history
      - vector: embedding similarity (if vector store available)
    """

    def __init__(self):
        self.index: dict[str, list[dict[str, Any]]] = {
            "graph": [],
            "semantic": [],
            "structural": [],
            "temporal": [],
            "vector": [],
        }
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            self._build_index()
            self._loaded = True

    def _build_index(self):
        """Build search index from all available knowledge stores."""
        # Observatory graph
        try:
            from genesis.observatory.graph import ObservatoryGraph
            g = ObservatoryGraph()
            for node in g.graph.nodes(data=True):
                self.index["graph"].append({
                    "id": node[0],
                    "name": node[1].get("name", ""),
                    "kind": node[1].get("kind", ""),
                    "language": node[1].get("language", ""),
                    "description": node[1].get("name", ""),
                })
            for edge in g.graph.edges(data=True):
                self.index["graph"].append({
                    "id": f"{edge[0]}->{edge[1]}",
                    "name": edge[1],
                    "kind": "edge",
                    "relation": edge[2].get("relation", ""),
                    "description": f"{edge[0]} --[{edge[2].get('relation', '')}]--> {edge[1]}",
                })
        except Exception:
            pass

        # Research library papers
        try:
            from genesis.civilization.research import ResearchLibrary
            lib = ResearchLibrary()
            for pid, paper in lib.papers.items():
                self.index["semantic"].append({
                    "id": pid,
                    "name": paper.title,
                    "kind": "paper",
                    "domain": paper.domain,
                    "description": paper.abstract[:300] or paper.title,
                    "tags": paper.tags,
                    "confidence": paper.confidence,
                })
        except Exception:
            pass

    def search(self, query: str, mode: str = "auto", max_results: int = 20,
               domain: str = "", min_score: float = 0.0) -> list[SearchResult]:
        """Execute a multi-modal search."""
        self._ensure_loaded()
        parsed = SearchQuery(
            raw=query,
            tokens=self._tokenize(query),
            domain_filter=domain,
            min_score=min_score,
            max_results=max_results,
        )

        all_results: list[SearchResult] = []

        if mode in ("auto", "semantic"):
            all_results.extend(self._semantic_search(parsed))
        if mode in ("auto", "graph"):
            all_results.extend(self._graph_search(parsed))
        if mode in ("auto", "structural"):
            all_results.extend(self._structural_search(parsed))
        if mode in ("auto", "temporal"):
            all_results.extend(self._temporal_search(parsed))
        if mode in ("auto", "vector"):
            all_results.extend(self._vector_search(parsed))

        # Deduplicate by id
        seen: set[str] = set()
        unique: list[SearchResult] = []
        for r in sorted(all_results, key=lambda x: -x.score):
            if r.id not in seen:
                seen.add(r.id)
                unique.append(r)

        return unique[:max_results]

    def _tokenize(self, text: str) -> list[str]:
        return [t.lower() for t in re.findall(r'\w+', text) if len(t) > 1]

    def _semantic_search(self, query: SearchQuery) -> list[SearchResult]:
        """Keyword + domain-aware semantic search."""
        results = []
        tokens = query.tokens
        if not tokens:
            return results

        for entry in self.index["semantic"]:
            if query.domain_filter and entry.get("domain") != query.domain_filter:
                continue

            text = f"{entry.get('name', '')} {entry.get('description', '')} {' '.join(entry.get('tags', []))}"
            text_lower = text.lower()

            matches = sum(1 for t in tokens if t in text_lower)
            if matches == 0:
                continue

            score = matches / len(tokens)
            title_match = any(t in entry.get('name', '').lower() for t in tokens)
            if title_match:
                score *= 1.5

            if score >= query.min_score:
                results.append(SearchResult(
                    id=entry.get("id", ""),
                    title=entry.get("name", ""),
                    snippet=entry.get("description", "")[:200],
                    score=round(score, 4),
                    source="semantic",
                    domain=entry.get("domain", ""),
                    metadata={"kind": entry.get("kind", ""), "confidence": entry.get("confidence", 0)},
                ))

        return results

    def _graph_search(self, query: SearchQuery) -> list[SearchResult]:
        """Graph traversal search."""
        results = []
        tokens = query.tokens
        if not tokens:
            return results

        for entry in self.index["graph"]:
            text = f"{entry.get('name', '')} {entry.get('description', '')} {entry.get('language', '')}"
            text_lower = text.lower()

            matches = sum(1 for t in tokens if t in text_lower)
            if matches == 0:
                continue

            score = matches / len(tokens) * 0.8
            if query.domain_filter and entry.get("language") == query.domain_filter:
                score *= 1.2

            if score >= query.min_score:
                results.append(SearchResult(
                    id=entry.get("id", ""),
                    title=f"{entry.get('name', '')} ({entry.get('kind', '')})",
                    snippet=entry.get("description", "")[:200],
                    score=round(score, 4),
                    source="graph",
                    domain=entry.get("language", ""),
                    metadata={"kind": entry.get("kind", ""), "relation": entry.get("relation", "")},
                ))

        return results

    def _structural_search(self, query: SearchQuery) -> list[SearchResult]:
        """USIR structural pattern matching (stub for AST-based search)."""
        results = []
        # Structural search requires USIR node tree traversal
        try:
            from genesis.usir.core import USIRNode, NodeKind
            # Stub: in production, this traverses USIR ASTs and matches subtree patterns
            pass
        except ImportError:
            pass
        return results

    def _temporal_search(self, query: SearchQuery) -> list[SearchResult]:
        """Temporal query over genome evolution history."""
        results = []
        try:
            from genesis.observatory.registry import RepositoryRegistry
            reg = RepositoryRegistry()
            repos = reg.list_repos()

            for repo in repos:
                fingerprint = repo.get("fingerprint_changed_at", 0)
                if fingerprint:
                    age_days = (time.time() - fingerprint) / 86400
                    if any(str(round(age_days)) in query.raw for t in query.tokens):
                        results.append(SearchResult(
                            id=repo.get("id", ""),
                            title=f"{repo.get('name', '')} (age: {age_days:.0f}d)",
                            snippet=f"Last changed: {age_days:.0f} days ago",
                            score=round(max(0, 1 - age_days / 365), 4),
                            source="temporal",
                            metadata={"age_days": age_days},
                        ))
        except ImportError:
            pass
        return results

    def _vector_search(self, query: SearchQuery) -> list[SearchResult]:
        """Vector similarity search (requires embedding store)."""
        results = []
        # Stub: integrate with sentence-transformers or similar
        return results

    def rebuild_index(self):
        """Force rebuild of search index."""
        self.index = {k: [] for k in self.index}
        self._loaded = False
        self._ensure_loaded()

    def summary(self) -> dict[str, Any]:
        return {
            "index_sizes": {k: len(v) for k, v in self.index.items()},
            "total_entries": sum(len(v) for v in self.index.values()),
        }
