"""Tests for Universal Query Engine (Mission 179)."""

from unittest.mock import MagicMock

from genesis.query import QueryEngine, Query, QueryResult


class TestQuery:
    def test_defaults(self):
        q = Query(text="test")
        assert q.text == "test"
        assert q.sources == ["all"]
        assert q.limit == 20


class TestQueryResult:
    def test_fields(self):
        r = QueryResult(source="test", type="obj", label="Test", relevance=0.9)
        assert r.source == "test"
        assert r.relevance == 0.9


class TestQueryEngine:
    def test_register_and_query(self):
        qe = QueryEngine()
        qe.register("test", lambda q: [
            QueryResult(source="test", type="item", label=f"Result for {q.text}", relevance=0.8)
        ])
        results = qe.search("hello")
        assert len(results) == 1
        assert "hello" in results[0].label

    def test_multiple_sources(self):
        qe = QueryEngine()
        qe.register("src_a", lambda q: [
            QueryResult(source="src_a", type="a", label="A1", relevance=0.9),
            QueryResult(source="src_a", type="a", label="A2", relevance=0.3),
        ])
        qe.register("src_b", lambda q: [
            QueryResult(source="src_b", type="b", label="B1", relevance=0.7),
        ])
        results = qe.search("test", limit=10)
        assert len(results) == 3
        # Sorted by relevance descending
        assert results[0].relevance >= results[1].relevance >= results[2].relevance

    def test_source_filtering(self):
        qe = QueryEngine()
        qe.register("src_a", lambda q: [QueryResult(source="src_a", type="a", label="A", relevance=0.9)])
        qe.register("src_b", lambda q: [QueryResult(source="src_b", type="b", label="B", relevance=0.8)])
        results = qe.search("test", sources=["src_a"])
        assert len(results) == 1
        assert results[0].source == "src_a"

    def test_min_relevance(self):
        qe = QueryEngine()
        qe.register("src", lambda q: [
            QueryResult(source="src", type="a", label="A", relevance=0.5),
            QueryResult(source="src", type="a", label="B", relevance=0.9),
        ])
        q = Query(text="test", min_relevance=0.7)
        results = qe.query(q)
        assert len(results) == 1
        assert results[0].relevance >= 0.7

    def test_limit(self):
        qe = QueryEngine()
        qe.register("src", lambda q: [
            QueryResult(source="src", type="a", label=f"R{i}", relevance=0.9)
            for i in range(100)
        ])
        results = qe.search("test", limit=5)
        assert len(results) == 5

    def test_error_handler_doesnt_break(self):
        qe = QueryEngine()
        qe.register("broken", lambda q: (_ for _ in ()).throw(RuntimeError("oops")))
        qe.register("good", lambda q: [QueryResult(source="good", type="g", label="OK", relevance=1.0)])
        results = qe.search("test")
        assert len(results) == 1
        assert results[0].source == "good"

    def test_register_fabric_kernel(self):
        kernel = MagicMock()
        kernel.query_events.return_value = []
        eng_mock = MagicMock()
        eng_mock.search.return_value = []
        kernel.engineering = eng_mock
        kernel.knowledge = MagicMock()
        kernel.knowledge.search.return_value = []
        kernel._audit = MagicMock()
        kernel._audit.query.return_value = []
        kernel.timeline = MagicMock()
        kernel.timeline.query.return_value = []
        kernel.ai = MagicMock()
        kernel.ai.list_providers.return_value = []
        kernel.agent_runtime = MagicMock()
        kernel.agent_runtime.list_agents.return_value = []

        qe = QueryEngine()
        qe.register_fabric_kernel(kernel)
        results = qe.search("anything")
        assert isinstance(results, list)
