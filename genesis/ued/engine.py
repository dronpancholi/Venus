from __future__ import annotations

import hashlib
import json
import struct
import time
import uuid
from collections import defaultdict
from threading import RLock
from typing import Any

from genesis.ued.types import (
    CollectionMeta, CollectionType, CompressionType, IsolationLevel,
    JournalEntry, MVCCEntry, StorageConfig, TransactionRecord,
)
from genesis.utils.identity import generate_id


class PageStore:
    """Fixed-size page-based append-only storage with optional compression."""

    def __init__(self, config: StorageConfig):
        self._config = config
        self._pages: dict[int, bytes] = {}
        self._free_pages: list[int] = []
        self._next_page = 0
        self._page_size = config.page_size
        self._lock = RLock()

    def alloc_page(self) -> int:
        with self._lock:
            if self._free_pages:
                pid = self._free_pages.pop()
            else:
                pid = self._next_page
                self._next_page += 1
            self._pages[pid] = b"\x00" * self._page_size
            return pid

    def free_page(self, pid: int):
        with self._lock:
            self._pages.pop(pid, None)
            self._free_pages.append(pid)

    def read_page(self, pid: int) -> bytes | None:
        with self._lock:
            return self._pages.get(pid)

    def write_page(self, pid: int, data: bytes):
        with self._lock:
            if len(data) < self._page_size:
                data = data + b"\x00" * (self._page_size - len(data))
            self._pages[pid] = data[:self._page_size]

    def page_count(self) -> int:
        return len(self._pages)

    def total_bytes(self) -> int:
        return self.page_count() * self._page_size


class Journal:
    """Write-ahead journal with checkpointing and crash recovery."""

    def __init__(self, config: StorageConfig):
        self._config = config
        self._entries: list[JournalEntry] = []
        self._checkpoint_seq = 0
        self._next_seq = 1
        self._bytes_written = 0
        self._lock = RLock()

    def append(self, action: str, collection: str, key: str,
               old_value: Any = None, new_value: Any = None,
               transaction_id: str = "") -> JournalEntry:
        with self._lock:
            content = json.dumps({
                "action": action, "collection": collection, "key": key,
                "old": old_value, "new": new_value, "txn": transaction_id,
            }, default=str, sort_keys=True)
            entry = JournalEntry(
                id=generate_id("jrnl", 12),
                seq=self._next_seq,
                action=action, collection=collection, key=key,
                old_value=old_value, new_value=new_value,
                transaction_id=transaction_id,
                timestamp=time.time(),
                checksum=hashlib.sha256(content.encode()).hexdigest()[:16],
            )
            self._entries.append(entry)
            self._next_seq += 1
            self._bytes_written += len(content)
            self._maybe_checkpoint()
            return entry

    def _maybe_checkpoint(self):
        if self._bytes_written > self._config.journal_max_bytes:
            self.checkpoint()

    def checkpoint(self) -> list[JournalEntry]:
        with self._lock:
            snapshot = list(self._entries)
            self._checkpoint_seq = self._next_seq - 1
            self._entries = []
            self._bytes_written = 0
            return snapshot

    def replay(self) -> list[JournalEntry]:
        return list(self._entries)

    def last_seq(self) -> int:
        return self._next_seq - 1

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "entries": len(self._entries),
                "bytes_written": self._bytes_written,
                "next_seq": self._next_seq,
                "checkpoint_seq": self._checkpoint_seq,
            }


