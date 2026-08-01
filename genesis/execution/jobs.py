from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class LongRunningJob:
    id: str = ""
    name: str = ""
    handler: Callable | None = None
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    checkpoint: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: str = ""
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("job", 14)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def duration_ms(self) -> float:
        end = self.completed_at or time.time()
        return (end - self.started_at) * 1000 if self.started_at else 0.0

    @property
    def running(self) -> bool:
        return self.status == JobStatus.RUNNING

    @property
    def finished(self) -> bool:
        return self.status in (JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED)


class JobManager:
    """Long-running job management with checkpoint/resume."""

    def __init__(self):
        self._jobs: dict[str, LongRunningJob] = {}
        self._lock = threading.RLock()

    def submit(self, name: str, handler: Callable | None = None) -> str:
        job = LongRunningJob(name=name, handler=handler)
        with self._lock:
            self._jobs[job.id] = job
        return job.id

    def start(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            job.status = JobStatus.RUNNING
            job.started_at = time.time()
            return True

    def update_progress(self, job_id: str, progress: float,
                        checkpoint: dict[str, Any] | None = None):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.progress = min(max(progress, 0.0), 1.0)
                if checkpoint:
                    job.checkpoint.update(checkpoint)

    def complete(self, job_id: str, result: Any = None):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.SUCCESS
                job.result = result
                job.completed_at = time.time()
                job.progress = 1.0

    def fail(self, job_id: str, error: str = ""):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.FAILED
                job.error = error
                job.completed_at = time.time()

    def pause(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.status == JobStatus.RUNNING:
                job.status = JobStatus.PAUSED
                return True
            return False

    def resume(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.status == JobStatus.PAUSED:
                job.status = JobStatus.RUNNING
                return True
            return False

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and not job.finished:
                job.status = JobStatus.CANCELLED
                job.completed_at = time.time()
                return True
            return False

    def get(self, job_id: str) -> LongRunningJob | None:
        return self._jobs.get(job_id)

    def list_jobs(self, status: JobStatus | None = None) -> list[LongRunningJob]:
        if status:
            return [j for j in self._jobs.values() if j.status == status]
        return list(self._jobs.values())

    def execute(self, job: LongRunningJob) -> Any:
        self.start(job.id)
        if job.handler:
            try:
                result = job.handler(job)
                self.complete(job.id, result)
                return result
            except Exception as e:
                self.fail(job.id, str(e))
                return None
        else:
            self.complete(job.id)
            return None

    def summary(self) -> dict[str, Any]:
        statuses: dict[str, int] = {}
        for j in self._jobs.values():
            statuses[j.status.value] = statuses.get(j.status.value, 0) + 1
        return {
            "jobs": len(self._jobs),
            "by_status": statuses,
        }
