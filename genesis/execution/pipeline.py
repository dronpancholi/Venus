from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class PipelineStage:
    id: str = ""
    name: str = ""
    handler: Callable | None = None
    input_key: str = ""
    output_key: str = ""
    timeout_secs: float = 300.0
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("pst", 12)


class PipelineEngine:
    """Sequential and conditional pipeline execution."""

    def __init__(self):
        self._pipelines: dict[str, list[PipelineStage]] = {}
        self._history: list[dict[str, Any]] = []

    def define(self, name: str, stages: list[PipelineStage]):
        self._pipelines[name] = stages

    def get_pipeline(self, name: str) -> list[PipelineStage] | None:
        return self._pipelines.get(name)

    def execute(self, name: str, initial_input: dict[str, Any] | None = None) -> dict[str, Any]:
        stages = self._pipelines.get(name)
        if not stages:
            raise ValueError(f"Pipeline '{name}' not found")
        context: dict[str, Any] = dict(initial_input or {})
        for stage in stages:
            input_data = context.get(stage.input_key, context) if stage.input_key else context
            for attempt in range(stage.max_retries):
                try:
                    result = stage.handler(input_data) if stage.handler else input_data
                    if stage.output_key:
                        context[stage.output_key] = result
                    else:
                        context.update(result if isinstance(result, dict) else {"result": result})
                    self._history.append({
                        "pipeline": name,
                        "stage": stage.name,
                        "status": "success",
                        "timestamp": time.time(),
                    })
                    break
                except Exception as e:
                    if attempt >= stage.max_retries - 1:
                        self._history.append({
                            "pipeline": name,
                            "stage": stage.name,
                            "status": "failed",
                            "error": str(e),
                            "timestamp": time.time(),
                        })
                        raise
        return context

    def list_pipelines(self) -> list[str]:
        return list(self._pipelines.keys())

    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def summary(self) -> dict[str, Any]:
        return {
            "pipelines": len(self._pipelines),
            "stages": sum(len(s) for s in self._pipelines.values()),
            "executions": len(self._history),
        }
