"""
test_metamodel.py — Global Meta Model tests.
"""

from __future__ import annotations

import pytest

from genesis.metamodel import (
    UnifiedEntity, EntityType, EntityRelation, EntityMetadata,
    UnifiedGraph, EntityTypeRegistry, EntityQuery,
)
from genesis.metamodel.registry import registry


# ── Entity Tests ──


def test_create_unified_entity():
    e = UnifiedEntity(name="test-entity", entity_type=EntityType.MODULE)
    assert e.uid
    assert e.name == "test-entity"
    assert e.entity_type == EntityType.MODULE
    assert e.metadata.created_at > 0


def test_entity_set_and_get():
    e = UnifiedEntity(name="repo", entity_type=EntityType.REPOSITORY)
    e.set("language", "python")
    e.set("stars", 100)
    assert e.get("language") == "python"
    assert e.get("stars") == 100
    assert e.get("nonexistent", "default") == "default"


def test_entity_to_dict_roundtrip():
    e = UnifiedEntity(name="service", entity_type=EntityType.SERVICE)
    e.set("port", 8080)
    e.metadata.tags = ["api", "production"]
    d = e.to_dict()
    e2 = UnifiedEntity.from_dict(d)
    assert e2.uid == e.uid
    assert e2.name == "service"
    assert e2.entity_type == EntityType.SERVICE
    assert e2.get("port") == 8080
    assert e2.metadata.tags == ["api", "production"]


def test_entity_equality():
    e1 = UnifiedEntity(name="a", entity_type=EntityType.REPOSITORY)
    e2 = UnifiedEntity(name="a", entity_type=EntityType.REPOSITORY)
    assert e1 == e1
    assert e1 != e2  # different uids


def test_entity_hash():
    e = UnifiedEntity(name="hash-test", entity_type=EntityType.CLASS)
    s = {e, e}
    assert len(s) == 1


@pytest.mark.parametrize("et", list(EntityType))
def test_all_entity_types_creatable(et):
    e = UnifiedEntity(name=et.value, entity_type=et)
    assert e.entity_type == et


@pytest.mark.parametrize("er", list(EntityRelation))
def test_all_relation_types_usable(er):
    e1 = UnifiedEntity(name="src", entity_type=EntityType.MODULE)
    e2 = UnifiedEntity(name="tgt", entity_type=EntityType.MODULE)
    g = UnifiedGraph()
    g.add_entity(e1)
    g.add_entity(e2)
    g.add_edge(e1, e2, er)
    assert len(g.edges) == 1
    assert g.edges[0].relation == er


# ── Graph Tests ──


@pytest.fixture
def populated_graph():
    g = UnifiedGraph(graph_id="test")
    repo = UnifiedEntity(name="venus", entity_type=EntityType.REPOSITORY)
    mod = UnifiedEntity(name="core", entity_type=EntityType.MODULE)
    cls = UnifiedEntity(name="Engine", entity_type=EntityType.CLASS)
    fn = UnifiedEntity(name="run", entity_type=EntityType.FUNCTION)
    spec = UnifiedEntity(name="spec-v1", entity_type=EntityType.SPECIFICATION)
    org = UnifiedEntity(name="Strategic", entity_type=EntityType.ORGANIZATION)

    for e in [repo, mod, cls, fn, spec, org]:
        g.add_entity(e)

    g.add_edge(repo, mod, EntityRelation.CONTAINS)
    g.add_edge(mod, cls, EntityRelation.CONTAINS)
    g.add_edge(cls, fn, EntityRelation.CONTAINS)
    g.add_edge(repo, spec, EntityRelation.REFERENCES_SPEC)
    g.add_edge(org, repo, EntityRelation.OWNS)

    return g, repo, mod, cls, fn, spec, org


def test_graph_add_entity(populated_graph):
    g, *_ = populated_graph
    assert g.entity_count() == 6


def test_graph_find_by_type(populated_graph):
    g, *_ = populated_graph
    repos = g.find_by_type(EntityType.REPOSITORY)
    assert len(repos) == 1
    assert repos[0].name == "venus"

    classes = g.find_by_type(EntityType.CLASS)
    assert len(classes) == 1
    assert classes[0].name == "Engine"


def test_graph_find(populated_graph):
    g, *_ = populated_graph
    results = g.find(name="venus")
    assert len(results) == 1

    results = g.find(EntityType.FUNCTION)
    assert len(results) == 1
    assert results[0].name == "run"


def test_graph_neighbors(populated_graph):
    g, repo, mod, *_ = populated_graph
    neighbors = g.neighbors(repo.uid, direction="out")
    assert len(neighbors) == 2  # contains mod, references_sec spec

    in_neighbors = g.neighbors(mod.uid, direction="in")
    assert len(in_neighbors) == 1  # repo contains mod


def test_graph_subgraph(populated_graph):
    g, repo, *_ = populated_graph
    sub = g.subgraph(repo.uid, depth=2)
    assert sub.entity_count() >= 3  # repo + mod + cls (depth 2)
    assert sub.graph_id.endswith(".sub")