class MVCCStore:
    """Multi-version concurrency control layer."""

    def __init__(self, config: StorageConfig):
        self._config = config
        self._entries: dict[str, list[MVCCEntry]] = defaultdict(list)
        self._version_counter = 0
        self._lock = RLock()

    def _next_version(self) -> int:
        self._version_counter += 1
        return self._version_counter

    def put(self, key: str, value: Any, transaction_id: str, read_ts: int):
        with self._lock:
            version = self._next_version()
            entry = MVCCEntry(
                key=key, value=value, version=version,
                created_by=transaction_id, deleted=False,
                min_visible=read_ts, max_visible=2**63 - 1,
            )
            versions = self._entries[key]
            if versions:
                versions[-1].max_visible = read_ts
            versions.append(entry)
            if len(versions) > self._config.mvcc_max_versions:
                self._compact_key(key, versions)

    def delete(self, key: str, transaction_id: str, read_ts: int):
        with self._lock:
            version = self._next_version()
            versions = self._entries[key]
            if versions:
                versions[-1].max_visible = read_ts
            entry = MVCCEntry(
                key=key, value=None, version=version,
                created_by=transaction_id, deleted=True,
                min_visible=read_ts, max_visible=2**63 - 1,
            )
            versions.append(entry)

    def get(self, key: str, read_ts: int) -> MVCCEntry | None:
        versions = self._entries.get(key, [])
        for entry in reversed(versions):
            if entry.visible_at(read_ts):
                return entry
        return None

    def scan(self, read_ts: int) -> list[MVCCEntry]:
        result: list[MVCCEntry] = []
        with self._lock:
            for key, versions in self._entries.items():
                for entry in reversed(versions):
                    if entry.visible_at(read_ts):
                        if not entry.deleted:
                            result.append(entry)
                        break
        return result

    def _compact_key(self, key: str, versions: list[MVCCEntry]):
        if len(versions) <= 2:
            return
        keep = versions[-self._config.mvcc_max_versions:]
        keep[0].min_visible = 0
        self._entries[key] = keep

    def version_count(self) -> int:
        total = 0
        with self._lock:
            for versions in self._entries.values():
                total += len(versions)
        return total


class TransactionManager:
    """Transaction lifecycle with deadlock detection."""

    def __init__(self, mvcc: MVCCStore):
        self._mvcc = mvcc
        self._transactions: dict[str, TransactionRecord] = {}
        self._lock = RLock()
        self._global_ts = 0

    def begin(self, isolation: IsolationLevel = IsolationLevel.READ_COMMITTED) -> TransactionRecord:
        with self._lock:
            self._global_ts += 1
            txn = TransactionRecord(
                id=generate_id("txn", 12),
                isolation=isolation,
                started_at=time.time(),
                read_ts=self._global_ts,
                write_ts=self._global_ts,
            )
            self._transactions[txn.id] = txn
            return txn

    def commit(self, txn_id: str) -> bool:
        with self._lock:
            txn = self._transactions.get(txn_id)
            if not txn or txn.status != "active":
                return False
            txn.status = "committed"
            txn.write_ts = self._global_ts + 1
            self._global_ts += 1
            return True

    def rollback(self, txn_id: str) -> bool:
        with self._lock:
            txn = self._transactions.get(txn_id)
            if not txn or txn.status != "active":
                return False
            txn.status = "rolled_back"
            return True

    def get(self, txn_id: str) -> TransactionRecord | None:
        return self._transactions.get(txn_id)

    def active_count(self) -> int:
        return sum(1 for t in self._transactions.values() if t.status == "active")

    def detect_deadlock(self, txn_id: str, resource: str) -> bool:
        with self._lock:
            txn = self._transactions.get(txn_id)
            if not txn:
                return False
            if resource in txn.locks:
                return False
            for tid, other in self._transactions.items():
                if tid != txn_id and other.status == "active":
                    if resource in other.locks and txn.id in other.locks:
                        other.status = "deadlocked"
                        return True
            return False

    def summary(self) -> dict[str, Any]:
        with self._lock:
            statuses: dict[str, int] = {}
            for t in self._transactions.values():
                statuses[t.status] = statuses.get(t.status, 0) + 1
            return {
                "total": len(self._transactions),
                "by_status": statuses,
                "global_ts": self._global_ts,
                "mvcc_versions": self._mvcc.version_count(),
            }


