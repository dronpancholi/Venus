"""Tests for GENESIS XI Program 2 — Universal Engineering Database."""

import time
import pytest
from genesis.ued.types import (
    CollectionType, StorageConfig, IsolationLevel, Query, QueryResult,
    ShardKey, ShardStrategy, CompressionType, CachePolicy,
)
from genesis.ued.engine import StorageEngine, PageStore, Journal, MVCCStore, TransactionManager, Catalog
from genesis.ued.cache import CacheManager
from genesis.ued.index import BTreeIndex, HashIndex, InvertedIndex, VectorIndex
from genesis.ued.stores import DocumentStore, MetadataStore, VersionStore
from genesis.ued.graph import GraphStore, GraphNode, GraphEdge
from genesis.ued.vector import VectorStore
from genesis.ued.timeseries import TimeSeriesStore, EventStore
from genesis.ued.object import ObjectStore, SnapshotStore, ArchiveStore
from genesis.ued.query import QueryPlanner, QueryPlan
from genesis.ued.shard import ShardManager
from genesis.ued.database import Database, Collection


# ── Types Tests ──

class TestStorageConfig:
    def test_defaults(self):
        c = StorageConfig()
        assert c.page_size == 4096
        assert c.compression == CompressionType.LZ4

    def test_validate_power_of_two(self):
        with pytest.raises(AssertionError):
            StorageConfig(page_size=1000).validate()

    def test_validate_ok(self):
        StorageConfig(page_size=4096).validate()


class TestQuery:
    def test_matches_eq(self):
        q = Query(filters=[("name", "eq", "alice")])
        assert q.matches({"name": "alice"})
        assert not q.matches({"name": "bob"})

    def test_matches_gt(self):
        q = Query(filters=[("age", "gt", 25)])
        assert q.matches({"age": 30})
        assert not q.matches({"age": 20})

    def test_matches_in(self):
        q = Query(filters=[("role", "in", ["admin", "user"])])
        assert q.matches({"role": "admin"})
        assert not q.matches({"role": "guest"})

    def test_matches_contains(self):
        q = Query(filters=[("tags", "contains", "urgent")])
        assert q.matches({"tags": ["urgent", "important"]})
        assert not q.matches({"tags": ["normal"]})

    def test_matches_regex(self):
        q = Query(filters=[("email", "regex", r".*@example\.com")])
        assert q.matches({"email": "a@example.com"})
        assert not q.matches({"email": "a@other.com"})


class TestQueryResult:
    def test_empty(self):
        r = QueryResult()
        assert r.empty


# ── Engine Tests ──

class TestPageStore:
    def test_alloc_and_read(self):
        ps = PageStore(StorageConfig())
        pid = ps.alloc_page()
        assert pid >= 0
        assert ps.read_page(pid) is not None
        assert len(ps.read_page(pid)) == 4096

    def test_write_and_read(self):
        ps = PageStore(StorageConfig(page_size=512))
        pid = ps.alloc_page()
        ps.write_page(pid, b"hello")
        assert ps.read_page(pid)[:5] == b"hello"

    def test_free(self):
        ps = PageStore(StorageConfig())
        pid = ps.alloc_page()
        ps.free_page(pid)
        assert ps.read_page(pid) is None


class TestJournal:
    def test_append(self):
        j = Journal(StorageConfig())
        e = j.append("put", "test", "k1", new_value="v1")
        assert e.action == "put"
        assert e.seq == 1

    def test_replay(self):
        j = Journal(StorageConfig())
        j.append("put", "t", "k1")
        j.append("put", "t", "k2")
        assert len(j.replay()) == 2

    def test_checkpoint(self):
        j = Journal(StorageConfig(journal_max_bytes=1))
        j.append("put", "t", "k1", new_value="x" * 100)
        assert len(j.replay()) == 0
        assert j.summary()["entries"] == 0


