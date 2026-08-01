from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SessionSnapshot:
    screen_id: str = "home"
    open_panels: list[str] = field(default_factory=list)
    open_projects: list[str] = field(default_factory=list)
    active_search: str = ""
    current_workflow_id: str = ""
    last_report: str = ""
    ai_session_id: str = ""
    context_summary: str = ""
    timestamp: float = 0.0
    environment: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "screen_id": self.screen_id,
            "open_panels": list(self.open_panels),
            "open_projects": list(self.open_projects),
            "active_search": self.active_search,
            "current_workflow_id": self.current_workflow_id,
            "last_report": self.last_report,
            "ai_session_id": self.ai_session_id,
            "context_summary": self.context_summary,
            "timestamp": self.timestamp,
            "environment": dict(self.environment),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionSnapshot:
        return cls(
            screen_id=data.get("screen_id", "home"),
            open_panels=list(data.get("open_panels", [])),
            open_projects=list(data.get("open_projects", [])),
            active_search=data.get("active_search", ""),
            current_workflow_id=data.get("current_workflow_id", ""),
            last_report=data.get("last_report", ""),
            ai_session_id=data.get("ai_session_id", ""),
            context_summary=data.get("context_summary", ""),
            timestamp=data.get("timestamp", 0.0),
            environment=dict(data.get("environment", {})),
        )


class WorkspaceMemory:
    _instance: WorkspaceMemory | None = None

    @classmethod
    def instance(cls) -> WorkspaceMemory:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if WorkspaceMemory._instance is not None:
            raise RuntimeError("WorkspaceMemory is a singleton. Use WorkspaceMemory.instance()")
        WorkspaceMemory._instance = self
        self._data: dict[str, Any] = {
            "last_screen": "home",
            "screen_history": [],
            "layout": {},
            "search_history": [],
            "command_history": [],
            "panels": {},
            "preferences": {
                "theme": "dark",
                "sidebar_visible": True,
                "activity_center_pinned": False,
            },
            "projects": {},
            "sessions": [],
            "current_task": "",
            "open_reports": [],
            "open_conversations": [],
        }
        self._lock = threading.RLock()
        self._persist_path: str | None = None
        self._dirty = False

    def boot(self, persist_path: str | None = None):
        if persist_path:
            self._persist_path = persist_path
            self._load()

    def _load(self):
        if not self._persist_path:
            return
        try:
            p = Path(self._persist_path)
            if p.exists():
                with open(p) as f:
                    loaded = json.load(f)
                    self._data.update(loaded)
        except Exception:
            pass

    def _save(self):
        if not self._persist_path or not self._dirty:
            return
        try:
            p = Path(self._persist_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, 'w') as f:
                json.dump(self._data, f, indent=2)
            self._dirty = False
        except Exception:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any):
        with self._lock:
            self._data[key] = value
            self._dirty = True

    def update(self, values: dict[str, Any]):
        with self._lock:
            self._data.update(values)
            self._dirty = True

    def get_project_state(self, project_id: str) -> dict[str, Any]:
        with self._lock:
            return self._data.setdefault("projects", {}).get(project_id, {})

    def set_project_state(self, project_id: str, state: dict[str, Any]):
        with self._lock:
            self._data.setdefault("projects", {})[project_id] = state
            self._dirty = True

    def record_navigation(self, screen_id: str):
        with self._lock:
            self._data["last_screen"] = screen_id
            history = self._data.setdefault("screen_history", [])
            history.append({"screen": screen_id, "timestamp": time.time()})
            if len(history) > 50:
                history.pop(0)
            self._dirty = True

    def record_search(self, query: str, source: str = ""):
        with self._lock:
            history = self._data.setdefault("search_history", [])
            history.append({"query": query, "source": source, "timestamp": time.time()})
            if len(history) > 100:
                history.pop(0)
            self._dirty = True

    def record_command(self, command: str):
        with self._lock:
            history = self._data.setdefault("command_history", [])
            history.append({"command": command, "timestamp": time.time()})
            if len(history) > 100:
                history.pop(0)
            self._dirty = True

    def recent_screens(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._data.get("screen_history", [])[-limit:])

    def recent_searches(self, limit: int = 10) -> list[str]:
        with self._lock:
            return [h["query"] for h in self._data.get("search_history", [])[-limit:]]

    def recent_commands(self, limit: int = 10) -> list[str]:
        with self._lock:
            return [h["command"] for h in self._data.get("command_history", [])[-limit:]]

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._data)

    def save_session(self, snapshot: SessionSnapshot) -> str:
        with self._lock:
            sessions = self._data.setdefault("sessions", [])
            snapshot.timestamp = time.time()
            snapshot.environment = dict(os.environ) if os.environ else {}
            sessions.append(snapshot.to_dict())
            if len(sessions) > 20:
                sessions.pop(0)
            self._dirty = True
        return f"session_{snapshot.timestamp}"

    def restore_latest_session(self) -> SessionSnapshot | None:
        with self._lock:
            sessions = self._data.get("sessions", [])
            if not sessions:
                return None
            latest = sessions[-1]
            return SessionSnapshot.from_dict(latest)

    def list_sessions(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._lock:
            sessions = self._data.get("sessions", [])
            return [
                {
                    "screen_id": s.get("screen_id", ""),
                    "timestamp": s.get("timestamp", 0),
                    "context": s.get("context_summary", "")[:100],
                    "projects": len(s.get("open_projects", [])),
                    "panels": len(s.get("open_panels", [])),
                }
                for s in sessions[-limit:]
            ]

    def set_current_task(self, task: str) -> None:
        self.set("current_task", task)

    def get_current_task(self) -> str:
        return self.get("current_task", "")

    def add_open_report(self, report_path: str) -> None:
        with self._lock:
            reports = self._data.setdefault("open_reports", [])
            if report_path not in reports:
                reports.append(report_path)
            self._dirty = True

    def add_open_conversation(self, conversation_id: str) -> None:
        with self._lock:
            convs = self._data.setdefault("open_conversations", [])
            if conversation_id not in convs:
                convs.append(conversation_id)
            self._dirty = True

    def restore_context(self) -> dict[str, Any]:
        session = self.restore_latest_session()
        if not session:
            return {"restored": False, "reason": "no_sessions"}
        return {
            "restored": True,
            "screen_id": session.screen_id,
            "open_panels": session.open_panels,
            "open_projects": session.open_projects,
            "active_search": session.active_search,
            "current_workflow_id": session.current_workflow_id,
            "last_report": session.last_report,
            "current_task": self.get_current_task(),
        }
