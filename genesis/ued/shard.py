from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

from genesis.ued.types import ShardKey, ShardStrategy


class ShardManager:
    """Data sharding with range, hash, and consistent hashing strategies."""

    def __init__(self, num_shards: int = 4):
        self._num_shards = num_shards
        self._shards: dict[int, dict[str, Any]] = {}
        self._key_to_shard: dict[str, int] = {}
        self._shard_keys: dict[str, ShardKey] = {}
        self._ring: list[int] = []
        self._virtual_nodes: int = 16
        for i in range(num_shards):
            self._shards[i] = {"id": i, "data": {}, "load": 0}

    def set_shard_key(self, collection: str, shard_key: ShardKey):
        self._shard_keys[collection] = shard_key

    def _hash_key(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

    def _range_shard(self, key: str, ranges: list[tuple[Any, Any]]) -> int:
        for i, (low, high) in enumerate(ranges):
            if low <= key <= high:
                return i % self._num_shards
        return self._num_shards - 1

    def _consistent_hash(self, key: str) -> int:
        if not self._ring:
            self._build_ring()
        h = self._hash_key(key)
        for rnode in self._ring:
            if h <= rnode:
                return rnode % self._num_shards
        return self._ring[0] % self._num_shards if self._ring else 0

    def _build_ring(self):
        self._ring = sorted(
            self._hash_key(f"shard_{s}_{v}")
            for s in range(self._num_shards)
            for v in range(self._virtual_nodes)
        )

    def locate(self, collection: str, key: str) -> int:
        sk = self._shard_keys.get(collection)
        if not sk:
            return self._hash_key(key) % self._num_shards
        if sk.strategy == ShardStrategy.RANGE:
            return self._range_shard(key, sk.ranges)
        elif sk.strategy == ShardStrategy.CONSISTENT:
            return self._consistent_hash(key)
        else:
            return self._hash_key(key) % self._num_shards

    def put(self, collection: str, key: str, value: Any):
        shard_id = self.locate(collection, key)
        self._shards[shard_id]["data"][f"{collection}:{key}"] = value
        self._shards[shard_id]["load"] += 1
        self._key_to_shard[f"{collection}:{key}"] = shard_id

    def get(self, collection: str, key: str) -> Any | None:
        shard_id = self._key_to_shard.get(f"{collection}:{key}")
        if shard_id is None:
            shard_id = self.locate(collection, key)
        return self._shards[shard_id]["data"].get(f"{collection}:{key}")

    def delete(self, collection: str, key: str) -> bool:
        shard_id = self._key_to_shard.pop(f"{collection}:{key}", None)
        if shard_id is None:
            return False
        result = self._shards[shard_id]["data"].pop(f"{collection}:{key}", None)
        if result is not None:
            self._shards[shard_id]["load"] = max(0, self._shards[shard_id]["load"] - 1)
            return True
        return False

    def rebalance(self) -> dict[int, int]:
        total_load = sum(s["load"] for s in self._shards.values())
        target = total_load // max(self._num_shards, 1)
        moved: dict[int, int] = {}
        overloaded = [s for s in self._shards.values() if s["load"] > target * 1.2]
        underloaded = [s for s in self._shards.values() if s["load"] < target * 0.8]
        for src in overloaded:
            items_to_move = list(src["data"].items())
            for key, value in items_to_move:
                if not underloaded:
                    break
                dst = underloaded[0]
                new_shard = self.locate(key.split(":", 1)[0], key.split(":", 1)[1])
                if new_dst := next((s for s in underloaded if s["id"] == new_shard), None):
                    dst = new_dst
                    underloaded.remove(dst)
                src["data"].pop(key)
                dst["data"][key] = value
                self._key_to_shard[key] = dst["id"]
                src["load"] -= 1
                dst["load"] += 1
                moved[dst["id"]] = moved.get(dst["id"], 0) + 1
                if dst["load"] >= target:
                    underloaded.remove(dst) if dst in underloaded else None
        return moved

    def shard_count(self) -> int:
        return self._num_shards

    def load_distribution(self) -> dict[int, int]:
        return {s["id"]: s["load"] for s in self._shards.values()}

    def summary(self) -> dict[str, Any]:
        return {
            "shards": self._num_shards,
            "total_items": sum(s["load"] for s in self._shards.values()),
            "load_distribution": self.load_distribution(),
            "shard_keys": list(self._shard_keys.keys()),
        }