def test_graph_remove_entity(populated_graph):
    g, repo, mod, *_ = populated_graph
    g.remove_entity(mod.uid)
    assert mod.uid not in g.entities
    # Edges involving mod should be removed
    for e in g.edges:
        assert e.source_uid != mod.uid
        assert e.target_uid != mod.uid


def test_graph_type_counts(populated_graph):
    g, *_ = populated_graph
    counts = g.type_counts()
    assert counts.get("repository") == 1
    assert counts.get("class") == 1


def test_graph_merge():
    g1 = UnifiedGraph()
    g2 = UnifiedGraph()
    e1 = UnifiedEntity(name="a", entity_type=EntityType.MODULE)
    e2 = UnifiedEntity(name="b", entity_type=EntityType.MODULE)
    g1.add_entity(e1)
    g2.add_entity(e2)
    g1.merge(g2)
    assert g1.entity_count() == 2


def test_graph_filter(populated_graph):
    g, *_ = populated_graph
    sub = g.filter(entity_type=EntityType.MODULE)
    assert sub.entity_count() == 1


def test_graph_save_load(tmp_path):
    g1 = UnifiedGraph(graph_id="save-test")
    e = UnifiedEntity(name="test-entity", entity_type=EntityType.SERVICE)
    g1.add_entity(e)
    path = tmp_path / "graph.json"
    g1.save(path)
    g2 = UnifiedGraph.load(path)
    assert g2.graph_id == "save-test"
    assert g2.entity_count() == 1
    assert g2.get_entity(e.uid) is not None


def test_graph_summary(populated_graph):
    g, *_ = populated_graph
    s = g.summary()
    assert s["entity_count"] == 6
    assert s["edge_count"] == 5


def test_graph_clear(populated_graph):
    g, *_ = populated_graph
    g.clear()
    assert g.entity_count() == 0
    assert len(g.edges) == 0


# ── Query Tests ──


def test_query_basic(populated_graph):
    g, *_ = populated_graph
    q = EntityQuery(g)
    result = q.of_type(EntityType.REPOSITORY).execute()
    assert result.count == 1
    assert result.entities[0].name == "venus"


def test_query_named(populated_graph):
    g, *_ = populated_graph
    q = EntityQuery(g)
    result = q.named("Engine").execute()
    assert result.count == 1


def test_query_limit(populated_graph):
    g, *_ = populated_graph
    q = EntityQuery(g)
    result = q.limit(2).execute()
    assert len(result.entities) <= 2


def test_query_first(populated_graph):
    g, *_ = populated_graph
    q = EntityQuery(g)
    e = q.of_type(EntityType.REPOSITORY).first()
    assert e is not None
    assert e.name == "venus"


def test_query_exists(populated_graph):
    g, *_ = populated_graph
    q = EntityQuery(g)
    assert q.of_type(EntityType.REPOSITORY).exists()
    assert not q.of_type(EntityType.DATABASE).exists()


def test_query_bfs(populated_graph):
    g, repo, *_ = populated_graph
    q = EntityQuery(g)
    results = q.bfs(repo.uid, max_depth=2)
    assert len(results) >= 2


def test_query_group_by_type(populated_graph):
    g, *_ = populated_graph
    q = EntityQuery(g)
    types = q.group_by_type()
    assert isinstance(types, dict)
    assert types.get("module") == 1


def test_query_statistics(populated_graph):
    g, *_ = populated_graph
    q = EntityQuery(g)
    stats = q.statistics()
    assert stats["total"] == 6
    assert stats["edges"] == 5


# ── Registry Tests ──


def test_registry_has_all_types():
    for et in EntityType:
        info = registry.get_type(et.value)
        assert info is not None, f"Missing type: {et.value}"


def test_registry_has_all_relations():
    for er in EntityRelation:
        info = registry.get_relation(er.value)
        assert info is not None, f"Missing relation: {er.value}"


def test_registry_all_types():
    types = registry.all_types()
    assert len(types) >= len(EntityType)


def test_registry_all_relations():
    rels = registry.all_relations()
    assert len(rels) >= len(EntityRelation)


def test_registry_summary():
    s = registry.summary()
    assert s["entity_types"] >= len(EntityType)
    assert s["relation_types"] >= len(EntityRelation)


# ── Edge Management Tests ──


def test_add_duplicate_edge(populated_graph):
    g, repo, mod, *_ = populated_graph
    g.add_edge(repo, mod, EntityRelation.CONTAINS)
    count = len(g.edges)
    g.add_edge(repo, mod, EntityRelation.CONTAINS)
    assert len(g.edges) == count + 1  # duplicates allowed


def test_edge_between(populated_graph):
    g, repo, mod, *_ = populated_graph
    edges = g.edges_between(repo.uid, mod.uid)
    assert len(edges) == 1
    assert edges[0].relation == EntityRelation.CONTAINS


def test_neighbor_direction(populated_graph):
    g, repo, mod, cls, fn, *_ = populated_graph
    # Out from mod: cls
    out = g.neighbors(mod.uid, direction="out")
    assert len(out) == 1
    assert out[0][0] == cls.uid

    # In to cls: mod
    inn = g.neighbors(cls.uid, direction="in")
    assert len(inn) == 1
    assert inn[0][0] == mod.uid
