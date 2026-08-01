"""
Universal Kernel: HealthManager — Health monitoring, probes, and alerting.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from genesis.kernel.types import HealthProbe


class HealthManager:
    """Monitors capability health with probes and heartbeats."""

    def __init__(self):
        self._probes: dict[str, HealthProbe] = {}
        self._heartbeats: dict[str, float] = {}
        self._alerts: list[dict[str, Any]] = []
        self._check_history: list[dict[str, Any]] = []

    def register_probe(self, capability_id: str, probe_type: str = "http",
                        endpoint: str = "", interval_ms: float = 30000.0,
                        timeout_ms: float = 5000.0, threshold: int = 3) -> HealthProbe:
        probe = HealthProbe(
            capability_id=capability_id,
            probe_type=probe_type,
            endpoint=endpoint,
            interval_ms=interval_ms,
            timeout_ms=timeout_ms,
            threshold=threshold,
        )
        self._probes[probe.id] = probe
        return probe

    def remove_probe(self, probe_id: str) -> bool:
        return self._probes.pop(probe_id, None) is not None

    def record_heartbeat(self, capability_id: str):
        self._heartbeats[capability_id] = time.time()

    def heartbeat_age(self, capability_id: str) -> float:
        last = self._heartbeats.get(capability_id, 0.0)
        return time.time() - last if last > 0 else float("inf")

    def check(self, probe_id: str, success: bool, response_time_ms: float = 0.0) -> bool:
        probe = self._probes.get(probe_id)
        if not probe:
            return False
        probe.last_check = time.time()
        probe.last_response_ms = response_time_ms
        if success:
            probe.consecutive_failures = 0
            probe.healthy = True
        else:
            probe.consecutive_failures += 1
            if probe.consecutive_failures >= probe.threshold:
                probe.healthy = False
                self._alerts.append({
                    "probe_id": probe_id,
                    "capability_id": probe.capability_id,
                    "type": "health_failure",
                    "consecutive_failures": probe.consecutive_failures,
                    "timestamp": time.time(),
                })
        self._check_history.append({
            "probe_id": probe_id,
            "capability_id": probe.capability_id,
            "success": success,
            "response_time_ms": response_time_ms,
            "timestamp": time.time(),
        })
        return probe.healthy

    def probes_for(self, capability_id: str) -> list[HealthProbe]:
        return [p for p in self._probes.values() if p.capability_id == capability_id]

    def unhealthy_capabilities(self) -> list[str]:
        unhealthy = set()
        for probe in self._probes.values():
            if not probe.healthy:
                unhealthy.add(probe.capability_id)
        for cap_id, last_heartbeat in self._heartbeats.items():
            if time.time() - last_heartbeat > 60:
                unhealthy.add(cap_id)
        return list(unhealthy)

    def alerts(self, since: float = 0.0) -> list[dict[str, Any]]:
        return [a for a in self._alerts if a["timestamp"] >= since]

    def summary(self) -> dict[str, Any]:
        return {
            "probes": len(self._probes),
            "heartbeats": len(self._heartbeats),
            "alerts": len(self._alerts),
            "unhealthy": len(self.unhealthy_capabilities()),
            "total_checks": len(self._check_history),
        }
