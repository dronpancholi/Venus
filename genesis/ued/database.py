from __future__ import annotations

from typing import Any

from genesis.ued.cache import CacheManager, CachePolicy
from genesis.ued.engine import StorageEngine
from genesis.ued.graph import GraphStore
from genesis.ued.object import ArchiveStore, ObjectStore, SnapshotStore
from genesis.ued.query import QueryPlanner
from genesis.ued.shard import ShardManager
from genesis.ued.stores import DocumentStore, MetadataStore, VersionStore
from genesis.ued.timeseries import EventStore, TimeSeriesStore
from genesis.ued.types import (
    CollectionType, IsolationLevel, Query, QueryResult, StorageConfig,
)
from genesis.ued.vector import VectorStore


class Collection:
    """A typed collection within the database."""

    def __init__(self, name: str, ctype: CollectionType, db: Database):
        self.name = name
        self.ctype = ctype
        self._db = db

    def insert(self, data: Any, **kwargs) -> Any:
        if self.ctype == CollectionType.DOCUMENT:
            return self._db._doc_store.insert(self.name, data)
        elif self.ctype == CollectionType.GRAPH:
            return self._db._graph_store.add_node(data)
        elif self.ctype == CollectionType.VECTOR:
            self._db._vec_store.insert(data["id"], data["vector"], data.get("metadata"))
            return data["id"]
        elif self.ctype == CollectionType.TIME_SERIES:
            self._db._ts_store.insert(self.name, data["timestamp"], data["value"], data.get("labels"))
            return data
        elif self.ctype == CollectionType.EVENT:
            return self._db._event_store.append(data.get("type", "event"), data.get("data", {}),
                                                 data.get("stream"))
        elif self.ctype == CollectionType.OBJECT:
            return self._db._obj_store.put(data, kwargs.get("metadata"))
        elif self.ctype == CollectionType.METADATA:
            self._db._meta_store.set(self.name, data["key"], data.get("value"), data.get("tags"))
            return data["key"]
        elif self.ctype == CollectionType.VERSION:
            self._db._ver_store.put(self.name, data["key"], data.get("value"),
                                     data.get("metadata"))
            return data["key"]
        return None

    def get(self, key: str, **kwargs) -> Any | None:
        if self.ctype == CollectionType.DOCUMENT:
            return self._db._doc_store.get(self.name, key)
        elif self.ctype == CollectionType.GRAPH:
            return self._db._graph_store.get_node(key)
        elif self.ctype == CollectionType.VECTOR:
            return self._db._vec_store.get(key)
        elif self.ctype == CollectionType.OBJECT:
            return self._db._obj_store.get(key)
        elif self.ctype == CollectionType.METADATA:
            return self._db._meta_store.get(self.name, key)
        elif self.ctype == CollectionType.VERSION:
            return self._db._ver_store.get(self.name, key, kwargs.get("version"))
        elif self.ctype == CollectionType.SNAPSHOT:
            return self._db._snap_store.get(key)
        elif self.ctype == CollectionType.ARCHIVE:
            return self._db._arch_store.retrieve(key)
        return None

    def delete(self, key: str) -> bool:
        if self.ctype == CollectionType.DOCUMENT:
            return self._db._doc_store.delete(self.name, key)
        elif self.ctype == CollectionType.GRAPH:
            return self._db._graph_store.delete_node(key)
        elif self.ctype == CollectionType.VECTOR:
            return self._db._vec_store.delete(key)
        elif self.ctype == CollectionType.OBJECT:
            return self._db._obj_store.delete(key)
        elif self.ctype == CollectionType.METADATA:
            return self._db._meta_store.delete(self.name, key)
        elif self.ctype == CollectionType.VERSION:
            return self._db._ver_store.delete_key(self.name, key)
        elif self.ctype == CollectionType.SNAPSHOT:
            return self._db._snap_store.delete(key)
        elif self.ctype == CollectionType.ARCHIVE:
            return self._db._arch_store.delete(key)
        return False

    def query(self, q: Query) -> QueryResult:
        if self.ctype in (CollectionType.DOCUMENT, CollectionType.METADATA):
            return self._db._doc_store.query(self.name, q)
        elif self.ctype == CollectionType.TIME_SERIES:
            start = 0.0
            end = float("inf")
            for field, op, value in q.filters:
                if field == "start" and op == "gte":
                    start = float(value)
                elif field == "end" and op == "lte":
                    end = float(value)
            records = self._db._ts_store.query_range(self.name, start, end)
            return QueryResult(records=records, total=len(records))
        return QueryResult()

    def search(self, vector: list[float], k: int = 10) -> list[tuple[str, float]]:
        if self.ctype == CollectionType.VECTOR:
            return self._db._vec_store.search(vector, k)
        return []

    def count(self) -> int:
        if self.ctype == CollectionType.DOCUMENT:
            return self._db._doc_store.count(self.name)
        elif self.ctype == CollectionType.GRAPH:
            return self._db._graph_store.node_count()
        elif self.ctype == CollectionType.VECTOR:
            return self._db._vec_store.count()
        elif self.ctype == CollectionType.TIME_SERIES:
            return self._db._ts_store.total_points()
        elif self.ctype == CollectionType.EVENT:
            return self._db._event_store.event_count()
        elif self.ctype == CollectionType.OBJECT:
            return self._db._obj_store.count()
        elif self.ctype == CollectionType.SNAPSHOT:
            return self._db._snap_store.count()
        elif self.ctype == CollectionType.ARCHIVE:
            return self._db._arch_store.count()
        return 0


