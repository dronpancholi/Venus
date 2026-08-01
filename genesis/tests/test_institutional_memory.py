from genesis.memory.institutional import (
    InstitutionalMemory, KnowledgeObject, KnowledgeType, RelationType,
    KnowledgeRelation, SearchResult,
)


def test_store_and_retrieve():
    im = InstitutionalMemory()
    obj = KnowledgeObject(name="Test Arch", knowledge_type=KnowledgeType.ARCHITECTURE, content="test")
    oid = im.store(obj)
    assert im.get(oid) is not None
    assert im.get(oid).name == "Test Arch"


def test_store_generates_id():
    im = InstitutionalMemory()
    oid = im.store(KnowledgeObject(name="X"))
    assert "ko:" in oid


def test_get_by_type():
    im = InstitutionalMemory()
    im.store(KnowledgeObject(name="A", knowledge_type=KnowledgeType.ARCHITECTURE))
    im.store(KnowledgeObject(name="B", knowledge_type=KnowledgeType.BENCHMARK))
    assert len(im.get_by_type(KnowledgeType.ARCHITECTURE)) == 1
    assert len(im.get_by_type(KnowledgeType.BENCHMARK)) == 1


def test_get_by_tag():
    im = InstitutionalMemory()
    im.store(KnowledgeObject(name="A", tags=["tag1"]))
    im.store(KnowledgeObject(name="B", tags=["tag2"]))
    assert len(im.get_by_tag("tag1")) == 1
    assert len(im.get_by_tag("tag2")) == 1


def test_relate():
    im = InstitutionalMemory()
    oid1 = im.store(KnowledgeObject(name="A"))
    oid2 = im.store(KnowledgeObject(name="B"))
    rid = im.relate(oid1, oid2, RelationType.DEPENDS_ON)
    assert rid is not None
    rels = im.get_relations(oid1)
    assert len(rels) == 1
    assert rels[0].relation_type == RelationType.DEPENDS_ON


def test_search():
    im = InstitutionalMemory()
    im.store(KnowledgeObject(name="Architecture Review", content="review of system architecture", tags=["arch"]))
    im.store(KnowledgeObject(name="Benchmark Results", content="performance metrics", tags=["perf"]))
    results = im.search("architecture")
    assert len(results) >= 1
    assert results[0].score > 0


def test_search_min_score():
    im = InstitutionalMemory()
    im.store(KnowledgeObject(name="Alpha", content="alpha beta gamma"))
    results = im.search("alpha delta", min_score=0.5)
    assert len(results) >= 0


def test_impact_analysis():
    im = InstitutionalMemory()
    a = im.store(KnowledgeObject(name="A"))
    b = im.store(KnowledgeObject(name="B"))
    im.relate(a, b, RelationType.DEPENDS_ON)
    impact = im.get_impact(a)
    assert len(impact["downstream"]) == 1
    assert len(impact["upstream"]) == 0
    impact2 = im.get_impact(b)
    assert len(impact2["upstream"]) == 1


def test_timeline():
    im = InstitutionalMemory()
    oid = im.store(KnowledgeObject(name="X"))
    entries = im.get_timeline()
    assert len(entries) >= 1
    obj_entries = im.get_timeline(oid)
    assert len(obj_entries) >= 1


def test_lineage():
    im = InstitutionalMemory()
    v1 = im.store(KnowledgeObject(name="V1"))
    v2 = im.store(KnowledgeObject(name="V2", derived_from=v1))
    v3 = im.store(KnowledgeObject(name="V3", derived_from=v2))
    lineage = im.get_lineage(v3)
    assert len(lineage) == 3


def test_supersede():
    im = InstitutionalMemory()
    oid1 = im.store(KnowledgeObject(name="Old"))
    oid2 = im.store(KnowledgeObject(name="New"))
    assert im.supersede(oid1, oid2)
    old = im.get(oid1)
    assert old.superseded_by == oid2


def test_summary():
    im = InstitutionalMemory()
    im.store(KnowledgeObject(name="A"))
    im.store(KnowledgeObject(name="B"))
    im.store(KnowledgeObject(name="C"))
    s = im.summary()
    assert s["total_objects"] == 3


def test_get_nonexistent():
    im = InstitutionalMemory()
    assert im.get("nonexistent") is None


def test_relate_nonexistent():
    im = InstitutionalMemory()
    rid = im.relate("no1", "no2")
    rels = im.get_relations("no1")
    assert len(rels) == 1


def test_empty_search():
    im = InstitutionalMemory()
    assert im.search("nothing") == []


def test_multiple_tags():
    im = InstitutionalMemory()
    im.store(KnowledgeObject(name="Multi", tags=["a", "b", "c"]))
    assert len(im.get_by_tag("a")) == 1
    assert len(im.get_by_tag("b")) == 1
    assert len(im.get_by_tag("c")) == 1
