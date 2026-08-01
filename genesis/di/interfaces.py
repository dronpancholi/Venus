"""
VENUS-II-DI-INT-01: Service Interface Protocols

Normative References:
  - VPS Part IX: Capability Model
  - GENESIS_II_ARCHITECTURE §3.3: Service Interfaces
  - ADR-003: Protocol-based DI instead of Abstract Base Classes

Purpose:
  Define typed protocols for all injectable Venus services.
  Using Protocol (structural subtyping) instead of ABC enables:
  1. Loose coupling — consumers depend on interfaces, not implementations
  2. Testability — mocks don't need to inherit from ABCs
  3. Migration — existing Genesis-I classes implement most protocols already
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CompilerService(Protocol):
    """Compilation pipeline interface."""

    def compile(self, source_path: str | Path) -> Any:
        """Compile a source file through the full pipeline."""
        ...

    def compile_string(self, content: str, fmt: str, source_name: str) -> Any:
        """Compile a string directly (no file needed)."""
        ...

    def generate(self, cu: Any, output_dir: str | Path | None = None) -> dict[str, list[Path]]:
        """Run all registered code generators."""
        ...


@runtime_checkable
class ValidationService(Protocol):
    """Validation engine interface."""

    def validate(self, target: Any, categories: list[str] | None = None) -> list[Any]:
        """Run all validators (optionally filtered by category)."""
        ...

    def summary(self, results: list[Any]) -> dict[str, Any]:
        """Compute summary statistics from validation results."""
        ...


@runtime_checkable
class GraphService(Protocol):
    """Unified graph engine interface."""

    def add_node(self, node_id: str, label: str = "", node_type: str = "knowledge_node", **attrs: Any) -> Any:
        """Add a node to the graph."""
        ...

    def add_edge(self, source: str, target: str, edge_type: str = "references", **attrs: Any) -> Any:
        """Add an edge to the graph."""
        ...

    def get_node(self, node_id_or_label: str) -> Any | None:
        """Retrieve a node by ID or label."""
        ...

    def find_nodes(self, node_type: str | None = None, label_contains: str = "") -> list[Any]:
        """Find nodes matching type and/or label."""
        ...

    def summary(self) -> dict[str, Any]:
        """Return graph statistics."""
        ...


@runtime_checkable
class ExecutionService(Protocol):
    """Execution engine interface."""

    def register_workflow(self, workflow: Any) -> None:
        ...

    def execute(self, workflow_id: str, sync: bool = True) -> list[dict[str, Any]]:
        """Execute a workflow."""
        ...

    def get_history(self, workflow_id: str | None = None) -> list[dict[str, Any]]:
        """Retrieve execution history."""
        ...


@runtime_checkable
class PluginService(Protocol):
    """Plugin manager interface."""

    def register_plugin(self, manifest: Any) -> Any:
        ...

    def activate(self, name: str) -> bool:
        ...

    def all(self) -> list[Any]:
        ...


@runtime_checkable
class CapabilityService(Protocol):
    """Capability registry interface."""

    def get(self, name: str) -> Any | None:
        ...

    def all(self) -> list[Any]:
        ...

    def find_by_interface(self, method: str, path: str) -> list[Any]:
        ...


@runtime_checkable
class MetadataService(Protocol):
    """Metadata engine interface."""

    def create_record(self, artifact_path: str, semantic_type: str = "unknown", version: str = "0.1.0") -> Any:
        ...

    def get_record(self, artifact_path: str) -> Any | None:
        ...

    def search(self, **filters: Any) -> list[Any]:
        ...


@runtime_checkable
class DiagnosticsService(Protocol):
    """Self-diagnostics interface."""

    def run(self, mode: str = "quick") -> list[dict[str, Any]]:
        ...

    def summary(self) -> dict[str, Any]:
        ...


@runtime_checkable
class ConfigService(Protocol):
    """Configuration interface."""

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value with env var → file → default resolution."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Set a config value at runtime."""
        ...

    def load(self, path: str | Path) -> None:
        """Load configuration from a file."""
        ...


@runtime_checkable
class CheckpointService(Protocol):
    """Platform state snapshot interface (VPS §10.1.5)."""

    def save_checkpoint(self, name: str, state: dict[str, Any]) -> Path:
        ...

    def load_checkpoint(self, name: str) -> dict[str, Any] | None:
        ...

    def list_checkpoints(self) -> list[str]:
        ...

    def checkpoint_exists(self, name: str) -> bool:
        ...


@runtime_checkable
class EventBus(Protocol):
    """Event bus interface for pub/sub communication."""

    def subscribe(self, event_type: str, handler: Any) -> None:
        """Register a handler for an event type."""
        ...

    def emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Emit an event to all registered handlers."""
        ...

    def unsubscribe(self, event_type: str, handler: Any) -> None:
        """Remove a handler registration."""
        ...
