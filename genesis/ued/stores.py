from __future__ import annotations

import json
import time
from typing import Any

from genesis.ued.engine import StorageEngine
from genesis.ued.index import BTreeIndex, HashIndex, InvertedIndex
from genesis.ued.types import CollectionType, Query, QueryResult, TransactionRecord
from genesis.utils.identity import generate_id


class DocumentStore:
    """JSON document storage with indexing and filtered queries."""

    def __init__(self, engine: StorageEngine):
        self._engine = engine
        self._collections: dict[str, dict[str, dict[str, Any]]] = {}
        self._indexes: dict[str, list[BTreeIndex | HashIndex | InvertedIndex]] = {}
        self._txn_store: dict[str, dict[str, list[dict[str, Any]]]] = {}

    def _get_store(self, collection: str) -> dict[str, dict[str, Any]]:
        if collection not in self._collections:
            self._collections[collection] = {}
            self._indexes[collection] = []
        return self._collections[collection]

    def insert(self, collection: str, document: dict[str, Any],
               txn: TransactionRecord | None = None) -> str:
        doc_id = document.get("id", generate_id("doc", 16))
        document["id"] = doc_id
        store = self._get_store(collection)
        store[doc_id] = document
        for idx in self._indexes.get(collection, []):
            field_val = document.get(idx.field)
            if field_val is not None:
                if isinstance(idx, InvertedIndex) and isinstance(field_val, str):
                    idx.index(doc_id, field_val)
                elif isinstance(idx, (BTreeIndex, HashIndex)):
                    idx.insert(field_val, doc_id)
        return doc_id

    def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        store = self._collections.get(collection, {})
        return store.get(doc_id)

    def update(self, collection: str, doc_id: str, updates: dict[str, Any]) -> bool:
        store = self._collections.get(collection, {})
        doc = store.get(doc_id)
        if not doc:
            return False
        old_text = doc.get("text") or doc.get("content", "")
        doc.update(updates)
        for idx in self._indexes.get(collection, []):
            val = updates.get(idx.field)
            if val is not None:
                if isinstance(idx, InvertedIndex) and isinstance(val, str):
                    idx.remove(doc_id, str(old_text))
                    idx.index(doc_id, val)
                elif isinstance(idx, (BTreeIndex, HashIndex)):
                    idx.delete(doc.get(idx.field), doc_id)
                    idx.insert(val, doc_id)
        return True

    def delete(self, collection: str, doc_id: str) -> bool:
        store = self._collections.get(collection, {})
        doc = store.pop(doc_id, None)
        if doc:
            for idx in self._indexes.get(collection, []):
                field_val = doc.get(idx.field)
                if field_val is not None:
                    if isinstance(idx, InvertedIndex) and isinstance(field_val, str):
                        idx.remove(doc_id, field_val)
                    elif isinstance(idx, (BTreeIndex, HashIndex)):
                        idx.delete(field_val, doc_id)
            return True
        return False

    def query(self, collection: str, q: Query) -> QueryResult:
        store = self._collections.get(collection, {})
        start = time.time()
        records: list[dict[str, Any]] = []
        scanned = 0
        for doc in store.values():
            scanned += 1
            if q.matches(doc):
                records.append(dict(doc))
        if q.sort:
            reverse = q.sort[0][1]
            key_field = q.sort[0][0]
            records.sort(key=lambda r: r.get(key_field, ""), reverse=reverse)
        total = len(records)
        if q.offset:
            records = records[q.offset:]
        if q.limit:
            records = records[:q.limit]
        if q.fields:
            records = [{k: r[k] for k in q.fields if k in r} for r in records]
        return QueryResult(
            records=records, total=total,
            offset=q.offset, limit=q.limit,
            execution_ms=(time.time() - start) * 1000,
            scanned=scanned,
        )

    def create_index(self, collection: str, field: str, index_type: str = "btree"):
        store = self._collections.get(collection)
        if store is None:
            return
        if collection not in self._indexes:
            self._indexes[collection] = []
        if index_type == "btree":
            idx = BTreeIndex(f"{collection}_{field}", field)
        elif index_type == "hash":
            idx = HashIndex(f"{collection}_{field}", field)
        elif index_type == "inverted":
            idx = InvertedIndex(f"{collection}_{field}", field)
        else:
            return
        for doc_id, doc in store.items():
            val = doc.get(field)
            if val is not None:
                if isinstance(idx, InvertedIndex) and isinstance(val, str):
                    idx.index(doc_id, val)
                else:
                    idx.insert(val, doc_id)
        self._indexes[collection].append(idx)

    def count(self, collection: str) -> int:
        return len(self._collections.get(collection, {}))

    def summary(self, collection: str) -> dict[str, Any]:
        store = self._collections.get(collection, {})
        return {
            "collection": collection,
            "documents": len(store),
            "indexes": len(self._indexes.get(collection, [])),
        }


