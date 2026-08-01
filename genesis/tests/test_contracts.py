"""Tests for Integration Contracts (Missions 185-187)."""

from genesis.contracts import (
    VENUS_CONTRACT, BUILDIT_CONTRACT, AGENTOS_CONTRACT,
    ALL_CONTRACTS, get_contract, list_contracts, check_compliance,
)


class TestVenusContract:
    def test_has_consumes(self):
        assert len(VENUS_CONTRACT.consumes) > 5

    def test_has_constraints(self):
        assert len(VENUS_CONTRACT.constraints) >= 3

    def test_product_name(self):
        assert VENUS_CONTRACT.product == "venus"


class TestBuilditContract:
    def test_has_consumes(self):
        assert len(BUILDIT_CONTRACT.consumes) > 3

    def test_product_name(self):
        assert BUILDIT_CONTRACT.product == "buildit"


class TestAgentosContract:
    def test_has_consumes(self):
        assert len(AGENTOS_CONTRACT.consumes) > 5

    def test_product_name(self):
        assert AGENTOS_CONTRACT.product == "agentos"


class TestContracts:
    def test_all_contracts_registered(self):
        assert "venus" in ALL_CONTRACTS
        assert "buildit" in ALL_CONTRACTS
        assert "agentos" in ALL_CONTRACTS

    def test_get_contract(self):
        c = get_contract("venus")
        assert c is not None
        assert c.product == "venus"
        assert get_contract("nonexistent") is None

    def test_list_contracts(self):
        listed = list_contracts()
        assert len(listed) == 3

    def test_compliance_compliant(self):
        actual = [
            "fabric.kernel.instance()",
            "fabric.kernel.emit()",
            "ai.registry",
            "knowledge.search",
        ]
        violations = check_compliance("venus", actual)
        assert len(violations) == 0

    def test_compliance_violation(self):
        actual = [
            "fabric.internal_secret",
            "genesis.something_private",
        ]
        violations = check_compliance("venus", actual)
        assert len(violations) > 0

    def test_compliance_unknown_product(self):
        violations = check_compliance("unknown", ["a", "b"])
        assert len(violations) == 1
