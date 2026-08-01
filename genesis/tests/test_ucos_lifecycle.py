"""Tests for UCOS CapabilityLifecycleManager."""

import pytest
from genesis.ucos.capability import CapabilityDefinition, CapabilityState
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.lifecycle import CapabilityLifecycleManager


@pytest.fixture
def lifecycle():
    reg = CapabilityRegistry()
    lc = CapabilityLifecycleManager(reg)
    reg.register(CapabilityDefinition(id="lc_a", name="LifecycleCap"))
    return reg, lc


def test_initial_state(lifecycle):
    reg, lc = lifecycle
    assert reg.get("lc_a").state == CapabilityState.REGISTERED


def test_verify(lifecycle):
    reg, lc = lifecycle
    assert lc.verify("lc_a")
    assert reg.get("lc_a").state == CapabilityState.VERIFIED


def test_ready(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    assert lc.ready("lc_a")
    assert reg.get("lc_a").state == CapabilityState.READY


def test_start_and_stop(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    lc.ready("lc_a")
    assert lc.start("lc_a")
    assert reg.get("lc_a").state == CapabilityState.RUNNING
    assert lc.stop("lc_a")
    assert reg.get("lc_a").state == CapabilityState.STOPPED


def test_fail_and_recover(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    lc.ready("lc_a")
    lc.start("lc_a")
    assert reg.get("lc_a").state == CapabilityState.RUNNING
    assert lc.fail("lc_a")
    assert reg.get("lc_a").state == CapabilityState.FAILED
    assert lc.recover("lc_a")
    assert reg.get("lc_a").state == CapabilityState.READY


def test_degrade(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    lc.ready("lc_a")
    lc.start("lc_a")
    assert lc.degrade("lc_a")
    assert reg.get("lc_a").state == CapabilityState.DEGRADED


def test_invalid_transition(lifecycle):
    reg, lc = lifecycle
    assert not lc.start("lc_a")
    assert reg.get("lc_a").state == CapabilityState.REGISTERED


def test_cannot_transition_function(lifecycle):
    reg, lc = lifecycle
    assert not lc.can_transition("lc_a", CapabilityState.RUNNING)
    assert lc.can_transition("lc_a", CapabilityState.VERIFIED)


def test_transition_with_reason(lifecycle):
    reg, lc = lifecycle
    assert lc.transition("lc_a", CapabilityState.VERIFIED, reason="testing")
    assert reg.get("lc_a").state == CapabilityState.VERIFIED


def test_get_history(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    lc.ready("lc_a")
    history = lc.get_history("lc_a")
    assert len(history) >= 2
    assert history[0].from_state == "registered"
    assert history[0].to_state == "verified"


def test_recent_events(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    lc.ready("lc_a")
    events = lc.recent_events()
    assert len(events) >= 2


def test_on_transition_hook(lifecycle):
    reg, lc = lifecycle
    hook_called = []
    lc.on_transition("verified", lambda cap, evt: hook_called.append(cap.id))
    lc.verify("lc_a")
    assert "lc_a" in hook_called


def test_failed_capabilities(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    lc.ready("lc_a")
    lc.start("lc_a")
    lc.fail("lc_a")
    failed = lc.failed_capabilities()
    assert len(failed) == 1
    assert failed[0].id == "lc_a"


def test_running_capabilities(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    lc.ready("lc_a")
    lc.start("lc_a")
    running = lc.running_capabilities()
    assert len(running) == 1


def test_recover_from_degraded(lifecycle):
    reg, lc = lifecycle
    lc.verify("lc_a")
    lc.ready("lc_a")
    lc.start("lc_a")
    lc.degrade("lc_a")
    assert lc.recover("lc_a")
    assert reg.get("lc_a").state == CapabilityState.READY


def test_transition_missing_capability(lifecycle):
    reg, lc = lifecycle
    assert not lc.can_transition("missing", CapabilityState.READY)
    assert not lc.transition("missing", CapabilityState.READY)
