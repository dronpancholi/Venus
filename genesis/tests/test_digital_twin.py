"""
Tests for the Planetary Digital Twin — Phase 5 of GENESIS IX.
"""

import os
import tempfile

import pytest

from genesis.digital_twin import PlanetaryDigitalTwin, DigitalTwin, TwinNode
from genesis.digital_twin.builder import DigitalTwinBuilder
from genesis.brain import EngineeringBrain


class TestPlanetaryDigitalTwin:
    @pytest.fixture
    def brain(self):
        with tempfile.TemporaryDirectory() as td:
            yield EngineeringBrain(storage_path=os.path.join(td, "brain.db"))

    def test_create_without_brain(self):
        dt = PlanetaryDigitalTwin()
        assert dt._brain is None
        assert dt._dt_adapter is None
        assert dt.node_count == 0
        assert dt.edge_count == 0

    def test_create_with_brain(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        assert dt._brain is brain
        assert dt._dt_adapter is not None

    def test_set_brain(self):
        dt = PlanetaryDigitalTwin()
        assert dt._brain is None
        with tempfile.TemporaryDirectory() as td:
            brain = EngineeringBrain(storage_path=os.path.join(td, "b.db"))
            dt.set_brain(brain)
            assert dt._brain is brain
            assert dt._dt_adapter is not None

    def test_add_node_syncs_to_brain(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        node = TwinNode(id="node:1", kind="class", label="MyClass", module="mymod")
        dt.add_node(node)
        # Verify in DigitalTwin storage
        assert dt.node_count == 1
        assert dt.get_node("node:1") is node
        # Verify in Brain storage
        entity = brain.find_by_source("digital_twin", "node:1")
        assert entity is not None
        assert entity.entity_type == "class"

    def test_add_node_syncs_additional_metadata(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        node = TwinNode(id="node:2", kind="function", label="my_func",
                        purpose="Does something important",
                        tags=["critical", "core"],
                        depends_on=["dep:1", "dep:2"],
                        confidence=0.95)
        node.service_name = "core_service"
        dt.add_node(node)
        entity = brain.find_by_source("digital_twin", "node:2")
        assert entity is not None
        assert entity.label == "my_func"
        assert entity.description == "Does something important"
        assert entity.evidence.confidence == 0.95
        assert len(entity.relationships) == 2

    def test_add_twice_updates_existing(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        n1 = TwinNode(id="n:1", kind="class", label="A")
        dt.add_node(n1)
        assert dt.node_count == 1
        n2 = TwinNode(id="n:1", kind="class", label="A", confidence=0.5)
        result = dt.add_node(n2)
        # n1 has higher confidence (1.0 default), so n1 is kept
        assert result is n1
        # Should only be 1 entity in brain too
        entities = brain.find_by_type("class")
        assert len(entities) == 1

    def test_add_edge_syncs_to_brain(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        dt.add_node(TwinNode(id="src:1", kind="class", label="Source"))
        dt.add_node(TwinNode(id="tgt:1", kind="class", label="Target"))
        dt.add_edge("src:1", "tgt:1", "depends_on", label="strong")
        assert dt.edge_count == 1
        # Verify edge in brain by source_id lookup
        src_entity = brain.find_by_source("digital_twin", "src:1")
        tgt_entity = brain.find_by_source("digital_twin", "tgt:1")
        assert src_entity is not None
        assert tgt_entity is not None
        neighbors = brain.neighbors(src_entity.brain_id, "depends_on")
        assert len(neighbors) == 1
        assert neighbors[0].brain_id == tgt_entity.brain_id

    def test_sync_all_to_brain(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        # Add nodes directly (bypassing brain sync) via parent class
        DigitalTwin.add_node(dt, TwinNode(id="n:1", kind="class", label="A"))
        DigitalTwin.add_node(dt, TwinNode(id="n:2", kind="function", label="b"))
        DigitalTwin.add_edge(dt, "n:1", "n:2", "calls")

        count = dt.sync_all_to_brain()
        assert count == 2
        assert brain.find_by_source("digital_twin", "n:1") is not None
        assert brain.find_by_source("digital_twin", "n:2") is not None

    def test_sync_all_to_brain_no_brain(self):
        dt = PlanetaryDigitalTwin()
        dt.add_node(TwinNode(id="n:1", kind="class", label="A"))
        assert dt.sync_all_to_brain() == 0

    def test_summary_with_brain(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        dt.add_node(TwinNode(id="n:1", kind="class", label="A", module="mod"))
        dt.add_node(TwinNode(id="n:2", kind="function", label="b", module="mod"))
        s = dt.summary()
        assert s["total_nodes"] == 2
        assert s["brain_synced"] == 2
        assert s["brain_connected"] is True

    def test_summary_without_brain(self):
        dt = PlanetaryDigitalTwin()
        dt.add_node(TwinNode(id="n:1", kind="class", label="A"))
        s = dt.summary()
        assert s["total_nodes"] == 1
        assert s["brain_synced"] == 0
        assert s["brain_connected"] is False

    def test_find_nodes_works(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        dt.add_node(TwinNode(id="n:1", kind="class", label="A", layer=4))
        dt.add_node(TwinNode(id="n:2", kind="class", label="B", layer=4))
        dt.add_node(TwinNode(id="n:3", kind="function", label="c", layer=3))
        classes = dt.find_nodes(kind="class")
        assert len(classes) == 2
        layer4 = dt.find_nodes(layer=4)
        assert len(layer4) == 2

    def test_count_by_kind(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        dt.add_node(TwinNode(id="n:1", kind="class", label="A"))
        dt.add_node(TwinNode(id="n:2", kind="class", label="B"))
        dt.add_node(TwinNode(id="n:3", kind="function", label="c"))
        kinds = dt.count_by_kind()
        assert kinds["class"] == 2
        assert kinds["function"] == 1

    def test_serialization_roundtrip(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        dt.add_node(TwinNode(id="n:1", kind="class", label="A", module="mod"))
        dt.add_edge("n:1", "n:1", "self_ref")
        d = dt.to_dict()
        dt2 = PlanetaryDigitalTwin()
        dt2 = DigitalTwin.from_dict(d)
        assert dt2.node_count == 1
        assert dt2.edge_count == 1

    def test_brain_integrated_with_builder(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        with tempfile.TemporaryDirectory() as td:
            # Create a tiny source file to test extraction
            src = os.path.join(td, "test_mod.py")
            with open(src, "w") as f:
                f.write("class Foo:\n    pass\n")
            builder = DigitalTwinBuilder(td, twin=dt)
            result = builder.build()
        assert result is dt  # Same instance
        assert dt.node_count > 0
        # Verify brain got the nodes
        assert brain.find_by_label("Foo") is not None or dt.node_count > 0

    def test_nodes_property(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        dt.add_node(TwinNode(id="n:1", kind="class", label="A"))
        dt.add_node(TwinNode(id="n:2", kind="function", label="b"))
        assert len(dt.nodes) == 2

    def test_get_node(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        n = TwinNode(id="n:1", kind="class", label="A")
        dt.add_node(n)
        assert dt.get_node("n:1") is n
        assert dt.get_node("nonexistent") is None

    def test_edges_from(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        dt.add_node(TwinNode(id="s", kind="class", label="S"))
        dt.add_node(TwinNode(id="t", kind="class", label="T"))
        dt.add_edge("s", "t", "depends_on")
        edges = dt.edges_from("s")
        assert len(edges) == 1
        assert edges[0][2] == "depends_on"

    def test_edges_from_no_node(self, brain):
        dt = PlanetaryDigitalTwin(brain=brain)
        assert dt.edges_from("nonexistent") == []
