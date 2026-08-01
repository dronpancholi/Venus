"""
CheckpointManager — snapshots system state for recovery.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class Checkpoint:
    """A system state checkpoint."""
    id: str = ""
    name: str = ""
    snapshot: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    size_bytes: int = 0
    version: str = "1.0"
    tags: list[str] = field(default_factory=list)


class CheckpointManager:
    """
    Creates and manages system state checkpoints.

    Checkpoints are full snapshots that can be restored on restart or failure.
    Supports automatic periodic checkpoints and manual checkpoints.
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "checkpoints"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.checkpoints: dict[str, Checkpoint] = {}
        self._save_hooks: list[Callable] = []
        self._load()

    def register_hook(self, hook: Callable):
        """Register a function that provides state to include in checkpoints."""
        self._save_hooks.append(hook)

    def create(self, name: str = "", tags: list[str] | None = None) -> Checkpoint:
        """Create a new checkpoint from all registered hooks."""
        snapshot = {}
        for hook in self._save_hooks:
            try:
                result = hook()
                if isinstance(result, dict):
                    snapshot.update(result)
            except Exception as e:
                snapshot[f"_error_{hook.__name__}"] = str(e)

        cp = Checkpoint(
            id=generate_id("ckpt", 10),
            name=name or f"checkpoint_{len(self.checkpoints) + 1}",
            snapshot=snapshot,
            created_at=time.time(),
            size_bytes=len(json.dumps(snapshot)),
            tags=tags or [],
        )

        self.checkpoints[cp.id] = cp
        self._save_checkpoint(cp)
        self._save_index()
        return cp

    def restore(self, checkpoint_id: str) -> dict[str, Any] | None:
        """Restore a checkpoint's snapshot data."""
        cp = self.checkpoints.get(checkpoint_id)
        if not cp:
            path = (self.storage_path / f"{checkpoint_id}.json")
            if path.exists():
                try:
                    cp = Checkpoint(**json.loads(path.read_text()))
                    self.checkpoints[cp.id] = cp
                except Exception:
                    return None
            else:
                return None
        return dict(cp.snapshot)

    def latest(self) -> Checkpoint | None:
        if not self.checkpoints:
            return None
        return max(self.checkpoints.values(), key=lambda c: c.created_at)

    def list_checkpoints(self, limit: int = 10) -> list[Checkpoint]:
        return sorted(self.checkpoints.values(),
                     key=lambda c: -c.created_at)[:limit]

    def summary(self) -> dict[str, Any]:
        return {
            "total_checkpoints": len(self.checkpoints),
            "latest": self.latest().name if self.latest() else None,
            "total_size_bytes": sum(c.size_bytes for c in self.checkpoints.values()),
        }

    def _save_checkpoint(self, cp: Checkpoint):
        path = self.storage_path / f"{cp.id}.json"
        path.write_text(json.dumps({
            "id": cp.id,
            "name": cp.name,
            "snapshot": cp.snapshot,
            "created_at": cp.created_at,
            "size_bytes": cp.size_bytes,
            "version": cp.version,
            "tags": cp.tags,
        }, indent=2, default=str))

    def _index_path(self) -> Path:
        return self.storage_path / "index.json"

    def _save_index(self):
        data = {
            cpid: {
                "id": cp.id, "name": cp.name,
                "created_at": cp.created_at,
                "size_bytes": cp.size_bytes,
                "tags": cp.tags,
            }
            for cpid, cp in self.checkpoints.items()
        }
        (self._index_path()).write_text(json.dumps(data, indent=2))

    def _load(self):
        path = self._index_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for cpid, cd in data.items():
                    self.checkpoints[cpid] = Checkpoint(
                        id=cd["id"], name=cd.get("name", ""),
                        created_at=cd.get("created_at", 0),
                        size_bytes=cd.get("size_bytes", 0),
                        tags=cd.get("tags", []),
                    )
            except Exception:
                pass
