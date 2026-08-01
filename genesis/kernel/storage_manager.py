"""
Universal Kernel: StorageManager — Persistent storage volume management.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from genesis.kernel.types import StorageClass, StorageVolume


class StorageManager:
    """Manages persistent storage volumes and allocations."""

    def __init__(self):
        self._volumes: dict[str, StorageVolume] = {}
        self._assignments: dict[str, str] = {}
        self._history: list[dict[str, Any]] = []

    def create_volume(self, name: str, total_bytes: int,
                      storage_class: StorageClass = StorageClass.HOT,
                      path: str = "", mount_point: str = "") -> StorageVolume:
        volume = StorageVolume(
            name=name,
            storage_class=storage_class,
            total_bytes=total_bytes,
            path=path,
            mount_point=mount_point,
        )
        self._volumes[volume.id] = volume
        self._history.append({
            "action": "create_volume",
            "volume_id": volume.id,
            "name": name,
            "total_bytes": total_bytes,
            "timestamp": time.time(),
        })
        return volume

    def delete_volume(self, volume_id: str) -> bool:
        return self._volumes.pop(volume_id, None) is not None

    def get_volume(self, volume_id: str) -> StorageVolume | None:
        return self._volumes.get(volume_id)

    def assign(self, capability_id: str, volume_id: str) -> bool:
        if volume_id not in self._volumes:
            return False
        if capability_id in self._assignments:
            self._assignments.pop(capability_id)
        self._assignments[capability_id] = volume_id
        return True

    def unassign(self, capability_id: str) -> bool:
        return self._assignments.pop(capability_id, None) is not None

    def volume_for(self, capability_id: str) -> StorageVolume | None:
        vol_id = self._assignments.get(capability_id)
        return self._volumes.get(vol_id) if vol_id else None

    def allocate(self, volume_id: str, size_bytes: int) -> bool:
        vol = self._volumes.get(volume_id)
        if not vol or vol.available_bytes < size_bytes:
            return False
        vol.used_bytes += size_bytes
        return True

    def deallocate(self, volume_id: str, size_bytes: int) -> bool:
        vol = self._volumes.get(volume_id)
        if not vol:
            return False
        vol.used_bytes = max(0, vol.used_bytes - size_bytes)
        return True

    def volumes_by_class(self, storage_class: StorageClass) -> list[StorageVolume]:
        return [v for v in self._volumes.values() if v.storage_class == storage_class]

    def summary(self) -> dict[str, Any]:
        total = sum(v.total_bytes for v in self._volumes.values())
        used = sum(v.used_bytes for v in self._volumes.values())
        return {
            "volumes": len(self._volumes),
            "assignments": len(self._assignments),
            "total_bytes": total,
            "used_bytes": used,
            "utilization": used / max(total, 1),
            "by_class": {
                sc.value: len(self.volumes_by_class(sc))
                for sc in StorageClass
            },
        }
