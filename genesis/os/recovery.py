"""
RecoveryManager — restores system state from failures.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class RecoveryAction:
    """A recorded recovery action."""
    id: str = ""
    event: str = ""
    action: str = ""
    status: str = "pending"  # pending, success, failed
    details: str = ""
    started_at: float = 0.0
    completed_at: float = 0.0


class RecoveryManager:
    """
    Manages system recovery from failures.

    Recovery strategies:
      - Restart failed components
      - Restore from latest checkpoint
      - Execute recovery plans
      - Log all recovery actions
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "recovery"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.history: list[RecoveryAction] = []
        self._recovery_handlers: dict[str, Callable] = {}
        self._load()

    def register_handler(self, event_type: str, handler: Callable):
        """Register a recovery handler for a specific event type."""
        self._recovery_handlers[event_type] = handler

    def handle(self, event: str, context: dict[str, Any] | None = None) -> RecoveryAction:
        """Handle a recovery event."""
        action = RecoveryAction(
            id=generate_id("recover", 10),
            event=event,
            action=f"recovery_{event}",
            status="pending",
            started_at=time.time(),
        )

        handler = self._recovery_handlers.get(event)
        if handler:
            try:
                result = handler(**(context or {}))
                action.status = "success"
                action.details = str(result)[:500]
            except Exception as e:
                action.status = "failed"
                action.details = str(e)
        else:
            action.status = "failed"
            action.details = f"No handler registered for event: {event}"

        action.completed_at = time.time()
        self.history.append(action)
        self._save()
        return action

    def restore_from_checkpoint(self, checkpoint_snapshot: dict[str, Any]) -> dict[str, Any]:
        """Attempt to restore system from a checkpoint snapshot."""
        results = {}
        for key, value in checkpoint_snapshot.items():
            try:
                handler = self._recovery_handlers.get(f"restore:{key}")
                if handler:
                    results[key] = handler(value)
                else:
                    results[key] = value
            except Exception as e:
                results[key] = f"Restore failed: {e}"
        return results

    def recent_actions(self, limit: int = 10) -> list[RecoveryAction]:
        return sorted(self.history, key=lambda a: -a.started_at)[:limit]

    def failure_rate(self) -> float:
        if not self.history:
            return 0.0
        failed = sum(1 for a in self.history if a.status == "failed")
        return failed / len(self.history)

    def summary(self) -> dict[str, Any]:
        statuses = {}
        for a in self.history:
            statuses[a.status] = statuses.get(a.status, 0) + 1
        return {
            "total_actions": len(self.history),
            "status_distribution": statuses,
            "failure_rate": self.failure_rate(),
            "handlers_registered": len(self._recovery_handlers),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "recovery_history.json"

    def _save(self):
        data = [a.__dict__ for a in self.history]
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.history = [RecoveryAction(**rd) for rd in data]
            except Exception:
                pass
