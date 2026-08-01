"""
Tests for 5 capability stub implementations + MemoryEngine.
Verifies EventBus integration, MemoryStore persistence, and basic operations.
"""

import tempfile
from pathlib import Path

from genesis.certification.engine import CertificationEngine
from genesis.events.bus import EventBus
from genesis.memory.engine import MemoryEngine
from genesis.package.manager import PackageManager
from genesis.persistence import MemoryStore
from genesis.project.manager import ProjectManager
from genesis.security.validator import SecurityValidator


# ── Helpers ──────────────────────────────────────────────────────────

def _make_bus_and_store():
    bus = EventBus()
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    store = MemoryStore(db.name)
    return bus, store, db.name


def _cleanup(db_path):
    Path(db_path).unlink(missing_ok=True)


# ── MemoryEngine Tests ───────────────────────────────────────────────

def test_memory_engine_basic():
    bus = EventBus()
    me = MemoryEngine(event_bus=bus)
    me.store("k1", "v1")
    assert me.recall("k1") == "v1"


def test_memory_engine_namespace():
    me = MemoryEngine()
    me.store("k", "ns1_val", namespace="ns1")
    me.store("k", "ns2_val", namespace="ns2")
    assert me.recall("k", namespace="ns1") == "ns1_val"
    assert me.recall("k", namespace="ns2") == "ns2_val"


def test_memory_engine_recall_nonexistent():
    me = MemoryEngine()
    assert me.recall("no_such_key") is None


def test_memory_engine_forget():
    me = MemoryEngine()
    me.store("k", "v")
    assert me.forget("k") is True
    assert me.recall("k") is None


def test_memory_engine_forget_nonexistent():
    me = MemoryEngine()
    assert me.forget("k") is False


def test_memory_engine_persistence():
    bus, store, db_path = _make_bus_and_store()
    try:
        me = MemoryEngine(memory_store=store, event_bus=bus)
        me.store("persist_key", "persist_val", namespace="permanent")
        me2 = MemoryEngine(memory_store=MemoryStore(db_path))
        assert me2.recall("persist_key", namespace="permanent") == "persist_val"
    finally:
        _cleanup(db_path)


# ── PackageManager Tests ─────────────────────────────────────────────

def test_package_install():
    pm = PackageManager()
    with tempfile.TemporaryDirectory() as tmp:
        pkg_path = Path(tmp) / "test_pkg.venus"
        pkg_path.write_text("content")
        result = pm.install(pkg_path)
        assert result["name"] == "test_pkg"
        assert result["installed"] is True


def test_package_uninstall():
    pm = PackageManager()
    with tempfile.TemporaryDirectory() as tmp:
        pkg_path = Path(tmp) / "pkg.venus"
        pkg_path.write_text("content")
        pm.install(pkg_path)
        assert pm.uninstall("pkg") is True
        assert len(pm.list_packages()) == 0


def test_package_uninstall_nonexistent():
    pm = PackageManager()
    assert pm.uninstall("does_not_exist") is False


def test_package_list():
    pm = PackageManager()
    with tempfile.TemporaryDirectory() as tmp:
        for name in ["a", "b", "c"]:
            p = Path(tmp) / f"{name}.venus"
            p.write_text("")
            pm.install(p)
        pkgs = pm.list_packages()
        assert len(pkgs) == 3
        names = [p["name"] for p in pkgs]
        assert "a" in names
        assert "b" in names
        assert "c" in names


def test_package_event():
    received = []
    bus = EventBus()
    bus.subscribe("package.installed", lambda t, d: received.append(d))
    pm = PackageManager(event_bus=bus)
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "e.venus"
        p.write_text("")
        pm.install(p)
        assert len(received) == 1
        assert received[0]["name"] == "e"


# ── ProjectManager Tests ─────────────────────────────────────────────

def test_project_create():
    pm = ProjectManager()
    proj = pm.create_project("test_project")
    assert proj["name"] == "test_project"
    assert proj["status"] == "active"


def test_project_get():
    pm = ProjectManager()
    pm.create_project("p1")
    proj = pm.get_project("p1")
    assert proj is not None
    assert proj["name"] == "p1"


def test_project_get_nonexistent():
    pm = ProjectManager()
    assert pm.get_project("no_such") is None


