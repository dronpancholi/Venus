"""
ResourceAllocator — tracks and allocates compute resources.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class ResourceReservation:
    """A reservation of compute resources."""
    id: str = ""
    owner: str = ""
    cpu_cores: float = 0.0
    memory_mb: float = 0.0
    disk_gb: float = 0.0
    gpu_count: int = 0
    priority: float = 0.5
    created_at: float = 0.0
    expires_at: float = 0.0
    status: str = "active"  # active, released, expired


class ResourceAllocator:
    """
    Tracks and allocates compute resources across the civilization.

    Resources: CPU cores, memory, disk, GPU
    Reservations can be made and released.
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "resources"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.total: dict[str, float] = {
            "cpu_cores": 32.0,
            "memory_mb": 65536.0,
            "disk_gb": 1000.0,
            "gpu_count": 4.0,
        }
        self.reservations: dict[str, ResourceReservation] = {}
        self._load()

    def reserve(self, owner: str, cpu_cores: float = 0, memory_mb: float = 0,
                 disk_gb: float = 0, gpu_count: int = 0,
                 duration_seconds: float = 3600,
                 priority: float = 0.5) -> ResourceReservation | None:
        """Reserve resources. Returns None if insufficient."""
        if not self._has_available(cpu_cores, memory_mb, disk_gb, gpu_count):
            return None

        res = ResourceReservation(
            id=generate_id("res", 10),
            owner=owner,
            cpu_cores=cpu_cores, memory_mb=memory_mb,
            disk_gb=disk_gb, gpu_count=gpu_count,
            priority=priority,
            created_at=time.time(),
            expires_at=time.time() + duration_seconds,
        )
        self.reservations[res.id] = res
        self._save()
        return res

    def release(self, reservation_id: str):
        res = self.reservations.pop(reservation_id, None)
        if res:
            res.status = "released"
            self._save()

    def _has_available(self, cpu=0, mem=0, disk=0, gpu=0) -> bool:
        used = self.used()
        return (
            used["cpu_cores"] + cpu <= self.total["cpu_cores"] and
            used["memory_mb"] + mem <= self.total["memory_mb"] and
            used["disk_gb"] + disk <= self.total["disk_gb"] and
            used["gpu_count"] + gpu <= self.total["gpu_count"]
        )

    def used(self) -> dict[str, float]:
        total = {"cpu_cores": 0.0, "memory_mb": 0.0, "disk_gb": 0.0, "gpu_count": 0.0}
        for res in self.reservations.values():
            if res.status == "active":
                total["cpu_cores"] += res.cpu_cores
                total["memory_mb"] += res.memory_mb
                total["disk_gb"] += res.disk_gb
                total["gpu_count"] += res.gpu_count
        return total

    def available(self) -> dict[str, float]:
        used = self.used()
        return {
            k: self.total[k] - used.get(k, 0)
            for k in self.total
        }

    def set_total(self, cpu_cores=32, memory_mb=65536, disk_gb=1000, gpu_count=4):
        self.total["cpu_cores"] = cpu_cores
        self.total["memory_mb"] = memory_mb
        self.total["disk_gb"] = disk_gb
        self.total["gpu_count"] = gpu_count
        self._save()

    def summary(self) -> dict[str, Any]:
        return {
            "total": dict(self.total),
            "used": self.used(),
            "available": self.available(),
            "active_reservations": len([r for r in self.reservations.values() if r.status == "active"]),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "resources.json"

    def _save(self):
        data = {
            "total": self.total,
            "reservations": {rid: r.__dict__ for rid, r in self.reservations.items()},
        }
        (self._state_path()).write_text(json.dumps(data, indent=2))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.total.update(data.get("total", {}))
                for rid, rd in data.get("reservations", {}).items():
                    self.reservations[rid] = ResourceReservation(**rd)
            except Exception:
                pass
