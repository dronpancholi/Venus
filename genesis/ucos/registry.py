"""
UCOS: CapabilityRegistry — Central registry for all platform capabilities.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from genesis.ucos.capability import (
    Capability, CapabilityDefinition, CapabilityCategory,
    CapabilityState, MaturityLevel,
)
from genesis.utils.identity import generate_id


class CapabilityRegistry:
    """Central registry. Every capability must register here."""

    def __init__(self):
        self._capabilities: dict[str, Capability] = {}
        self._index_by_category: dict[CapabilityCategory, set[str]] = defaultdict(set)
        self._index_by_maturity: dict[MaturityLevel, set[str]] = defaultdict(set)
        self._index_by_tag: dict[str, set[str]] = defaultdict(set)
        self._index_by_owner: dict[str, set[str]] = defaultdict(set)
        self._registration_log: list[dict[str, Any]] = []
        self._version_history: dict[str, list[CapabilityDefinition]] = defaultdict(list)

    def register(self, definition: CapabilityDefinition,
                 implementation: Any = None) -> Capability:
        cap = Capability(definition, implementation)
        self._capabilities[cap.id] = cap
        self._index_by_category[definition.category].add(cap.id)
        self._index_by_maturity[definition.maturity].add(cap.id)
        for tag in definition.tags:
            self._index_by_tag[tag].add(cap.id)
        if definition.owner:
            self._index_by_owner[definition.owner].add(cap.id)
        definition.state = CapabilityState.REGISTERED
        definition.touch()
        self._registration_log.append({
            "capability_id": cap.id,
            "name": definition.name,
            "category": definition.category.value,
            "timestamp": time.time(),
        })
        self._version_history[cap.id].append(definition)
        return cap

    def get(self, capability_id: str) -> Capability | None:
        return self._capabilities.get(capability_id)

    def get_definition(self, capability_id: str) -> CapabilityDefinition | None:
        cap = self._capabilities.get(capability_id)
        return cap.definition if cap else None

    def find(self, category: CapabilityCategory | None = None,
             maturity: MaturityLevel | None = None,
             tag: str = "", owner: str = "",
             state: CapabilityState | None = None,
             name_contains: str = "") -> list[Capability]:
        results = set(self._capabilities.values())
        if category:
            ids = self._index_by_category.get(category, set())
            results = {c for c in results if c.id in ids}
        if maturity:
            ids = self._index_by_maturity.get(maturity, set())
            results = {c for c in results if c.id in ids}
        if tag:
            ids = self._index_by_tag.get(tag, set())
            results = {c for c in results if c.id in ids}
        if owner:
            ids = self._index_by_owner.get(owner, set())
            results = {c for c in results if c.id in ids}
        if state:
            results = {c for c in results if c.state == state}
        if name_contains:
            results = {c for c in results if name_contains.lower() in c.name.lower()}
        return sorted(results, key=lambda c: c.name)

    def unregister(self, capability_id: str) -> bool:
        cap = self._capabilities.pop(capability_id, None)
        if not cap:
            return False
        d = cap.definition
        self._index_by_category[d.category].discard(capability_id)
        self._index_by_maturity[d.maturity].discard(capability_id)
        for tag in d.tags:
            self._index_by_tag[tag].discard(capability_id)
        if d.owner:
            self._index_by_owner[d.owner].discard(capability_id)
        return True

    def update_maturity(self, capability_id: str, maturity: MaturityLevel) -> bool:
        cap = self._capabilities.get(capability_id)
        if not cap:
            return False
        old_maturity = cap.definition.maturity
        self._index_by_maturity[old_maturity].discard(capability_id)
        cap.definition.maturity = maturity
        self._index_by_maturity[maturity].add(capability_id)
        cap.definition.touch()
        return True

    def set_state(self, capability_id: str, state: CapabilityState) -> bool:
        cap = self._capabilities.get(capability_id)
        if not cap:
            return False
        cap.state = state
        cap.definition.touch()
        return True

    def record_version(self, capability_id: str) -> CapabilityDefinition | None:
        cap = self._capabilities.get(capability_id)
        if not cap:
            return None
        clone = cap.definition.clone(capability_id)
        cap.definition.version.bump_patch()
        self._version_history[capability_id].append(clone)
        cap.definition.touch()
        return clone

    def get_version_history(self, capability_id: str) -> list[CapabilityDefinition]:
        return list(self._version_history.get(capability_id, []))

    def register_consumer(self, capability_id: str, consumer_id: str) -> bool:
        cap = self._capabilities.get(capability_id)
        if not cap:
            return False
        cap.definition.register_consumer(consumer_id)
        return True

    def register_provider(self, capability_id: str, provider_id: str) -> bool:
        cap = self._capabilities.get(capability_id)
        if not cap:
            return False
        cap.definition.register_provider(provider_id)
        return True

    def resolve_dependencies(self, capability_id: str) -> list[Capability]:
        cap = self._capabilities.get(capability_id)
        if not cap:
            return []
        resolved = []
        visited = set()

        def resolve(dep_id: str):
            if dep_id in visited:
                return
            visited.add(dep_id)
            dep = self._capabilities.get(dep_id)
            if dep:
                for d in dep.definition.dependencies:
                    resolve(d)
                resolved.append(dep)

        for dep_id in cap.definition.dependencies:
            resolve(dep_id)
        return resolved

    def dependency_chain(self, capability_id: str) -> list[list[str]]:
        chains = []
        cap = self._capabilities.get(capability_id)
        if not cap:
            return chains
        queue: list[tuple[str, list[str]]] = [(capability_id, [capability_id])]
        while queue and len(chains) < 50:
            current, path = queue.pop(0)
            current_cap = self._capabilities.get(current)
            if not current_cap or not current_cap.definition.dependencies:
                chains.append(path)
                continue
            for dep_id in current_cap.definition.dependencies:
                if dep_id not in path:
                    queue.append((dep_id, path + [dep_id]))
        return chains

    @property
    def count(self) -> int:
        return len(self._capabilities)

    @property
    def all(self) -> list[Capability]:
        return list(self._capabilities.values())

    def summary(self) -> dict[str, Any]:
        cat_counts = {cat.value: len(ids) for cat, ids in self._index_by_category.items()}
        state_counts: dict[str, int] = {}
        for cap in self._capabilities.values():
            s = cap.state.value
            state_counts[s] = state_counts.get(s, 0) + 1
        return {
            "total_capabilities": self.count,
            "by_category": cat_counts,
            "by_state": state_counts,
            "total_registrations": len(self._registration_log),
            "versioned_capabilities": len(self._version_history),
        }
