"""
Tests for GENESIS-IX Phase 8: Engineering Mathematics V2.
"""

import math
import pytest
from genesis.mathematics_v2 import (
    ArchitectureAlgebra, CapabilityVector, DependencyTensor,
    EntropyModels, ResilienceEquations, OptimizationTheory,
    InformationTheory, NetworkScience, CategoryTheory, Obj, Mor,
    GameTheory, ControlTheory, EngineeringMathematics,
)


class TestArchitectureAlgebra:
    def test_coupling_product(self):
        matrix = [
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0],
        ]
        cp = ArchitectureAlgebra.coupling_product(matrix)
        assert cp > 0
        assert cp <= 1

    def test_coupling_product_empty(self):
        assert ArchitectureAlgebra.coupling_product([]) == 0.0

    def test_coupling_product_single(self):
        assert ArchitectureAlgebra.coupling_product([[0]]) == 0.0

    def test_cohesion(self):
        matrix = [
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 0],
        ]
        c = ArchitectureAlgebra.cohesion(matrix, clusters=[[0, 1], [2]])
        assert c > 0

    def test_module_similarity(self):
        a = {"cpu": 0.5, "mem": 0.8}
        b = {"cpu": 0.5, "mem": 0.8}
        assert abs(ArchitectureAlgebra.module_similarity(a, b) - 1.0) < 0.01

    def test_module_similarity_no_common(self):
        assert ArchitectureAlgebra.module_similarity({"a": 1}, {"b": 1}) == 0.0


class TestCapabilityVector:
    def test_add(self):
        a = CapabilityVector({"cpu": 1.0, "mem": 2.0})
        b = CapabilityVector({"cpu": 0.5, "disk": 1.0})
        c = a + b
        assert c.vec["cpu"] == 1.5
        assert c.vec["mem"] == 2.0
        assert c.vec["disk"] == 1.0

    def test_subtract(self):
        a = CapabilityVector({"cpu": 2.0, "mem": 3.0})
        b = CapabilityVector({"cpu": 1.0})
        c = a - b
        assert c.vec["cpu"] == 1.0

    def test_magnitude(self):
        v = CapabilityVector({"x": 3.0, "y": 4.0})
        assert abs(v.magnitude() - 5.0) < 0.01

    def test_dot(self):
        a = CapabilityVector({"x": 1, "y": 2})
        b = CapabilityVector({"x": 3, "y": 4})
        assert a.dot(b) == 11

    def test_similarity(self):
        a = CapabilityVector({"x": 1, "y": 0})
        b = CapabilityVector({"x": 1, "y": 0})
        assert abs(a.similarity(b) - 1.0) < 0.01

    def test_gap(self):
        current = CapabilityVector({"cpu": 2.0})
        required = CapabilityVector({"cpu": 5.0, "mem": 3.0})
        gap = current.gap(required)
        assert gap.vec["cpu"] == 3.0
        assert gap.vec["mem"] == 3.0


class TestDependencyTensor:
    def setup_method(self):
        self.dt = DependencyTensor()

    def test_set_and_get(self):
        self.dt.set("svc_a", "svc_b", "depends_on", 0.8)
        assert self.dt.get("svc_a", "svc_b", "depends_on") == 0.8
        assert self.dt.get("svc_a", "svc_b", "references") == 0.0

    def test_source_sum(self):
        self.dt.set("a", "b", "depends", 0.5)
        self.dt.set("a", "c", "depends", 0.3)
        self.dt.set("b", "c", "depends", 0.2)
        assert abs(self.dt.source_sum("a") - 0.8) < 0.01
        assert abs(self.dt.source_sum("b") - 0.2) < 0.01

    def test_target_sum(self):
        self.dt.set("a", "b", "depends", 0.5)
        self.dt.set("c", "b", "depends", 0.3)
        assert abs(self.dt.target_sum("b") - 0.8) < 0.01

    def test_contract(self):
        self.dt.set("a", "b", "depends", 0.5)
        self.dt.set("b", "c", "depends", 0.3)
        mat = self.dt.contract()
        assert len(mat) >= 3


class TestEntropyModels:
    def test_architecture_entropy(self):
        types = {"service": 10, "agent": 5, "database": 2}
        h = EntropyModels.architecture_entropy(types)
        assert 0 <= h <= 1

    def test_architecture_entropy_empty(self):
        assert EntropyModels.architecture_entropy({}) == 0.0

    def test_knowledge_entropy(self):
        dist = {"a": 0.5, "b": 0.3, "c": 0.2}
        h = EntropyModels.knowledge_entropy(dist)
        assert h > 0

    def test_knowledge_entropy_empty(self):
        assert EntropyModels.knowledge_entropy({}) == 0.0

    def test_cross_entropy(self):
        ce = EntropyModels.cross_entropy([0.5, 0.5], [0.5, 0.5])
        assert ce > 0


class TestResilienceEquations:
    def test_system_resilience(self):
        r = ResilienceEquations.system_resilience(
            test_coverage=0.8, complexity=0.3, coupling=0.2
        )
        assert r > 0

    def test_failure_rate(self):
        f = ResilienceEquations.failure_rate(
            complexity=0.5, coupling=0.4, test_coverage=0.7
        )
        assert 0 <= f <= 1

    def test_recovery_time(self):
        t = ResilienceEquations.recovery_time(module_count=10, test_coverage=0.8)
        assert t > 0


