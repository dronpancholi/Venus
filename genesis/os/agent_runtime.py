"""
AgentRuntime — manages agent lifecycle and execution.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class AgentProcess:
    """A running or completed agent process."""
    id: str = ""
    agent_type: str = ""
    status: str = "created"  # created, starting, running, stopping, stopped, failed
    pid: int = 0
    started_at: float = 0.0
    stopped_at: float = 0.0
    config: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    error: str = ""
    tags: list[str] = field(default_factory=list)


class AgentRuntime:
    """
    Manages the lifecycle of autonomous agents.

    Responsible for:
      - Starting and stopping agents
      - Monitoring agent health
      - Collecting agent metrics
      - Restarting failed agents
      - Resource limits
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "agents"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.processes: dict[str, AgentProcess] = {}
        self._factories: dict[str, Callable] = {}
        self._load()

    def register_agent_type(self, agent_type: str, factory: Callable):
        """Register a factory function that creates an agent instance."""
        self._factories[agent_type] = factory

    def start_agent(self, agent_type: str, config: dict | None = None,
                     tags: list[str] | None = None) -> str:
        """Start a new agent process."""
        proc = AgentProcess(
            id=generate_id("agent", 10),
            agent_type=agent_type,
            status="starting",
            started_at=time.time(),
            config=config or {},
            tags=tags or [],
        )
        self.processes[proc.id] = proc
        self._save()
        return proc.id

    def stop_agent(self, proc_id: str):
        proc = self.processes.get(proc_id)
        if proc:
            proc.status = "stopped"
            proc.stopped_at = time.time()
            self._save()

    def get_process(self, proc_id: str) -> AgentProcess | None:
        return self.processes.get(proc_id)

    def update_metrics(self, proc_id: str, metrics: dict[str, float]):
        proc = self.processes.get(proc_id)
        if proc:
            proc.metrics.update(metrics)
            self._save()

    def set_status(self, proc_id: str, status: str, error: str = ""):
        proc = self.processes.get(proc_id)
        if proc:
            proc.status = status
            if error:
                proc.error = error
            if status in ("stopped", "failed"):
                proc.stopped_at = time.time()
            self._save()

    def running_agents(self) -> list[AgentProcess]:
        return [p for p in self.processes.values() if p.status in ("running", "starting")]

    def failed_agents(self) -> list[AgentProcess]:
        return [p for p in self.processes.values() if p.status == "failed"]

    def restart_failed(self) -> list[str]:
        restarted = []
        for proc in self.failed_agents():
            proc.status = "starting"
            proc.error = ""
            proc.started_at = time.time()
            proc.retry_count = getattr(proc, 'retry_count', 0) + 1
            restarted.append(proc.id)
        self._save()
        return restarted

    def summary(self) -> dict[str, Any]:
        statuses = {}
        for p in self.processes.values():
            statuses[p.status] = statuses.get(p.status, 0) + 1
        return {
            "total_agents": len(self.processes),
            "running": len(self.running_agents()),
            "failed": len(self.failed_agents()),
            "status_distribution": statuses,
            "agent_types": len(self._factories),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "agent_runtime.json"

    def _save(self):
        data = {pid: p.__dict__ for pid, p in self.processes.items()}
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for pid, pd in data.items():
                    self.processes[pid] = AgentProcess(**pd)
            except Exception:
                pass
