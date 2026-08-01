from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state import get_state


@dataclass
class KnowledgeCluster:
    id: str
    name: str
    topics: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    items: list[dict[str, Any]] = field(default_factory=list)
    access_count: int = 0
    strength: float = 1.0
    last_accessed: float = 0.0


class SelfOrganizingKnowledge:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._state = get_state()
        self._clusters: dict[str, KnowledgeCluster] = {}
        self._concept_map: dict[str, str] = {}
        self._access_log: list[dict[str, Any]] = []
        self._lock = threading.RLock()
        self._ko_obj: EngineeringObject | None = None
        self._booted = False
        self._consolidation_interval = 300.0

    def boot(self):
        if self._booted:
            return
        self._booted = True
        self._ko_obj = EngineeringObject(
            object_type=EngineeringObjectType.KNOWLEDGE_NODE,
            name="SelfOrganizingKnowledge",
            description="Knowledge that reorganizes itself — clusters emerge, duplicates merge, hierarchy forms",
            tags=["knowledge", "living", "self_organizing"],
        )
        self._registry.register(self._ko_obj)
        self._state.set("knowledge_v2", "clusters", 0)
        self._state.set("knowledge_v2", "concepts", 0)
        self._seed_from_knowledge_engine()

    def _seed_from_knowledge_engine(self):
        if not self._kernel:
            return
        ke = self._kernel.knowledge
        if not hasattr(ke, 'summary'):
            return
        try:
            summary = ke.summary() if hasattr(ke, 'summary') else {}
            if isinstance(summary, dict):
                for topic, _ in list(summary.items())[:20]:
                    self._ensure_cluster(topic)
        except Exception:
            pass

    def _ensure_cluster(self, name: str) -> KnowledgeCluster:
        with self._lock:
            cid = name.lower().replace(" ", "_")
            if cid not in self._clusters:
                cluster = KnowledgeCluster(id=cid, name=name)
                self._clusters[cid] = cluster
                self._state.set("knowledge_v2", "clusters", len(self._clusters))
            return self._clusters[cid]

    def add_concept(self, concept: str, topic: str = "general",
                    content: str = "", source: str = ""):
        with self._lock:
            cluster = self._ensure_cluster(topic)
            if concept not in cluster.concepts:
                cluster.concepts.append(concept)
                self._concept_map[concept.lower()] = cluster.id
                self._state.set("knowledge_v2", "concepts", len(self._concept_map))
            cluster.items.append({
                "concept": concept,
                "content": content[:200],
                "source": source,
                "timestamp": time.time(),
            })
            self._trigger_consolidation()

    def access(self, concept: str):
        cid = self._concept_map.get(concept.lower())
        if cid and cid in self._clusters:
            cluster = self._clusters[cid]
            cluster.access_count += 1
            cluster.strength = min(cluster.strength + 0.1, 2.0)
            cluster.last_accessed = time.time()
            self._access_log.append({"concept": concept, "cluster": cid, "timestamp": time.time()})
            if len(self._access_log) > 1000:
                self._access_log = self._access_log[-1000:]

    def search(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        q = query.lower()
        results = []
        for cluster in self._clusters.values():
            for item in cluster.items:
                if q in item.get("concept", "").lower() or q in item.get("content", "").lower():
                    results.append({**item, "cluster": cluster.name, "strength": cluster.strength})
                    if len(results) >= limit:
                        return results
        for cluster in self._clusters.values():
            if q in cluster.name.lower():
                results.append({"cluster": cluster.name, "concepts": len(cluster.concepts),
                                "strength": cluster.strength, "type": "cluster"})
        return results[:limit]

    def _trigger_consolidation(self):
        if len(self._access_log) % 50 == 0:
            threading.Thread(target=self.consolidate, daemon=True).start()

    def consolidate(self):
        with self._lock:
            merged = set()
            names = list(self._clusters.keys())
            for i, a in enumerate(names):
                if a in merged:
                    continue
                for b in names[i + 1:]:
                    if b in merged:
                        continue
                    ca = self._clusters[a]
                    cb = self._clusters[b]
                    overlap = len(set(ca.concepts) & set(cb.concepts))
                    if overlap > 0 and (overlap / max(len(ca.concepts | set(cb.concepts)), 1)) > 0.3:
                        ca.concepts.extend(cb.concepts)
                        ca.items.extend(cb.items)
                        for concept in cb.concepts:
                            self._concept_map[concept.lower()] = a
                        merged.add(b)
            for m in merged:
                del self._clusters[m]
            inactive = [cid for cid, c in self._clusters.items()
                        if c.strength < 0.3 and time.time() - c.last_accessed > 3600 * 24]
            for cid in inactive:
                del self._clusters[cid]
            self._state.set("knowledge_v2", "clusters", len(self._clusters))

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "clusters": len(self._clusters),
                "concepts": len(self._concept_map),
                "total_items": sum(len(c.items) for c in self._clusters.values()),
                "access_log_size": len(self._access_log),
                "strongest": max((c for c in self._clusters.values()), key=lambda c: c.strength).name
                if self._clusters else "none",
            }
