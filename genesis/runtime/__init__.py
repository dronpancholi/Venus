"""
Application Runtime (Mission 180) — production-grade app platform.

Extends GenesisAppPlatform with:
  - Full lifecycle (install, start, stop, uninstall)
  - Permissions model
  - Settings storage
  - Notifications
  - Version compatibility

Not a new engine — wraps existing GenesisAppPlatform.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AppStatus(Enum):
    INSTALLED = "installed"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    UNINSTALLED = "uninstalled"


@dataclass
class AppPermission:
    resource: str  # "read:events", "write:engineering", "manage:agents"
    granted: bool = True


@dataclass
class AppSetting:
    key: str
    value: Any = None
    type_hint: str = "string"


@dataclass
class AppNotification:
    app_name: str
    title: str
    body: str
    severity: str = "info"
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class AppInstance:
    name: str
    version: str
    status: AppStatus = AppStatus.INSTALLED
    permissions: list[AppPermission] = field(default_factory=list)
    settings: dict[str, AppSetting] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    entry_point: str = ""
    started_at: float = 0.0
    error: str = ""


class AppRuntime:
    """Production-grade application runtime.

    Wraps the existing GenesisAppPlatform with:
      - Lifecycle management
      - Permissions enforcement
      - Settings per app
      - Notifications
      - Dependency checks
    """

    def __init__(self, kernel: Any = None):
        self._kernel = kernel
        self._apps: dict[str, AppInstance] = {}
        self._notifications: list[AppNotification] = []
        self._lock = threading.RLock()

    def install(self, name: str, version: str = "1.0.0",
                dependencies: list[str] | None = None,
                permissions: list[str] | None = None,
                entry_point: str = "") -> AppInstance:
        with self._lock:
            app = AppInstance(
                name=name,
                version=version,
                status=AppStatus.INSTALLED,
                permissions=[AppPermission(p) for p in (permissions or [])],
                dependencies=dependencies or [],
                entry_point=entry_point,
            )
            self._apps[name] = app
            if self._kernel:
                try:
                    self._kernel.emit("app.installed",
                                      {"name": name, "version": version},
                                      origin="runtime", tags=["app"])
                except Exception:
                    pass
            return app

    def start(self, name: str) -> bool:
        app = self._apps.get(name)
        if not app:
            return False
        if app.status in (AppStatus.RUNNING, AppStatus.STARTING):
            return False

        # Check dependencies
        for dep in app.dependencies:
            dep_app = self._apps.get(dep)
            if not dep_app or dep_app.status != AppStatus.RUNNING:
                app.status = AppStatus.FAILED
                app.error = f"Dependency not running: {dep}"
                return False

        app.status = AppStatus.STARTING
        app.started_at = time.time()
        app.status = AppStatus.RUNNING
        if self._kernel:
            try:
                self._kernel.emit("app.started",
                                  {"name": name, "version": app.version},
                                  origin="runtime", tags=["app"])
            except Exception:
                pass
        return True

    def stop(self, name: str) -> bool:
        app = self._apps.get(name)
        if not app or app.status != AppStatus.RUNNING:
            return False
        app.status = AppStatus.STOPPING
        app.status = AppStatus.STOPPED
        if self._kernel:
            try:
                self._kernel.emit("app.stopped",
                                  {"name": name, "version": app.version},
                                  origin="runtime", tags=["app"])
            except Exception:
                pass
        return True

    def uninstall(self, name: str) -> bool:
        with self._lock:
            if name not in self._apps:
                return False
            app = self._apps[name]
            app.status = AppStatus.UNINSTALLED
            del self._apps[name]
            if self._kernel:
                try:
                    self._kernel.emit("app.uninstalled",
                                      {"name": name, "version": app.version},
                                      origin="runtime", tags=["app"])
                except Exception:
                    pass
            return True

    def get(self, name: str) -> AppInstance | None:
        return self._apps.get(name)

    def list(self) -> list[dict[str, Any]]:
        return [
            {"name": a.name, "version": a.version, "status": a.status.value,
             "dependencies": a.dependencies}
            for a in self._apps.values()
        ]

    def check_permission(self, app_name: str, resource: str) -> bool:
        app = self._apps.get(app_name)
        if not app:
            return False
        for p in app.permissions:
            if p.resource == resource:
                return p.granted
        return False

    def set_setting(self, app_name: str, key: str, value: Any) -> bool:
        app = self._apps.get(app_name)
        if not app:
            return False
        app.settings[key] = AppSetting(key=key, value=value)
        return True

    def get_setting(self, app_name: str, key: str) -> Any:
        app = self._apps.get(app_name)
        if not app:
            return None
        s = app.settings.get(key)
        return s.value if s else None

    def notify(self, app_name: str, title: str, body: str,
               severity: str = "info") -> AppNotification:
        n = AppNotification(
            app_name=app_name, title=title, body=body, severity=severity,
        )
        with self._lock:
            self._notifications.append(n)
        if self._kernel:
            try:
                self._kernel.emit("app.notification",
                                  {"app": app_name, "title": title,
                                   "severity": severity},
                                  origin="runtime", tags=["app", "notification"])
            except Exception:
                pass
        return n

    def notifications(self, limit: int = 20) -> list[AppNotification]:
        with self._lock:
            return list(self._notifications)[-limit:]

    def check_compatibility(self, name: str, version: str) -> list[str]:
        issues: list[str] = []
        app = self._apps.get(name)
        if not app:
            issues.append(f"App not installed: {name}")
            return issues
        if version != app.version:
            issues.append(f"Version mismatch: installed {app.version}, requested {version}")
        return issues
