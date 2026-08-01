"""
EventWatcherSystem — autonomous event-driven watchers for the Engineering OS.

Each watcher monitors an external event source and emits signals into
the runtime for processing. Integrates with:
  - AutonomousRuntime event system
  - PersistentScheduler for periodic checks
  - ObservationManager for metrics
  - RecoveryManager for failure handling
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class WatcherEvent:
    source: str = ""
    event_type: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    severity: str = "info"  # info, warning, error, critical

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp,
            "severity": self.severity,
        }


class BaseWatcher(ABC):
    """Base class for all event watchers."""

    def __init__(self, name: str = "", check_interval: float = 60.0):
        self.name = name or self.__class__.__name__
        self.check_interval = check_interval
        self._last_check: float = 0.0
        self._handlers: dict[str, list[Callable]] = {}
        self._enabled = True

    @abstractmethod
    def check(self) -> list[WatcherEvent]:
        ...

    def on(self, event_type: str, handler: Callable):
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event: WatcherEvent):
        for handler in self._handlers.get(event.event_type, []):
            handler(event)
        for handler in self._handlers.get("*", []):
            handler(event)

    def tick(self) -> list[WatcherEvent]:
        if not self._enabled:
            return []
        now = time.time()
        if now - self._last_check < self.check_interval:
            return []
        self._last_check = now
        events = self.check()
        for event in events:
            self.emit(event)
        return events

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self._enabled,
            "check_interval": self.check_interval,
            "handlers": len(self._handlers),
        }


class GitWatcher(BaseWatcher):
    """Watches a git repository for changes (commits, branches, tags)."""

    def __init__(self, repo_path: str | Path = ".",
                 check_interval: float = 300.0):
        super().__init__(name="git_watcher", check_interval=check_interval)
        self.repo_path = Path(repo_path)
        self._last_commit: str = ""
        self._last_branch: str = ""

    def check(self) -> list[WatcherEvent]:
        events = []
        if not (self.repo_path / ".git").exists():
            return events

        try:
            branch = self._run("git rev-parse --abbrev-ref HEAD")
            commit = self._run("git rev-parse HEAD")
            changes = self._run("git status --porcelain")

            if self._last_commit and commit != self._last_commit:
                log = self._run(
                    f"git log --oneline {self._last_commit}..{commit} --no-merges -10"
                )
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="new_commit",
                    data={
                        "repo": str(self.repo_path),
                        "branch": branch,
                        "old_commit": self._last_commit,
                        "new_commit": commit,
                        "log": log,
                    },
                    timestamp=time.time(),
                    severity="info",
                ))

            if self._last_branch and branch != self._last_branch:
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="branch_change",
                    data={
                        "repo": str(self.repo_path),
                        "old_branch": self._last_branch,
                        "new_branch": branch,
                    },
                    timestamp=time.time(),
                    severity="info",
                ))

            if changes:
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="working_tree_changes",
                    data={
                        "repo": str(self.repo_path),
                        "changes": changes,
                        "changed_files": len(changes.split("\n")) if changes else 0,
                    },
                    timestamp=time.time(),
                    severity="info",
                ))

            self._last_commit = commit
            self._last_branch = branch

        except Exception as e:
            events.append(WatcherEvent(
                source=self.name,
                event_type="check_error",
                data={"repo": str(self.repo_path), "error": str(e)},
                timestamp=time.time(),
                severity="error",
            ))

        return events

    def _run(self, cmd: str) -> str:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            cwd=self.repo_path,
            timeout=30,
        )
        return result.stdout.strip()


class FileWatcher(BaseWatcher):
    """Watches files and directories for changes."""

    def __init__(self, paths: list[str | Path] | None = None,
                 patterns: list[str] | None = None,
                 check_interval: float = 60.0):
        super().__init__(name="file_watcher", check_interval=check_interval)
        self.paths = [Path(p) for p in (paths or [])]
        self.patterns = patterns or ["*"]
        self._file_states: dict[str, tuple[float, int]] = {}

    def check(self) -> list[WatcherEvent]:
        events = []
        for path in self.paths:
            key = str(path)
            if path.is_file():
                events.extend(self._check_file(path))
            elif path.is_dir():
                events.extend(self._check_dir(path))
            elif key in self._file_states:
                del self._file_states[key]
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="file_deleted",
                    data={"path": key},
                    timestamp=time.time(),
                    severity="warning",
                ))
        return events

    def _check_file(self, path: Path) -> list[WatcherEvent]:
        events = []
        key = str(path)
        try:
            stat = path.stat()
            mtime = stat.st_mtime
            size = stat.st_size

            old_state = self._file_states.get(key)
            if old_state is None:
                self._file_states[key] = (mtime, size)
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="file_created",
                    data={"path": key, "size": size},
                    timestamp=time.time(),
                    severity="info",
                ))
            elif abs(mtime - old_state[0]) > 0.01 or size != old_state[1]:
                self._file_states[key] = (mtime, size)
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="file_modified",
                    data={"path": key, "size": size, "old_size": old_state[1]},
                    timestamp=time.time(),
                    severity="info",
                ))
        except FileNotFoundError:
            if key in self._file_states:
                del self._file_states[key]
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="file_deleted",
                    data={"path": key},
                    timestamp=time.time(),
                    severity="warning",
                ))

        return events

    def _check_dir(self, path: Path) -> list[WatcherEvent]:
        events = []
        current_files: set[str] = set()
        for f in path.rglob("*"):
            if f.is_file():
                for pattern in self.patterns:
                    if f.match(pattern):
                        current_files.add(str(f))
                        events.extend(self._check_file(f))
                        break

        for key in list(self._file_states.keys()):
            if key.startswith(str(path)) and key not in current_files:
                try:
                    p = Path(key)
                    if not p.exists():
                        del self._file_states[key]
                        events.append(WatcherEvent(
                            source=self.name,
                            event_type="file_deleted",
                            data={"path": key},
                            timestamp=time.time(),
                            severity="warning",
                        ))
                except Exception:
                    pass

        return events


class ProcessWatcher(BaseWatcher):
    """Watches system processes and resource usage."""

    def __init__(self, check_interval: float = 60.0):
        super().__init__(name="process_watcher", check_interval=check_interval)
        self._thresholds = {
            "cpu_percent": 95.0,
            "memory_percent": 90.0,
            "disk_percent": 90.0,
        }

    def set_threshold(self, metric: str, value: float):
        self._thresholds[metric] = value

    def check(self) -> list[WatcherEvent]:
        events = []
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            if cpu > self._thresholds.get("cpu_percent", 95):
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="high_cpu",
                    data={"cpu_percent": cpu},
                    timestamp=time.time(),
                    severity="warning",
                ))

            if memory.percent > self._thresholds.get("memory_percent", 90):
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="high_memory",
                    data={
                        "memory_percent": memory.percent,
                        "available_mb": memory.available / 1024 / 1024,
                    },
                    timestamp=time.time(),
                    severity="warning",
                ))

            if disk.percent > self._thresholds.get("disk_percent", 90):
                events.append(WatcherEvent(
                    source=self.name,
                    event_type="low_disk",
                    data={
                        "disk_percent": disk.percent,
                        "free_gb": disk.free / 1024 / 1024 / 1024,
                    },
                    timestamp=time.time(),
                    severity="warning",
                ))

        except ImportError:
            pass
        except Exception as e:
            events.append(WatcherEvent(
                source=self.name,
                event_type="check_error",
                data={"error": str(e)},
                timestamp=time.time(),
                severity="error",
            ))

        return events


class WatcherRegistry:
    """Registry of all active watchers, managed by AutonomousRuntime."""

    def __init__(self):
        self._watchers: dict[str, BaseWatcher] = {}
        self._event_history: list[WatcherEvent] = []
        self._max_history: int = 1000

    def register(self, watcher: BaseWatcher):
        self._watchers[watcher.name] = watcher

    def get(self, name: str) -> BaseWatcher | None:
        return self._watchers.get(name)

    def unregister(self, name: str):
        self._watchers.pop(name, None)

    def all(self) -> list[BaseWatcher]:
        return list(self._watchers.values())

    def names(self) -> list[str]:
        return list(self._watchers.keys())

    def tick_all(self) -> list[WatcherEvent]:
        events = []
        for watcher in self._watchers.values():
            try:
                watcher_events = watcher.tick()
                events.extend(watcher_events)
            except Exception:
                pass
        self._event_history.extend(events)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        return events

    def recent_events(self, limit: int = 50) -> list[WatcherEvent]:
        return self._event_history[-limit:]

    def summary(self) -> dict[str, Any]:
        return {
            "watchers": {w.name: w.summary() for w in self._watchers.values()},
            "recent_events": len(self._event_history),
        }
