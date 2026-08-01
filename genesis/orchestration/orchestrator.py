from __future__ import annotations

import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.orchestration.service_def import ServiceDef, ServiceStatus, BootPhase


@dataclass
class BootStep:
    service_id: str = ""
    phase: BootPhase = BootPhase.CONFIG_LOAD
    status: ServiceStatus = ServiceStatus.PENDING
    duration_ms: float = 0.0
    dependencies_met: bool = True
    error: str | None = None
    started_at: float = 0.0


@dataclass
class BootReport:
    steps: list[BootStep] = field(default_factory=list)
    started_at: float = 0.0
    completed_at: float = 0.0
    total_duration_ms: float = 0.0
    healthy_count: int = 0
    degraded_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0

    def summary(self) -> dict[str, Any]:
        return {
            "total_duration_ms": self.total_duration_ms,
            "steps": len(self.steps),
            "healthy": self.healthy_count,
            "degraded": self.degraded_count,
            "failed": self.failed_count,
            "skipped": self.skipped_count,
            "all_healthy": self.failed_count == 0 and self.degraded_count == 0,
        }


class PlatformOrchestrator:
    def __init__(self):
        self._services: dict[str, ServiceDef] = {}
        self._instances: dict[str, Any] = {}
        self._status: dict[str, ServiceStatus] = {}
        self._lock = threading.Lock()
        self._report = BootReport()

    # ── Registration ────────────────────────────────────────────

    def register(self, svc: ServiceDef):
        if svc.id in self._services:
            raise ValueError(f"Service already registered: {svc.id}")
        self._services[svc.id] = svc
        self._status[svc.id] = ServiceStatus.PENDING

    def register_many(self, services: list[ServiceDef]):
        for svc in services:
            self.register(svc)

    # ── Validation ──────────────────────────────────────────────

    def validate_dependencies(self) -> list[str]:
        errors = []
        for sid, svc in self._services.items():
            for dep in svc.dependencies:
                if dep not in self._services:
                    errors.append(f"Service '{sid}' depends on unknown service '{dep}'")
        return errors

    def detect_cycles(self) -> list[list[str]]:
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[list[str]] = []
        parent: dict[str, str | None] = {}

        def dfs(sid: str):
            visited.add(sid)
            rec_stack.add(sid)
            svc = self._services[sid]
            for dep in svc.dependencies:
                if dep not in self._services:
                    continue
                if dep not in visited:
                    parent[dep] = sid
                    dfs(dep)
                elif dep in rec_stack:
                    cycle = [dep]
                    cur = sid
                    while cur != dep:
                        cycle.append(cur)
                        cur = parent.get(cur, "")
                    cycle.append(dep)
                    cycles.append(list(reversed(cycle)))
            rec_stack.discard(sid)

        for sid in self._services:
            if sid not in visited:
                dfs(sid)
        return cycles

    # ── Boot Order ──────────────────────────────────────────────

    def compute_boot_order(self) -> list[list[str]]:
        deps = {sid: set(svc.dependencies) & set(self._services.keys())
                for sid, svc in self._services.items()}
        remaining = set(self._services.keys())
        levels: list[list[str]] = []

        while remaining:
            level = [sid for sid in remaining if not deps[sid]]
            if not level:
                remaining_deps = {sid: deps[sid] for sid in remaining}
                raise ValueError(
                    f"Boot order stuck — remaining services with unmet dependencies: {remaining_deps}"
                )
            levels.append(level)
            for sid in level:
                remaining.discard(sid)
                for other in remaining:
                    deps[other].discard(sid)

        return levels

    def compute_shutdown_order(self) -> list[str]:
        boot_order = self.compute_boot_order()
        flat = [sid for level in reversed(boot_order) for sid in level]
        return flat

    def compute_critical_path(self) -> list[str]:
        longest: dict[str, float] = {}
        for level in self.compute_boot_order():
            for sid in level:
                svc = self._services[sid]
                max_dep = 0.0
                for dep in svc.dependencies:
                    if dep in longest:
                        max_dep = max(max_dep, longest[dep])
                longest[sid] = max_dep + svc.estimated_startup_ms
        sorted_svcs = sorted(longest.items(), key=lambda x: -x[1])
        return [s[0] for s in sorted_svcs]

    # ── Boot ────────────────────────────────────────────────────

    def boot(self, provider: Any = None) -> BootReport:
        dep_errors = self.validate_dependencies()
        if dep_errors:
            raise ValueError(f"Dependency errors:\n" + "\n".join(dep_errors))

        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Dependency cycles detected: {cycles}")

        self._report = BootReport(started_at=time.time())

        for level in self.compute_boot_order():
            threads = []
            results: dict[str, BootStep | None] = {sid: None for sid in level}

            lock = threading.Lock()

            def boot_service(sid: str):
                svc = self._services[sid]
                started = time.time()
                step = BootStep(service_id=sid, phase=BootPhase.SERVICE_INIT,
                                status=ServiceStatus.PENDING, started_at=started)

                deps_met = all(
                    self._status.get(d) in (ServiceStatus.HEALTHY, ServiceStatus.DEGRADED)
                    for d in svc.dependencies
                )
                step.dependencies_met = deps_met

                if not deps_met:
                    step.status = ServiceStatus.BLOCKED
                    step.error = "Dependencies not healthy"
                    with lock:
                        self._status[sid] = ServiceStatus.FAILED
                        results[sid] = step
                        self._report.steps.append(step)
                        self._report.failed_count += 1
                    return

                step.status = ServiceStatus.BOOTING

                try:
                    if svc.factory:
                        instance = svc.factory()
                    else:
                        instance = None

                    with lock:
                        self._instances[sid] = instance
                        self._status[sid] = ServiceStatus.BOOTING

                    if svc.startup_hook and instance is not None:
                        svc.startup_hook(instance)

                    if svc.verification_hook and instance is not None:
                        verified = svc.verification_hook(instance)
                        if not verified:
                            step.status = ServiceStatus.FAILED
                            step.error = "Verification hook failed"
                            with lock:
                                self._status[sid] = ServiceStatus.FAILED
                                results[sid] = step
                                self._report.steps.append(step)
                                self._report.failed_count += 1
                            return

                    if svc.health_check and instance is not None:
                        healthy = svc.health_check(instance)
                    else:
                        healthy = True

                    if healthy:
                        step.status = ServiceStatus.HEALTHY
                        with lock:
                            self._status[sid] = ServiceStatus.HEALTHY
                            self._report.healthy_count += 1
                    else:
                        step.status = ServiceStatus.DEGRADED
                        step.error = "Health check failed"
                        with lock:
                            self._status[sid] = ServiceStatus.DEGRADED
                            self._report.degraded_count += 1

                except Exception as e:
                    step.status = ServiceStatus.FAILED
                    step.error = str(e)
                    with lock:
                        self._status[sid] = ServiceStatus.FAILED
                        self._report.failed_count += 1

                step.duration_ms = (time.time() - started) * 1000
                with lock:
                    results[sid] = step
                    self._report.steps.append(step)

            for sid in level:
                t = threading.Thread(target=boot_service, args=(sid,), daemon=True)
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            failed_critical = any(
                self._services[sid].critical and self._status.get(sid) == ServiceStatus.FAILED
                for sid in level
            )
            if failed_critical:
                break

        self._report.completed_at = time.time()
        self._report.total_duration_ms = (self._report.completed_at - self._report.started_at) * 1000
        return self._report

    # ── Shutdown ────────────────────────────────────────────────

    def shutdown(self):
        order = self.compute_shutdown_order()
        for sid in order:
            svc = self._services[sid]
            instance = self._instances.get(sid)
            start = time.time()
            step = BootStep(service_id=sid, phase=BootPhase.SHUTDOWN,
                            status=ServiceStatus.PENDING, started_at=start)
            try:
                if svc.shutdown_hook and instance is not None:
                    svc.shutdown_hook(instance)
                step.status = ServiceStatus.HEALTHY
                step.duration_ms = (time.time() - start) * 1000
            except Exception as e:
                step.status = ServiceStatus.FAILED
                step.error = str(e)
                step.duration_ms = (time.time() - start) * 1000
            self._report.steps.append(step)

    # ── Diagnostics ─────────────────────────────────────────────

    def get_status(self, service_id: str) -> ServiceStatus | None:
        return self._status.get(service_id)

    def get_instance(self, service_id: str) -> Any:
        return self._instances.get(service_id)

    def all_status(self) -> dict[str, ServiceStatus]:
        return dict(self._status)

    def dependency_graph(self) -> dict[str, list[str]]:
        return {sid: list(svc.dependencies) for sid, svc in self._services.items()}

    def get_report(self) -> BootReport:
        return self._report

    def get_instance(self, service_id: str) -> Any:
        return self._instances.get(service_id)
