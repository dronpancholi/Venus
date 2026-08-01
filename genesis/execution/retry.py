from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class RetryPolicy:
    max_retries: int = 3
    base_delay_secs: float = 1.0
    max_delay_secs: float = 60.0
    backoff_multiplier: float = 2.0
    retryable_exceptions: tuple[type, ...] = (Exception,)

    def delay(self, attempt: int) -> float:
        d = self.base_delay_secs * (self.backoff_multiplier ** attempt)
        return min(d, self.max_delay_secs)

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return attempt < self.max_retries and isinstance(exception, self.retryable_exceptions)


@dataclass
class CompensationAction:
    id: str = ""
    name: str = ""
    handler: Callable | None = None
    compensated_at: float = 0.0
    status: str = "pending"
    error: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("comp", 12)

    def execute(self, context: dict[str, Any]) -> bool:
        if self.handler:
            try:
                self.handler(context)
                self.status = "completed"
                self.compensated_at = time.time()
                return True
            except Exception as e:
                self.status = "failed"
                self.error = str(e)
                return False
        self.status = "skipped"
        return True


class CompensationEngine:
    """Compensation and rollback for distributed operations."""

    def __init__(self):
        self._actions: dict[str, list[CompensationAction]] = {}
        self._history: list[dict[str, Any]] = []

    def register(self, transaction_id: str, action: CompensationAction):
        self._actions.setdefault(transaction_id, []).append(action)

    def compensate(self, transaction_id: str,
                   context: dict[str, Any] | None = None) -> list[CompensationAction]:
        actions = list(reversed(self._actions.get(transaction_id, [])))
        results: list[CompensationAction] = []
        for action in actions:
            success = action.execute(context or {})
            self._history.append({
                "transaction_id": transaction_id,
                "action": action.name,
                "status": action.status,
                "timestamp": time.time(),
            })
            results.append(action)
            if not success:
                break
        return results

    def rollback_all(self, context: dict[str, Any] | None = None) -> dict[str, int]:
        total = 0
        succeeded = 0
        for txn_id in list(self._actions.keys()):
            results = self.compensate(txn_id, context)
            total += len(results)
            succeeded += sum(1 for r in results if r.status == "completed")
        return {"total": total, "succeeded": succeeded}

    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def summary(self) -> dict[str, Any]:
        return {
            "active_transactions": len(self._actions),
            "total_compensations": len(self._history),
        }
