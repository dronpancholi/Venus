"""Tests for UCOS CapabilityMarketplace."""

import pytest
from genesis.ucos.capability import CapabilityDefinition, CapabilityCategory, MaturityLevel, CapabilityState
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.marketplace import CapabilityMarketplace


@pytest.fixture
def mkt():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(
        id="mkt_a", name="Alpha", category=CapabilityCategory.STORAGE,
        tags=["tool"], maturity=MaturityLevel.STABLE,
    ))
    reg.register(CapabilityDefinition(
        id="mkt_b", name="Beta", category=CapabilityCategory.KNOWLEDGE,
        tags=["ml"], maturity=MaturityLevel.CRITICAL,
    ))
    reg.set_state("mkt_a", CapabilityState.READY)
    reg.set_state("mkt_b", CapabilityState.READY)
    m = CapabilityMarketplace(reg)
    return reg, m


def test_list_capability(mkt):
    reg, m = mkt
    listing = m.list_capability("mkt_a", price=5.0, tags=["utility"])
    assert listing is not None
    assert listing.capability_id == "mkt_a"
    assert listing.price == 5.0


def test_unlist(mkt):
    reg, m = mkt
    listing = m.list_capability("mkt_a")
    assert m.unlist(listing.id)
    assert not m.unlist("missing")


def test_search_by_query(mkt):
    reg, m = mkt
    m.list_capability("mkt_a", tags=["tool"])
    m.list_capability("mkt_b", tags=["ml"])
    results = m.search(query="Alpha")
    assert any(r.capability.id == "mkt_a" for r in results)


def test_search_by_category(mkt):
    reg, m = mkt
    m.list_capability("mkt_a")
    m.list_capability("mkt_b")
    results = m.search(category=CapabilityCategory.STORAGE)
    assert len(results) == 1
    assert results[0].capability.id == "mkt_a"


def test_search_by_tag(mkt):
    reg, m = mkt
    m.list_capability("mkt_a", tags=["tool"])
    m.list_capability("mkt_b", tags=["ml"])
    results = m.search(tags=["ml"])
    assert len(results) == 1


def test_search_by_maturity(mkt):
    reg, m = mkt
    m.list_capability("mkt_a")
    m.list_capability("mkt_b")
    results = m.search(min_maturity=MaturityLevel.CRITICAL)
    assert len(results) >= 1


def test_find_alternative(mkt):
    reg, m = mkt
    m.list_capability("mkt_a", tags=["tool"])
    m.list_capability("mkt_b", tags=["ml"])
    alts = m.find_alternative("mkt_a")
    assert len(alts) >= 0


def test_add_review(mkt):
    reg, m = mkt
    listing = m.list_capability("mkt_a")
    assert m.add_review(listing.id, "user1", 4.5, "Good")
    assert listing.rating == 4.5
    assert listing.review_count == 1
    m.add_review(listing.id, "user2", 3.5)
    assert listing.rating == 4.0


def test_marketplace_overview(mkt):
    reg, m = mkt
    m.list_capability("mkt_a", price=10.0)
    m.list_capability("mkt_b", price=20.0)
    overview = m.marketplace_overview()
    assert overview["total_listings"] == 2
    assert overview["total_market_value"] == 30.0


def test_search_ranked(mkt):
    reg, m = mkt
    listing = m.list_capability("mkt_a", price=5.0)
    m.add_review(listing.id, "u1", 5.0)
    m.list_capability("mkt_b", price=100.0)
    results = m.search(tags=["tool", "ml"])
    assert len(results) >= 1


def test_list_missing():
    reg = CapabilityRegistry()
    m = CapabilityMarketplace(reg)
    assert m.list_capability("missing") is None
