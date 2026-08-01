"""Ω³ Phase 10: Digital Civilization tests."""

from genesis.ontology import URelType, RelationshipEngine
from genesis.digital_civilization import (
    DigitalCivilization, Institute, InstituteType, InstituteStatus,
    Contract, ReputationEvent, build_default_civilization,
)


class TestInstitute:
    def test_defaults(self):
        inst = Institute(name="Test Institute")
        assert inst.type == InstituteType.UNIVERSITY
        assert inst.status == InstituteStatus.PROPOSED
        assert inst.reputation == 0.5
        assert inst.id != ""

    def test_add_member(self):
        inst = Institute(name="Test", id="test:id")
        inst.add_member("member:1")
        assert "member:1" in inst.members
        assert len(inst.members) == 1

    def test_add_member_dedup(self):
        inst = Institute(name="Test", id="test:id")
        inst.add_member("m:1")
        inst.add_member("m:1")
        assert len(inst.members) == 1

    def test_add_capability(self):
        inst = Institute(name="Test", id="test:id")
        inst.add_capability("architecture_review")
        assert "architecture_review" in inst.capabilities

    def test_institute_types(self):
        assert InstituteType.UNIVERSITY.value == "university"
        assert InstituteType.LABORATORY.value == "laboratory"
        assert InstituteType.COMPANY.value == "company"
        assert InstituteType.STANDARDS_BODY.value == "standards_body"
        assert InstituteType.MARKET.value == "market"
        assert InstituteType.FOUNDATION.value == "foundation"


class TestContract:
    def test_defaults(self):
        c = Contract(name="Test", producer="p:id", consumer="c:id")
        assert c.id != ""
        assert c.status == "active"

    def test_value(self):
        c = Contract(name="Test", producer="p", consumer="c", value=100.0)
        assert c.value == 100.0


class TestReputationEvent:
    def test_defaults(self):
        e = ReputationEvent(institute_id="inst:id", delta=0.1, reason="good work")
        assert e.delta == 0.1
        assert e.timestamp > 0


