from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


class MemoryLayer(Enum):
    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPHEMERAL = "ephemeral"


@dataclass
class MemoryEntry:
    key: str
    content: str
    layer: MemoryLayer = MemoryLayer.WORKING
    tags: list[str] = field(default_factory=list)
    source: str = ""
    timestamp: float = 0.0
    ttl: float = 0.0


class EngineeringMemoryV2:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._layers: dict[MemoryLayer, dict[str, MemoryEntry]] = {
            layer: {} for layer in MemoryLayer
        }
        self._mem_obj: EngineeringObject | None = None

    def boot(self):
        self._mem_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="EngineeringMemoryV2",
            description="Multi-layer memory system with working, short-term, long-term, and ephemeral layers",
            tags=["memory", "v2"],
        )
        self._registry.register(self._mem_obj)

    def store(self, key: str, content: str,
              layer: MemoryLayer = MemoryLayer.WORKING,
              tags: list[str] | None = None,
              source: str = "",
              ttl: float = 0.0):
        entry = MemoryEntry(
            key=key, content=content,
            layer=layer, tags=tags or [],
            source=source,
            timestamp=time.time(),
            ttl=ttl,
        )
        self._layers[layer][key] = entry
        if layer == MemoryLayer.WORKING:
            if len(self._layers[layer]) > 100:
                oldest = min(self._layers[layer].values(), key=lambda e: e.timestamp)
                if oldest:
                    self._layers[layer].pop(oldest.key, None)

    def recall(self, key: str, layer: MemoryLayer | None = None) -> MemoryEntry | None:
        if layer:
            e = self._layers[layer].get(key)
            if e and e.ttl > 0 and time.time() - e.timestamp > e.ttl:
                self._layers[layer].pop(key, None)
                return None
            return e
        for layer in MemoryLayer:
            e = self._layers[layer].get(key)
            if e:
                if e.ttl > 0 and time.time() - e.timestamp > e.ttl:
                    self._layers[layer].pop(key, None)
                    continue
                return e
        return None

    def search(self, query: str, limit: int = 20) -> list[MemoryEntry]:
        q = query.lower()
        results = []
        for layer, entries in self._layers.items():
            for entry in entries.values():
                if q in entry.key.lower() or q in entry.content.lower() or any(q in t.lower() for t in entry.tags):
                    if entry.ttl > 0 and time.time() - entry.timestamp > entry.ttl:
                        continue
                    results.append(entry)
        results.sort(key=lambda e: -e.timestamp)
        return results[:limit]

    def promote(self, key: str, target: MemoryLayer):
        entry = self.recall(key)
        if entry:
            self._layers[entry.layer].pop(key, None)
            entry.layer = target
            entry.timestamp = time.time()
            self._layers[target][key] = entry

    def consolidate(self):
        working = dict(self._layers[MemoryLayer.WORKING])
        for key, entry in working.items():
            if time.time() - entry.timestamp > 300:
                self._layers[MemoryLayer.WORKING].pop(key, None)
                entry.layer = MemoryLayer.SHORT_TERM
                self._layers[MemoryLayer.SHORT_TERM][key] = entry
        short = dict(self._layers[MemoryLayer.SHORT_TERM])
        for key, entry in short.items():
            if time.time() - entry.timestamp > 3600:
                self._layers[MemoryLayer.SHORT_TERM].pop(key, None)
                entry.layer = MemoryLayer.LONG_TERM
                self._layers[MemoryLayer.LONG_TERM][key] = entry
        ephem = dict(self._layers[MemoryLayer.EPHEMERAL])
        for key, entry in ephem.items():
            if entry.ttl > 0 and time.time() - entry.timestamp > entry.ttl:
                self._layers[MemoryLayer.EPHEMERAL].pop(key, None)

    def stats(self) -> dict[str, int]:
        return {layer.value: len(entries) for layer, entries in self._layers.items()}
