"""
Memory Consolidation — knowledge consolidation, compression, provenance, contradiction detection.
"""

from __future__ import annotations

import math
import time
from typing import Any

from genesis.memory.types import BaseMemory, MemoryEntry, MemoryQuery


class MemoryConsolidator:
    """Consolidates memory by identifying duplicates, compressing, and propagating confidence."""

    def __init__(self, min_similarity: float = 0.8):
        self._min_similarity = min_similarity

    def deduplicate(self, memory: BaseMemory) -> int:
        entries = memory.all_entries()
        removed = 0
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                if self._is_duplicate(entries[i], entries[j]):
                    self._merge(entries[i], entries[j])
                    memory.forget(entries[j].id)
                    removed += 1
        return removed

    def consolidate(self, memories: list[BaseMemory]) -> dict[str, list[MemoryEntry]]:
        merged: dict[str, list[MemoryEntry]] = {}
        for mem in memories:
            for entry in mem.all_entries():
                key = self._canonical_key(entry)
                merged.setdefault(key, []).append(entry)
        return merged

    def propagate_confidence(self, memory: BaseMemory):
        entries = memory.all_entries()
        for entry in entries:
            count = sum(1 for e in entries if e.key == entry.key)
            if count > 1:
                entry.confidence = 1.0 - (1.0 / (count + 1))

    def compute_provenance(self, memory: BaseMemory, entry_id: str) -> list[str]:
        entry = memory.get(entry_id)
        if not entry:
            return []
        sources = {entry.source}
        for tag in entry.tags:
            q = MemoryQuery(tags=[tag], source=entry.source)
            related = memory.query(q)
            for r in related.entries:
                if r.source:
                    sources.add(r.source)
        return list(sources)

    def detect_contradictions(self, memory: BaseMemory) -> list[tuple[str, str, float]]:
        entries = memory.all_entries()
        contradictions: list[tuple[str, str, float]] = []
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                e1, e2 = entries[i], entries[j]
                if e1.key == e2.key and abs(e1.confidence - e2.confidence) > 0.5:
                    contradictions.append((e1.id, e2.id, abs(e1.confidence - e2.confidence)))
        return contradictions

    def compress(self, memory: BaseMemory, max_entries: int) -> int:
        if memory.entry_count <= max_entries:
            return 0
        sorted_entries = sorted(memory.all_entries(), key=lambda e: e.relevance())
        to_remove = memory.entry_count - max_entries
        for i in range(to_remove):
            memory.forget(sorted_entries[i].id)
        return to_remove

    @staticmethod
    def _is_duplicate(a: MemoryEntry, b: MemoryEntry) -> bool:
        if a.key == b.key:
            return True
        if a.content == b.content and a.memory_type == b.memory_type:
            return True
        return False

    @staticmethod
    def _merge(keep: MemoryEntry, remove: MemoryEntry):
        keep.access_count += remove.access_count
        keep.confidence = max(keep.confidence, remove.confidence)
        keep.importance = max(keep.importance, remove.importance)
        keep.provenance.extend(remove.provenance)
        for tag in remove.tags:
            if tag not in keep.tags:
                keep.tags.append(tag)

    @staticmethod
    def _canonical_key(entry: MemoryEntry) -> str:
        return f"{entry.memory_type.value}:{entry.key}"


class ForgettingMechanism:
    """Controls forgetting via decay curves and importance thresholds."""

    def __init__(self, base_decay_rate: float = 0.01, importance_threshold: float = 0.1):
        self._base_decay_rate = base_decay_rate
        self._importance_threshold = importance_threshold

    def apply_decay(self, memory: BaseMemory, days_passed: float = 1.0) -> int:
        forgotten = 0
        for entry in memory.all_entries():
            entry.confidence *= math.exp(-self._base_decay_rate * days_passed)
            entry.importance *= math.exp(-self._base_decay_rate * days_passed * 0.5)
            if entry.importance < self._importance_threshold:
                memory.forget(entry.id)
                forgotten += 1
        return forgotten

    def boost_by_access(self, memory: BaseMemory, min_access: int = 3):
        for entry in memory.all_entries():
            if entry.access_count >= min_access:
                entry.importance = min(1.0, entry.importance * 1.5)
                entry.confidence = min(1.0, entry.confidence * 1.1)
