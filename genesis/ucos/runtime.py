"""
UCOS: CapabilityRuntime — Executes capabilities with context, isolation, and monitoring.
"""

from __future__ import annotations

import time
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.ucos.capability import Capability, CapabilityState
from genesis.utils.identity import generate_id


@dataclass
class ExecutionContext:
    id: str = ""
    capability_id: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    started_at: float = 0.0
    completed_at: float = 0.0
    duration_ms: float = 0.0
    success: bool = False
    error: str = ""
    call_stack: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("exec", 14)
        if not self.started_at:
            self.started_at = time.time()


class CapabilityRuntime:
    """Runtime execution environment for capabilities."""

    def __init__(self, registry):
        self._registry = registry
        self._contexts: dict[str, ExecutionContext] = {}
        self._context_history: list[ExecutionContext] = []
        self._middleware: list[Callable] = []
        self._max_concurrent: int = 100
        self._active_count: int = 0

    def use(self, middleware: Callable):
        self._middleware.append(middleware)

    def execute(self, capability_id: str, **inputs) -> ExecutionContext:
        cap = self._registry.get(capability_id)
        if not cap:
            ctx = ExecutionContext(capability_id=capability_id, success=False,
                                    error="Capability not found")
            self._context_history.append(ctx)
            return ctx

        if self._active_count >= self._max_concurrent:
            ctx = ExecutionContext(capability_id=capability_id, success=False,
                                    error="Max concurrent executions reached")
            self._context_history.append(ctx)
            return ctx

        self._active_count += 1
        ctx = ExecutionContext(capability_id=capability_id, inputs=inputs)

        # Pre-execution middleware
        for mw in self._middleware:
            try:
                mw("before", cap, ctx)
            except Exception:
                pass

        try:
            if cap.state not in (CapabilityState.READY, CapabilityState.RUNNING):
                cap.state = CapabilityState.RUNNING
            result = cap.execute(**inputs)
            ctx.outputs = {"result": result} if result is not None else {}
            ctx.success = True
        except Exception as e:
            ctx.success = False
            ctx.error = f"{type(e).__name__}: {e}"
            ctx.outputs = {"traceback": traceback.format_exc()}
            cap.definition.health.message = ctx.error

        ctx.completed_at = time.time()
        ctx.duration_ms = (ctx.completed_at - ctx.started_at) * 1000
        self._context_history.append(ctx)
        self._contexts[ctx.id] = ctx
        self._active_count -= 1

        # Post-execution middleware
        for mw in self._middleware:
            try:
                mw("after", cap, ctx)
            except Exception:
                pass

        return ctx

    def execute_plan(self, capability_ids: list[str],
                     order: list[str] | None = None,
                     **global_inputs) -> list[ExecutionContext]:
        exec_order = order or capability_ids
        results = []
        for cid in exec_order:
            if cid in capability_ids:
                ctx = self.execute(cid, **global_inputs)
                results.append(ctx)
        return results

    def get_context(self, context_id: str) -> ExecutionContext | None:
        return self._contexts.get(context_id)

    def recent(self, n: int = 100) -> list[ExecutionContext]:
        return sorted(self._context_history, key=lambda c: c.started_at, reverse=True)[:n]

    def failed_executions(self) -> list[ExecutionContext]:
        return [c for c in self._context_history if not c.success]

    def success_rate(self) -> float:
        if not self._context_history:
            return 1.0
        successes = sum(1 for c in self._context_history if c.success)
        return successes / len(self._context_history)

    def avg_duration_ms(self) -> float:
        durations = [c.duration_ms for c in self._context_history if c.success]
        return sum(durations) / max(len(durations), 1)

    def summary(self) -> dict[str, Any]:
        return {
            "total_executions": len(self._context_history),
            "active": self._active_count,
            "success_rate": self.success_rate(),
            "avg_duration_ms": self.avg_duration_ms(),
            "failed": len(self.failed_executions()),
        }
