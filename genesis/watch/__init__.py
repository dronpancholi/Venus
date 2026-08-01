"""
Continuous Engineering (Mission 62) — watches repositories, git, deps, and providers,
emitting Fabric events for every change so the system stays synchronized.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from genesis.fabric.events import EngineeringEvent, EventSeverity
from genesis.fabric.kernel import FabricKernel


@dataclass
class WatcherState:
    active: bool = True
    last_scan: float = 0.0
    scan_count: int = 0
    change_count: int = 0
    error_count: int = 0
    last_error: str = ""


class AutonomousTrigger(ABC):
    """A trigger that runs automatically when certain conditions are met."""

    def __init__(self, name: str, kernel: Any = None):
        self.name = name
        self._kernel = kernel

    @abstractmethod
    def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Evaluate conditions and return actions to execute."""
        ...


class Watcher(ABC):
    """Base class for all continuous engineering watchers."""

    def __init__(self, name: str, kernel: FabricKernel | None = None,
                 interval_secs: float = 5.0):
        self.name = name
        self._kernel = kernel or FabricKernel.instance()
        self._interval = interval_secs
        self._state = WatcherState()
        self._lock = threading.RLock()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._triggers: list[AutonomousTrigger] = []

    def add_trigger(self, trigger: AutonomousTrigger) -> None:
        self._triggers.append(trigger)

    @abstractmethod
    def scan(self) -> list[EngineeringEvent]:
        """Scan for changes and return events. Called every interval."""
        ...

    def evaluate_triggers(self) -> list[dict[str, Any]]:
        """Evaluate all autonomous triggers."""
        context = {"watcher": self.name, "state": self._state}
        actions = []
        for trigger in self._triggers:
            try:
                actions.extend(trigger.evaluate(context))
            except Exception:
                pass
        return actions

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._state.active = True
            self._thread = threading.Thread(target=self._loop, daemon=True,
                                            name=f"watch-{self.name}")
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        with self._lock:
            self._state.active = False

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                events = self.scan()
                with self._lock:
                    self._state.last_scan = time.time()
                    self._state.scan_count += 1
                for event in events:
                    self._kernel.emit(
                        event_type=event.type,
                        payload=event.payload,
                        origin=event.origin or self.name,
                        tags=event.tags or ["watch"],
                        severity=event.severity,
                        confidence=event.confidence,
                    )
                    with self._lock:
                        self._state.change_count += 1
            except Exception as e:
                with self._lock:
                    self._state.error_count += 1
                    self._state.last_error = str(e)
            self._stop_event.wait(self._interval)

    @property
    def state(self) -> WatcherState:
        with self._lock:
            return WatcherState(
                active=self._state.active,
                last_scan=self._state.last_scan,
                scan_count=self._state.scan_count,
                change_count=self._state.change_count,
                error_count=self._state.error_count,
                last_error=self._state.last_error,
            )


class FilesystemWatcher(Watcher):
    """Watches a directory tree for file changes using checksums."""

    def __init__(self, root_path: str | Path, kernel: FabricKernel | None = None,
                 interval_secs: float = 3.0, extensions: list[str] | None = None):
        super().__init__("filesystem", kernel, interval_secs)
        self._root = Path(root_path)
        self._extensions = extensions or [".py", ".md", ".toml", ".cfg", ".json", ".yaml", ".yml"]
        self._checksums: dict[str, str] = {}

    def scan(self) -> list[EngineeringEvent]:
        events: list[EngineeringEvent] = []
        current: dict[str, str] = {}

        for path in self._root.rglob("*"):
            if not path.is_file():
                continue
            if self._extensions and path.suffix not in self._extensions:
                continue
            try:
                digest = self._hash_file(path)
            except (IOError, PermissionError):
                continue
            rel = str(path.relative_to(self._root))
            current[rel] = digest

            if rel not in self._checksums:
                events.append(EngineeringEvent(
                    type="fs.file.created",
                    origin="filesystem_watcher",
                    payload={"path": rel, "size": path.stat().st_size},
                    tags=["watch", "filesystem", "created"],
                ))
            elif self._checksums[rel] != digest:
                events.append(EngineeringEvent(
                    type="fs.file.changed",
                    origin="filesystem_watcher",
                    payload={"path": rel, "size": path.stat().st_size},
                    tags=["watch", "filesystem", "changed"],
                ))

        for rel in set(self._checksums) - set(current):
            events.append(EngineeringEvent(
                type="fs.file.deleted",
                origin="filesystem_watcher",
                payload={"path": rel},
                tags=["watch", "filesystem", "deleted"],
            ))

        self._checksums = current
        return events

    @staticmethod
    def _hash_file(path: Path, chunk_size: int = 65536) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()[:32]


class GitWatcher(Watcher):
    """Watches a git repository for new commits."""

    def __init__(self, root_path: str | Path, kernel: FabricKernel | None = None,
                 interval_secs: float = 10.0):
        super().__init__("git", kernel, interval_secs)
        self._root = Path(root_path)
        self._last_hash = self._current_head()

    def scan(self) -> list[EngineeringEvent]:
        head = self._current_head()
        if not head:
            return []
        if head == self._last_hash:
            return []
        self._last_hash = head
        return [
            EngineeringEvent(
                type="git.commit.pushed",
                origin="git_watcher",
                payload={"hash": head, "repository": str(self._root)},
                tags=["watch", "git"],
            )
        ]

    def _current_head(self) -> str:
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, cwd=self._root, timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""


