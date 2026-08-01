from __future__ import annotations

import time
from collections import OrderedDict, defaultdict
from threading import Lock
from typing import Any

from genesis.ued.types import CacheEntry, CachePolicy


class CacheManager:
    """Multi-level cache with pluggable eviction policies."""

    def __init__(self, max_entries_l1: int = 10000, max_entries_l2: int = 100000,
                 policy: CachePolicy = CachePolicy.LRU):
        self._max_l1 = max_entries_l1
        self._max_l2 = max_entries_l2
        self._policy = policy
        self._l1: dict[str, CacheEntry] = OrderedDict()
        self._l2: dict[str, CacheEntry] = OrderedDict()
        self._hits_l1 = 0
        self._hits_l2 = 0
        self._misses = 0
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._l1.get(key)
            if entry:
                if entry.ttl_secs > 0 and time.time() - entry.last_access > entry.ttl_secs:
                    del self._l1[key]
                    self._misses += 1
                    return None
                self._hits_l1 += 1
                entry.access_count += 1
                entry.last_access = time.time()
                self._touch_l1(key)
                return entry.value

            entry = self._l2.get(key)
            if entry:
                if entry.ttl_secs > 0 and time.time() - entry.last_access > entry.ttl_secs:
                    del self._l2[key]
                    self._misses += 1
                    return None
                self._hits_l2 += 1
                entry.access_count += 1
                entry.last_access = time.time()
                self._promote(key, entry)
                return entry.value

            self._misses += 1
            return None

    def set(self, key: str, value: Any, ttl_secs: float = 0.0, size_bytes: int = 0):
        with self._lock:
            entry = CacheEntry(
                key=key, value=value, size_bytes=size_bytes,
                ttl_secs=ttl_secs, created_at=time.time(), last_access=time.time(),
            )
            self._l1[key] = entry
            self._touch_l1(key)
            self._evict_l1()

    def set_l2(self, key: str, value: Any, ttl_secs: float = 0.0, size_bytes: int = 0):
        with self._lock:
            entry = CacheEntry(
                key=key, value=value, size_bytes=size_bytes,
                ttl_secs=ttl_secs, created_at=time.time(), last_access=time.time(),
            )
            self._l2[key] = entry
            self._touch_l2(key)
            self._evict_l2()

    def invalidate(self, key: str):
        with self._lock:
            self._l1.pop(key, None)
            self._l2.pop(key, None)

    def clear(self):
        with self._lock:
            self._l1.clear()
            self._l2.clear()

    def _promote(self, key: str, entry: CacheEntry):
        self._l2.pop(key, None)
        self._l1[key] = entry
        self._touch_l1(key)
        self._evict_l1()

    def _touch_l1(self, key: str):
        if self._policy == CachePolicy.LRU:
            self._l1.move_to_end(key)
        elif self._policy == CachePolicy.LFU:
            pass

    def _touch_l2(self, key: str):
        if self._policy == CachePolicy.LRU:
            self._l2.move_to_end(key)

    def _evict_l1(self):
        while len(self._l1) > self._max_l1:
            if self._policy == CachePolicy.LRU:
                key, entry = next(iter(self._l1.items()))
                del self._l1[key]
                self._l2[key] = entry
                self._touch_l2(key)
                self._evict_l2()

    def _evict_l2(self):
        while len(self._l2) > self._max_l2:
            if self._policy == CachePolicy.LRU:
                self._l2.popitem(last=False)

    def hit_rate(self) -> float:
        total = self._hits_l1 + self._hits_l2 + self._misses
        return (self._hits_l1 + self._hits_l2) / max(total, 1)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "l1_entries": len(self._l1),
                "l2_entries": len(self._l2),
                "hits_l1": self._hits_l1,
                "hits_l2": self._hits_l2,
                "misses": self._misses,
                "hit_rate": self.hit_rate(),
                "max_l1": self._max_l1,
                "max_l2": self._max_l2,
                "policy": self._policy.value,
            }
