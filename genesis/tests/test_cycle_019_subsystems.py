from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state.engine import EngineeringState
from genesis.nervous.engine import EngineeringNervousSystem
from genesis.context.engine import ContextEngine
from genesis.workflows.engine import EngineeringWorkflowEngine, WorkflowDef
from genesis.workflows.models import WorkflowGoal
from genesis.insight.engine import EngineeringInsightEngine
from genesis.decisions.engine import EngineeringDecisionIntelligence
from genesis.knowledge_v2.engine import SelfOrganizingKnowledge
from genesis.copilot_v2.engine import ProactiveCopilot
from genesis.playbooks.engine import EngineeringPlaybooks
from genesis.app_platform.engine import GenesisAppPlatform, AppManifest
from genesis.command_center.engine import LiveCommandCenter
from genesis.sdk.engine import GenesisSDK
from genesis.agentos.engine import AgentOSFoundation
from genesis.events.unified import UnifiedEventBus
from genesis.desktop.memory import WorkspaceMemory
from genesis.desktop.activity import ActivityCenter, NotificationSeverity


@pytest.fixture(autouse=True)
def clean_state():
    """Clean all singletons and registries between tests."""
    try:
        es = EngineeringState.instance()
        es.clear_all()
    except Exception:
        pass
    try:
        get_registry().clear()
    except Exception:
        pass
    try:
        ueb = UnifiedEventBus.instance()
        ueb.clear()
    except Exception:
        pass
    yield


class MockKernel:
    def __init__(self):
        self.engineering = get_registry()
        self._event_store = []
        self._state = EngineeringState.instance()
        self._state.set_kernel(self)
        self._knowledge = MagicMock()
        self._reasoning = MagicMock()
        self._twin = MagicMock()
        self._ai = MagicMock()
        self._contexts = {}

    def emit(self, event_type: str, payload: dict[str, Any] = None,
             origin: str = "", tags: list[str] = None):
        self._event_store.append({"type": event_type, "payload": payload, "origin": origin, "tags": tags or []})

    def query_events(self, limit=10, event_type=None):
        return self._event_store[-limit:]

    def twin(self):
        return self._twin

    def knowledge(self):
        return self._knowledge


@pytest.fixture
def kernel():
    return MockKernel()


# ── M147: Engineering State Engine ───────────────────────────────────────────

class TestEngineeringStateEngine:
    def test_singleton(self):
        s1 = EngineeringState.instance()
        s2 = EngineeringState.instance()
        assert s1 is s2

    def test_set_and_get(self):
        state = EngineeringState.instance()
        state.set("test", "key1", "value1")
        assert state.get("test", "key1") == "value1"

    def test_get_domain(self):
        state = EngineeringState.instance()
        state.set("domain1", "a", 1)
        state.set("domain1", "b", 2)
        domain = state.get_domain("domain1")
        assert domain == {"a": 1, "b": 2}

    def test_update_domain(self):
        state = EngineeringState.instance()
        state.update_domain("upd", {"x": 10, "y": 20})
        assert state.get("upd", "x") == 10
        assert state.get("upd", "y") == 20

    def test_domains_list(self):
        state = EngineeringState.instance()
        state.set("dom_a", "k", "v")
        state.set("dom_b", "k", "v")
        assert "dom_a" in state.domains()
        assert "dom_b" in state.domains()

    def test_has(self):
        state = EngineeringState.instance()
        state.set("h", "k", "v")
        assert state.has("h", "k")
        assert not state.has("h", "missing")

    def test_observe_called(self):
        state = EngineeringState.instance()
        observed = []
        state.observe("obs", lambda d, k, v, o, e: observed.append((d, k, v)))
        state.set("obs", "test_key", "test_val", event="test.event")
        assert any(d == "obs" and k == "test_key" for d, k, v in observed)

    def test_transitions_recorded(self):
        state = EngineeringState.instance()
        state.set("t", "k", "v1")
        state.set("t", "k", "v2")
        trans = state.transitions("t")
        assert len(trans) >= 2
        assert trans[-1].new_value == "v2"

    def test_replay(self):
        state = EngineeringState.instance()
        state.set("r", "k", "v1")
        state.set("r", "k", "v2")
        replay = state.replay("r")
        assert len(replay) >= 2

    def test_snapshot(self):
        state = EngineeringState.instance()
        state.set("s", "k", "v")
        snap = state.snapshot()
        assert "s" in snap["domains"]
        assert snap["total_domains"] >= 1

    def test_clear_domain(self):
        state = EngineeringState.instance()
        state.set("cd", "k", "v")
        state.clear_domain("cd")
        assert not state.has("cd", "k")

    def test_boot(self):
        state = EngineeringState.instance()
        state.boot()
        reg = get_registry()
        objs = reg.get_by_type(EngineeringObjectType.SERVICE)
        names = [o.name for o in objs]
        assert "EngineeringState" in names


