from __future__ import annotations

import time
from typing import Any

from genesis.ued.types import Query, QueryResult


class QueryPlan:
    """A query plan consisting of sequential execution steps."""

    def __init__(self, plan_id: str = ""):
        self.id = plan_id
        self.steps: list[dict[str, Any]] = []
        self.estimated_cost: float = 0.0

    def add_step(self, step_type: str, params: dict[str, Any]):
        self.steps.append({"type": step_type, "params": params})

    @property
    def step_count(self) -> int:
        return len(self.steps)


class QueryPlanner:
    """Multi-store query planner with optimization and execution."""

    def __init__(self):
        self._store_registry: dict[str, Any] = {}
        self._plan_history: list[dict[str, Any]] = []

    def register_store(self, name: str, store: Any):
        self._store_registry[name] = store

    def plan(self, query: Query) -> QueryPlan:
        plan = QueryPlan()
        plan.add_step("filter", {"collection": query.collection, "filters": query.filters})
        if query.sort:
            plan.add_step("sort", {"sort": query.sort})
        plan.add_step("offset_limit", {"offset": query.offset, "limit": query.limit})
        if query.fields:
            plan.add_step("project", {"fields": query.fields})
        plan.estimated_cost = self._estimate_cost(query)
        return plan

    def _estimate_cost(self, query: Query) -> float:
        cost = 1.0
        cost += len(query.filters) * 0.5
        if query.sort:
            cost += 2.0
        if query.limit:
            cost *= min(1.0, query.limit / 1000.0)
        return cost

    def explain(self, query: Query) -> dict[str, Any]:
        plan = self.plan(query)
        return {
            "steps": plan.steps,
            "estimated_cost": plan.estimated_cost,
            "step_count": plan.step_count,
            "query": {
                "collection": query.collection,
                "filters": len(query.filters),
                "sort": len(query.sort),
                "limit": query.limit,
                "offset": query.offset,
            },
        }

    def execute(self, query: Query, store: Any | None = None) -> QueryResult:
        start = time.time()
        if store is not None:
            result = store.query(query.collection, query) if hasattr(store, "query") else QueryResult()
        else:
            store_obj = self._store_registry.get(query.collection)
            if store_obj and hasattr(store_obj, "query"):
                result = store_obj.query(query.collection, query)
            else:
                result = QueryResult()
        result.execution_ms = (time.time() - start) * 1000
        self._plan_history.append({
            "collection": query.collection,
            "filters": len(query.filters),
            "records": len(result.records),
            "execution_ms": result.execution_ms,
            "timestamp": time.time(),
        })
        return result

    def optimize(self, query: Query) -> Query:
        optimized = Query(
            collection=query.collection,
            filters=list(query.filters),
            sort=list(query.sort),
            limit=query.limit,
            offset=query.offset,
            fields=list(query.fields) if query.fields else None,
            projection=dict(query.projection) if query.projection else None,
        )
        if optimized.limit == 0:
            optimized.limit = 1000
        if optimized.offset < 0:
            optimized.offset = 0
        seen_filters: set[str] = set()
        unique_filters: list[tuple[str, str, Any]] = []
        for f in optimized.filters:
            key = f"{f[0]}:{f[1]}:{str(f[2])}"
            if key not in seen_filters:
                seen_filters.add(key)
                unique_filters.append(f)
        optimized.filters = unique_filters
        return optimized

    def plan_history(self) -> list[dict[str, Any]]:
        return list(self._plan_history)

    def summary(self) -> dict[str, Any]:
        return {
            "registered_stores": len(self._store_registry),
            "total_plans": len(self._plan_history),
            "avg_execution_ms": (
                sum(p["execution_ms"] for p in self._plan_history) / max(len(self._plan_history), 1)
            ),
        }
