"""
Universal Kernel: CheckpointManager — State checkpointing and restore.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import defaultdict
from typing import Any

from genesis.kernel.types import Checkpoint


class CheckpointManager:
    """Manages capability state checkpointing and restoration."""

    def __init__(self):
        self._checkpoints: dict[str, Checkpoint] = {}
        self._checkpoints_by_cap: dict[str, list[str]] = defaultdict(list)
        self._history: list[dict[str, Any]] = []

    def create(self, capability_id: str, state_data: dict[str, Any],
               memory_snapshot: dict[str, Any] | None = None) -> Checkpoint:
        mem = memory_snapshot or {}
        serialized = json.dumps({"state": state_data, "memory": mem},
                                 sort_keys=True, default=str)
        cp = Checkpoint(
            capability_id=capability_id,
            state_data=state_data,
            memory_snapshot=mem,
            size_bytes=len(serialized.encode()),
            version=len(self._checkpoints_by_cap[capability_id]) + 1,
            checksum=hashlib.sha256(serialized.encode()).hexdigest()[:16],
        )
        self._checkpoints[cp.id] = cp
        self._checkpoints_by_cap[capability_id].append(cp.id)
        self._history.append({
            "action": "create_checkpoint",
            "checkpoint_id": cp.id,
            "capability_id": capability_id,
            "version": cp.version,
            "size_bytes": cp.size_bytes,
            "timestamp": time.time(),
        })
        return cp

    def get(self, checkpoint_id: str) -> Checkpoint | None:
        return self._checkpoints.get(checkpoint_id)

    def latest(self, capability_id: str) -> Checkpoint | None:
        cp_ids = self._checkpoints_by_cap.get(capability_id, [])
        if not cp_ids:
            return None
        return self._checkpoints.get(cp_ids[-1])

    def list_for(self, capability_id: str) -> list[Checkpoint]:
        return [self._checkpoints[cid] for cid in self._checkpoints_by_cap.get(capability_id, [])
                if cid in self._checkpoints]

    def restore(self, capability_id: str, checkpoint_id: str | None = None) -> dict[str, Any] | None:
        cp = self.get(checkpoint_id) if checkpoint_id else self.latest(capability_id)
        if not cp:
            return None
        self._history.append({
            "action": "restore",
            "checkpoint_id": cp.id,
            "capability_id": capability_id,
            "version": cp.version,
            "timestamp": time.time(),
        })
        return {"state": cp.state_data, "memory": cp.memory_snapshot}

    def delete(self, checkpoint_id: str) -> bool:
        cp = self._checkpoints.pop(checkpoint_id, None)
        if not cp:
            return False
        cap_id = cp.capability_id
        if checkpoint_id in self._checkpoints_by_cap.get(cap_id, []):
            self._checkpoints_by_cap[cap_id].remove(checkpoint_id)
        return True

    def delete_all(self, capability_id: str) -> int:
        count = 0
        for cpid in list(self._checkpoints_by_cap.get(capability_id, [])):
            if self._checkpoints.pop(cpid, None):
                count += 1
        self._checkpoints_by_cap[capability_id] = []
        return count

    def verify(self, checkpoint_id: str) -> bool:
        cp = self._checkpoints.get(checkpoint_id)
        if not cp:
            return False
        serialized = json.dumps({"state": cp.state_data, "memory": cp.memory_snapshot},
                                 sort_keys=True, default=str)
        expected = hashlib.sha256(serialized.encode()).hexdigest()[:16]
        return cp.checksum == expected

    def summary(self) -> dict[str, Any]:
        return {
            "total_checkpoints": len(self._checkpoints),
            "capabilities_with_checkpoints": len(self._checkpoints_by_cap),
            "total_size_bytes": sum(cp.size_bytes for cp in self._checkpoints.values()),
            "total_operations": len(self._history),
        }
