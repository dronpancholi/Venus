from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class NotificationSeverity(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Notification:
    id: str = ""
    title: str = ""
    message: str = ""
    severity: NotificationSeverity = NotificationSeverity.INFO
    source: str = ""
    timestamp: float = 0.0
    read: bool = False
    dismissed: bool = False
    action: str = ""
    action_label: str = ""
    category: str = "general"

    def __post_init__(self):
        if not self.id:
            from genesis.utils.identity import generate_id
            self.id = generate_id("notif", 8)
        if not self.timestamp:
            self.timestamp = time.time()


class ActivityCenter:
    _instance: ActivityCenter | None = None

    @classmethod
    def instance(cls) -> ActivityCenter:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if ActivityCenter._instance is not None:
            raise RuntimeError("ActivityCenter is a singleton. Use ActivityCenter.instance()")
        ActivityCenter._instance = self
        self._notifications: list[Notification] = []
        self._max_notifications = 500
        self._listeners: list[Callable[[Notification], None]] = []
        self._lock = threading.RLock()

    def notify(self, title: str, message: str = "",
               severity: NotificationSeverity = NotificationSeverity.INFO,
               source: str = "", category: str = "general",
               action: str = "", action_label: str = "") -> Notification:
        n = Notification(
            title=title, message=message, severity=severity,
            source=source, category=category,
            action=action, action_label=action_label,
        )
        with self._lock:
            self._notifications.append(n)
            if len(self._notifications) > self._max_notifications:
                self._notifications.pop(0)
        for listener in self._listeners:
            try:
                listener(n)
            except Exception:
                pass
        return n

    def mark_read(self, nid: str) -> bool:
        with self._lock:
            for n in self._notifications:
                if n.id == nid:
                    n.read = True
                    return True
        return False

    def mark_all_read(self):
        with self._lock:
            for n in self._notifications:
                n.read = True

    def dismiss(self, nid: str) -> bool:
        with self._lock:
            for n in self._notifications:
                if n.id == nid:
                    n.dismissed = True
                    return True
        return False

    def dismiss_all(self):
        with self._lock:
            for n in self._notifications:
                n.dismissed = True

    def subscribe(self, listener: Callable[[Notification], None]):
        with self._lock:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Callable):
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def unread_count(self) -> int:
        with self._lock:
            return sum(1 for n in self._notifications if not n.read and not n.dismissed)

    def recent(self, limit: int = 20, category: str = "",
               include_dismissed: bool = False) -> list[Notification]:
        with self._lock:
            result = list(self._notifications)
        if category:
            result = [n for n in result if n.category == category]
        if not include_dismissed:
            result = [n for n in result if not n.dismissed]
        result.sort(key=lambda n: n.timestamp, reverse=True)
        return result[:limit]

    def by_severity(self, severity: NotificationSeverity, limit: int = 20) -> list[Notification]:
        with self._lock:
            result = [n for n in self._notifications if n.severity == severity and not n.dismissed]
        result.sort(key=lambda n: n.timestamp, reverse=True)
        return result[:limit]

    def clear(self):
        with self._lock:
            self._notifications.clear()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = len(self._notifications)
            unread = sum(1 for n in self._notifications if not n.read and not n.dismissed)
            by_sev = {}
            for n in self._notifications:
                if not n.dismissed:
                    sev = n.severity.value
                    by_sev[sev] = by_sev.get(sev, 0) + 1
            return {
                "total": total,
                "unread": unread,
                "by_severity": by_sev,
                "listeners": len(self._listeners),
            }
