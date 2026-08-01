"""
Universal Kernel: ProcessManager — Process lifecycle and scheduling.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable

from genesis.kernel.types import ProcessInfo, ProcessState


class ProcessManager:
    """Manages process creation, scheduling, and lifecycle."""

    def __init__(self):
        self._processes: dict[str, ProcessInfo] = {}
        self._handlers: dict[str, Callable] = {}
        self._history: list[dict[str, Any]] = []

    def create(self, name: str, capability_id: str,
               handler: Callable | None = None) -> ProcessInfo:
        proc = ProcessInfo(name=name, capability_id=capability_id)
        self._processes[proc.id] = proc
        if handler:
            self._handlers[proc.id] = handler
        self._history.append({
            "action": "create",
            "process_id": proc.id,
            "name": name,
            "capability_id": capability_id,
            "timestamp": time.time(),
        })
        return proc

    def start(self, process_id: str) -> bool:
        proc = self._processes.get(process_id)
        if not proc or proc.state != ProcessState.CREATED:
            return False
        proc.state = ProcessState.RUNNING
        proc.started_at = time.time()
        handler = self._handlers.get(process_id)
        if handler:
            try:
                handler(proc)
            except Exception as e:
                proc.state = ProcessState.FAILED
                proc.error = str(e)
        return True

    def suspend(self, process_id: str) -> bool:
        proc = self._processes.get(process_id)
        if not proc or proc.state != ProcessState.RUNNING:
            return False
        proc.state = ProcessState.SUSPENDED
        return True

    def resume(self, process_id: str) -> bool:
        proc = self._processes.get(process_id)
        if not proc or proc.state != ProcessState.SUSPENDED:
            return False
        proc.state = ProcessState.RUNNING
        return True

    def terminate(self, process_id: str, exit_code: int = 0) -> bool:
        proc = self._processes.get(process_id)
        if not proc:
            return False
        proc.state = ProcessState.TERMINATED
        proc.exit_code = exit_code
        proc.stopped_at = time.time()
        return True

    def fail(self, process_id: str, error: str = "") -> bool:
        proc = self._processes.get(process_id)
        if not proc:
            return False
        proc.state = ProcessState.FAILED
        proc.error = error
        proc.stopped_at = time.time()
        return True

    def get(self, process_id: str) -> ProcessInfo | None:
        return self._processes.get(process_id)

    def processes_for(self, capability_id: str) -> list[ProcessInfo]:
        return [p for p in self._processes.values() if p.capability_id == capability_id]

    def running(self) -> list[ProcessInfo]:
        return [p for p in self._processes.values() if p.state == ProcessState.RUNNING]

    def failed(self) -> list[ProcessInfo]:
        return [p for p in self._processes.values() if p.state == ProcessState.FAILED]

    def cleanup(self, max_age_seconds: float = 86400) -> int:
        now = time.time()
        removed = 0
        for pid in list(self._processes.keys()):
            proc = self._processes[pid]
            if proc.state in (ProcessState.TERMINATED, ProcessState.FAILED):
                if now - proc.stopped_at > max_age_seconds:
                    self._processes.pop(pid)
                    self._handlers.pop(pid, None)
                    removed += 1
        return removed

    def summary(self) -> dict[str, Any]:
        states: dict[str, int] = {}
        for p in self._processes.values():
            states[p.state.value] = states.get(p.state.value, 0) + 1
        return {
            "total": len(self._processes),
            "by_state": states,
            "running": len(self.running()),
            "failed": len(self.failed()),
            "total_operations": len(self._history),
        }