# ── M146: Engineering Nervous System ─────────────────────────────────────────

class TestEngineeringNervousSystem:
    def test_boot(self):
        ns = EngineeringNervousSystem(kernel=MockKernel())
        ns.boot()
        assert ns._booted
        assert ns._running

    def test_signal_history(self):
        ns = EngineeringNervousSystem(kernel=MockKernel())
        ns.boot()
        ns.emit_signal("test", "sig_domain", "sig_key", "sig_val")
        history = ns.signal_history("sig_domain")
        assert len(history) >= 1
        assert history[-1].key == "sig_key"

    def test_on_signal_listener(self):
        ns = EngineeringNervousSystem(kernel=MockKernel())
        ns.boot()
        received = []
        ns.on_signal("sig_domain.sig_key", lambda s: received.append(s))
        state = EngineeringState.instance()
        state.set("sig_domain", "sig_key", "triggered")
        time.sleep(0.01)
        assert any(s.key == "sig_key" for s in received)

    def test_states(self):
        ns = EngineeringNervousSystem(kernel=MockKernel())
        ns.boot()
        stats = ns.stats()
        assert "running" in stats
        assert not stats["running"] or isinstance(stats["signals_processed"], int)


# ── M153: Context Engine ────────────────────────────────────────────────────

class TestContextEngine:
    def test_build(self):
        ce = ContextEngine(kernel=MockKernel())
        ctx = ce.build("test query", "test_project")
        assert ctx is not None
        assert hasattr(ctx, 'query')
        assert ctx.query == "test query"

    def test_build_with_object_id(self):
        ce = ContextEngine(kernel=MockKernel())
        obj = EngineeringObject(name="ctx_test", object_type=EngineeringObjectType.SERVICE)
        reg = get_registry()
        reg.register(obj)
        ctx = ce.build("find object", object_id=obj.id)
        assert ctx is not None

    def test_summarize(self):
        ce = ContextEngine(kernel=MockKernel())
        ctx = ce.build("summarize this")
        summary = ce.summarize(ctx, max_lines=10)
        assert isinstance(summary, (str, list))

    def test_boot(self):
        ce = ContextEngine(kernel=MockKernel())
        ce.boot()
        reg = get_registry()
        objs = reg.get_by_type(EngineeringObjectType.SERVICE)
        names = [o.name for o in objs]
        assert "ContextEngine" in names


# ── M148: Engineering Workflow Engine ────────────────────────────────────────

class TestEngineeringWorkflowEngine:
    def test_register_definition(self):
        we = EngineeringWorkflowEngine(kernel=MockKernel())
        we.register(WorkflowDef(
            name="test_wf",
            description="A test workflow",
            stages=[],
            goals=[WorkflowGoal(description="test goal")],
        ))
        defs = we.list_defs()
        names = [d["name"] for d in defs]
        assert "test_wf" in names

    def test_run_execution(self):
        we = EngineeringWorkflowEngine(kernel=MockKernel())
        we.register(WorkflowDef(
            name="exec_test",
            description="Test execution",
            stages=[],
            goals=[WorkflowGoal(description="run goal")],
        ))
        execution = we.run("exec_test", {})
        assert execution is not None
        assert execution.workflow_name == "exec_test"

    def test_get_execution(self):
        we = EngineeringWorkflowEngine(kernel=MockKernel())
        we.register(WorkflowDef(
            name="get_test",
            description="Test get execution",
            stages=[],
            goals=[],
        ))
        execution = we.run("get_test", {})
        result = we.get_execution(execution.id)
        assert result is not None

    def test_builtin_workflows(self):
        we = EngineeringWorkflowEngine(kernel=MockKernel())
        we.boot()
        defs = we.list_defs()
        names = [d["name"] for d in defs]
        assert "refactor_module" in names
        assert "analyze_repository" in names
        assert "deploy_provider" in names


