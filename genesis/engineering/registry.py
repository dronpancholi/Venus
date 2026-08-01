from __future__ import annotations

import threading
import time
from typing import Any

from genesis.engineering.object import EngineeringObject, EngineeringObjectType


_registry_instance: EngineeringRegistry | None = None
_registry_lock = threading.Lock()


def get_registry() -> EngineeringRegistry:
    global _registry_instance
    if _registry_instance is None:
        with _registry_lock:
            if _registry_instance is None:
                _registry_instance = EngineeringRegistry()
    return _registry_instance


class EngineeringRegistry:
    def __init__(self, max_objects: int = 100000):
        self._objects: dict[str, EngineeringObject] = {}
        self._by_type: dict[str, list[str]] = {}
        self._by_tag: dict[str, list[str]] = {}
        self._max_objects = max_objects
        self._lock = threading.RLock()

    def register(self, obj: EngineeringObject) -> str:
        with self._lock:
            self._objects[obj.id] = obj
            t = obj.object_type.value
            self._by_type.setdefault(t, []).append(obj.id)
            for tag in obj.tags:
                self._by_tag.setdefault(tag, []).append(obj.id)
            if len(self._objects) > self._max_objects:
                oldest = min(self._objects.keys(), key=lambda k: self._objects[k].created_at)
                del self._objects[oldest]
            return obj.id

    def unregister(self, object_id: str) -> bool:
        with self._lock:
            if object_id not in self._objects:
                return False
            obj = self._objects.pop(object_id)
            t = obj.object_type.value
            if t in self._by_type and obj.id in self._by_type[t]:
                self._by_type[t].remove(obj.id)
            for tag in obj.tags:
                if tag in self._by_tag and obj.id in self._by_tag[tag]:
                    self._by_tag[tag].remove(obj.id)
            return True

    def get(self, object_id: str) -> EngineeringObject | None:
        with self._lock:
            return self._objects.get(object_id)

    def get_by_type(self, object_type: EngineeringObjectType | str) -> list[EngineeringObject]:
        t = object_type.value if isinstance(object_type, EngineeringObjectType) else object_type
        with self._lock:
            ids = self._by_type.get(t, [])
            return [self._objects[i] for i in ids if i in self._objects]

    def get_by_tag(self, tag: str) -> list[EngineeringObject]:
        with self._lock:
            ids = self._by_tag.get(tag, [])
            return [self._objects[i] for i in ids if i in self._objects]

    def search(self, query: str, limit: int = 50) -> list[EngineeringObject]:
        q = query.lower()
        results = []
        with self._lock:
            for obj in self._objects.values():
                if len(results) >= limit:
                    break
                if (q in obj.name.lower() or
                    q in obj.description.lower() or
                    q in obj.object_type.value.lower() or
                    q in obj.id.lower() or
                    any(q in t.lower() for t in obj.tags)):
                    results.append(obj)
        return results

    def count(self) -> int:
        with self._lock:
            return len(self._objects)

    def count_by_type(self) -> dict[str, int]:
        with self._lock:
            return {t: len(ids) for t, ids in self._by_type.items()}

    def latest(self, limit: int = 20) -> list[EngineeringObject]:
        with self._lock:
            sorted_objs = sorted(
                self._objects.values(),
                key=lambda o: o.created_at,
                reverse=True,
            )
            return sorted_objs[:limit]

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total": len(self._objects),
                "by_type": {t: len(ids) for t, ids in self._by_type.items()},
                "by_tag": {t: len(ids) for t, ids in self._by_tag.items()},
            }

    def clear(self):
        with self._lock:
            self._objects.clear()
            self._by_type.clear()
            self._by_tag.clear()
