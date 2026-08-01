"""Tests for GENESIS Ω² — Civilization II: Temporal Model."""

from genesis.ontology import (
    UniversalEntity, TemporalEventType, TemporalEvent,
    EntitySnapshot, EntityBranch, Prediction,
)


class TestTemporalEventType:
    def test_all_types(self):
        types = [
            TemporalEventType.CREATED, TemporalEventType.MODIFIED,
            TemporalEventType.ACTIVATED, TemporalEventType.RETIRED,
            TemporalEventType.ARCHIVED, TemporalEventType.SUPERSEDED,
            TemporalEventType.REBORN, TemporalEventType.FORKED,
            TemporalEventType.MERGED, TemporalEventType.CAUSED,
            TemporalEventType.PREDICTED, TemporalEventType.EXPERIMENT,
        ]
        assert len(types) == 12
        for t in types:
            assert t.value


class TestTemporalEvent:
    def test_create_minimal(self):
        e = TemporalEvent(event_type=TemporalEventType.CREATED, entity_id="T:x")
        assert e.event_type == TemporalEventType.CREATED
        assert e.entity_id == "T:x"
        assert e.timestamp != ""

    def test_create_full(self):
        e = TemporalEvent(
            event_type=TemporalEventType.MODIFIED,
            entity_id="M:y",
            prior_fingerprint="abc",
            new_fingerprint="def",
            actor="planner",
            description="Updated attributes",
            causality=["decision:opt1"],
            attributes_changed=["maturity", "risk"],
            branch="experiment",
            confidence=0.9,
        )
        assert e.actor == "planner"
        assert len(e.causality) == 1
        assert len(e.attributes_changed) == 2


class TestEntitySnapshot:
    def test_create(self):
        s = EntitySnapshot(entity_id="T:x", fingerprint="fp123")
        assert s.entity_id == "T:x"
        assert s.fingerprint == "fp123"
        assert s.state == {}
        assert s.timestamp != ""

    def test_with_state(self):
        s = EntitySnapshot(entity_id="T:x", fingerprint="fp456", state={"maturity": 0.8})
        assert s.state["maturity"] == 0.8


class TestEntityBranch:
    def test_create(self):
        b = EntityBranch(name="experiment-1", description="Testing new approach")
        assert b.name == "experiment-1"
        assert b.parent_branch == "main"
        assert b.status == "active"

    def test_merged(self):
        b = EntityBranch(name="feature_x", parent_branch="develop",
                         merged_into="main", status="merged")
        assert b.merged_into == "main"
        assert b.status == "merged"


class TestPrediction:
    def test_create(self):
        p = Prediction(
            target_entity="Module:genesis.planner",
            metric="maturity",
            predicted_value=0.85,
            confidence=0.7,
            assumptions=["Continued test coverage growth"],
            evidence=["Test history shows 5% quarterly growth"],
            error_bounds=(0.75, 0.95),
        )
        assert p.target_entity == "Module:genesis.planner"
        assert p.metric == "maturity"
        assert p.confidence == 0.7
        assert len(p.assumptions) == 1
        assert p.created_at != ""

    def test_verify(self):
        p = Prediction(target_entity="T:x", metric="m", predicted_value=0.8)
        p.actual_value = 0.82
        p.accurate = abs(p.actual_value - p.predicted_value) / p.predicted_value < 0.1
        p.verified_at = "2025-01-01T00:00:00"
        assert p.accurate


class TestEntityTemporalMethods:
    def test_add_event(self):
        e = UniversalEntity(type_name="T", identity="temporal.test")
        e.add_event(TemporalEventType.CREATED, actor="system", description="Entity created")
        assert len(e.timeline) == 1
        assert e.timeline[0].event_type == TemporalEventType.CREATED
        assert e.timeline[0].actor == "system"

    def test_snapshot(self):
        e = UniversalEntity(type_name="T", identity="snap.test", attributes={"x": 1})
        e.snapshot()
        assert len(e.snapshots) == 1
        assert e.snapshots[0].entity_id == e.id
        assert e.snapshots[0].state["attributes"]["x"] == 1

    def test_multiple_snapshots(self):
        e = UniversalEntity(type_name="T", identity="multi.snap")
        e.attributes["version"] = 1
        e.snapshot("v1")
        e.attributes["version"] = 2
        e.snapshot("v2")
        assert len(e.snapshots) == 2
        assert e.snapshots[0].state["attributes"]["version"] == 1
        assert e.snapshots[1].state["attributes"]["version"] == 2

    def test_create_branch(self):
        e = UniversalEntity(type_name="T", identity="branch.test")
        b = e.create_branch("experiment", "Testing alternative approach")
        assert len(e.branches) == 1
        assert b.name == "experiment"
        assert b.parent_branch == "main"
        # Verify event was recorded
        assert len(e.timeline) >= 1
        assert e.timeline[-1].event_type == TemporalEventType.FORKED

    def test_add_prediction(self):
        e = UniversalEntity(type_name="T", identity="pred.test")
        p = e.add_prediction("maturity", 0.85, confidence=0.7,
                             assumptions=["Tests will grow"])
        assert len(e.predictions) == 1
        assert p.metric == "maturity"
        assert p.predicted_value == 0.85
        assert p.target_entity == e.id

    def test_timeline_ordered(self):
        e = UniversalEntity(type_name="T", identity="timeline.test")
        e.add_event(TemporalEventType.CREATED)
        e.add_event(TemporalEventType.MODIFIED)
        e.add_event(TemporalEventType.ACTIVATED)
        assert len(e.timeline) == 3
        assert e.timeline[0].event_type == TemporalEventType.CREATED
        assert e.timeline[1].event_type == TemporalEventType.MODIFIED
        assert e.timeline[2].event_type == TemporalEventType.ACTIVATED

    def test_to_dict_includes_temporal(self):
        e = UniversalEntity(type_name="T", identity="export.test")
        e.add_event(TemporalEventType.CREATED)
        e.snapshot()
        d = e.to_dict()
        assert "timeline" in d
        assert "snapshots" in d
        assert "branches" in d
        assert "predictions" in d
        assert len(d["timeline"]) == 1
        assert len(d["snapshots"]) == 1

    def test_backward_compat(self):
        """Existing code that creates UniversalEntity without temporal fields still works."""
        e = UniversalEntity(type_name="M", identity="old_style")
        assert e.type_name == "M"
        assert e.version == 1
        assert e.timeline == []
        assert e.snapshots == []
        assert e.branches == []
        assert e.predictions == []
        assert e.superseded_by == ""

    def test_historical_confidence(self):
        e = UniversalEntity(type_name="T", identity="confidence.test")
        e.historical_confidence = [0.5, 0.6, 0.7, 0.8]
        assert len(e.historical_confidence) == 4
        assert e.historical_confidence[-1] == 0.8

    def test_causality_in_events(self):
        e = UniversalEntity(type_name="T", identity="causality.test")
        e.add_event(TemporalEventType.MODIFIED, causality=["ADR-042", "PR #153"])
        assert len(e.timeline[0].causality) == 2
        assert "ADR-042" in e.timeline[0].causality

    def test_entity_superseded(self):
        old = UniversalEntity(type_name="T", identity="old_version")
        new = UniversalEntity(type_name="T", identity="new_version")
        old.superseded_by = new.id
        assert old.superseded_by == "T:new_version"
        old.add_event(TemporalEventType.SUPERSEDED, description=f"Superseded by {new.id}")
        assert old.timeline[0].event_type == TemporalEventType.SUPERSEDED