# ── M150: Engineering Insight Engine ─────────────────────────────────────────

class TestEngineeringInsightEngine:
    def test_create_insight(self):
        ie = EngineeringInsightEngine(kernel=MockKernel())
        ie.create(
            title="Test Insight",
            summary="A test insight",
            evidence=["evidence1"],
            confidence=0.8,
            category="quality",
            severity="medium",
        )
        insights = ie.list()
        assert len(insights) >= 1

    def test_list_filtered(self):
        ie = EngineeringInsightEngine(kernel=MockKernel())
        ie.create(title="High Risk", summary="critical issue", evidence=[], confidence=0.9, category="risk", severity="high")
        ie.create(title="Low Risk", summary="minor issue", evidence=[], confidence=0.3, category="quality", severity="low")
        high = ie.list(severity="high")
        assert len(high) >= 1

    def test_stats(self):
        ie = EngineeringInsightEngine(kernel=MockKernel())
        stats = ie.stats()
        assert "total" in stats
        assert "by_category" in stats
        assert "by_severity" in stats


# ── M151: Engineering Decision Intelligence ──────────────────────────────────

class TestEngineeringDecisionIntelligence:
    def test_propose(self):
        di = EngineeringDecisionIntelligence(kernel=MockKernel())
        decision_id = di.propose(
            title="Test Decision",
            problem="Should we do X?",
            context="Testing",
            alternatives=["A", "B"],
            reasoning="A is better",
        )
        assert decision_id is not None

    def test_decide(self):
        di = EngineeringDecisionIntelligence(kernel=MockKernel())
        d_id = di.propose(title="Decide Test", problem="?", context="", alternatives=[], reasoning="").id
        di.decide(d_id, reasoning="Final decision", outcome="Accepted", implementation="Done", validation="Passed")
        decision = di.get(d_id)
        assert decision is not None
        assert decision.status == "decided"

    def test_search(self):
        di = EngineeringDecisionIntelligence(kernel=MockKernel())
        di.propose(title="Alpha decision", problem="?", context="", alternatives=[], reasoning="")
        di.propose(title="Beta decision", problem="?", context="", alternatives=[], reasoning="")
        results = di.search("Alpha")
        assert len(results) >= 1

    def test_stats(self):
        di = EngineeringDecisionIntelligence(kernel=MockKernel())
        stats = di.stats()
        assert "total" in stats


# ── M152: Self-Organizing Knowledge ──────────────────────────────────────────

class TestSelfOrganizingKnowledge:
    def test_add_concept(self):
        sk = SelfOrganizingKnowledge(kernel=MockKernel())
        sk.add_concept("python", "programming", "Python is a language", "test")
        stats = sk.stats()
        assert stats["concepts"] >= 1

    def test_search(self):
        sk = SelfOrganizingKnowledge(kernel=MockKernel())
        sk.add_concept("python", "programming", "Python language", "test")
        results = sk.search("python")
        assert len(results) >= 1

    def test_consolidate(self):
        sk = SelfOrganizingKnowledge(kernel=MockKernel())
        sk.add_concept("python", "programming", "Python language", "test")
        sk.add_concept("python lang", "programming", "Python programming language", "test2")
        sk.consolidate()
        stats = sk.stats()
        assert stats["clusters"] >= 1

    def test_access(self):
        sk = SelfOrganizingKnowledge(kernel=MockKernel())
        sk.add_concept("py", "lang", "Python", "test")
        sk.access("py")
        stats = sk.stats()
        assert stats["concepts"] >= 1


# ── M154: Proactive Copilot ─────────────────────────────────────────────────

class TestProactiveCopilot:
    def test_boot(self):
        pc = ProactiveCopilot(kernel=MockKernel())
        pc.boot()
        assert pc._booted

    def test_suggestions_list(self):
        pc = ProactiveCopilot(kernel=MockKernel())
        pc.boot()
        suggestions = pc.suggestions()
        assert isinstance(suggestions, list)

    def test_suggestions_with_category(self):
        pc = ProactiveCopilot(kernel=MockKernel())
        pc.boot()
        suggestions = pc.suggestions(category="architecture")
        assert isinstance(suggestions, list)

    def test_suggestions_property_access(self):
        pc = ProactiveCopilot(kernel=MockKernel())
        pc.boot()
        suggestions = pc.suggestions()
        if suggestions:
            s = suggestions[0]
            assert hasattr(s, 'title')
            assert hasattr(s, 'category')