class ProviderWatcher(Watcher):
    """Periodically checks AI provider health and emits status events."""

    def __init__(self, kernel: FabricKernel | None = None, interval_secs: float = 30.0):
        super().__init__("provider", kernel, interval_secs)
        self._last_health: dict[str, bool] = {}

    def scan(self) -> list[EngineeringEvent]:
        from genesis.ai.registry import ProviderRegistry
        events: list[EngineeringEvent] = []
        for provider in ProviderRegistry.list_providers():
            try:
                health = provider.health()
                prev = self._last_health.get(provider.provider_id)
                if prev is not None and prev != health.healthy:
                    events.append(EngineeringEvent(
                        type="provider.status.changed",
                        origin="provider_watcher",
                        payload={
                            "provider_id": provider.provider_id,
                            "healthy": health.healthy,
                            "latency_ms": health.latency_ms,
                            "message": health.message,
                        },
                        severity=EventSeverity.WARNING if not health.healthy else EventSeverity.INFO,
                        tags=["watch", "provider"],
                    ))
                self._last_health[provider.provider_id] = health.healthy
            except Exception:
                pass
        return events


class TwinRefreshTrigger(AutonomousTrigger):
    """Trigger a digital twin refresh when files change."""

    def __init__(self, kernel: Any):
        super().__init__("twin_refresh", kernel)

    def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        state = context.get("state")
        if not state or state.change_count == 0:
            return []
        return [{"action": "refresh_twin", "reason": f"{state.change_count} file changes detected"}]


class CopilotTrigger(AutonomousTrigger):
    """Trigger copilot suggestions periodically."""

    def __init__(self, kernel: Any):
        super().__init__("copilot", kernel)

    def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        state = context.get("state")
        if not state or state.scan_count < 3:
            return []
        return [{"action": "generate_suggestions", "reason": "periodic suggestion check"}]


class ContinuousEngineering:
    """Manages all watchers as a group. Start once, stop on shutdown."""

    def __init__(self, kernel: FabricKernel | None = None):
        self._kernel = kernel or FabricKernel.instance()
        self._watchers: dict[str, Watcher] = {}
        self._autonomous_triggers: list[AutonomousTrigger] = []

    def add_watcher(self, watcher: Watcher):
        self._watchers[watcher.name] = watcher

    def add_autonomous_trigger(self, trigger: AutonomousTrigger) -> None:
        self._autonomous_triggers.append(trigger)

    def run_autonomous_triggers(self) -> list[dict[str, Any]]:
        """Evaluate all autonomous triggers across all watchers."""
        all_actions = []
        for watcher in self._watchers.values():
            watcher_actions = watcher.evaluate_triggers()
            all_actions.extend(watcher_actions)
            for action in watcher_actions:
                self._execute_autonomous_action(action)
        for trigger in self._autonomous_triggers:
            context = {"all_watchers": self.states()}
            try:
                actions = trigger.evaluate(context)
                all_actions.extend(actions)
                for action in actions:
                    self._execute_autonomous_action(action)
            except Exception:
                pass
        return all_actions

    def _execute_autonomous_action(self, action: dict[str, Any]) -> None:
        action_name = action.get("action", "")
        reason = action.get("reason", "")
        k = self._kernel
        try:
            if action_name == "refresh_twin" and hasattr(k, 'twin'):
                if hasattr(k.twin, 'scan'):
                    k.twin.scan()
                    if hasattr(k, 'observability'):
                        k.observability.record(
                            type_=__import__('genesis.observability.engine', fromlist=['ActionType']).ActionType.TWIN_SCAN,
                            subsystem="continuous_engineering", action="autonomous_twin_scan",
                            detail=reason,
                        )
            elif action_name == "generate_suggestions" and hasattr(k, 'proactive_copilot'):
                if hasattr(k.proactive_copilot, 'generate'):
                    k.proactive_copilot.generate()
        except Exception:
            pass

    def start_all(self):
        for name, watcher in self._watchers.items():
            watcher.start()
        self._kernel.emit("continuous_engineering.started", {
            "watchers": list(self._watchers.keys()),
        }, origin="continuous_engineering")

    def stop_all(self):
        for watcher in self._watchers.values():
            watcher.stop()
        self._kernel.emit("continuous_engineering.stopped", {}, origin="continuous_engineering")

    def states(self) -> dict[str, WatcherState]:
        return {name: w.state for name, w in self._watchers.items()}

    def setup_defaults(self, repo_path: str | Path = "."):
        fs_watcher = FilesystemWatcher(repo_path, self._kernel)
        fs_watcher.add_trigger(TwinRefreshTrigger(self._kernel))
        self.add_watcher(fs_watcher)
        try:
            self.add_watcher(GitWatcher(repo_path, self._kernel))
        except Exception:
            pass
        self.add_watcher(ProviderWatcher(self._kernel))
        self.add_autonomous_trigger(CopilotTrigger(self._kernel))
        return self
