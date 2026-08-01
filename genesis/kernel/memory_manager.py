"""
Universal Kernel: MemoryManager — Memory pool allocation and tracking.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from genesis.kernel.types import MemoryBlock, MemoryScope


class MemoryManager:
    """Manages memory allocation across capabilities."""

    def __init__(self, max_bytes: int = 8 * 1024 * 1024 * 1024):
        self._max_bytes = max_bytes
        self._blocks: dict[str, MemoryBlock] = {}
        self._allocations: dict[str, list[str]] = defaultdict(list)
        self._history: list[dict[str, Any]] = []

    @property
    def used_bytes(self) -> int:
        return sum(b.size_bytes for b in self._blocks.values())

    @property
    def available_bytes(self) -> int:
        return self._max_bytes - self.used_bytes

    @property
    def utilization(self) -> float:
        return self.used_bytes / max(self._max_bytes, 1)

    def allocate(self, capability_id: str, size_bytes: int,
                 scope: MemoryScope = MemoryScope.CAPABILITY,
                 tags: dict[str, str] | None = None) -> MemoryBlock | None:
        if self.available_bytes < size_bytes:
            return None
        block = MemoryBlock(
            capability_id=capability_id,
            scope=scope,
            size_bytes=size_bytes,
            tags=tags or {},
        )
        self._blocks[block.id] = block
        self._allocations[capability_id].append(block.id)
        self._history.append({
            "action": "allocate",
            "block_id": block.id,
            "capability_id": capability_id,
            "size_bytes": size_bytes,
            "timestamp": time.time(),
        })
        return block

    def free(self, block_id: str) -> bool:
        block = self._blocks.pop(block_id, None)
        if not block:
            return False
        cap_id = block.capability_id
        if block_id in self._allocations.get(cap_id, []):
            self._allocations[cap_id].remove(block_id)
        self._history.append({
            "action": "free",
            "block_id": block_id,
            "capability_id": cap_id,
            "size_bytes": block.size_bytes,
            "timestamp": time.time(),
        })
        return True

    def free_all(self, capability_id: str) -> int:
        freed = 0
        for block_id in list(self._allocations.get(capability_id, [])):
            if self.free(block_id):
                freed += 1
        return freed

    def get_block(self, block_id: str) -> MemoryBlock | None:
        return self._blocks.get(block_id)

    def blocks_for(self, capability_id: str) -> list[MemoryBlock]:
        return [self._blocks[bid] for bid in self._allocations.get(capability_id, [])
                if bid in self._blocks]

    def compact(self) -> int:
        reclaimed = 0
        for block in list(self._blocks.values()):
            if block.last_access > 0 and time.time() - block.last_access > 3600:
                if block.utilization < 0.1:
                    block.size_bytes = max(block.used_bytes, 1024)
                    reclaimed += 1
        return reclaimed

    def summary(self) -> dict[str, Any]:
        return {
            "max_bytes": self._max_bytes,
            "used_bytes": self.used_bytes,
            "available_bytes": self.available_bytes,
            "utilization": self.utilization,
            "blocks": len(self._blocks),
            "capabilities": len(self._allocations),
            "total_operations": len(self._history),
        }