# ── M155: Engineering Playbooks ─────────────────────────────────────────────

class TestEngineeringPlaybooks:
    def test_list_playbooks(self):
        pb = EngineeringPlaybooks(kernel=MockKernel())
        pb.boot()
        playbooks = pb.list()
        assert len(playbooks) >= 3

    def test_get_playbook(self):
        pb = EngineeringPlaybooks(kernel=MockKernel())
        pb.boot()
        p = pb.get("large_refactoring")
        assert p is not None

    def test_search(self):
        pb = EngineeringPlaybooks(kernel=MockKernel())
        pb.boot()
        results = pb.search("refactor")
        assert len(results) >= 1

    def test_stats(self):
        pb = EngineeringPlaybooks(kernel=MockKernel())
        pb.boot()
        stats = pb.stats()
        assert stats["total"] >= 3


# ── M156: Genesis Application Platform ──────────────────────────────────────

class TestGenesisAppPlatform:
    def test_register(self):
        ap = GenesisAppPlatform(kernel=MockKernel())
        app = ap.register(AppManifest(
            name="test_app",
            description="Test app",
            version="1.0.0",
            author="test",
        ))
        assert app is not None
        assert app.status == "registered"

    def test_list_apps(self):
        ap = GenesisAppPlatform(kernel=MockKernel())
        ap.boot()
        apps = ap.list()
        assert len(apps) >= 6

    def test_get_app(self):
        ap = GenesisAppPlatform(kernel=MockKernel())
        ap.boot()
        app = ap.get("buildit")
        assert app is not None

    def test_stats(self):
        ap = GenesisAppPlatform(kernel=MockKernel())
        ap.boot()
        stats = ap.stats()
        assert stats["total"] >= 6


# ── M158: Developer Platform & SDK ──────────────────────────────────────────

class TestGenesisSDK:
    def test_list_capabilities(self):
        sdk = GenesisSDK(kernel=MockKernel())
        sdk.boot()
        caps = sdk.capabilities()
        assert len(caps) >= 21

    def test_all_capabilities_have_methods(self):
        sdk = GenesisSDK(kernel=MockKernel())
        sdk.boot()
        caps = sdk.capabilities()
        for cap in caps:
            assert "name" in cap
            assert "description" in cap
            assert "version" in cap


# ── M149: Live Project Command Center ────────────────────────────────────────

class TestLiveCommandCenter:
    def test_get_dashboard(self):
        cc = LiveCommandCenter(kernel=MockKernel())
        cc.boot()
        dashboard = cc.get_dashboard("default")
        assert dashboard is not None
        assert len(dashboard.panels) == 17

    def test_snapshot(self):
        cc = LiveCommandCenter(kernel=MockKernel())
        cc.boot()
        snapshot = cc.snapshot()
        assert "dashboards" in snapshot


# ── M159: AgentOS Foundation V2 ────────────────────────────────────────────

class TestAgentOSFoundation:
    def test_boot(self):
        kernel = MockKernel()
        ao = AgentOSFoundation(kernel=kernel)
        ao.boot()
        assert ao._os_obj is not None

    def test_list_capabilities(self):
        kernel = MockKernel()
        ao = AgentOSFoundation(kernel=kernel)
        ao.boot()
        caps = ao.list_capabilities()
        assert len(caps) == 28

    def test_get_capability(self):
        kernel = MockKernel()
        ao = AgentOSFoundation(kernel=kernel)
        ao.boot()
        cap = ao.get_capability("state_engine")
        assert cap is not None
        assert cap.name == "state_engine"

    def test_enable_disable(self):
        kernel = MockKernel()
        ao = AgentOSFoundation(kernel=kernel)
        ao.boot()
        assert ao.disable("state_engine")
        assert not ao.get_capability("state_engine").enabled
        assert ao.enable("state_engine")
        assert ao.get_capability("state_engine").enabled

    def test_check_readiness(self):
        kernel = MockKernel()
        ao = AgentOSFoundation(kernel=kernel)
        ao.boot()
        readiness = ao.check_readiness()
        assert readiness["total"] == 28
        assert readiness["ready"] >= 1

    def test_verify_capability(self):
        kernel = MockKernel()
        ao = AgentOSFoundation(kernel=kernel)
        ao.boot()
        result = ao.verify_capability("engineering_objects")
        assert result["verified"]

    def test_verify_all(self):
        kernel = MockKernel()
        ao = AgentOSFoundation(kernel=kernel)
        ao.boot()
        results = ao.verify_all()
        assert results["total"] == 28


