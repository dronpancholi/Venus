"""
GENESIS-VIII Program 2: Universal Memory Architecture.

Memory types: episodic, semantic, procedural, architectural, research,
organizational, temporal, causal, execution, agent, world, graph,
specification, conversation, simulation, reflection.

Features: knowledge consolidation, forgetting, compression, provenance,
contradiction detection, confidence propagation.
"""

from genesis.memory.engine import MemoryEngine
from genesis.memory.types import (
    MemoryType, MemoryEntry, MemoryQuery, MemoryResult,
    EpisodicMemory, SemanticMemory, ProceduralMemory,
    ArchitecturalMemory, ResearchMemory, OrganizationalMemory,
    TemporalMemory, CausalMemory, ExecutionMemory,
    AgentMemory, WorldMemory, GraphMemory,
    SpecificationMemory, ConversationMemory,
    SimulationMemory, ReflectionMemory,
)
from genesis.memory.consolidation import MemoryConsolidator, ForgettingMechanism

__all__ = [
    "MemoryEngine",
    "MemoryType", "MemoryEntry", "MemoryQuery", "MemoryResult",
    "EpisodicMemory", "SemanticMemory", "ProceduralMemory",
    "ArchitecturalMemory", "ResearchMemory", "OrganizationalMemory",
    "TemporalMemory", "CausalMemory", "ExecutionMemory",
    "AgentMemory", "WorldMemory", "GraphMemory",
    "SpecificationMemory", "ConversationMemory",
    "SimulationMemory", "ReflectionMemory",
    "MemoryConsolidator", "ForgettingMechanism",
]
