from __future__ import annotations

import bisect
import json
import math
from collections import defaultdict
from typing import Any

from genesis.ued.types import IndexType
from genesis.utils.identity import generate_id


class BTreeIndex:
    """Simple B-tree index for range scans and equality lookups."""

    def __init__(self, name: str, field: str, order: int = 4):
        self.name = name
        self.field = field
        self.order = order
        self._entries: dict[tuple, list[str]] = {}
        self._sorted_keys: list[tuple] = []

    def insert(self, key: Any, record_id: str):
        k = (key,) if not isinstance(key, tuple) else key
        if k not in self._entries:
            self._entries[k] = []
            bisect.insort(self._sorted_keys, k)
        self._entries[k].append(record_id)

    def delete(self, key: Any, record_id: str):
        k = (key,) if not isinstance(key, tuple) else key
        records = self._entries.get(k)
        if records:
            try:
                records.remove(record_id)
            except ValueError:
                pass
            if not records:
                del self._entries[k]
                self._sorted_keys.remove(k)

    def search(self, key: Any) -> list[str]:
        k = (key,) if not isinstance(key, tuple) else key
        return list(self._entries.get(k, []))

    def range_scan(self, low: Any, high: Any) -> list[str]:
        low_k = (low,) if not isinstance(low, tuple) else low
        high_k = (high,) if not isinstance(high, tuple) else high
        results: list[str] = []
        for k in self._sorted_keys:
            if low_k <= k <= high_k:
                results.extend(self._entries[k])
            elif k > high_k:
                break
        return results

    def prefix_scan(self, prefix: str) -> list[str]:
        results: list[str] = []
        for k in self._sorted_keys:
            key_str = str(k[0])
            if key_str.startswith(prefix):
                results.extend(self._entries[k])
        return results

    def count(self) -> int:
        return sum(len(v) for v in self._entries.values())

    def unique_keys(self) -> int:
        return len(self._entries)


class HashIndex:
    """Hash index for O(1) equality lookups."""

    def __init__(self, name: str, field: str):
        self.name = name
        self.field = field
        self._buckets: dict[int, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    def _hash_key(self, key: Any) -> int:
        return hash(str(key)) % 256

    def insert(self, key: Any, record_id: str):
        bucket = self._hash_key(key)
        self._buckets[bucket][str(key)].append(record_id)

    def delete(self, key: Any, record_id: str):
        bucket = self._hash_key(key)
        records = self._buckets[bucket][str(key)]
        try:
            records.remove(record_id)
        except ValueError:
            pass
        if not records:
            del self._buckets[bucket][str(key)]

    def search(self, key: Any) -> list[str]:
        bucket = self._hash_key(key)
        return list(self._buckets[bucket].get(str(key), []))

    def bucket_distribution(self) -> dict[int, int]:
        return {b: sum(len(v) for v in entries.values())
                for b, entries in self._buckets.items()}

    def count(self) -> int:
        return sum(sum(len(v) for v in entries.values())
                   for entries in self._buckets.values())


class InvertedIndex:
    """Inverted index for full-text search across document fields."""

    def __init__(self, name: str, field: str):
        self.name = name
        self.field = field
        self._postings: dict[str, set[str]] = defaultdict(set)
        self._stop_words: set[str] = {
            "the", "a", "an", "in", "on", "at", "to", "for", "of",
            "and", "or", "is", "are", "was", "were", "be", "been",
        }

    def tokenize(self, text: str) -> list[str]:
        tokens: list[str] = []
        current: list[str] = []
        for ch in text.lower():
            if ch.isalnum() or ch in ("_", "-"):
                current.append(ch)
            else:
                if current:
                    token = "".join(current)
                    if len(token) > 1 and token not in self._stop_words:
                        tokens.append(token)
                    current = []
        if current:
            token = "".join(current)
            if len(token) > 1 and token not in self._stop_words:
                tokens.append(token)
        return tokens

    def index(self, record_id: str, text: str):
        for token in self.tokenize(text):
            self._postings[token].add(record_id)

    def remove(self, record_id: str, text: str):
        for token in self.tokenize(text):
            self._postings[token].discard(record_id)
            if not self._postings[token]:
                del self._postings[token]

    def search(self, query: str) -> set[str]:
        tokens = self.tokenize(query)
        if not tokens:
            return set()
        result = self._postings.get(tokens[0], set()).copy()
        for token in tokens[1:]:
            result &= self._postings.get(token, set())
        return result

    def search_or(self, query: str) -> set[str]:
        tokens = self.tokenize(query)
        result: set[str] = set()
        for token in tokens:
            result |= self._postings.get(token, set())
        return result

    def term_count(self) -> int:
        return len(self._postings)

    def total_postings(self) -> int:
        return sum(len(v) for v in self._postings.values())


class VectorIndex:
    """Vector index with brute-force (exact) and IVF (approximate) search."""

    def __init__(self, name: str, dimension: int, cells: int = 16):
        self.name = name
        self.dimension = dimension
        self.cells = cells
        self._vectors: dict[str, list[float]] = {}
        self._centroids: dict[int, list[str]] = defaultdict(list)
        self._built = False

    def insert(self, record_id: str, vector: list[float]):
        if len(vector) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {len(vector)}")
        self._vectors[record_id] = vector
        self._built = False

    def delete(self, record_id: str):
        self._vectors.pop(record_id, None)
        self._built = False

    def count(self) -> int:
        return len(self._vectors)

    def build_index(self):
        if self._built or len(self._vectors) < self.cells:
            self._centroids.clear()
            return
        vecs = list(self._vectors.items())
        chunk = max(1, len(vecs) // self.cells)
        self._centroids.clear()
        for i in range(0, len(vecs), chunk):
            cell = i // chunk
            for rid, _ in vecs[i:i + chunk]:
                self._centroids[cell].append(rid)
        self._built = True

    def _dot(self, a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def _norm(self, v: list[float]) -> float:
        return math.sqrt(sum(x * x for x in v))

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        na, nb = self._norm(a), self._norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return self._dot(a, b) / (na * nb)

    def search(self, query: list[float], k: int = 10) -> list[tuple[str, float]]:
        if len(query) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}")
        scored: list[tuple[str, float]] = []
        for rid, vec in self._vectors.items():
            sim = self._cosine_similarity(query, vec)
            scored.append((rid, sim))
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    def search_approximate(self, query: list[float], k: int = 10) -> list[tuple[str, float]]:
        if not self._built:
            self.build_index()
        candidates: set[str] = set()
        for cell_vecs in self._centroids.values():
            candidates.update(cell_vecs[:max(1, k)])
        if not candidates:
            return self.search(query, k)
        scored: list[tuple[str, float]] = []
        for rid in candidates:
            vec = self._vectors.get(rid)
            if vec:
                sim = self._cosine_similarity(query, vec)
                scored.append((rid, sim))
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    def summary(self) -> dict[str, Any]:
        return {
            "vectors": len(self._vectors),
            "dimension": self.dimension,
            "cells": self.cells,
            "built": self._built,
        }