class Database:
    """Unified Database facade — multi-model engineering database."""

    def __init__(self, config: StorageConfig | None = None):
        self._config = config or StorageConfig()
        self._engine = StorageEngine(self._config)
        self._cache = CacheManager(
            max_entries_l1=self._config.cache_max_entries_l1,
            max_entries_l2=self._config.cache_max_entries_l2,
        )
        self._query_planner = QueryPlanner()
        self._shard_mgr = ShardManager()

        self._doc_store = DocumentStore(self._engine)
        self._graph_store = GraphStore()
        self._vec_store = VectorStore(
            dimension=self._config.vector_dimension,
            index_cells=self._config.vector_index_cells,
        )
        self._ts_store = TimeSeriesStore(
            retention_days=self._config.time_series_retention_days,
        )
        self._event_store = EventStore()
        self._obj_store = ObjectStore(self._config)
        self._meta_store = MetadataStore(self._engine)
        self._ver_store = VersionStore(self._engine)
        self._snap_store = SnapshotStore(self._obj_store)
        self._arch_store = ArchiveStore(self._obj_store)

        self._collections: dict[str, Collection] = {}
        self._query_planner.register_store("document", self._doc_store)

    def collection(self, name: str, ctype: CollectionType = CollectionType.DOCUMENT) -> Collection:
        if name not in self._collections:
            self._engine.create_collection(name, ctype)
            self._collections[name] = Collection(name, ctype, self)
        return self._collections[name]

    def drop(self, name: str) -> bool:
        if name in self._collections:
            del self._collections[name]
        return self._engine.catalog.drop(name)

    def list_collections(self) -> list[dict[str, Any]]:
        return [
            {"name": c.name, "type": c.ctype.value}
            for c in self._collections.values()
        ]

    def begin(self, isolation: IsolationLevel = IsolationLevel.READ_COMMITTED):
        return self._engine.begin(isolation)

    def commit(self, txn_id: str) -> bool:
        return self._engine.commit(txn_id)

    def rollback(self, txn_id: str) -> bool:
        return self._engine.rollback(txn_id)

    @property
    def cache(self) -> CacheManager:
        return self._cache

    @property
    def query_planner(self) -> QueryPlanner:
        return self._query_planner

    @property
    def shard_manager(self) -> ShardManager:
        return self._shard_mgr

    @property
    def graph(self) -> GraphStore:
        return self._graph_store

    @property
    def vector(self) -> VectorStore:
        return self._vec_store

    @property
    def timeseries(self) -> TimeSeriesStore:
        return self._ts_store

    @property
    def events(self) -> EventStore:
        return self._event_store

    @property
    def objects(self) -> ObjectStore:
        return self._obj_store

    @property
    def metadata(self) -> MetadataStore:
        return self._meta_store

    @property
    def versions(self) -> VersionStore:
        return self._ver_store

    @property
    def snapshots(self) -> SnapshotStore:
        return self._snap_store

    @property
    def archives(self) -> ArchiveStore:
        return self._arch_store

    def summary(self) -> dict[str, Any]:
        return {
            "collections": len(self._collections),
            "cache": self._cache.summary(),
            "engine": self._engine.summary(),
            "stores": {
                "graph": self._graph_store.summary(),
                "vector": self._vec_store.summary(),
                "timeseries": self._ts_store.summary(),
                "events": self._event_store.summary(),
                "objects": self._obj_store.summary(),
                "metadata": self._meta_store.summary(),
                "versions": self._ver_store.summary(),
                "snapshots": self._snap_store.summary(),
                "archives": self._arch_store.summary(),
            },
            "query_planner": self._query_planner.summary(),
            "shards": self._shard_mgr.summary(),
        }
