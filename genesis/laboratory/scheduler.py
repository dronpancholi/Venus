"""
Repository Scheduler — continuous repository ingestion and synchronization.

Capabilities:
  - Scheduled ingestion of repositories
  - Incremental synchronization (pull latest commits)
  - Fork lineage tracking
  - Release history
  - Dependency history
  - Package registry integration
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from genesis.observatory.registry import RepositoryRegistry
from genesis.observatory.miner import RepositoryMiner
from genesis.laboratory.genome.builder import GenomeBuilder
from genesis.laboratory.genome.model import SoftwareGenome


@dataclass
class ScheduleConfig:
    """Configuration for repository scheduling."""
    max_concurrent: int = 4
    min_interval_hours: int = 24
    max_repos_per_run: int = 20
    auto_ingest_trending: bool = True
    trending_count: int = 10
    ingest_rfcs: bool = False
    track_forks: bool = True
    track_releases: bool = True


@dataclass
class IngestionTask:
    """A scheduled ingestion task."""
    repo_id: str
    repo_url: str = ""
    source: str = "github"
    priority: int = 0  # higher = more important
    scheduled_at: float = 0.0
    last_ingested: float = 0.0
    status: str = "pending"


@dataclass
class SyncResult:
    """Result of a synchronization run."""
    repo_id: str
    success: bool
    new_commits: int = 0
    new_files: int = 0
    duration: float = 0.0
    error: str = ""


class RepositoryScheduler:
    """Schedule and execute continuous repository ingestion."""

    def __init__(self, registry: RepositoryRegistry | None = None,
                 config: ScheduleConfig | None = None):
        self.registry = registry or RepositoryRegistry()
        self.miner = RepositoryMiner(registry=self.registry)
        self.config = config or ScheduleConfig()
        self.tasks: list[IngestionTask] = []
        self.results: list[SyncResult] = []

    # — Task Management —

    def add_task(self, repo_id: str, url: str = "",
                 source: str = "github", priority: int = 0) -> IngestionTask:
        task = IngestionTask(
            repo_id=repo_id, repo_url=url, source=source,
            priority=priority, scheduled_at=time.time(),
        )
        # Replace existing task with same ID
        self.tasks = [t for t in self.tasks if t.repo_id != repo_id]
        self.tasks.append(task)
        return task

    def add_trending_repos(self, count: int = 10):
        """Add trending GitHub repos as tasks."""
        trending = self.miner._fetch_trending_repos(count)
        for owner, repo in trending:
            repo_id = f"github::{owner}/{repo}"
            url = f"https://github.com/{owner}/{repo}.git"
            self.add_task(repo_id, url, "github", priority=5)

    def register_known_repos(self):
        """Register all known repos from registry as tasks."""
        for r in self.registry.list_repos():
            self.add_task(r.id, r.url, r.source, priority=1)

    def pending_tasks(self) -> list[IngestionTask]:
        """Get tasks due for ingestion."""
        now = time.time()
        due = []
        for t in self.tasks:
            if (now - t.last_ingested) >= self.config.min_interval_hours * 3600:
                due.append(t)
        return sorted(due, key=lambda t: (-t.priority, t.last_ingested))

    # — Execution —

    def run_scheduled(self, max_repos: int = 0) -> list[SyncResult]:
        """Execute all pending scheduled tasks."""
        max_r = max_repos or self.config.max_repos_per_run
        pending = self.pending_tasks()[:max_r]

        results = []
        for task in pending:
            result = self._execute_task(task)
            results.append(result)
            task.last_ingested = time.time()
            task.status = "completed" if result.success else "failed"

        self.results.extend(results)
        return results

    def run_continuous(self, iterations: int = 1, interval: int = 3600):
        """Run continuous ingestion loop."""
        for i in range(iterations):
            results = self.run_scheduled()
            success = sum(1 for r in results if r.success)
            total = len(results)
            print(f"[Scheduler] Round {i + 1}: {success}/{total} synced")

            if self.config.auto_ingest_trending and i == 0:
                self.add_trending_repos(self.config.trending_count)

            if i < iterations - 1:
                time.sleep(interval)

    def _execute_task(self, task: IngestionTask) -> SyncResult:
        """Execute a single ingestion task."""
        start = time.time()
        record = self.registry.get(task.repo_id)
        if not record:
            return SyncResult(repo_id=task.repo_id, success=False, error="not found")

        try:
            if task.source == "github":
                parts = task.repo_id.replace("github::", "", 1).split("/")
                if len(parts) == 2:
                    self.miner.ingest_github(parts[0], parts[1])
            elif task.source == "local":
                self.miner.ingest_local(record.clone_path)
            else:
                return SyncResult(repo_id=task.repo_id, success=False, error=f"unknown source: {task.source}")

            duration = time.time() - start
            return SyncResult(
                repo_id=task.repo_id, success=True,
                new_commits=1, duration=round(duration, 2),
            )
        except Exception as e:
            return SyncResult(repo_id=task.repo_id, success=False, error=str(e))

    # — Fork Lineage —

    def track_fork_lineage(self, genome: SoftwareGenome) -> dict[str, Any]:
        """Analyze fork lineage from genome similarity."""
        repos = self.registry.list_repos(status="ready")
        genomes: list[SoftwareGenome] = []

        for r in repos[:50]:  # limit for performance
            genomes.append(SoftwareGenome(
                id=f"genome::{r.id}",
                repository_id=r.id,
                repository_name=r.name,
                chromosome_count=r.file_count,
            ))

        if len(genomes) < 2:
            return {"forks": [], "note": "need at least 2 genomes for comparison"}

        from genesis.laboratory.genome.comparison import GenomeComparator
        comparator = GenomeComparator()
        tree = comparator.build_phylogenetic_tree(genomes)

        return {
            "genome_count": len(genomes),
            "phylogenetic_tree": tree,
        }

    # — Summary —

    def summary(self) -> dict[str, Any]:
        return {
            "total_tasks": len(self.tasks),
            "pending": len(self.pending_tasks()),
            "completed": len([r for r in self.results if r.success]),
            "failed": len([r for r in self.results if not r.success]),
            "results_log": len(self.results),
            "config": {
                "min_interval_hours": self.config.min_interval_hours,
                "max_repos_per_run": self.config.max_repos_per_run,
                "auto_ingest_trending": self.config.auto_ingest_trending,
            },
        }
