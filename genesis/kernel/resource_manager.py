"""
Universal Kernel: ResourceManager — Track and allocate CPU, memory, storage, network.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from genesis.kernel.types import ResourceReservation


class ResourceManager:
    """Tracks system resources and manages allocations across capabilities."""

    def __init__(self, total_cpu: float = 16.0, total_memory_mb: int = 32768,
                 total_storage_mb: int = 512000, total_network_mbps: float = 1000.0,
                 total_gpu_cores: float = 4.0):
        self._limits = {
            "cpu": total_cpu,
            "memory": total_memory_mb,
            "storage": total_storage_mb,
            "network": total_network_mbps,
            "gpu": total_gpu_cores,
        }
        self._used: dict[str, float] = {"cpu": 0.0, "memory": 0.0, "storage": 0.0,
                                         "network": 0.0, "gpu": 0.0}
        self._reservations: dict[str, ResourceReservation] = {}
        self._history: list[dict[str, Any]] = []

    @property
    def cpu_available(self) -> float:
        return self._limits["cpu"] - self._used["cpu"]

    @property
    def memory_available(self) -> int:
        return int(self._limits["memory"] - self._used["memory"])

    @property
    def storage_available(self) -> int:
        return int(self._limits["storage"] - self._used["storage"])

    def reserve(self, capability_id: str, cpu: float = 0.0, memory_mb: int = 0,
                storage_mb: int = 0, network_mbps: float = 0.0,
                gpu_cores: float = 0.0, priority: int = 0,
                duration_ms: float = 0.0) -> ResourceReservation | None:
        if self.cpu_available < cpu:
            return None
        if self.memory_available < memory_mb:
            return None
        if self.storage_available < storage_mb:
            return None
        reservation = ResourceReservation(
            capability_id=capability_id,
            cpu_cores=cpu,
            memory_mb=memory_mb,
            storage_mb=storage_mb,
            network_mbps=network_mbps,
            gpu_cores=gpu_cores,
            priority=priority,
            expires_at=(time.time() + duration_ms / 1000) if duration_ms > 0 else 0.0,
        )
        self._reservations[reservation.id] = reservation
        self._used["cpu"] += cpu
        self._used["memory"] += memory_mb
        self._used["storage"] += storage_mb
        self._used["network"] += network_mbps
        self._used["gpu"] += gpu_cores
        self._history.append({
            "action": "reserve",
            "reservation_id": reservation.id,
            "capability_id": capability_id,
            "resources": {"cpu": cpu, "memory_mb": memory_mb, "storage_mb": storage_mb},
            "timestamp": time.time(),
        })
        return reservation

    def release(self, reservation_id: str) -> bool:
        res = self._reservations.pop(reservation_id, None)
        if not res:
            return False
        self._used["cpu"] -= res.cpu_cores
        self._used["memory"] -= res.memory_mb
        self._used["storage"] -= res.storage_mb
        self._used["network"] -= res.network_mbps
        self._used["gpu"] -= res.gpu_cores
        res.status = "released"
        self._history.append({
            "action": "release",
            "reservation_id": reservation_id,
            "capability_id": res.capability_id,
            "timestamp": time.time(),
        })
        return True

    def release_all(self, capability_id: str) -> int:
        released = 0
        for rid in list(self._reservations.keys()):
            if self._reservations[rid].capability_id == capability_id:
                if self.release(rid):
                    released += 1
        return released

    def get_reservation(self, reservation_id: str) -> ResourceReservation | None:
        return self._reservations.get(reservation_id)

    def reservations_for(self, capability_id: str) -> list[ResourceReservation]:
        return [r for r in self._reservations.values() if r.capability_id == capability_id]

    def utilization(self) -> dict[str, float]:
        return {
            "cpu": self._used["cpu"] / max(self._limits["cpu"], 1),
            "memory": self._used["memory"] / max(self._limits["memory"], 1),
            "storage": self._used["storage"] / max(self._limits["storage"], 1),
            "network": self._used["network"] / max(self._limits["network"], 1),
            "gpu": self._used["gpu"] / max(self._limits["gpu"], 1),
        }

    def summary(self) -> dict[str, Any]:
        return {
            "limits": dict(self._limits),
            "used": dict(self._used),
            "utilization": self.utilization(),
            "active_reservations": len(self._reservations),
            "total_allocations": len(self._history),
        }
