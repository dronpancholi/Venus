"""
GENESIS-VIII Brain — Universal Engineering Intelligence Platform V2.

The Engineering Brain V2 adds a complete cognitive architecture:
belief systems, goal hierarchy, multi-modal reasoning, working/episodic
memory, attention, reflection, strategy, decision engine, and multi-agent
orchestration — all integrated with the existing entity model, graph,
sync adapters, and EventBus.

Subsystems:
  entity      — BrainEntity, Relationship, Confidence, Lineage, Capability, Evidence
  graph       — BrainGraph — persistent universal graph (wraps PersistentGraphDB)
  sync        — Bidirectional adapters for all existing subsystems
  integration — EventBus-driven auto-registration + runtime lifecycle
  embeddings  — 5-vector embedding storage (placeholder for model inference)
  cognition   — CognitiveArchitecture: belief, goals, reasoning, memory, attention,
                reflection, strategy, decision, orchestration
"""

from __future__ import annotations

import time
from typing import Any

from genesis.brain.entity import (
    BrainEntity, BrainEntityType, Relationship, Confidence, Lineage,
    Capability, Evidence, RuntimeState, ResearchState, EntityEmbedding,
    ChangeRecord,
)
from genesis.brain.graph import BrainGraph
from genesis.brain.sync import (
    DigitalTwinAdapter, UIRAdapter, KnowledgeArtifactAdapter,
    FindingAdapter, VRIPAdapter, GraphDBAdapter,
    get_adapter, register_adapter, ADAPTERS,
)
from genesis.brain.integration import BrainIntegration
from genesis.brain.embeddings import EmbeddingStore
from genesis.brain.cognition import (
    CognitiveArchitecture, BeliefSystem, Belief, BeliefEvidence,
    BeliefStatus, EvidenceKind, GoalHierarchy, Goal, GoalStatus,
    GoalPriority, ReasoningEngine, CausalLink, Inference, ReasoningMode,
    WorkingMemory, EpisodicMemory, AttentionMechanism, AttentionFocus,
    ReflectionEngine, Reflection, StrategyEngine, Tool, Strategy,
    DecisionEngine, Alternative, Decision, Criterion, DecisionMode,
    Orchestrator, CognitiveAgent, AgentTask,
)
from genesis.graphdb import PersistentGraphDB
from genesis.utils.identity import generate_id

__all__ = [
    "EngineeringBrain",
    "BrainEntity", "BrainEntityType", "Relationship",
    "Confidence", "Lineage", "Capability", "Evidence",
    "RuntimeState", "ResearchState", "EntityEmbedding", "ChangeRecord",
    "BrainGraph", "EmbeddingStore", "BrainIntegration",
    "DigitalTwinAdapter", "UIRAdapter", "KnowledgeArtifactAdapter",
    "FindingAdapter", "VRIPAdapter", "GraphDBAdapter",
    "get_adapter", "register_adapter",
    "CognitiveArchitecture", "BeliefSystem", "Belief", "BeliefEvidence",
    "BeliefStatus", "EvidenceKind", "GoalHierarchy", "Goal", "GoalStatus",
    "GoalPriority", "ReasoningEngine", "CausalLink", "Inference", "ReasoningMode",
    "WorkingMemory", "EpisodicMemory", "AttentionMechanism", "AttentionFocus",
    "ReflectionEngine", "Reflection", "StrategyEngine", "Tool", "Strategy",
    "DecisionEngine", "Alternative", "Decision", "Criterion", "DecisionMode",
    "Orchestrator", "CognitiveAgent", "AgentTask",
]


