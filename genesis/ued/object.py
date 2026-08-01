from __future__ import annotations

import gzip
import hashlib
import io
import time
import zlib
from typing import Any

from genesis.ued.types import CompressionType, StorageConfig
from genesis.utils.identity import generate_id


class ObjectStore:
    """Binary object storage with content-addressed deduplication."""

    def __init__(self, config: StorageConfig | None = None):
        self._config = config or StorageConfig()
        self._objects: dict[str, bytes] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._ref_counts: dict[str, int] = {}
        self._chunk_size = 64 * 1024

    def _content_hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()[:32]

    def put(self, data: bytes, metadata: dict[str, Any] | None = None) -> str:
        checksum = self._content_hash(data)
        if checksum in self._objects:
            self._ref_counts[checksum] += 1
            return checksum
        compressed = self._compress(data)
        self._objects[checksum] = compressed
        self._ref_counts[checksum] = 1
        self._metadata[checksum] = {
            "size_bytes": len(data),
            "compressed_bytes": len(compressed),
            "compression": self._config.compression.value,
            "chunks": max(1, len(data) // self._chunk_size),
            "created_at": time.time(),
            **(metadata or {}),
        }
        return checksum

    def put_chunked(self, data: bytes, metadata: dict[str, Any] | None = None) -> list[str]:
        checksums: list[str] = []
        for i in range(0, len(data), self._chunk_size):
            chunk = data[i:i + self._chunk_size]
            checksums.append(self.put(chunk, metadata))
        return checksums

    def get(self, checksum: str) -> bytes | None:
        compressed = self._objects.get(checksum)
        if compressed is None:
            return None
        return self._decompress(compressed, checksum)

    def get_chunked(self, checksums: list[str]) -> bytes:
        parts: list[bytes] = []
        for c in checksums:
            part = self.get(c)
            if part:
                parts.append(part)
        return b"".join(parts)

    def delete(self, checksum: str) -> bool:
        if checksum not in self._objects:
            return False
        self._ref_counts[checksum] -= 1
        if self._ref_counts[checksum] <= 0:
            del self._objects[checksum]
            self._metadata.pop(checksum, None)
            del self._ref_counts[checksum]
        return True

    def exists(self, checksum: str) -> bool:
        return checksum in self._objects

    def metadata(self, checksum: str) -> dict[str, Any] | None:
        return self._metadata.get(checksum)

    def dedup_ratio(self) -> float:
        raw = sum(m["size_bytes"] for m in self._metadata.values())
        stored = sum(len(d) for d in self._objects.values())
        return raw / max(stored, 1)

    def _compress(self, data: bytes) -> bytes:
        ct = self._config.compression
        if ct == CompressionType.GZIP:
            return gzip.compress(data, compresslevel=self._config.compression_level)
        elif ct == CompressionType.ZSTD:
            try:
                import zstd
                return zstd.compress(data, self._config.compression_level)
            except ImportError:
                return zlib.compress(data, self._config.compression_level)
        elif ct == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.compress(data, compression_level=self._config.compression_level)
            except ImportError:
                return data
        return data

    def _decompress(self, data: bytes, checksum: str) -> bytes:
        meta = self._metadata.get(checksum)
        ct = (meta.get("compression") if meta else CompressionType.NONE.value)
        if ct == CompressionType.GZIP.value:
            return gzip.decompress(data)
        elif ct == CompressionType.ZSTD.value:
            try:
                import zstd
                return zstd.decompress(data)
            except ImportError:
                return zlib.decompress(data)
        elif ct == CompressionType.LZ4.value:
            try:
                import lz4.frame
                return lz4.frame.decompress(data)
            except ImportError:
                return data
        return data

    def count(self) -> int:
        return len(self._objects)

    def summary(self) -> dict[str, Any]:
        total_raw = sum(m.get("size_bytes", 0) for m in self._metadata.values())
        total_stored = sum(len(d) for d in self._objects.values())
        return {
            "objects": len(self._objects),
            "unique_checksums": len(self._objects),
            "raw_bytes": total_raw,
            "stored_bytes": total_stored,
            "dedup_ratio": round(self.dedup_ratio(), 2),
            "compression": self._config.compression.value,
        }


class SnapshotStore:
    """Point-in-time snapshots with incremental support."""

    def __init__(self, object_store: ObjectStore):
        self._object_store = object_store
        self._snapshots: dict[str, dict[str, Any]] = {}
        self._snapshot_index: dict[str, list[str]] = {}  # snapshot_id -> [checksums]

    def create(self, name: str, data: bytes,
               parent: str | None = None) -> str:
        snap_id = generate_id("snap", 16)
        checksums = self._object_store.put_chunked(data)
        self._snapshot_index[snap_id] = checksums
        parent_id = parent or ""
        if parent and parent in self._snapshot_index:
            parent_checksums = self._snapshot_index[parent]
            new_checksums = [c for c in checksums if c not in parent_checksums]
            incremental_size = sum(
                self._object_store.metadata(c).get("size_bytes", 0)
                for c in new_checksums if self._object_store.metadata(c)
            )
        else:
            incremental_size = len(data)
        self._snapshots[snap_id] = {
            "id": snap_id,
            "name": name,
            "parent": parent_id,
            "created_at": time.time(),
            "checksum_count": len(checksums),
            "incremental_bytes": incremental_size,
            "total_bytes": len(data),
            "is_incremental": parent is not None,
        }
        return snap_id

    def get(self, snap_id: str) -> bytes | None:
        checksums = self._snapshot_index.get(snap_id)
        if not checksums:
            return None
        return self._object_store.get_chunked(checksums)

    def delete(self, snap_id: str) -> bool:
        if snap_id not in self._snapshots:
            return False
        checksums = self._snapshot_index.pop(snap_id, [])
        for c in checksums:
            self._object_store.delete(c)
        del self._snapshots[snap_id]
        return True

    def list_snapshots(self) -> list[dict[str, Any]]:
        return list(self._snapshots.values())

    def latest(self) -> dict[str, Any] | None:
        if not self._snapshots:
            return None
        return max(self._snapshots.values(), key=lambda s: s["created_at"])

    def count(self) -> int:
        return len(self._snapshots)

    def summary(self) -> dict[str, Any]:
        return {
            "snapshots": self.count(),
            "latest": self.latest()["name"] if self.latest() else None,
        }


class ArchiveStore:
    """Tiered archival storage with compression and retrieval."""

    TIERS = ["hot", "warm", "cold"]
    MOVE_TO_COLD_AFTER_DAYS = 90
    MOVE_TO_WARM_AFTER_DAYS = 30

    def __init__(self, object_store: ObjectStore):
        self._object_store = object_store
        self._archives: dict[str, dict[str, Any]] = {}
        self._tier_index: dict[str, set[str]] = {t: set() for t in self.TIERS}

    def archive(self, name: str, data: bytes,
                tier: str = "hot",
                retention_days: float = 365.0) -> str:
        if tier not in self.TIERS:
            raise ValueError(f"Invalid tier: {tier}. Must be one of {self.TIERS}")
        archive_id = generate_id("arch", 16)
        checksum = self._object_store.put(data, {"archive_id": archive_id, "name": name})
        self._archives[archive_id] = {
            "id": archive_id,
            "name": name,
            "checksum": checksum,
            "tier": tier,
            "size_bytes": len(data),
            "retention_days": retention_days,
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 0,
        }
        self._tier_index[tier].add(archive_id)
        return archive_id

    def retrieve(self, archive_id: str) -> bytes | None:
        archive = self._archives.get(archive_id)
        if not archive:
            return None
        archive["last_accessed"] = time.time()
        archive["access_count"] += 1
        return self._object_store.get(archive["checksum"])

    def delete(self, archive_id: str) -> bool:
        archive = self._archives.pop(archive_id, None)
        if archive:
            self._object_store.delete(archive["checksum"])
            for tier_set in self._tier_index.values():
                tier_set.discard(archive_id)
            return True
        return False

    def move_tier(self, archive_id: str, target_tier: str) -> bool:
        if target_tier not in self.TIERS:
            return False
        archive = self._archives.get(archive_id)
        if not archive:
            return False
        old_tier = archive["tier"]
        if old_tier != target_tier:
            self._tier_index[old_tier].discard(archive_id)
            self._tier_index[target_tier].add(archive_id)
            archive["tier"] = target_tier
        return True

    def list_archives(self, tier: str | None = None) -> list[dict[str, Any]]:
        if tier:
            return [self._archives[a] for a in self._tier_index.get(tier, [])
                    if a in self._archives]
        return list(self._archives.values())

    def apply_retention_policy(self) -> int:
        now = time.time()
        deleted = 0
        for archive_id, archive in list(self._archives.items()):
            age_days = (now - archive["created_at"]) / 86400
            if age_days > archive["retention_days"]:
                if self.delete(archive_id):
                    deleted += 1
        return deleted

    def apply_tier_policy(self) -> int:
        now = time.time()
        moved = 0
        for archive_id, archive in list(self._archives.items()):
            age_days = (now - archive["created_at"]) / 86400
            if archive["tier"] == "hot" and age_days > self.MOVE_TO_WARM_AFTER_DAYS:
                if self.move_tier(archive_id, "warm"):
                    moved += 1
            elif archive["tier"] == "warm" and age_days > self.MOVE_TO_COLD_AFTER_DAYS:
                if self.move_tier(archive_id, "cold"):
                    moved += 1
        return moved

    def count(self) -> int:
        return len(self._archives)

    def summary(self) -> dict[str, Any]:
        return {
            "total_archives": self.count(),
            "by_tier": {t: len(ids) for t, ids in self._tier_index.items()},
            "total_bytes": sum(a["size_bytes"] for a in self._archives.values()),
        }
