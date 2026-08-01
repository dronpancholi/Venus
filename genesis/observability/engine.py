from __future__ import annotations

import time
import json
import threading
import traceback
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable


class ActionType(Enum):
    API_CALL = "api_call"
    DESKTOP_INTERACTION = "desktop_interaction"
    AI_REQUEST = "ai_request"
    WORKFLOW = "workflow"
    EVENT = "event"
    ENGINEERING_OBJECT_MUTATION = "engineering_object_mutation"
    PLUGIN = "plugin"
    SEARCH = "search"
    RECOMMENDATION = "recommendation"
    REPORT_GENERATION = "report_generation"
    BOOT = "boot"
    SHUTDOWN = "shutdown"
    HEALTH_CHECK = "health_check"
    KNOWLEDGE_UPDATE = "knowledge_update"
    TWIN_SCAN = "twin_scan"
    SDK_CALL = "sdk_call"
    REASONING = "reasoning"
    DECISION = "decision"
    NAVIGATION = "navigation"
    COMMAND = "command"

    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").title()


class ActionSeverity(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ActionRecord:
    id: str
    type: ActionType
    subsystem: str
    action: str
    severity: ActionSeverity = ActionSeverity.INFO
    timestamp: float = 0.0
    duration: float = 0.0
    success: bool = True
    actor: str = "system"
    detail: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    trace: str | None = None
    parent_id: str | None = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "subsystem": self.subsystem,
            "action": self.action,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "duration": round(self.duration, 4),
            "success": self.success,
            "actor": self.actor,
            "detail": self.detail,
            "error": self.error,
            "parent_id": self.parent_id,
            "tags": self.tags,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ActionFilter:
    types: list[ActionType] | None = None
    subsystems: list[str] | None = None
    severities: list[ActionSeverity] | None = None
    success: bool | None = None
    actor: str | None = None
    since: float = 0.0
    until: float = 0.0
    search: str | None = None
    limit: int = 100
    offset: int = 0

    def matches(self, record: ActionRecord) -> bool:
        if self.types and record.type not in self.types:
            return False
        if self.subsystems and record.subsystem not in self.subsystems:
            return False
        if self.severities and record.severity not in self.severities:
            return False
        if self.success is not None and record.success != self.success:
            return False
        if self.actor and record.actor != self.actor:
            return False
        if self.since and record.timestamp < self.since:
            return False
        if self.until and record.timestamp > self.until:
            return False
        if self.search:
            s = self.search.lower()
            if s not in record.action.lower() and s not in record.detail.lower():
                return False
        return True


def _generate_action_id() -> str:
    import random
    import string
    ts = hex(int(time.time() * 1000))[2:]
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"act_{ts}_{rand}"


class ObservableMixin:
    def __init__(self) -> None:
        self._observability: ObservabilityEngine | None = None

    def bind_observability(self, engine: ObservabilityEngine) -> None:
        self._observability = engine

    def record(self, type_: ActionType, action: str, subsystem: str = "",
               severity: ActionSeverity = ActionSeverity.INFO,
               detail: str = "", metadata: dict[str, Any] | None = None,
               error: str | None = None) -> ActionRecord | None:
        if self._observability:
            return self._observability.record(
                type_=type_, subsystem=subsystem or type(self).__name__,
                action=action, severity=severity, detail=detail,
                metadata=metadata, error=error,
            )
        return None


def record_action(type_: ActionType, subsystem: str = "",
                  severity: ActionSeverity = ActionSeverity.INFO):
    def decorator(fn: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            engine = getattr(kwargs.get('kernel'), 'observability', None)
            start = time.time()
            try:
                result = fn(*args, **kwargs)
                if engine:
                    engine.record(
                        type_=type_, subsystem=subsystem,
                        action=fn.__name__,
                        severity=severity,
                        duration=time.time() - start,
                        success=True,
                    )
                return result
            except Exception as e:
                if engine:
                    engine.record(
                        type_=type_, subsystem=subsystem,
                        action=fn.__name__,
                        severity=ActionSeverity.ERROR,
                        duration=time.time() - start,
                        success=False,
                        error=str(e),
                        trace=traceback.format_exc(),
                    )
                raise
        return wrapper
    return decorator


class ObservabilityEngine:
    def __init__(self, kernel: Any, max_records: int = 100000) -> None:
        self._kernel = kernel
        self._records: list[ActionRecord] = []
        self._max_records = max_records
        self._lock = threading.RLock()
        self._by_type: dict[ActionType, list[ActionRecord]] = defaultdict(list)
        self._by_subsystem: dict[str, list[ActionRecord]] = defaultdict(list)
        self._booted = False
        self._export_path: str | None = None

    def boot(self) -> None:
        if self._booted:
            return
        self._booted = True

    def set_export_path(self, path: str) -> None:
        self._export_path = path

    @property
    def record_count(self) -> int:
        return len(self._records)

    def record(self, type_: ActionType, subsystem: str, action: str,
               severity: ActionSeverity = ActionSeverity.INFO,
               timestamp: float | None = None,
               duration: float = 0.0,
               success: bool = True,
               actor: str = "system",
               detail: str = "",
               metadata: dict[str, Any] | None = None,
               error: str | None = None,
               trace: str | None = None,
               parent_id: str | None = None,
               tags: list[str] | None = None) -> ActionRecord:
        record = ActionRecord(
            id=_generate_action_id(),
            type=type_,
            subsystem=subsystem,
            action=action,
            severity=severity,
            timestamp=timestamp or time.time(),
            duration=duration,
            success=success,
            actor=actor,
            detail=detail,
            metadata=metadata or {},
            error=error,
            trace=trace,
            parent_id=parent_id,
            tags=tags or [],
        )

        with self._lock:
            self._records.append(record)
            self._by_type[type_].append(record)
            self._by_subsystem[subsystem].append(record)

            if len(self._records) > self._max_records:
                self._trim()

        if error and self._kernel.health_engine:
            try:
                snap = self._kernel.health_engine.snapshot()
            except Exception:
                pass

        return record

    def _trim(self) -> None:
        overflow = len(self._records) - self._max_records
        if overflow > 0:
            self._records = self._records[overflow:]
            for t in self._by_type:
                self._by_type[t] = self._by_type[t][overflow:]
            for s in self._by_subsystem:
                self._by_subsystem[s] = self._by_subsystem[s][overflow:]

    def query(self, filter_: ActionFilter | None = None) -> list[ActionRecord]:
        if filter_ is None:
            return list(self._records)

        results = [
            r for r in self._records if filter_.matches(r)
        ]

        results.reverse()

        if filter_.offset:
            results = results[filter_.offset:]
        if filter_.limit:
            results = results[:filter_.limit]

        return results

    def query_by_type(self, type_: ActionType, limit: int = 50) -> list[ActionRecord]:
        records = list(self._by_type.get(type_, []))
        records.reverse()
        return records[:limit]

    def query_by_subsystem(self, subsystem: str, limit: int = 50) -> list[ActionRecord]:
        records = list(self._by_subsystem.get(subsystem, []))
        records.reverse()
        return records[:limit]

    def errors(self, since: float = 0.0, limit: int = 50) -> list[ActionRecord]:
        filter_ = ActionFilter(
            severities=[ActionSeverity.ERROR, ActionSeverity.CRITICAL],
            since=since,
            limit=limit,
        )
        return self.query(filter_)

    def stats(self) -> dict[str, Any]:
        with self._lock:
            type_counts = {
                t.value: len(records) for t, records in self._by_type.items()
            }
            subsystem_counts = {
                s: len(records) for s, records in self._by_subsystem.items()
            }
            error_count = sum(
                1 for r in self._records
                if r.severity in (ActionSeverity.ERROR, ActionSeverity.CRITICAL)
            )
            success_count = sum(1 for r in self._records if r.success)
            total = len(self._records)

        return {
            "total_records": total,
            "by_type": type_counts,
            "by_subsystem": subsystem_counts,
            "errors": error_count,
            "success_rate": round(success_count / total, 4) if total > 0 else 1.0,
        }

    def export(self, format: str = "json", filter_: ActionFilter | None = None) -> str:
        records = self.query(filter_)
        if format == "json":
            data = [r.to_dict() for r in records]
            return json.dumps(data, indent=2)
        elif format == "csv":
            import io
            buf = io.StringIO()
            buf.write("id,type,subsystem,action,severity,timestamp,duration,success,actor,detail,error\n")
            for r in records:
                ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(r.timestamp))
                detail = r.detail.replace('"', '""')
                error = (r.error or "").replace('"', '""')
                buf.write(
                    f'"{r.id}","{r.type.value}","{r.subsystem}","{r.action}",'
                    f'"{r.severity.value}","{ts}",{r.duration:.4f},{r.success},'
                    f'"{r.actor}","{detail}","{error}"\n'
                )
            return buf.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def export_to_file(self, path: str, format: str = "json",
                       filter_: ActionFilter | None = None) -> str:
        content = self.export(format=format, filter_=filter_)
        with open(path, "w") as f:
            f.write(content)
        return path

    def replay(self, record_id: str) -> ActionRecord | None:
        for r in self._records:
            if r.id == record_id:
                return r
        return None

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._by_type.clear()
            self._by_subsystem.clear()
