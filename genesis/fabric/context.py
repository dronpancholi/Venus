from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class CorrelationID:
    id: str = ""
    parent_id: str = ""
    source: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("cid", 16)
        if not self.created_at:
            self.created_at = time.time()

    def child(self, source: str = "") -> "CorrelationID":
        return CorrelationID(
            id=generate_id("cid", 16),
            parent_id=self.id,
            source=source,
        )


@dataclass
class TransactionSpan:
    """A span within a distributed transaction."""

    id: str = ""
    transaction_id: str = ""
    parent_span_id: str = ""
    operation: str = ""
    service: str = ""
    started_at: float = 0.0
    completed_at: float = 0.0
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("span", 12)
        if not self.started_at:
            self.started_at = time.time()

    def complete(self, status: str = "success"):
        self.completed_at = time.time()
        self.status = status

    @property
    def duration_ms(self) -> float:
        end = self.completed_at or time.time()
        return (end - self.started_at) * 1000


class Context:
    """Distributed context with correlation IDs, transaction IDs, and metadata."""

    def __init__(self, correlation_id: str = "",
                 transaction_id: str = "",
                 session_id: str = "",
                 metadata: dict[str, Any] | None = None):
        self.correlation_id = correlation_id or generate_id("corr", 12)
        self.transaction_id = transaction_id or ""
        self.session_id = session_id or ""
        self._metadata: dict[str, Any] = metadata or {}
        self._spans: dict[str, TransactionSpan] = {}
        self._created_at = time.time()

    def set(self, key: str, value: Any):
        self._metadata[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    def has(self, key: str) -> bool:
        return key in self._metadata

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def begin_span(self, operation: str, service: str = "") -> TransactionSpan:
        span = TransactionSpan(
            transaction_id=self.transaction_id,
            operation=operation,
            service=service,
        )
        self._spans[span.id] = span
        return span

    def end_span(self, span_id: str, status: str = "success"):
        span = self._spans.get(span_id)
        if span:
            span.complete(status)

    def spans(self) -> list[TransactionSpan]:
        return list(self._spans.values())

    def child(self) -> "Context":
        child_cid = CorrelationID(id=generate_id("cid", 16),
                                   parent_id=self.correlation_id).id
        return Context(
            correlation_id=child_cid,
            transaction_id=self.transaction_id,
            session_id=self.session_id,
            metadata=dict(self._metadata),
        )

    def summary(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "transaction_id": self.transaction_id,
            "session_id": self.session_id,
            "spans": len(self._spans),
            "metadata_keys": list(self._metadata.keys()),
            "age_secs": time.time() - self._created_at,
        }