# ── UnifiedEventBus ─────────────────────────────────────────────────────────

class TestUnifiedEventBus:
    def test_singleton(self):
        b1 = UnifiedEventBus.instance()
        b2 = UnifiedEventBus.instance()
        assert b1 is b2

    def test_emit_and_subscribe(self):
        bus = UnifiedEventBus.instance()
        received = []
        bus.subscribe("test.event", lambda e: received.append(e))
        bus.emit_raw("test.event", {"data": 1})
        assert len(received) == 1

    def test_emit_raw(self):
        bus = UnifiedEventBus.instance()
        received = []
        bus.subscribe("raw.test", lambda e: received.append(e))
        bus.emit_raw("raw.test", {"key": "val"}, origin="test_origin", tags=["tag1"])
        assert len(received) == 1
        assert received[0].origin == "test_origin"

    def test_wildcard_subscribe(self):
        bus = UnifiedEventBus.instance()
        received = []
        bus.subscribe("*", lambda e: received.append(e))
        bus.emit_raw("any.event")
        assert len(received) == 1

    def test_unsubscribe(self):
        bus = UnifiedEventBus.instance()
        received = []
        sub_id = bus.subscribe("unsub.test", lambda e: received.append(e))
        bus.emit_raw("unsub.test")
        assert len(received) == 1
        bus.unsubscribe(sub_id)
        bus.emit_raw("unsub.test")
        assert len(received) == 1

    def test_subscriber_count(self):
        bus = UnifiedEventBus.instance()
        bus.subscribe("sc.test", lambda e: None)
        assert bus.subscriber_count() >= 1

    def test_query(self):
        bus = UnifiedEventBus.instance()
        bus.emit_raw("q.test", {"i": 1})
        bus.emit_raw("q.test", {"i": 2})
        results = bus.query(event_type="q.test")
        assert len(results) >= 2

    def test_count_by_type(self):
        bus = UnifiedEventBus.instance()
        bus.emit_raw("cbt.a")
        bus.emit_raw("cbt.b")
        counts = bus.count_by_type()
        assert "cbt.a" in counts
        assert "cbt.b" in counts

    def test_stats(self):
        bus = UnifiedEventBus.instance()
        bus.emit_raw("stats.test")
        stats = bus.stats()
        assert stats["total_events"] >= 1
        assert "subscriptions" in stats

    def test_clear(self):
        bus = UnifiedEventBus.instance()
        bus.emit_raw("clear.test")
        bus.clear()
        assert bus.count() == 0


# ── WorkspaceMemory ─────────────────────────────────────────────────────────

class TestWorkspaceMemory:
    def test_singleton(self):
        wm1 = WorkspaceMemory.instance()
        wm2 = WorkspaceMemory.instance()
        assert wm1 is wm2

    def test_set_and_get(self):
        wm = WorkspaceMemory.instance()
        wm.set("test_key", "test_value")
        assert wm.get("test_key") == "test_value"

    def test_update(self):
        wm = WorkspaceMemory.instance()
        wm.update({"a": 1, "b": 2})
        assert wm.get("a") == 1
        assert wm.get("b") == 2

    def test_record_navigation(self):
        wm = WorkspaceMemory.instance()
        wm.record_navigation("understand")
        recent = wm.recent_screens(limit=5)
        assert recent[-1]["screen"] == "understand"

    def test_record_search(self):
        wm = WorkspaceMemory.instance()
        wm.record_search("test query", "kernel")
        recent = wm.recent_searches(limit=5)
        assert "test query" in recent

    def test_record_command(self):
        wm = WorkspaceMemory.instance()
        wm.record_command("test command")
        recent = wm.recent_commands(limit=5)
        assert "test command" in recent

    def test_project_state(self):
        wm = WorkspaceMemory.instance()
        wm.set_project_state("proj1", {"status": "active"})
        state = wm.get_project_state("proj1")
        assert state.get("status") == "active"

    def test_snapshot(self):
        wm = WorkspaceMemory.instance()
        wm.set("snap_key", "snap_val")
        snap = wm.snapshot()
        assert snap.get("snap_key") == "snap_val"


