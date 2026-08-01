"""
Tests for GENESIS-VIII Program 9: Universal Engineering Mathematics.
"""

import pytest
from genesis.mathematics import (
    ArchitectureAlgebra, ArchitectureElement, CapabilityVector,
    TopologicalSpace, GraphCalculus, KnowledgeEntropy,
    DecisionTheory, Optimization, NetworkScience,
    InformationTheory, CategoryTheory, CategoryObject, CategoryMorphism,
    ConstraintSatisfaction, Constraint,
)


class TestArchitectureAlgebra:
    def test_coupling_sum(self):
        elems = [ArchitectureElement(coupling=0.5), ArchitectureElement(coupling=0.3)]
        assert ArchitectureAlgebra.coupling_sum(elems) == 0.8

    def test_cohesion_ratio(self):
        elems = [ArchitectureElement(cohesion=0.7, coupling=0.3)]
        assert 0.0 < ArchitectureAlgebra.cohesion_ratio(elems) <= 1.0

    def test_layered_distance(self):
        a = ArchitectureElement(element_type="core")
        b = ArchitectureElement(element_type="ui")
        layer_map = {"core": 0, "ui": 2}
        assert ArchitectureAlgebra.layered_distance(a, b, layer_map) == 2


class TestCapabilityVector:
    def test_dot(self):
        v1 = CapabilityVector({"a": 0.5, "b": 0.8})
        v2 = CapabilityVector({"a": 0.9, "b": 0.2})
        assert v1.dot(v2) == 0.5 * 0.9 + 0.8 * 0.2

    def test_cosine_similarity(self):
        v1 = CapabilityVector({"a": 1.0, "b": 0.0})
        v2 = CapabilityVector({"a": 1.0, "b": 0.0})
        assert v1.cosine_similarity(v2) == 1.0

    def test_capability_gap(self):
        current = CapabilityVector({"a": 0.3, "b": 0.9})
        required = CapabilityVector({"a": 0.8, "b": 0.5, "c": 0.7})
        gap = current.capability_gap(required)
        assert gap.capabilities.get("a") == 0.5
        assert gap.capabilities.get("c") == 0.7
        assert "b" not in gap.capabilities


class TestTopologicalSpace:
    def test_dependency_closure(self):
        ts = TopologicalSpace(["a", "b", "c"], [("a", "b"), ("b", "c")])
        closure = ts.dependency_closure("a")
        assert closure == {"a", "b", "c"}

    def test_separation_degree(self):
        ts = TopologicalSpace(["a", "b"], [("a", "b")])
        assert 0.0 <= ts.separation_degree() <= 1.0


class TestGraphCalculus:
    def test_adjacency_matrix(self):
        mat = GraphCalculus.adjacency_matrix(["a", "b"], [("a", "b")])
        assert mat[0][1] == 1
        assert mat[1][0] == 0

    def test_degree_centrality(self):
        cent = GraphCalculus.degree_centrality(["a", "b"], [("a", "b")])
        assert cent["a"]["out"] > 0


class TestKnowledgeEntropy:
    def test_shannon_entropy(self):
        h = KnowledgeEntropy.shannon_entropy([0.5, 0.5])
        assert h == 1.0

    def test_knowledge_diversity(self):
        d = KnowledgeEntropy.knowledge_diversity({"a": 10, "b": 10})
        assert d == 1.0

    def test_mutual_information(self):
        mi = KnowledgeEntropy.mutual_information({("x", "y"): 1.0})
        assert mi >= 0


class TestDecisionTheory:
    def test_expected_value(self):
        ev = DecisionTheory.expected_value([(0.5, 100), (0.5, 0)])
        assert ev == 50.0

    def test_regret(self):
        alts = {"A": [(1.0, 100)], "B": [(1.0, 80)]}
        regret = DecisionTheory.regret(alts)
        assert regret["A"] == 0
        assert regret["B"] == 20


class TestOptimization:
    def test_pareto_frontier(self):
        points = [(1, 9), (2, 8), (9, 1), (8, 2)]
        frontier = Optimization.pareto_frontier(points, (True, True))
        assert len(frontier) > 0

    def test_weighted_sum(self):
        ws = Optimization.weighted_sum([0.8, 0.6], [1.0, 2.0])
        assert ws > 0

    def test_min_max_normalize(self):
        norm = Optimization.min_max_normalize([1, 2, 3])
        assert norm[0] == 0.0
        assert norm[2] == 1.0


class TestNetworkScience:
    def test_clustering_coefficient(self):
        adj = {"a": {"b", "c"}, "b": {"a"}, "c": {"a"}}
        cc = NetworkScience.clustering_coefficient(adj)
        assert 0 <= cc <= 1


class TestInformationTheory:
    def test_kolmogorov_complexity_estimate(self):
        k = InformationTheory.kolmogorov_complexity_estimate("a b c a b c")
        assert k > 0

    def test_redundancy(self):
        r = InformationTheory.redundancy(100, 50)
        assert 0 <= r <= 1


class TestCategoryTheory:
    def test_compose_valid(self):
        f = CategoryMorphism(source="A", target="B")
        g = CategoryMorphism(source="B", target="C")
        h = CategoryTheory.compose(f, g)
        assert h is not None
        assert h.source == "A"
        assert h.target == "C"

    def test_compose_invalid(self):
        f = CategoryMorphism(source="A", target="B")
        g = CategoryMorphism(source="C", target="D")
        assert CategoryTheory.compose(f, g) is None


class TestConstraintSatisfaction:
    def test_check_all(self):
        cs = ConstraintSatisfaction()
        cs.add(Constraint(name="c1", variables=["x", "y"]))
        results = cs.check_all({"x": 1.0, "y": 2.0})
        assert len(results) == 1

    def test_feasible_region(self):
        cs = ConstraintSatisfaction()
        region = cs.feasible_region({"x": (0, 1)}, lambda p: p["x"] > 0.5, samples=100)
        assert 0 <= region <= 1
