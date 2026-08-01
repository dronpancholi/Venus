"""
PersistentScheduler — time-based + event-based persistent scheduler.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class ScheduledJob:
    """A job scheduled for execution."""
    id: str = ""
    name: str = ""
    job_type: str = ""  # once, recurring, event
    interval_seconds: float = 0.0  # for recurring
    next_run: float = 0.0
    handler: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    retry_count: int = 0
    last_run: float = 0.0
    last_status: str = "pending"  # pending, running, success, failed
    created_at: float = 0.0
    tags: list[str] = field(default_factory=list)
    timeout: float = 0.0  # max execution time in seconds (0 = no limit)
    depends_on: list[str] = field(default_factory=list)

    def is_due(self) -> bool:
        return time.time() >= self.next_run

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ScheduledJob:
        return cls(**d)


class PersistentScheduler:
    """
    Persistent, restartable scheduler.

    Jobs persist to disk. On restart, pending jobs are re-queued.
    Supports cron-like recurring jobs, one-off jobs, and event-triggered jobs.
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "scheduler"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.jobs: dict[str, ScheduledJob] = {}
        self._handlers: dict[str, Callable] = {}
        self._running = False
        self._load()

    def register_handler(self, name: str, handler: Callable):
        self._handlers[name] = handler

    def add_job(self, job: ScheduledJob) -> str:
        if not job.id:
            job.id = generate_id("job", 10)
        if not job.created_at:
            job.created_at = time.time()
        if not job.next_run:
            job.next_run = time.time()
        self.jobs[job.id] = job
        self._save()
        return job.id

    def add_recurring(self, name: str, handler: str,
                       interval_seconds: float, params: dict | None = None,
                       tags: list[str] | None = None) -> str:
        job = ScheduledJob(
            id=generate_id("job", 10),
            name=name, job_type="recurring",
            interval_seconds=interval_seconds,
            next_run=time.time() + interval_seconds,
            handler=handler, params=params or {},
            tags=tags or [],
        )
        return self.add_job(job)

    def add_once(self, name: str, handler: str, delay_seconds: float = 0,
                  params: dict | None = None) -> str:
        job = ScheduledJob(
            id=generate_id("job", 10),
            name=name, job_type="once",
            next_run=time.time() + delay_seconds,
            handler=handler, params=params or {},
        )
        return self.add_job(job)

    def get_job(self, job_id: str) -> ScheduledJob | None:
        return self.jobs.get(job_id)

    def cancel(self, job_id: str):
        self.jobs.pop(job_id, None)
        self._save()

    def due_jobs(self) -> list[ScheduledJob]:
        return [j for j in self.jobs.values() if j.is_due() and j.last_status != "running"]

    def tick(self) -> list[tuple[str, str, Any]]:
        """Execute all due jobs. Returns [(job_id, status, result)]."""
        results = []
        for job in self.due_jobs():
            result = self._execute(job)
            results.append((job.id, job.last_status, result))
        return results

    def run_forever(self, tick_interval: float = 1.0):
        """Run the scheduler loop (blocking)."""
        self._running = True
        while self._running:
            self.tick()
            time.sleep(tick_interval)

    def stop(self):
        self._running = False

    def _execute(self, job: ScheduledJob) -> Any:
        job.last_status = "running"
        job.retry_count += 1
        handler = self._handlers.get(job.handler)
        if not handler:
            job.last_status = "failed"
            return None

        try:
            if job.timeout > 0:
                import signal
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Job {job.id} timed out after {job.timeout}s")
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(job.timeout))

            result = handler(**job.params)

            if job.timeout > 0:
                signal.alarm(0)

            job.last_status = "success"
            job.last_run = time.time()

            if job.job_type == "recurring":
                job.next_run = time.time() + job.interval_seconds
                job.retry_count = 0
            elif job.job_type == "once":
                pass  # stays as success

            self._save()
            return result

        except Exception as e:
            job.last_status = "failed"
            job.last_run = time.time()
            if job.job_type == "recurring" and job.retry_count < job.max_retries:
                job.next_run = time.time() + job.interval_seconds
            self._save()
            return str(e)

    def job_count(self) -> int:
        return len(self.jobs)

    def summary(self) -> dict[str, Any]:
        statuses = {}
        for j in self.jobs.values():
            statuses[j.last_status] = statuses.get(j.last_status, 0) + 1
        return {
            "total_jobs": len(self.jobs),
            "due_jobs": len(self.due_jobs()),
            "status_distribution": statuses,
            "handlers_registered": len(self._handlers),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "scheduler_state.json"

    def _save(self):
        data = {jid: j.to_dict() for jid, j in self.jobs.items()}
        (self._state_path()).write_text(json.dumps(data, indent=2))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.jobs = {jid: ScheduledJob.from_dict(jd) for jid, jd in data.items()}
            except Exception:
                pass