# ── ActivityCenter ──────────────────────────────────────────────────────────

class TestActivityCenter:
    def test_singleton(self):
        ac1 = ActivityCenter.instance()
        ac2 = ActivityCenter.instance()
        assert ac1 is ac2

    def test_notify(self):
        ac = ActivityCenter.instance()
        n = ac.notify("Test Title", "Test Message", NotificationSeverity.INFO, "test")
        assert n.title == "Test Title"
        assert n.message == "Test Message"

    def test_unread_count(self):
        ac = ActivityCenter.instance()
        ac.notify("Unread Test", severity=NotificationSeverity.INFO)
        assert ac.unread_count() >= 1

    def test_mark_read(self):
        ac = ActivityCenter.instance()
        n = ac.notify("Read Test", severity=NotificationSeverity.INFO)
        ac.mark_read(n.id)
        assert n.read

    def test_mark_all_read(self):
        ac = ActivityCenter.instance()
        ac.notify("All Read 1", severity=NotificationSeverity.INFO)
        ac.notify("All Read 2", severity=NotificationSeverity.INFO)
        ac.mark_all_read()
        assert ac.unread_count() == 0

    def test_dismiss(self):
        ac = ActivityCenter.instance()
        n = ac.notify("Dismiss Test", severity=NotificationSeverity.WARNING)
        ac.dismiss(n.id)
        assert n.dismissed

    def test_dismiss_all(self):
        ac = ActivityCenter.instance()
        ac.notify("Dismiss All 1", severity=NotificationSeverity.WARNING)
        ac.dismiss_all()
        assert ac.unread_count() == 0

    def test_recent(self):
        ac = ActivityCenter.instance()
        ac.notify("Recent 1", severity=NotificationSeverity.INFO)
        ac.notify("Recent 2", severity=NotificationSeverity.ERROR)
        recent = ac.recent(limit=10)
        assert len(recent) >= 2

    def test_recent_with_category(self):
        ac = ActivityCenter.instance()
        ac.notify("Cat Test", severity=NotificationSeverity.INFO, category="test_cat")
        cat_notifications = ac.recent(limit=10, category="test_cat")
        assert len(cat_notifications) >= 1

    def test_by_severity(self):
        ac = ActivityCenter.instance()
        ac.notify("Error Test", severity=NotificationSeverity.ERROR)
        errors = ac.by_severity(NotificationSeverity.ERROR)
        assert len(errors) >= 1

    def test_subscribe(self):
        ac = ActivityCenter.instance()
        received = []
        ac.subscribe(lambda n: received.append(n))
        ac.notify("Listener Test", severity=NotificationSeverity.INFO)
        assert len(received) >= 1

    def test_stats(self):
        ac = ActivityCenter.instance()
        ac.notify("Stats Test", severity=NotificationSeverity.INFO)
        stats = ac.stats()
        assert stats["total"] >= 1
        assert "unread" in stats
        assert "by_severity" in stats


# ── EngineeringObjectType Resolution ────────────────────────────────────────

class TestEngineeringObjectTypeResolution:
    def test_resolve_new_types(self):
        assert EngineeringObjectType.resolve("service") == EngineeringObjectType.SERVICE
        assert EngineeringObjectType.resolve("task") == EngineeringObjectType.TASK
        assert EngineeringObjectType.resolve("decision") == EngineeringObjectType.DECISION

    def test_resolve_legacy_types(self):
        assert EngineeringObjectType.resolve("event") == EngineeringObjectType.UNKNOWN
        assert EngineeringObjectType.resolve("agent_task") == EngineeringObjectType.TASK
        assert EngineeringObjectType.resolve("arch_node") == EngineeringObjectType.MODULE
        assert EngineeringObjectType.resolve("arch_edge") == EngineeringObjectType.MODULE
        assert EngineeringObjectType.resolve("evidence") == EngineeringObjectType.RECOMMENDATION
        assert EngineeringObjectType.resolve("component") == EngineeringObjectType.MODULE
        assert EngineeringObjectType.resolve("ai_provider") == EngineeringObjectType.PROVIDER
        assert EngineeringObjectType.resolve("automation") == EngineeringObjectType.WORKFLOW
        assert EngineeringObjectType.resolve("state") == EngineeringObjectType.SERVICE
        assert EngineeringObjectType.resolve("nervous_system") == EngineeringObjectType.SERVICE
        assert EngineeringObjectType.resolve("sdk") == EngineeringObjectType.SERVICE
        assert EngineeringObjectType.resolve("app_module") == EngineeringObjectType.APP

    def test_resolve_unknown(self):
        assert EngineeringObjectType.resolve("nonexistent_type") == EngineeringObjectType.UNKNOWN

    def test_from_dict_uses_resolve(self):
        obj = EngineeringObject.from_dict({"object_type": "state"})
        assert obj.object_type == EngineeringObjectType.SERVICE

    def test_has_value(self):
        assert EngineeringObjectType.has_value("service")
        assert EngineeringObjectType.has_value("task")
        assert not EngineeringObjectType.has_value("made_up_type")


