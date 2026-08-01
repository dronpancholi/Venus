from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class ServiceHealth:
    status: str = "unknown"
    uptime_seconds: float = 0.0
    services_count: int = 0
    messages_sent: int = 0
    active_sessions: int = 0
    threads: int = 0
    last_heartbeat: float = 0.0
    errors: list[str] = field(default_factory=list)

    def __getattr__(self, name: str) -> Any:
        mapping = {"services": self.services_count, "messages": self.messages_sent}
        if name in mapping:
            return mapping[name]
        raise AttributeError(f"'ServiceHealth' object has no attribute '{name}'")


@dataclass
class ServiceInstance:
    id: str = ""
    name: str = ""
    version: str = "1.0.0"
    capabilities: list[str] = field(default_factory=list)
    status: str = "registered"
    registered_at: float = 0.0
    last_heartbeat: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("svc", 12)
        if not self.registered_at:
            self.registered_at = time.time()
            self.last_heartbeat = time.time()

    def heartbeat(self):
        self.last_heartbeat = time.time()

    @property
    def healthy(self) -> bool:
        return time.time() - self.last_heartbeat < 60.0


class ServiceRegistry:
    """Service registry with health checking and capability discovery."""

    def __init__(self):
        self._instances: dict[str, ServiceInstance] = {}
        self._by_name: dict[str, list[str]] = {}
        self._by_capability: dict[str, list[str]] = {}
        self._lock = threading.RLock()

    def register(self, name: str, version: str = "1.0.0",
                 capabilities: list[str] | None = None) -> ServiceInstance:
        with self._lock:
            instance = ServiceInstance(
                name=name,
                version=version,
                capabilities=capabilities or [],
            )
            self._instances[instance.id] = instance
            self._by_name.setdefault(name, []).append(instance.id)
            for cap in instance.capabilities:
                self._by_capability.setdefault(cap, []).append(instance.id)
            return instance

    def unregister(self, instance_id: str) -> bool:
        with self._lock:
            instance = self._instances.pop(instance_id, None)
            if not instance:
                return False
            by_name = self._by_name.get(instance.name, [])
            if instance_id in by_name:
                by_name.remove(instance_id)
            for cap in instance.capabilities:
                by_cap = self._by_capability.get(cap, [])
                if instance_id in by_cap:
                    by_cap.remove(instance_id)
            return True

    def get(self, instance_id: str) -> ServiceInstance | None:
        return self._instances.get(instance_id)

    def find_by_name(self, name: str) -> list[ServiceInstance]:
        ids = self._by_name.get(name, [])
        return [self._instances[i] for i in ids if i in self._instances]

    def find_by_capability(self, capability: str) -> list[ServiceInstance]:
        ids = self._by_capability.get(capability, [])
        return [self._instances[i] for i in ids if i in self._instances]

    def list_services(self) -> list[ServiceInstance]:
        return list(self._instances.values())

    def heartbeat(self, instance_id: str):
        instance = self._instances.get(instance_id)
        if instance:
            instance.heartbeat()

    def health(self, instance_id: str) -> ServiceHealth:
        instance = self._instances.get(instance_id)
        if not instance:
            return ServiceHealth(status="not_found")
        return ServiceHealth(
            status="healthy" if instance.healthy else "unhealthy",
            uptime_seconds=time.time() - instance.registered_at,
            last_heartbeat=instance.last_heartbeat,
        )

    def prune_unhealthy(self, max_age_secs: float = 60.0) -> int:
        now = time.time()
        pruned: list[str] = []
        for iid, inst in list(self._instances.items()):
            if now - inst.last_heartbeat > max_age_secs:
                self.unregister(iid)
                pruned.append(iid)
        return len(pruned)

    def count(self) -> int:
        return len(self._instances)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total_instances": len(self._instances),
                "by_name": {n: len(ids) for n, ids in self._by_name.items()},
                "by_capability": {c: len(ids) for c, ids in self._by_capability.items()},
            }