class EngineeringBrain:
    """
    Engineering Brain — the universal facade for the platform.

    This is the single entry point for all entity/relationship operations.
    All subsystems communicate through this brain.

    Usage:
        brain = EngineeringBrain(storage_path="brain.db")
        entity = brain.entity(label="MyEntity", entity_type="service")
        brain.register(entity)
        brain.relate(entity_id_1, entity_id_2, "depends_on")
        brain.sync_digital_twin(twin)
    """

    def __init__(self, storage_path: str = "",
                 event_bus=None):
        self._graph = BrainGraph(storage_path=storage_path)
        self._embeddings = EmbeddingStore(
            storage_path=storage_path.replace(".db", "") if storage_path else ""
        )
        self._integration = BrainIntegration(self._graph, event_bus)
        self._cognition = CognitiveArchitecture()
        self._started_at = time.time()
        self._metrics: dict[str, float] = {
            "entities_registered": 0.0,
            "relationships_created": 0.0,
            "sync_operations": 0.0,
        }

    @property
    def graph(self) -> BrainGraph:
        return self._graph

    @property
    def embeddings(self) -> EmbeddingStore:
        return self._embeddings

    @property
    def integration(self) -> BrainIntegration:
        return self._integration

    @property
    def cognition(self) -> CognitiveArchitecture:
        """The cognitive architecture (beliefs, goals, reasoning, memory, etc.)."""
        return self._cognition

    # ——— Entity CRUD ———

    def entity(self, label: str = "", entity_type: str = "unknown",
               description: str = "", source_system: str = "",
               source_id: str = "", **kwargs) -> BrainEntity:
        """Create a new BrainEntity (not yet registered)."""
        return BrainEntity(
            label=label,
            entity_type=entity_type,
            description=description,
            source_system=source_system,
            source_id=source_id or generate_id(entity_type, 16),
            **kwargs,
        )

    def register(self, entity: BrainEntity) -> BrainEntity:
        """Register an entity in the brain."""
        result = self._graph.register(entity)
        self._metrics["entities_registered"] += 1
        return result

    def get(self, brain_id: str) -> BrainEntity | None:
        return self._graph.get(brain_id)

    def find_by_type(self, entity_type: str) -> list[BrainEntity]:
        return self._graph.find_by_type(entity_type)

    def find_by_label(self, label_contains: str) -> list[BrainEntity]:
        return self._graph.find_by_label(label_contains)

    def find_by_source(self, source_system: str, source_id: str) -> BrainEntity | None:
        return self._graph.find_by_source(source_system, source_id)

    def remove(self, brain_id: str) -> bool:
        self._embeddings.delete_all(brain_id)
        return self._graph.remove(brain_id)

    def all_entities(self) -> list[BrainEntity]:
        return self._graph.all_entities()

    # ——— Relationships ———

    def relate(self, source_id: str, target_id: str, relation: str = "references",
               weight: float = 1.0, **metadata) -> bool:
        result = self._graph.relate(source_id, target_id, relation, weight, **metadata)
        if result:
            self._metrics["relationships_created"] += 1
        return result

    def neighbors(self, brain_id: str, relation: str | None = None) -> list[BrainEntity]:
        return self._graph.get_neighbors(brain_id, relation)

    def relationships(self, brain_id: str) -> list[Relationship]:
        return self._graph.get_relationships(brain_id)

    # ——— Sync ———

    def sync_digital_twin(self, twin) -> int:
        """Sync all DigitalTwin nodes into the brain."""
        adapter = DigitalTwinAdapter()
        self._metrics["sync_operations"] += 1
        return self._integration.sync_adapter("digital_twin", twin)

    def sync_uir_graph(self, uir_graph) -> int:
        """Sync all UIRGraph nodes into the brain."""
        adapter = UIRAdapter()
        self._metrics["sync_operations"] += 1
        return self._integration.sync_adapter("uir", uir_graph)

    def sync_knowledge_base(self, knowledge_base) -> int:
        """Sync all KnowledgeBase artifacts into the brain."""
        self._metrics["sync_operations"] += 1
        count = 0
        if hasattr(knowledge_base, "artifacts"):
            adapter = KnowledgeArtifactAdapter()
            for artifact in knowledge_base.artifacts.values():
                try:
                    entity = adapter.to_entity(artifact)
                    self.register(entity)
                    count += 1
                except Exception:
                    pass
        return count

    def sync_vrip_kg(self, vrip_kg) -> int:
        """Sync all VRIP knowledge graph nodes into the brain."""
        adapter = VRIPAdapter()
        self._metrics["sync_operations"] += 1
        return self._integration.sync_adapter("vrip", vrip_kg)

    def sync_graphdb(self, graphdb: PersistentGraphDB) -> int:
        """Sync all PersistentGraphDB nodes into the brain."""
        adapter = GraphDBAdapter()
        self._metrics["sync_operations"] += 1
        return self._integration.sync_adapter("graphdb", graphdb)

    def sync_civilization(self, overseer) -> int:
        """Sync all civilization agents/findings into the brain."""
        self._metrics["sync_operations"] += 1
        count = 0
        if hasattr(overseer, "agents"):
            adapter = FindingAdapter()
            for agent in overseer.agents.values():
                if hasattr(agent, "memory") and hasattr(agent.memory, "findings"):
                    for finding in agent.memory.findings.values():
                        try:
                            entity = adapter.to_entity(finding)
                            entity.attributes["agent_id"] = agent.agent_id
                            entity.attributes["agent_name"] = getattr(agent, "name", "")
                            self.register(entity)
                            count += 1
                        except Exception:
                            pass
        return count

    # ——— Embeddings ———

    def store_embedding(self, entity_id: str, kind: str, vector: list[float],
                        model: str = "") -> EntityEmbedding:
        return self._embeddings.store(entity_id, kind, vector, model)

    def get_embedding(self, entity_id: str, kind: str) -> EntityEmbedding | None:
        return self._embeddings.get(entity_id, kind)

    # ——— Integration ———

    def start_integration(self):
        """Start listening to platform events."""
        self._integration.start()

    def stop_integration(self):
        self._integration.stop()

    # ——— Analysis ———

    def summary(self) -> dict[str, Any]:
        graph_summary = self._graph.summary()
        return {
            "brain": {
                "uptime_seconds": time.time() - self._started_at,
                "entities_registered": int(self._metrics["entities_registered"]),
                "relationships_created": int(self._metrics["relationships_created"]),
                "sync_operations": int(self._metrics["sync_operations"]),
                "integration_active": self._integration._started,
            },
            "graph": graph_summary,
            "embeddings": self._embeddings.summary(),
            "integration_stats": self._integration.summary(),
        }
