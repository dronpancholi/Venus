"""
MemoryManager — multi-tier memory hierarchy (working, short-term, long-term, archival).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str = ""
    key: str = ""
    value: Any = None
    tier: str = "working"  # working, short_term, long_term, archival
    ttl_seconds: float = 0.0  # 0 = no TTL
    created_at: float = 0.0
    access_count: int = 0
    last_access: float = 0.0
    tags: list[str] = field(default_factory=list)
    source: str = ""


class MemoryManager:
    """
    Multi-tier persistent memory hierarchy.

    Tiers:
      - working: current session, fast access, small capacity
      - short_term: recent context, medium capacity
      - long_term: learned knowledge, large capacity
      - archival: permanent storage, unlimited capacity

    Each tier has configurable max entries and TTL.
    Entries automatically migrate between tiers based on access frequency.
    """

    TIER_CONFIGS = {
        "working": {"max_entries": 100, "default_ttl": 3600},
        "short_term": {"max_entries": 1000, "default_ttl": 86400},
        "long_term": {"max_entries": 10000, "default_ttl": 2592000},
        "archival": {"max_entries": 100000, "default_ttl": 0},
    }

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "memory"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.entries: dict[str, MemoryEntry] = {}
        self._key_index: dict[str, str] = {}  # key -> entry_id
        self._load()

    def store(self, key: str, value: Any, tier: str = "working",
               ttl_seconds: float = 0, tags: list[str] | None = None,
               source: str = "") -> str:
        """Store a value in memory."""
        config = self.TIER_CONFIGS.get(tier, self.TIER_CONFIGS["working"])
        if ttl_seconds <= 0:
            ttl_seconds = config["default_ttl"]

        entry = MemoryEntry(
            id=generate_id("mem", 10),
            key=key, value=value, tier=tier,
            ttl_seconds=ttl_seconds,
            created_at=time.time(),
            last_access=time.time(),
            tags=tags or [], source=source,
        )

        # Enforce max entries by evicting oldest
        tier_entries = [e for e in self.entries.values() if e.tier == tier]
        if len(tier_entries) >= config["max_entries"]:
            oldest = min(tier_entries, key=lambda e: e.last_access)
            self._remove(oldest.id)

        # Remove old key if exists
        if key in self._key_index:
            self._remove(self._key_index[key])

        self.entries[entry.id] = entry
        self._key_index[key] = entry.id
        self._save()
        return entry.id

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value by key."""
        entry_id = self._key_index.get(key)
        if not entry_id or entry_id not in self.entries:
            return default
        entry = self.entries[entry_id]
        if self._is_expired(entry):
            self._remove(entry_id)
            return default
        entry.access_count += 1
        entry.last_access = time.time()
        self._promote_if_frequent(entry)
        self._save()
        return entry.value

    def search(self, query: str, tier: str = "", max_results: int = 20) -> list[MemoryEntry]:
        """Search memory entries by key or tag."""
        q = query.lower()
        results = []
        for entry in self.entries.values():
            if tier and entry.tier != tier:
                continue
            if self._is_expired(entry):
                continue
            if q in entry.key.lower() or any(q in t.lower() for t in entry.tags):
                results.append(entry)
                if len(results) >= max_results:
                    break
        return results

    def forget(self, key: str):
        """Remove an entry by key."""
        entry_id = self._key_index.pop(key, None)
        if entry_id:
            self._remove(entry_id)

    def tier_count(self, tier: str) -> int:
        return sum(1 for e in self.entries.values() if e.tier == tier)

    def clear_tier(self, tier: str):
        for eid in list(self.entries.keys()):
            if self.entries[eid].tier == tier:
                self._remove(eid)

    def clear_all(self):
        self.entries.clear()
        self._key_index.clear()
        self._save()

    def _remove(self, entry_id: str):
        entry = self.entries.pop(entry_id, None)
        if entry and entry.key in self._key_index and self._key_index[entry.key] == entry_id:
            del self._key_index[entry.key]

    def _is_expired(self, entry: MemoryEntry) -> bool:
        if entry.ttl_seconds <= 0:
            return False
        return time.time() - entry.created_at > entry.ttl_seconds

    def _promote_if_frequent(self, entry: MemoryEntry):
        """Promote frequently accessed entries to higher tiers."""
        if entry.tier == "working" and entry.access_count > 10:
            entry.tier = "short_term"
            entry.ttl_seconds = self.TIER_CONFIGS["short_term"]["default_ttl"]
        elif entry.tier == "short_term" and entry.access_count > 50:
            entry.tier = "long_term"
            entry.ttl_seconds = self.TIER_CONFIGS["long_term"]["default_ttl"]
        elif entry.tier == "long_term" and entry.access_count > 200:
            entry.tier = "archival"
            entry.ttl_seconds = 0

    def summary(self) -> dict[str, Any]:
        now = time.time()
        expired = sum(1 for e in self.entries.values() if self._is_expired(e))
        return {
            "total_entries": len(self.entries),
            "expired_entries": expired,
            "tier_distribution": {
                "working": self.tier_count("working"),
                "short_term": self.tier_count("short_term"),
                "long_term": self.tier_count("long_term"),
                "archival": self.tier_count("archival"),
            },
            "total_accesses": sum(e.access_count for e in self.entries.values()),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "memory.json"

    def _save(self):
        data = {
            "entries": {eid: e.__dict__ for eid, e in self.entries.items()},
            "key_index": dict(self._key_index),
        }
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for eid, ed in data.get("entries", {}).items():
                    self.entries[eid] = MemoryEntry(**ed)
                self._key_index = dict(data.get("key_index", {}))
            except Exception:
                pass