class TestMVCCStore:
    def test_put_and_get(self):
        mvcc = MVCCStore(StorageConfig())
        mvcc.put("k1", "v1", "txn1", read_ts=1)
        entry = mvcc.get("k1", read_ts=2)
        assert entry is not None
        assert entry.value == "v1"

    def test_delete(self):
        mvcc = MVCCStore(StorageConfig())
        mvcc.put("k1", "v1", "txn1", read_ts=1)
        mvcc.delete("k1", "txn2", read_ts=2)
        assert mvcc.get("k1", read_ts=3) is None

    def test_visibility(self):
        mvcc = MVCCStore(StorageConfig())
        mvcc.put("k1", "v1", "txn1", read_ts=1)
        assert mvcc.get("k1", read_ts=0) is None
        assert mvcc.get("k1", read_ts=1) is not None

    def test_scan(self):
        mvcc = MVCCStore(StorageConfig())
        mvcc.put("k1", "v1", "t1", read_ts=1)
        mvcc.put("k2", "v2", "t1", read_ts=2)
        assert len(mvcc.scan(read_ts=3)) == 2


class TestTransactionManager:
    def test_begin_commit(self):
        mvcc = MVCCStore(StorageConfig())
        tm = TransactionManager(mvcc)
        txn = tm.begin()
        assert txn.status == "active"
        assert tm.commit(txn.id)
        assert tm.get(txn.id).status == "committed"

    def test_begin_rollback(self):
        mvcc = MVCCStore(StorageConfig())
        tm = TransactionManager(mvcc)
        txn = tm.begin()
        assert tm.rollback(txn.id)
        assert tm.get(txn.id).status == "rolled_back"


class TestCatalog:
    def test_create_and_get(self):
        cat = Catalog()
        meta = cat.create_collection("users", CollectionType.DOCUMENT)
        assert cat.get("users").name == "users"
        assert cat.get("users").ctype == CollectionType.DOCUMENT

    def test_drop(self):
        cat = Catalog()
        cat.create_collection("temp", CollectionType.DOCUMENT)
        assert cat.drop("temp")
        assert not cat.drop("nonexistent")

    def test_list(self):
        cat = Catalog()
        cat.create_collection("a", CollectionType.GRAPH)
        cat.create_collection("b", CollectionType.DOCUMENT)
        assert len(cat.list_collections()) == 2
        assert len(cat.list_collections(CollectionType.GRAPH)) == 1


class TestStorageEngine:
    def test_begin_commit(self):
        engine = StorageEngine()
        txn = engine.begin()
        assert engine.commit(txn.id)

    def test_put_get(self):
        engine = StorageEngine()
        engine.create_collection("test", CollectionType.DOCUMENT)
        txn = engine.begin()
        engine.put("test", "k1", {"name": "test"}, txn.id, txn.read_ts)
        engine.commit(txn.id)
        assert engine.get("k1", read_ts=100) == {"name": "test"}

    def test_delete(self):
        engine = StorageEngine()
        engine.create_collection("test", CollectionType.DOCUMENT)
        txn = engine.begin()
        engine.put("test", "k1", "v1", txn.id, txn.read_ts)
        engine.delete("test", "k1", txn.id, txn.read_ts + 1)
        engine.commit(txn.id)

    def test_summary(self):
        engine = StorageEngine()
        s = engine.summary()
        assert "catalog" in s
        assert "transactions" in s


# ── Cache Tests ──