class TestDigitalCivilization:
    def test_empty(self):
        civ = DigitalCivilization()
        assert civ.summary()["total_institutes"] == 0

    def test_charter_institute(self):
        civ = DigitalCivilization()
        inst = civ.charter_institute("Test Lab", InstituteType.LABORATORY,
                                     mission="Research", capabilities=["exp"])
        assert inst.status == InstituteStatus.CHARTERED
        assert inst.mission == "Research"
        assert len(civ.all_institutes()) == 1

    def test_charter_with_members(self):
        civ = DigitalCivilization()
        inst = civ.charter_institute("Team", InstituteType.COMPANY,
                                     members=["member:1", "member:2"])
        assert len(inst.members) == 2

    def test_activate_institute(self):
        civ = DigitalCivilization()
        inst = civ.charter_institute("Lab", InstituteType.LABORATORY)
        result = civ.activate_institute(inst.id)
        assert result is not None
        assert result.status == InstituteStatus.ACTIVE

    def test_activate_nonexistent(self):
        civ = DigitalCivilization()
        result = civ.activate_institute("nonexistent")
        assert result is None

    def test_get_institute(self):
        civ = DigitalCivilization()
        inst = civ.charter_institute("Test", InstituteType.UNIVERSITY)
        assert civ.get_institute(inst.id) is inst
        assert civ.get_institute("nonexistent") is None

    def test_find_by_name(self):
        civ = DigitalCivilization()
        civ.charter_institute("Alpha Lab", InstituteType.LABORATORY)
        civ.charter_institute("Beta Lab", InstituteType.LABORATORY)
        results = civ.find_institute(name="Alpha")
        assert len(results) == 1

    def test_find_by_type(self):
        civ = DigitalCivilization()
        civ.charter_institute("U1", InstituteType.UNIVERSITY)
        civ.charter_institute("L1", InstituteType.LABORATORY)
        results = civ.find_institute(inst_type=InstituteType.UNIVERSITY)
        assert len(results) == 1

    def test_find_by_name_and_type(self):
        civ = DigitalCivilization()
        civ.charter_institute("Research U", InstituteType.UNIVERSITY)
        results = civ.find_institute(name="Research", inst_type=InstituteType.UNIVERSITY)
        assert len(results) == 1

    def test_create_contract(self):
        civ = DigitalCivilization()
        p = civ.charter_institute("Producer", InstituteType.COMPANY)
        c = civ.charter_institute("Consumer", InstituteType.COMPANY)
        contract = civ.create_contract("Service Agreement", p.id, c.id,
                                       terms="Deliver X", value=1000.0)
        assert contract.value == 1000.0
        assert contract.producer == p.id

    def test_contract_creates_relationship(self):
        civ = DigitalCivilization()
        p = civ.charter_institute("P", InstituteType.COMPANY)
        c = civ.charter_institute("C", InstituteType.COMPANY)
        civ.create_contract("Deal", p.id, c.id, value=500.0)
        rels = civ.engine.outgoing(p.id)
        assert len(rels) >= 1

    def test_contracts_for(self):
        civ = DigitalCivilization()
        a = civ.charter_institute("A", InstituteType.COMPANY)
        b = civ.charter_institute("B", InstituteType.COMPANY)
        civ.create_contract("C1", a.id, b.id)
        civ.create_contract("C2", a.id, b.id)
        assert len(civ.contracts_for(a.id)) == 2
        assert len(civ.contracts_for(b.id)) == 2

    def test_adjust_reputation(self):
        civ = DigitalCivilization()
        inst = civ.charter_institute("Test", InstituteType.UNIVERSITY)
        civ.adjust_reputation(inst.id, 0.2, "Great work")
        assert inst.reputation == 0.7

    def test_reputation_clamped(self):
        civ = DigitalCivilization()
        inst = civ.charter_institute("Test", InstituteType.UNIVERSITY)
        civ.adjust_reputation(inst.id, 2.0, "Too much")
        assert inst.reputation == 1.0
        civ.adjust_reputation(inst.id, -5.0, "Too low")
        assert inst.reputation == 0.0

    def test_reputation_history(self):
        civ = DigitalCivilization()
        inst = civ.charter_institute("Test", InstituteType.UNIVERSITY)
        civ.adjust_reputation(inst.id, 0.1, "A")
        civ.adjust_reputation(inst.id, -0.05, "B")
        history = civ.reputation_history(inst.id)
        assert len(history) == 2

    def test_connect_institutes(self):
        civ = DigitalCivilization()
        a = civ.charter_institute("A", InstituteType.COMPANY)
        b = civ.charter_institute("B", InstituteType.UNIVERSITY)
        civ.connect_institutes(a.id, b.id, URelType.FUNDS)
        rels = civ.engine.outgoing(a.id)
        assert len(rels) == 1
        assert rels[0].rel_type == URelType.FUNDS

    def test_summary(self):
        civ = DigitalCivilization()
        civ.charter_institute("U1", InstituteType.UNIVERSITY)
        civ.charter_institute("L1", InstituteType.LABORATORY)
        s = civ.summary()
        assert s["total_institutes"] == 2
        assert s["by_type"]["university"] == 1
        assert s["by_type"]["laboratory"] == 1

    def test_build_default(self):
        civ = build_default_civilization()
        assert civ.summary()["total_institutes"] == 17
        assert civ.summary()["total_relationships"] >= 4

    def test_build_default_all_active(self):
        civ = build_default_civilization()
        for inst in civ.all_institutes():
            assert inst.status == InstituteStatus.ACTIVE

    def test_build_default_with_engine(self):
        eng = RelationshipEngine()
        civ = build_default_civilization(engine=eng)
        assert civ.summary()["total_institutes"] == 17
        assert civ.engine is eng
