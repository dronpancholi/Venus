from __future__ import annotations

import math
from typing import Any

from genesis.ued.types import Query, QueryResult
from genesis.utils.identity import generate_id


class VectorStore:
    """Dense vector storage with exact and approximate similarity search."""

    def __init__(self, dimension: int = 384, index_cells: int = 16):
        self.dimension = dimension
        self._index_cells = index_cells
        self._vectors: dict[str, list[float]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._centroids: dict[int, list[str]] = {}
        self._centroids_built = False

    def insert(self, vector_id: str, vector: list[float],
               metadata: dict[str, Any] | None = None):
        if len(vector) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {len(vector)}")
        self._vectors[vector_id] = vector
        self._metadata[vector_id] = metadata or {}
        self._centroids_built = False

    def get(self, vector_id: str) -> tuple[list[float], dict[str, Any]] | None:
        vec = self._vectors.get(vector_id)
        if vec is None:
            return None
        return vec, self._metadata.get(vector_id, {})

    def delete(self, vector_id: str) -> bool:
        if vector_id in self._vectors:
            del self._vectors[vector_id]
            self._metadata.pop(vector_id, None)
            self._centroids_built = False
            return True
        return False

    def count(self) -> int:
        return len(self._vectors)

    def _dot(self, a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def _norm(self, v: list[float]) -> float:
        return math.sqrt(sum(x * x for x in v))

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        na, nb = self._norm(a), self._norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return self._dot(a, b) / (na * nb)

    def _euclidean_distance(self, a: list[float], b: list[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def _build_centroids(self):
        if self._centroids_built or len(self._vectors) < self._index_cells:
            return
        vecs = list(self._vectors.items())
        chunk = max(1, len(vecs) // self._index_cells)
        self._centroids.clear()
        for i in range(0, len(vecs), chunk):
            cell = i // chunk
            self._centroids[cell] = [rid for rid, _ in vecs[i:i + chunk]]
        self._centroids_built = True

    def search(self, query: list[float], k: int = 10,
               metric: str = "cosine") -> list[tuple[str, float]]:
        if len(query) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}")
        scored: list[tuple[str, float]] = []
        for rid, vec in self._vectors.items():
            if metric == "cosine":
                dist = self._cosine_similarity(query, vec)
            else:
                dist = -self._euclidean_distance(query, vec)
            scored.append((rid, dist))
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    def search_approximate(self, query: list[float], k: int = 10,
                           metric: str = "cosine") -> list[tuple[str, float]]:
        self._build_centroids()
        candidates: set[str] = set()
        for cell_vecs in self._centroids.values():
            candidates.update(cell_vecs[:k])
        if not candidates:
            return self.search(query, k, metric)
        scored: list[tuple[str, float]] = []
        for rid in candidates:
            vec = self._vectors.get(rid)
            if vec:
                if metric == "cosine":
                    dist = self._cosine_similarity(query, vec)
                else:
                    dist = -self._euclidean_distance(query, vec)
                scored.append((rid, dist))
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    def search_with_filter(self, query: list[float], q: Query,
                           k: int = 10, metric: str = "cosine") -> list[tuple[str, float]]:
        scored: list[tuple[str, float]] = []
        for rid, vec in self._vectors.items():
            meta = self._metadata.get(rid, {})
            if q.matches(meta):
                if metric == "cosine":
                    dist = self._cosine_similarity(query, vec)
                else:
                    dist = -self._euclidean_distance(query, vec)
                scored.append((rid, dist))
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    def summary(self) -> dict[str, Any]:
        return {
            "vectors": len(self._vectors),
            "dimension": self.dimension,
            "index_cells": self._index_cells,
            "centroids_built": self._centroids_built,
        }