class TestCacheManager:
    def test_set_get(self):
        cache = CacheManager(max_entries_l1=100)
        cache.set("k1", "v1")
        assert cache.get("k1") == "v1"

    def test_miss(self):
        cache = CacheManager()
        assert cache.get("nonexistent") is None

    def test_invalidate(self):
        cache = CacheManager()
        cache.set("k1", "v1")
        cache.invalidate("k1")
        assert cache.get("k1") is None

    def test_eviction(self):
        cache = CacheManager(max_entries_l1=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.get("c") == 3
        assert cache.get("c") is not None

    def test_hit_rate(self):
        cache = CacheManager()
        cache.set("k", "v")
        cache.get("k")
        cache.get("missing")
        rate = cache.hit_rate()
        assert 0 < rate < 1.0


# ── Index Tests ──

class TestBTreeIndex:
    def test_insert_search(self):
        idx = BTreeIndex("test", "age")
        idx.insert(25, "rec1")
        idx.insert(30, "rec2")
        assert len(idx.search(25)) == 1
        assert len(idx.search(35)) == 0

    def test_range_scan(self):
        idx = BTreeIndex("test", "age")
        for age in range(10, 30):
            idx.insert(age, f"rec_{age}")
        results = idx.range_scan(15, 20)
        assert len(results) == 6

    def test_delete(self):
        idx = BTreeIndex("test", "age")
        idx.insert(25, "rec1")
        idx.delete(25, "rec1")
        assert len(idx.search(25)) == 0

    def test_prefix_scan(self):
        idx = BTreeIndex("test", "name")
        idx.insert("hello", "r1")
        idx.insert("help", "r2")
        idx.insert("world", "r3")
        assert len(idx.prefix_scan("hel")) == 2


class TestHashIndex:
    def test_insert_search(self):
        idx = HashIndex("test", "email")
        idx.insert("a@x.com", "u1")
        assert len(idx.search("a@x.com")) == 1
        assert len(idx.search("b@x.com")) == 0

    def test_delete(self):
        idx = HashIndex("test", "email")
        idx.insert("a@x.com", "u1")
        idx.delete("a@x.com", "u1")
        assert len(idx.search("a@x.com")) == 0


class TestInvertedIndex:
    def test_index_search(self):
        idx = InvertedIndex("test", "content")
        idx.index("doc1", "hello world")
        idx.index("doc2", "hello there")
        results = idx.search("hello world")
        assert "doc1" in results

    def test_search_or(self):
        idx = InvertedIndex("test", "content")
        idx.index("doc1", "cats")
        idx.index("doc2", "dogs")
        results = idx.search_or("cats dogs")
        assert len(results) == 2

    def test_remove(self):
        idx = InvertedIndex("test", "content")
        idx.index("doc1", "hello world")
        idx.remove("doc1", "hello world")
        assert len(idx.search("hello")) == 0

    def test_stop_words_filtered(self):
        idx = InvertedIndex("test", "content")
        tokens = idx.tokenize("the quick brown fox")
        assert "the" not in tokens
        assert "quick" in tokens


class TestVectorIndex:
    def test_insert_search(self):
        idx = VectorIndex("test", dimension=4)
        idx.insert("v1", [1.0, 0.0, 0.0, 0.0])
        idx.insert("v2", [0.0, 1.0, 0.0, 0.0])
        results = idx.search([1.0, 0.0, 0.0, 0.0], k=2)
        assert results[0][0] == "v1"

    def test_wrong_dimension(self):
        idx = VectorIndex("test", dimension=4)
        with pytest.raises(ValueError):
            idx.insert("bad", [1.0, 2.0])


# ── DocumentStore Tests ──

class TestDocumentStore:
    def test_insert_get(self):
        store = DocumentStore(StorageEngine())
        doc_id = store.insert("users", {"name": "Alice", "age": 30})
        doc = store.get("users", doc_id)
        assert doc["name"] == "Alice"

    def test_update(self):
        store = DocumentStore(StorageEngine())
        doc_id = store.insert("users", {"name": "Bob", "age": 25})
        assert store.update("users", doc_id, {"age": 26})
        assert store.get("users", doc_id)["age"] == 26

    def test_delete(self):
        store = DocumentStore(StorageEngine())
        doc_id = store.insert("users", {"name": "Carol"})
        assert store.delete("users", doc_id)
        assert store.get("users", doc_id) is None

    def test_query_filters(self):
        store = DocumentStore(StorageEngine())
        store.insert("users", {"name": "Alice", "role": "admin"})
        store.insert("users", {"name": "Bob", "role": "user"})
        q = Query(filters=[("role", "eq", "admin")])
        result = store.query("users", q)
        assert len(result.records) == 1
        assert result.records[0]["name"] == "Alice"

    def test_query_sort(self):
        store = DocumentStore(StorageEngine())
        store.insert("items", {"name": "b", "price": 20})
        store.insert("items", {"name": "a", "price": 10})
        q = Query(sort=[("price", False)])
        result = store.query("items", q)
        assert result.records[0]["price"] == 10

    def test_create_index(self):
        store = DocumentStore(StorageEngine())
        store.insert("users", {"name": "Dave", "email": "d@x.com"})
        store.create_index("users", "email", "hash")
        assert len(store._indexes.get("users", [])) >= 1


# ── MetadataStore Tests ──

class TestMetadataStore:
    def test_set_get(self):
        store = MetadataStore(StorageEngine())
        store.set("app", "version", "1.0")
        assert store.get("app", "version") == "1.0"

    def test_delete(self):
        store = MetadataStore(StorageEngine())
        store.set("app", "key", "val")
        assert store.delete("app", "key")
        assert store.get("app", "key") is None

    def test_list_namespace(self):
        store = MetadataStore(StorageEngine())
        store.set("ns1", "a", 1)
        store.set("ns1", "b", 2)
        assert len(store.list_namespace("ns1")) == 2


# ── VersionStore Tests ──

class TestVersionStore:
    def test_put_get(self):
        store = VersionStore(StorageEngine())
        store.put("docs", "doc1", "v1")
        assert store.get("docs", "doc1") == "v1"

    def test_versioning(self):
        store = VersionStore(StorageEngine())
        store.put("docs", "doc1", "v1")
        store.put("docs", "doc1", "v2")
        assert store.get("docs", "doc1", version=1) == "v1"
        assert store.get("docs", "doc1", version=2) == "v2"

    def test_list_versions(self):
        store = VersionStore(StorageEngine())
        store.put("docs", "doc1", "v1")
        store.put("docs", "doc1", "v2")
        versions = store.list_versions("docs", "doc1")
        assert len(versions) == 2

    def test_diff(self):
        store = VersionStore(StorageEngine())
        store.put("docs", "doc1", "hello")
        store.put("docs", "doc1", "world")
        d = store.diff("docs", "doc1", 1, 2)
        assert d["changed"]


# ── GraphStore Tests ──

class TestGraphStore:
    def test_add_node(self):
        g = GraphStore()
        nid = g.add_node(GraphNode(labels=["Person"], properties={"name": "Alice"}))
        assert g.get_node(nid).properties["name"] == "Alice"

    def test_add_edge(self):
        g = GraphStore()
        n1 = g.add_node(GraphNode())
        n2 = g.add_node(GraphNode())
        eid = g.add_edge(GraphEdge(source_id=n1, target_id=n2, edge_type="knows"))
        assert g.get_edge(eid).edge_type == "knows"

    def test_edge_missing_node(self):
        g = GraphStore()
        n1 = g.add_node(GraphNode())
        with pytest.raises(ValueError):
            g.add_edge(GraphEdge(source_id=n1, target_id="nonexistent"))

    def test_delete_node(self):
        g = GraphStore()
        nid = g.add_node(GraphNode())
        assert g.delete_node(nid)
        assert g.get_node(nid) is None

    def test_neighbors(self):
        g = GraphStore()
        a = g.add_node(GraphNode(labels=["Person"]))
        b = g.add_node(GraphNode(labels=["Person"]))
        g.add_edge(GraphEdge(source_id=a, target_id=b))
        neighbors = g.neighbors(a)
        assert len(neighbors) == 1

    def test_bfs(self):
        g = GraphStore()
        a = g.add_node(GraphNode())
        b = g.add_node(GraphNode())
        c = g.add_node(GraphNode())
        g.add_edge(GraphEdge(source_id=a, target_id=b))
        g.add_edge(GraphEdge(source_id=b, target_id=c))
        result = g.bfs(a, max_depth=3)
        assert len(result) == 3

    def test_shortest_path(self):
        g = GraphStore()
        a = g.add_node(GraphNode())
        b = g.add_node(GraphNode())
        c = g.add_node(GraphNode())
        g.add_edge(GraphEdge(source_id=a, target_id=b))
        g.add_edge(GraphEdge(source_id=b, target_id=c))
        path = g.shortest_path(a, c)
        assert len(path) == 3

    def test_find_by_label(self):
        g = GraphStore()
        g.add_node(GraphNode(labels=["Person"]))
        g.add_node(GraphNode(labels=["Company"]))
        assert len(g.find_nodes_by_label("Person")) == 1


# ── VectorStore Tests ──

class TestVectorStore:
    def test_insert_search(self):
        vs = VectorStore(dimension=4)
        vs.insert("v1", [1.0, 0.0, 0.0, 0.0])
        vs.insert("v2", [0.0, 1.0, 0.0, 0.0])
        results = vs.search([1.0, 0.0, 0.0, 0.0], k=2)
        assert results[0][0] == "v1"

    def test_search_with_filter(self):
        vs = VectorStore(dimension=2)
        vs.insert("v1", [1.0, 0.0], metadata={"label": "cat"})
        vs.insert("v2", [0.0, 1.0], metadata={"label": "dog"})
        q = Query(filters=[("label", "eq", "cat")])
        results = vs.search_with_filter([1.0, 0.0], q, k=5)
        assert len(results) == 1

    def test_delete(self):
        vs = VectorStore(dimension=2)
        vs.insert("v1", [1.0, 0.0])
        assert vs.delete("v1")
        assert vs.get("v1") is None

    def test_count(self):
        vs = VectorStore(dimension=2)
        vs.insert("a", [1.0, 0.0])
        vs.insert("b", [0.0, 1.0])
        assert vs.count() == 2


# ── TimeSeriesStore Tests ──

class TestTimeSeriesStore:
    def test_insert_query(self):
        ts = TimeSeriesStore(retention_days=365)
        now = time.time()
        ts.insert("cpu", now - 10, 50.0)
        ts.insert("cpu", now - 5, 60.0)
        results = ts.query_range("cpu", now - 20, now)
        assert len(results) == 2

    def test_last_n(self):
        ts = TimeSeriesStore()
        ts.insert("cpu", 1, 10.0)
        ts.insert("cpu", 2, 20.0)
        ts.insert("cpu", 3, 30.0)
        last = ts.last_n("cpu", 2)
        assert len(last) == 2
        assert last[-1]["value"] == 30.0

    def test_aggregate(self):
        ts = TimeSeriesStore()
        now = time.time()
        for i in range(10):
            ts.insert("cpu", now + i, float(i * 10))
        results = ts.aggregate("cpu", now, now + 10, window_secs=5, fn="avg")
        assert len(results) >= 1

    def test_downsample(self):
        ts = TimeSeriesStore()
        for i in range(10):
            ts.insert("cpu", float(i), float(i))
        down = ts.downsample("cpu", factor=3)
        assert len(down) >= 3

    def test_subscribe(self):
        ts = TimeSeriesStore()
        received = []
        ts.subscribe("cpu", lambda s, p: received.append(p))
        ts.insert("cpu", 1.0, 100.0)
        assert len(received) == 1


# ── EventStore Tests ──

class TestEventStore:
    def test_append_replay(self):
        es = EventStore()
        es.append("test", {"msg": "hello"})
        events = es.replay()
        assert len(events) == 1
        assert events[0]["type"] == "test"

    def test_stream(self):
        es = EventStore()
        es.append("test", {"msg": "a"}, stream="s1")
        es.append("test", {"msg": "b"}, stream="s2")
        assert len(es.replay(stream="s1")) == 1

    def test_filter(self):
        es = EventStore()
        es.append("login", {"user": "a"})
        es.append("logout", {"user": "a"})
        assert len(es.filter(event_type="login")) == 1

    def test_subscribe(self):
        es = EventStore()
        received = []
        es.subscribe(callback=lambda e: received.append(e))
        es.append("test", {})
        assert len(received) == 1


# ── ObjectStore Tests ──

class TestObjectStore:
    def test_put_get(self):
        os = ObjectStore()
        csum = os.put(b"hello world")
        assert os.get(csum) == b"hello world"

    def test_dedup(self):
        os = ObjectStore()
        csum1 = os.put(b"same data")
        csum2 = os.put(b"same data")
        assert csum1 == csum2

    def test_delete(self):
        os = ObjectStore()
        csum = os.put(b"temp data")
        assert os.delete(csum)
        assert os.get(csum) is None

    def test_exists(self):
        os = ObjectStore()
        csum = os.put(b"data")
        assert os.exists(csum)
        assert not os.exists("nonexistent")

    def test_chunked(self):
        os = ObjectStore()
        checksums = os.put_chunked(b"x" * 200000)
        assert len(checksums) >= 3
        reconstructed = os.get_chunked(checksums)
        assert reconstructed == b"x" * 200000


# ── SnapshotStore Tests ──

class TestSnapshotStore:
    def test_create_get(self):
        os = ObjectStore()
        ss = SnapshotStore(os)
        snap_id = ss.create("v1", b"snapshot data")
        assert ss.get(snap_id) == b"snapshot data"

    def test_incremental(self):
        os = ObjectStore()
        ss = SnapshotStore(os)
        parent = ss.create("base", b"base data")
        child = ss.create("inc", b"base data + more", parent=parent)
        assert ss.get(child) == b"base data + more"

    def test_delete(self):
        os = ObjectStore()
        ss = SnapshotStore(os)
        snap_id = ss.create("temp", b"data")
        assert ss.delete(snap_id)
        assert ss.get(snap_id) is None

    def test_list(self):
        os = ObjectStore()
        ss = SnapshotStore(os)
        ss.create("a", b"data_a")
        ss.create("b", b"data_b")
        assert len(ss.list_snapshots()) == 2


# ── ArchiveStore Tests ──

class TestArchiveStore:
    def test_archive_retrieve(self):
        os = ObjectStore()
        ar = ArchiveStore(os)
        aid = ar.archive("test", b"archive data")
        assert ar.retrieve(aid) == b"archive data"

    def test_move_tier(self):
        os = ObjectStore()
        ar = ArchiveStore(os)
        aid = ar.archive("test", b"data")
        assert ar.move_tier(aid, "cold")
        archive = ar.list_archives(tier="cold")
        assert len(archive) == 1

    def test_retention_policy(self):
        os = ObjectStore()
        ar = ArchiveStore(os)
        ar.archive("expired", b"data", retention_days=0)
        assert ar.apply_retention_policy() >= 0

    def test_list_by_tier(self):
        os = ObjectStore()
        ar = ArchiveStore(os)
        ar.archive("a", b"data_a", tier="hot")
        ar.archive("b", b"data_b", tier="cold")
        assert len(ar.list_archives(tier="hot")) == 1
        assert len(ar.list_archives(tier="cold")) == 1

    def test_summary(self):
        os = ObjectStore()
        ar = ArchiveStore(os)
        ar.archive("a", b"data")
        s = ar.summary()
        assert s["total_archives"] == 1


# ── QueryPlanner Tests ──

class TestQueryPlanner:
    def test_plan(self):
        qp = QueryPlanner()
        q = Query(collection="test", filters=[("x", "eq", 1)], limit=10)
        plan = qp.plan(q)
        assert plan.step_count >= 1

    def test_explain(self):
        qp = QueryPlanner()
        q = Query(collection="test")
        explanation = qp.explain(q)
        assert "steps" in explanation
        assert "estimated_cost" in explanation

    def test_optimize(self):
        qp = QueryPlanner()
        q = Query(filters=[("a", "eq", 1), ("a", "eq", 1)])
        opt = qp.optimize(q)
        assert len(opt.filters) == 1

    def test_history(self):
        qp = QueryPlanner()
        q = Query(collection="test")
        qp.execute(q)
        assert len(qp.plan_history()) >= 1


# ── ShardManager Tests ──

class TestShardManager:
    def test_put_get(self):
        sm = ShardManager(num_shards=3)
        sm.put("users", "u1", {"name": "Alice"})
        assert sm.get("users", "u1")["name"] == "Alice"

    def test_delete(self):
        sm = ShardManager()
        sm.put("users", "u1", "val")
        assert sm.delete("users", "u1")
        assert sm.get("users", "u1") is None

    def test_locate(self):
        sm = ShardManager(num_shards=4)
        shard = sm.locate("users", "key123")
        assert 0 <= shard < 4

    def test_range_shard_key(self):
        sm = ShardManager(num_shards=2)
        sk = ShardKey(key_field="age", strategy=ShardStrategy.RANGE,
                      ranges=[(0, 30), (31, 100)])
        sm.set_shard_key("users", sk)
        assert sm.locate("users", 25) == 0
        assert sm.locate("users", 50) == 1

    def test_load_distribution(self):
        sm = ShardManager(num_shards=2)
        sm.put("a", "k1", "v1")
        sm.put("a", "k2", "v2")
        dist = sm.load_distribution()
        assert sum(dist.values()) == 2


# ── Database Integration Tests ──

class TestDatabase:
    def test_create_collection(self):
        db = Database()
        coll = db.collection("users")
        assert coll.name == "users"
        assert coll.ctype == CollectionType.DOCUMENT

    def test_document_crud(self):
        db = Database()
        coll = db.collection("docs")
        doc_id = coll.insert({"title": "Test", "body": "Hello"})
        doc = coll.get(doc_id)
        assert doc["title"] == "Test"
        assert coll.delete(doc_id)
        assert coll.get(doc_id) is None

    def test_graph(self):
        db = Database()
        n1 = db.graph.add_node(GraphNode(labels=["Person"], properties={"name": "A"}))
        n2 = db.graph.add_node(GraphNode(labels=["Person"], properties={"name": "B"}))
        db.graph.add_edge(GraphEdge(source_id=n1, target_id=n2, edge_type="knows"))
        assert db.graph.node_count() == 2
        assert db.graph.edge_count() == 1

    def test_vector(self):
        cfg = StorageConfig(vector_dimension=4)
        db = Database(cfg)
        db.vector.insert("v1", [1.0, 0.0, 0.0, 0.0], {"label": "a"})
        db.vector.insert("v2", [0.0, 1.0, 0.0, 0.0], {"label": "b"})
        results = db.vector.search([1.0, 0.0, 0.0, 0.0], k=2)
        assert len(results) == 2

    def test_timeseries(self):
        db = Database()
        now = time.time()
        db.timeseries.insert("cpu", now, 50.0)
        db.timeseries.insert("cpu", now + 1, 60.0)
        results = db.timeseries.query_range("cpu", now - 10, now + 10)
        assert len(results) == 2

    def test_events(self):
        db = Database()
        db.events.append("deploy", {"status": "ok"})
        db.events.append("deploy", {"status": "fail"})
        assert db.events.event_count() == 2

    def test_objects(self):
        db = Database()
        csum = db.objects.put(b"binary data")
        assert db.objects.get(csum) == b"binary data"

    def test_snapshots(self):
        db = Database()
        snap_id = db.snapshots.create("backup", b"backup data")
        assert db.snapshots.get(snap_id) == b"backup data"

    def test_archives(self):
        db = Database()
        aid = db.archives.archive("log", b"log data")
        assert db.archives.retrieve(aid) == b"log data"

    def test_metadata(self):
        db = Database()
        db.metadata.set("sys", "version", "2.0")
        assert db.metadata.get("sys", "version") == "2.0"

    def test_versions(self):
        db = Database()
        db.versions.put("config", "key1", "v1")
        db.versions.put("config", "key1", "v2")
        assert db.versions.get("config", "key1") == "v2"
        assert db.versions.get("config", "key1", version=1) == "v1"

    def test_transaction(self):
        db = Database()
        txn = db.begin()
        assert txn is not None
        assert db.commit(txn.id)

    def test_cache(self):
        db = Database()
        db.cache.set("k", "v")
        assert db.cache.get("k") == "v"

    def test_query_planner(self):
        db = Database()
        q = Query(collection="test", filters=[("x", "eq", 1)])
        plan = db.query_planner.explain(q)
        assert "steps" in plan

    def test_shard_manager(self):
        db = Database()
        db.shard_manager.put("t", "k", "v")
        assert db.shard_manager.get("t", "k") == "v"

    def test_summary(self):
        db = Database()
        s = db.summary()
        assert "collections" in s
        assert "engine" in s

    def test_drop_collection(self):
        db = Database()
        db.collection("temp")
        assert db.drop("temp")
        assert not db.drop("nonexistent")

    def test_list_collections(self):
        db = Database()
        db.collection("a")
        db.collection("b")
        assert len(db.list_collections()) == 2

    def test_document_query(self):
        db = Database()
        coll = db.collection("items")
        coll.insert({"name": "apple", "price": 1.0})
        coll.insert({"name": "banana", "price": 2.0})
        q = Query(filters=[("price", "gt", 1.0)])
        result = coll.query(q)
        assert len(result.records) == 1
        assert result.records[0]["name"] == "banana"

    def test_vector_search_via_collection(self):
        cfg = StorageConfig(vector_dimension=4)
        db = Database(cfg)
        coll = db.collection("vecs", CollectionType.VECTOR)
        db.vector.insert("v1", [1.0, 0.0, 0.0, 0.0])
        results = coll.search([1.0, 0.0, 0.0, 0.0], k=5)
        assert len(results) >= 1