class MetadataStore:
    """Key-value metadata storage."""

    def __init__(self, engine: StorageEngine):
        self._engine = engine
        self._data: dict[str, dict[str, Any]] = {}
        self._tags: dict[str, set[str]] = {}

    def set(self, namespace: str, key: str, value: Any, tags: list[str] | None = None):
        if namespace not in self._data:
            self._data[namespace] = {}
        self._data[namespace][key] = value
        if tags:
            if namespace not in self._tags:
                self._tags[namespace] = set()
            self._tags[namespace].update(tags)

    def get(self, namespace: str, key: str) -> Any | None:
        ns = self._data.get(namespace, {})
        return ns.get(key)

    def delete(self, namespace: str, key: str) -> bool:
        ns = self._data.get(namespace)
        if ns and key in ns:
            del ns[key]
            return True
        return False

    def list_namespace(self, namespace: str) -> list[tuple[str, Any]]:
        ns = self._data.get(namespace, {})
        return list(ns.items())

    def search_by_tag(self, tag: str) -> list[str]:
        results: list[str] = []
        for ns, tags in self._tags.items():
            if tag in tags:
                results.extend(self._data[ns].keys())
        return results

    def summary(self) -> dict[str, Any]:
        return {
            "namespaces": len(self._data),
            "entries": sum(len(v) for v in self._data.values()),
        }


class VersionStore:
    """Versioned key-value storage with full history tracking."""

    def __init__(self, engine: StorageEngine):
        self._engine = engine
        self._data: dict[str, dict[str, list[dict[str, Any]]]] = {}

    def _ensure(self, collection: str):
        if collection not in self._data:
            self._data[collection] = {}

    def put(self, collection: str, key: str, value: Any,
            metadata: dict[str, Any] | None = None):
        self._ensure(collection)
        if key not in self._data[collection]:
            self._data[collection][key] = []
        self._data[collection][key].append({
            "value": value,
            "version": len(self._data[collection][key]) + 1,
            "timestamp": time.time(),
            "metadata": metadata or {},
        })

    def get(self, collection: str, key: str, version: int | None = None) -> Any | None:
        versions = self._data.get(collection, {}).get(key)
        if not versions:
            return None
        if version is not None:
            for v in versions:
                if v["version"] == version:
                    return v["value"]
            return None
        return versions[-1]["value"]

    def list_versions(self, collection: str, key: str) -> list[dict[str, Any]]:
        versions = self._data.get(collection, {}).get(key, [])
        return [{"version": v["version"], "timestamp": v["timestamp"],
                 "metadata": v["metadata"]} for v in versions]

    def diff(self, collection: str, key: str, v1: int, v2: int) -> dict[str, Any]:
        versions = self._data.get(collection, {}).get(key, [])
        val1 = next((v["value"] for v in versions if v["version"] == v1), None)
        val2 = next((v["value"] for v in versions if v["version"] == v2), None)
        return {"from_version": v1, "to_version": v2,
                "from_value": val1, "to_value": val2,
                "changed": val1 != val2}

    def delete_key(self, collection: str, key: str) -> bool:
        coll = self._data.get(collection, {})
        if key in coll:
            del coll[key]
            return True
        return False

    def count(self, collection: str) -> int:
        return len(self._data.get(collection, {}))

    def summary(self) -> dict[str, Any]:
        total_versions = 0
        for coll in self._data.values():
            for versions in coll.values():
                total_versions += len(versions)
        return {
            "collections": len(self._data),
            "total_versions": total_versions,
        }
