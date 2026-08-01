"""Tests for UCOS CapabilityNegotiator."""

import pytest
from genesis.ucos.capability import CapabilityDefinition, CapabilityState
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.negotiator import CapabilityNegotiator


@pytest.fixture
def neg():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="provider", name="Provider",
                                       execution_policy={"guarantees": {"uptime": "99.9%"}}))
    reg.register(CapabilityDefinition(id="consumer", name="Consumer"))
    n = CapabilityNegotiator(reg)
    reg.set_state("provider", CapabilityState.READY)
    return reg, n


def test_propose_agreement(neg):
    reg, n = neg
    agreement = n.propose("consumer", "provider")
    assert agreement is not None
    assert agreement.status == "proposed"
    assert agreement.consumer_id == "consumer"
    assert agreement.capability_id == "provider"


def test_accept_agreement(neg):
    reg, n = neg
    agreement = n.propose("consumer", "provider")
    assert n.accept(agreement.id)
    assert agreement.status == "accepted"
    assert agreement.accepted_at > 0


def test_reject_agreement(neg):
    reg, n = neg
    agreement = n.propose("consumer", "provider")
    assert n.reject(agreement.id, "Not needed")
    assert "Not needed" in agreement.status


def test_revoke_agreement(neg):
    reg, n = neg
    agreement = n.propose("consumer", "provider")
    n.accept(agreement.id)
    assert n.revoke(agreement.id)
    assert agreement.status == "revoked"


def test_find_providers(neg):
    reg, n = neg
    providers = n.find_providers("provider")
    assert len(providers) >= 1


def test_active_agreements(neg):
    reg, n = neg
    a1 = n.propose("consumer", "provider")
    a2 = n.propose("consumer", "provider")
    n.accept(a1.id)
    active = n.active_agreements()
    assert len(active) == 1
    assert active[0].id == a1.id


def test_agreements_for_consumer(neg):
    reg, n = neg
    a = n.propose("consumer", "provider")
    consumer_agreements = n.agreements_for_consumer("consumer")
    assert len(consumer_agreements) == 1


def test_propose_unregistered_consumer(neg):
    reg, n = neg
    assert n.propose("missing", "provider") is None


def test_propose_when_not_ready():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="p", name="Prov"))
    reg.register(CapabilityDefinition(id="c", name="Cons"))
    n = CapabilityNegotiator(reg)
    assert reg.get("p").state == CapabilityState.REGISTERED
    agreement = n.propose("c", "p")
    assert agreement is None