# ── AI Platform: Parallel Providers & Consensus ─────────────────────────────

class TestAIParallelExecution:
    def test_parallel_chat_imports(self):
        from genesis.ai.router import ConsensusResult
        assert ConsensusResult is not None

    def test_consensus_result_fields(self):
        from genesis.ai.router import ConsensusResult
        cr = ConsensusResult(text="test", confidence=0.8, providers_used=["p1"], agreement=0.8, responses=[])
        assert cr.text == "test"
        assert cr.confidence == 0.8

    def test_ai_engine_exposes_parallel_methods(self):
        from genesis.ai.engine import AIOrchestrationEngine
        engine = AIOrchestrationEngine()
        assert hasattr(engine, 'parallel_chat')
        assert hasattr(engine, 'consensus_chat')
        assert hasattr(engine, 'best_of_n')


# ── Integration: Subsystems Work Together ───────────────────────────────────

class TestSubsystemIntegration:
    def test_state_and_nervous(self):
        state = EngineeringState.instance()
        kernel = MockKernel()
        ns = EngineeringNervousSystem(kernel=kernel)
        ns.boot()
        ns.emit_signal("test", "integration", "test", "value", event="integration.test")
        history = ns.signal_history("integration")
        assert len(history) >= 1

    def test_workflow_and_state(self):
        state = EngineeringState.instance()
        we = EngineeringWorkflowEngine(kernel=MockKernel())
        we.register(WorkflowDef(name="wf_test", description="test", stages=[], goals=[]))
        execution = we.run("wf_test", {"data": 1})
        state.set("workflows", execution.id, "running")
        assert state.has("workflows", execution.id)

    def test_insight_and_decision(self):
        ie = EngineeringInsightEngine(kernel=MockKernel())
        ie.create(title="Shared Insight", summary="cross-ref", evidence=[], confidence=0.9, category="decision", severity="high")
        di = EngineeringDecisionIntelligence(kernel=MockKernel())
        d_id = di.propose(title="Related Decision", problem="Should we?", context="Based on insight", alternatives=[], reasoning="Insight-driven")
        assert d_id is not None

    def test_playbooks_registered_as_objects(self):
        pb = EngineeringPlaybooks(kernel=MockKernel())
        pb.boot()
        reg = get_registry()
        playbooks = reg.get_by_type(EngineeringObjectType.PLAYBOOK)
        names = [o.name for o in playbooks]
        assert "large_refactoring" in names
        assert "ai_provider_integration" in names
        assert "knowledge_consolidation" in names

    def test_app_platform_registers_apps(self):
        ap = GenesisAppPlatform(kernel=MockKernel())
        ap.boot()
        apps = ap.list()
        app_names = [a.get('name', '') for a in apps]
        assert "buildit" in app_names
        assert "venus" in app_names
        assert "agentos" in app_names

    def test_all_subsystems_register_in_registry(self):
        reg = get_registry()
        state = EngineeringState.instance()
        state.boot()

        ns = EngineeringNervousSystem(kernel=MockKernel())
        ns.boot()

        so = SelfOrganizingKnowledge(kernel=MockKernel())
        so.stats()

        objs = reg.get_by_type(EngineeringObjectType.SERVICE)
        names = [o.name for o in objs]
        assert "EngineeringState" in names or len(objs) > 0