class Catalog:
    """Collection catalog — schema and metadata registry."""

    def __init__(self):
        self._collections: dict[str, CollectionMeta] = {}
        self._lock = RLock()

    def create_collection(self, name: str, ctype: CollectionType,
                          config: dict[str, Any] | None = None) -> CollectionMeta:
        with self._lock:
            if name in self._collections:
                raise ValueError(f"Collection '{name}' already exists")
            meta = CollectionMeta(
                id=generate_id("coll", 12),
                name=name, ctype=ctype,
                config=config or {},
                created_at=time.time(),
            )
            self._collections[name] = meta
            return meta

    def get(self, name: str) -> CollectionMeta | None:
        return self._collections.get(name)

    def drop(self, name: str) -> bool:
        with self._lock:
            return self._collections.pop(name, None) is not None

    def list_collections(self, ctype: CollectionType | None = None) -> list[CollectionMeta]:
        if ctype:
            return [c for c in self._collections.values() if c.ctype == ctype]
        return list(self._collections.values())

    def update_stats(self, name: str, record_count: int | None = None,
                     storage_bytes: int | None = None):
        meta = self._collections.get(name)
        if meta:
            if record_count is not None:
                meta.record_count = record_count
            if storage_bytes is not None:
                meta.storage_bytes = storage_bytes

    def summary(self) -> dict[str, Any]:
        return {
            "collections": len(self._collections),
            "by_type": {t.value: sum(1 for c in self._collections.values() if c.ctype == t)
                       for t in CollectionType},
        }


class StorageEngine:
    """Unified storage engine combining page store, journal, MVCC, transactions, and catalog."""

    def __init__(self, config: StorageConfig | None = None):
        self._config = config or StorageConfig()
        self._config.validate()
        self._pages = PageStore(self._config)
        self._journal = Journal(self._config)
        self._mvcc = MVCCStore(self._config)
        self._txn_mgr = TransactionManager(self._mvcc)
        self._catalog = Catalog()

    @property
    def config(self) -> StorageConfig:
        return self._config

    @property
    def catalog(self) -> Catalog:
        return self._catalog

    @property
    def journal(self) -> Journal:
        return self._journal

    @property
    def txn_mgr(self) -> TransactionManager:
        return self._txn_mgr

    @property
    def mvcc(self) -> MVCCStore:
        return self._mvcc

    @property
    def pages(self) -> PageStore:
        return self._pages

    def begin(self, isolation: IsolationLevel = IsolationLevel.READ_COMMITTED) -> TransactionRecord:
        return self._txn_mgr.begin(isolation)

    def commit(self, txn_id: str) -> bool:
        return self._txn_mgr.commit(txn_id)

    def rollback(self, txn_id: str) -> bool:
        return self._txn_mgr.rollback(txn_id)

    def put(self, collection: str, key: str, value: Any, txn_id: str, read_ts: int):
        self._journal.append("put", collection, key, new_value=value, transaction_id=txn_id)
        self._mvcc.put(key, value, txn_id, read_ts)
        self._catalog.update_stats(collection, record_count=self._mvcc.version_count())

    def get(self, key: str, read_ts: int) -> Any | None:
        entry = self._mvcc.get(key, read_ts)
        return entry.value if entry and not entry.deleted else None

    def delete(self, collection: str, key: str, txn_id: str, read_ts: int):
        self._journal.append("delete", collection, key, transaction_id=txn_id)
        self._mvcc.delete(key, txn_id, read_ts)

    def scan(self, read_ts: int) -> list[MVCCEntry]:
        return self._mvcc.scan(read_ts)

    def create_collection(self, name: str, ctype: CollectionType,
                          config: dict[str, Any] | None = None) -> CollectionMeta:
        return self._catalog.create_collection(name, ctype, config)

    def summary(self) -> dict[str, Any]:
        return {
            "pages": self._pages.page_count(),
            "storage_bytes": self._pages.total_bytes(),
            "journal": self._journal.summary(),
            "transactions": self._txn_mgr.summary(),
            "catalog": self._catalog.summary(),
        }
