"""
Acquisition Orchestrator — integrates acquisition pipeline with the Engineering OS.

Schedules periodic acquisition runs, manages state persistence,
observes metrics, and handles failures through the OS components.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from genesis.acquisition import AcquisitionPipeline, AcquisitionSource
from genesis.acquisition.sources import (
    GitHubSource, GitLabSource, NPMSource, PyPISource, CargoSource,
    MavenSource, NuGetSource, GoSource, DockerSource,
    RFCSource, CVESource, NISTSource, CNCFSource, OWASPSource,
    IETFSource, W3CSource, ADRSource,
)
from genesis.utils.identity import generate_id


class AcquisitionOrchestrator:
    """
    Orchestrates the full acquisition lifecycle.

    Integrates with OS components via callbacks:
      - Scheduler: periodic acquisition runs
      - Queue: work items for targeted fetches
      - ObservationManager: metrics on acquisition throughput
      - RecoveryManager: event handlers for failures
      - CheckpointManager: state persistence hooks
    """

    def __init__(self, graph=None, persistence_dir: str = ""):
        self.pipeline = AcquisitionPipeline(graph=graph)
        self.persistence_dir = Path(persistence_dir or "~/.venus/acquisition").expanduser()
        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        self._last_run: dict[str, float] = {}
        self._stats: dict[str, dict[str, Any]] = {}

    def register_all_sources(self, config: dict[str, Any] | None = None):
        cfg = config or {}
        sources: list[AcquisitionSource] = [
            GitHubSource(
                token=cfg.get("github_token", ""),
                orgs=cfg.get("github_orgs", []),
            ),
            GitLabSource(
                token=cfg.get("gitlab_token", ""),
                groups=cfg.get("gitlab_groups", []),
            ),
            NPMSource(packages=cfg.get("npm_packages", [])),
            PyPISource(packages=cfg.get("pypi_packages", [])),
            CargoSource(crates=cfg.get("cargo_crates", [])),
            MavenSource(artifacts=cfg.get("maven_artifacts", [])),
            NuGetSource(packages=cfg.get("nuget_packages", [])),
            GoSource(modules=cfg.get("go_modules", [])),
            DockerSource(images=cfg.get("docker_images", [])),
            RFCSource(rfc_numbers=cfg.get("rfc_numbers", [])),
            CVESource(cve_ids=cfg.get("cve_ids", [])),
            NISTSource(publications=cfg.get("nist_publications", [])),
            CNCFSource(projects=cfg.get("cncf_projects", [])),
            OWASPSource(projects=cfg.get("owasp_projects", [])),
            IETFSource(documents=cfg.get("ietf_documents", [])),
            W3CSource(specs=cfg.get("w3c_specs", [])),
            ADRSource(adr_urls=cfg.get("adr_urls", [])),
        ]
        self.pipeline.register_many(*sources)

    def run_once(self, source_name: str = "") -> dict[str, int]:
        if source_name:
            count = self.pipeline.acquire_source(source_name)
            result = {source_name: count}
        else:
            result = self.pipeline.acquire_all()
        now = time.time()
        for name in result:
            self._last_run[name] = now
        self._update_stats(result)
        self._save_state()
        return result

    def _update_stats(self, results: dict[str, int]):
        for name, count in results.items():
            if name not in self._stats:
                self._stats[name] = {
                    "total_items": 0,
                    "total_runs": 0,
                    "last_count": 0,
                    "error_count": 0,
                }
            self._stats[name]["total_items"] += count
            self._stats[name]["total_runs"] += 1
            self._stats[name]["last_count"] = count
            if count == 0:
                self._stats[name]["error_count"] += 1

    def run_all(self) -> dict[str, int]:
        return self.run_once()

    def get_last_run(self, source: str) -> float:
        return self._last_run.get(source, 0.0)

    def get_stats(self) -> dict[str, Any]:
        return dict(self._stats)

    def summary(self) -> dict[str, Any]:
        return {
            "pipeline": self.pipeline.summary(),
            "stats": self._stats,
            "last_run_count": len(self._last_run),
            "sources_last_run": {
                k: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v))
                for k, v in self._last_run.items()
            },
        }

    def _save_state(self):
        state = {
            "last_run": self._last_run,
            "stats": self._stats,
            "updated_at": time.time(),
        }
        path = self.persistence_dir / "orchestrator_state.json"
        try:
            path.write_text(json.dumps(state, indent=2, default=str))
        except Exception:
            pass

    def load_state(self):
        path = self.persistence_dir / "orchestrator_state.json"
        if path.exists():
            try:
                state = json.loads(path.read_text())
                self._last_run = state.get("last_run", {})
                self._stats = state.get("stats", {})
            except Exception:
                pass