class TestOptimizationTheory:
    def test_pareto_frontier(self):
        points = [(1, 3), (2, 2), (3, 1)]
        frontier = OptimizationTheory.pareto_frontier(points)
        assert len(frontier) >= 1

    def test_pareto_frontier_empty(self):
        assert OptimizationTheory.pareto_frontier([]) == []

    def test_weighted_sum(self):
        ws = OptimizationTheory.weighted_sum([10, 20], [0.5, 0.5])
        assert abs(ws - 15.0) < 0.01

    def test_weighted_sum_empty(self):
        assert OptimizationTheory.weighted_sum([], []) == 0.0


class TestInformationTheory:
    def test_entropy(self):
        h = InformationTheory.entropy([0.5, 0.5])
        assert abs(h - 1.0) < 0.01

    def test_entropy_empty(self):
        assert InformationTheory.entropy([]) == 0.0

    def test_mutual_information(self):
        joint = {("a", "x"): 0.3, ("a", "y"): 0.2,
                  ("b", "x"): 0.1, ("b", "y"): 0.4}
        mi = InformationTheory.mutual_information(joint)
        assert mi > 0

    def test_kl_divergence(self):
        kl = InformationTheory.kl_divergence([0.5, 0.5], [0.5, 0.5])
        assert abs(kl) < 0.001

    def test_redundancy(self):
        r = InformationTheory.redundancy(code_length=8, vocab_size=256)
        assert 0 <= r <= 1


class TestNetworkScience:
    def test_degree_distribution(self):
        adj = {"a": {"b", "c"}, "b": {"a"}, "c": {"a"}}
        dist = NetworkScience.degree_distribution(adj)
        assert dist.get(2, 0) == 1
        assert dist.get(1, 0) == 2

    def test_clustering_coefficient(self):
        adj = {"a": {"b", "c"}, "b": {"a", "c"}, "c": {"a", "b"}}
        cc = NetworkScience.clustering_coefficient(adj)
        assert abs(cc - 1.0) < 0.01

    def test_small_world_coefficient(self):
        adj = {"a": {"b", "c"}, "b": {"a", "c"}, "c": {"a", "b"}}
        swc = NetworkScience.small_world_coefficient(adj)
        assert swc >= 1


class TestCategoryTheory:
    def test_compose_valid(self):
        f = Mor(src="a", tgt="b", name="f")
        g = Mor(src="b", tgt="c", name="g")
        result = CategoryTheory.compose(f, g)
        assert result is not None
        assert result.src == "a"
        assert result.tgt == "c"

    def test_compose_invalid(self):
        f = Mor(src="a", tgt="b")
        g = Mor(src="c", tgt="d")
        assert CategoryTheory.compose(f, g) is None

    def test_identity(self):
        obj = Obj(name="X")
        mor = CategoryTheory.identity(obj)
        assert mor.src == "X"
        assert mor.tgt == "X"

    def test_is_iso(self):
        f = Mor(src="a", tgt="b")
        g = Mor(src="b", tgt="a")
        assert CategoryTheory.is_iso(f, g) is True

    def test_is_iso_false(self):
        f = Mor(src="a", tgt="b")
        g = Mor(src="c", tgt="d")
        assert CategoryTheory.is_iso(f, g) is False

    def test_functor(self):
        result = CategoryTheory.functor({"A": "X"}, {"f": "g"})
        assert result["A"] == "X"
        assert result["f"] == "g"


class TestGameTheory:
    def test_nash_equilibrium_2x2(self):
        matrix = [[3, 0], [5, 1]]
        eq = GameTheory.nash_equilibrium(matrix)
        assert len(eq) == 2
        assert all(0 <= v <= 1 for v in eq)
        assert abs(sum(eq) - 1.0) < 0.01

    def test_nash_equilibrium_empty(self):
        assert GameTheory.nash_equilibrium([]) == []

    def test_expected_payoff(self):
        payoff = GameTheory.expected_payoff([0.5, 0.5], [[1, 0], [0, 1]])
        assert abs(payoff - 1.0) < 0.01

    def test_nash_equilibrium_large(self):
        matrix = [[1, 2], [3, 4], [5, 6]]
        eq = GameTheory.nash_equilibrium(matrix)
        assert len(eq) > 0


class TestControlTheory:
    def test_pid_control(self):
        output, integral, error = ControlTheory.pid_control(
            setpoint=100, current=80, kp=1.0, ki=0.1, kd=0.05
        )
        assert output > 0
        assert integral != 0
        assert error == 20

    def test_pid_control_at_setpoint(self):
        output, integral, error = ControlTheory.pid_control(
            setpoint=100, current=100
        )
        assert output == 0.0
        assert error == 0.0

    def test_transfer_function(self):
        result = ControlTheory.transfer_function(gain=2.0, time_constant=1.0, input_val=10)
        assert result > 0


class TestEngineeringMathematics:
    def setup_method(self):
        self.em = EngineeringMathematics()

    def test_summary(self):
        s = self.em.summary()
        assert len(s["models"]) == 19
        assert s["executable"] is True

    def test_all_modules_accessible(self):
        assert hasattr(self.em, "architecture")
        assert hasattr(self.em, "entropy")
        assert hasattr(self.em, "resilience")
        assert hasattr(self.em, "optimization")
        assert hasattr(self.em, "information")
        assert hasattr(self.em, "network")
        assert hasattr(self.em, "categories")
        assert hasattr(self.em, "games")
        assert hasattr(self.em, "control")
