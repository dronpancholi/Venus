from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CollectionType(Enum):
    GRAPH = "graph"
    VECTOR = "vector"
    DOCUMENT = "document"
    TIME_SERIES = "time_series"
    EVENT = "event"
    OBJECT = "object"
    METADATA = "metadata"
    VERSION = "version"
    SNAPSHOT = "snapshot"
    ARCHIVE = "archive"


class IsolationLevel(Enum):
    READ_UNCOMMITTED = 0
    READ_COMMITTED = 1
    REPEATABLE_READ = 2
    SERIALIZABLE = 3


class IndexType(Enum):
    BTREE = "btree"
    HASH = "hash"
    INVERTED = "inverted"
    VECTOR = "vector"


class CompressionType(Enum):
    NONE = "none"
    GZIP = "gzip"
    ZSTD = "zstd"
    LZ4 = "lz4"


class CachePolicy(Enum):
    LRU = "lru"
    LFU = "lfu"
    ARC = "arc"


class ShardStrategy(Enum):
    RANGE = "range"
    HASH = "hash"
    CONSISTENT = "consistent"


@dataclass
class StorageConfig:
    page_size: int = 4096
    max_collections: int = 256
    max_collection_size: int = 2**40
    compression: CompressionType = CompressionType.LZ4
    compression_level: int = 6
    fsync_on_commit: bool = True
    journal_max_bytes: int = 64 * 1024 * 1024
    checkpoint_interval_secs: float = 60.0
    mvcc_max_versions: int = 100
    cache_max_entries_l1: int = 10000
    cache_max_entries_l2: int = 100000
    vector_dimension: int = 384
    vector_index_cells: int = 16
    time_series_retention_days: int = 365
    archive_compression: CompressionType = CompressionType.GZIP

    def validate(self):
        assert self.page_size >= 256, "page_size must be >= 256"
        assert self.page_size & (self.page_size - 1) == 0, "page_size must be power of 2"
        assert self.mvcc_max_versions >= 2, "mvcc_max_versions must be >= 2"


@dataclass
class Query:
    collection: str = ""
    filters: list[tuple[str, str, Any]] = field(default_factory=list)
    sort: list[tuple[str, bool]] = field(default_factory=list)
    limit: int = 0
    offset: int = 0
    fields: list[str] | None = None
    projection: dict[str, bool] | None = None

    def matches(self, record: dict[str, Any]) -> bool:
        for field, op, value in self.filters:
            actual = record.get(field)
            if op == "eq" and actual != value:
                return False
            if op == "neq" and actual == value:
                return False
            if op == "gt" and not (actual is not None and actual > value):
                return False
            if op == "gte" and not (actual is not None and actual >= value):
                return False
            if op == "lt" and not (actual is not None and actual < value):
                return False
            if op == "lte" and not (actual is not None and actual <= value):
                return False
            if op == "in" and actual not in value:
                return False
            if op == "nin" and actual in value:
                return False
            if op == "contains" and (actual is None or value not in actual):
                return False
            if op == "regex":
                import re
                if actual is None or not re.search(str(value), str(actual)):
                    return False
        return True


@dataclass
class QueryResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: int = 0
    execution_ms: float = 0.0
    scanned: int = 0

    @property
    def empty(self) -> bool:
        return len(self.records) == 0


@dataclass
class ShardKey:
    key_field: str = ""
    strategy: ShardStrategy = ShardStrategy.HASH
    ranges: list[tuple[Any, Any]] = field(default_factory=list)


@dataclass
class TransactionRecord:
    id: str = ""
    isolation: IsolationLevel = IsolationLevel.READ_COMMITTED
    started_at: float = 0.0
    read_ts: int = 0
    write_ts: int = 0
    status: str = "active"
    writes: dict[str, list[tuple[str, str, Any]]] = field(default_factory=dict)
    locks: set[str] = field(default_factory=set)

    def elapsed(self) -> float:
        return time.time() - self.started_at


@dataclass
class MVCCEntry:
    key: str = ""
    value: Any = None
    version: int = 0
    created_by: str = ""
    deleted: bool = False
    min_visible: int = 0
    max_visible: int = 2**63 - 1

    def visible_at(self, read_ts: int) -> bool:
        return self.min_visible <= read_ts < self.max_visible and not self.deleted


@dataclass
class JournalEntry:
    id: str = ""
    seq: int = 0
    action: str = ""
    collection: str = ""
    key: str = ""
    old_value: Any = None
    new_value: Any = None
    transaction_id: str = ""
    timestamp: float = 0.0
    checksum: str = ""


@dataclass
class CollectionMeta:
    id: str = ""
    name: str = ""
    ctype: CollectionType = CollectionType.DOCUMENT
    config: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    record_count: int = 0
    storage_bytes: int = 0
    indexes: list[str] = field(default_factory=list)


@dataclass
class CacheEntry:
    key: str = ""
    value: Any = None
    size_bytes: int = 0
    access_count: int = 0
    created_at: float = 0.0
    last_access: float = 0.0
    ttl_secs: float = 0.0
    dirty: bool = False