def test_project_close():
    pm = ProjectManager()
    pm.create_project("p1")
    assert pm.close_project("p1") is True
    assert pm.get_project("p1")["status"] == "closed"


def test_project_close_nonexistent():
    pm = ProjectManager()
    assert pm.close_project("no_such") is False


def test_project_list():
    pm = ProjectManager()
    pm.create_project("a")
    pm.create_project("b")
    assert len(pm.list_projects()) == 2


# ── CertificationEngine Tests ────────────────────────────────────────

def test_certify():
    ce = CertificationEngine()
    result = ce.certify("art_1", "gold")
    assert result is not None
    assert result["level"] == "gold"
    assert result["artifact_id"] == "art_1"


def test_certify_invalid_level():
    ce = CertificationEngine()
    result = ce.certify("art_1", "invalid_level")
    assert result is None


def test_certify_default_level():
    ce = CertificationEngine()
    result = ce.certify("art_1")
    assert result["level"] == "bronze"


def test_get_certification():
    ce = CertificationEngine()
    ce.certify("art_1", "silver")
    cert = ce.get_certification("art_1")
    assert cert["level"] == "silver"


def test_get_certification_nonexistent():
    ce = CertificationEngine()
    assert ce.get_certification("no_such") is None


def test_revoke():
    ce = CertificationEngine()
    ce.certify("art_1")
    assert ce.revoke("art_1") is True
    assert ce.get_certification("art_1") is None


def test_revoke_nonexistent():
    ce = CertificationEngine()
    assert ce.revoke("no_such") is False


def test_list_by_level():
    ce = CertificationEngine()
    ce.certify("a", "gold")
    ce.certify("b", "gold")
    ce.certify("c", "silver")
    gold = ce.list_by_level("gold")
    assert len(gold) == 2
    silver = ce.list_by_level("silver")
    assert len(silver) == 1


# ── SecurityValidator Tests ──────────────────────────────────────────

def test_add_policy():
    sv = SecurityValidator()
    policy = sv.add_policy("p1", "rule1", "critical")
    assert policy["name"] == "p1"
    assert policy["severity"] == "critical"


def test_validate_no_policies():
    sv = SecurityValidator()
    results = sv.validate("target")
    assert results == []


def test_validate_with_policies():
    sv = SecurityValidator()
    sv.add_policy("check_a", "rule_a", "warning")
    sv.add_policy("check_b", "rule_b", "error")
    results = sv.validate("target")
    assert len(results) == 2
    assert all(r["passed"] for r in results)


def test_validate_filtered():
    sv = SecurityValidator()
    sv.add_policy("check_a", "rule_a")
    sv.add_policy("check_b", "rule_b")
    results = sv.validate("target", checks=["check_a"])
    assert len(results) == 1
    assert results[0]["policy"] == "check_a"


def test_audit_log():
    sv = SecurityValidator()
    sv.add_policy("p1", "r1")
    sv.validate("target")
    assert len(sv.audit_log()) == 1


# ── EventBus Integration Tests ────────────────────────────────────────

def test_all_services_emit_on_eventbus():
    """Verify all 5 capability stubs emit events when EventBus is wired."""
    received = []
    bus = EventBus()
    bus.subscribe("memory.stored", lambda t, d: received.append(("memory", d)))
    bus.subscribe("package.installed", lambda t, d: received.append(("package", d)))
    bus.subscribe("project.created", lambda t, d: received.append(("project", d)))
    bus.subscribe("artifact.certified", lambda t, d: received.append(("cert", d)))
    bus.subscribe("security.validation.completed", lambda t, d: received.append(("sec", d)))

    me = MemoryEngine(event_bus=bus)
    pg = PackageManager(event_bus=bus)
    pr = ProjectManager(event_bus=bus)
    ce = CertificationEngine(event_bus=bus)
    sv = SecurityValidator(event_bus=bus)

    me.store("k", "v")
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "p.venus"
        p.write_text("")
        pg.install(p)
    pr.create_project("test")
    ce.certify("a1")
    sv.add_policy("p", "r")
    sv.validate("t")

    # 5 events expected (some services may emit multiple)
    event_types = {e[0] for e in received}
    for expected in ("memory", "package", "project", "cert", "sec"):
        assert expected in event_types, f"Missing event: {expected}"
