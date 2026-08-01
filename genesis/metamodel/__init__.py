"""
Global Meta Model — unified engineering metamodel for all entities.

Everything is an Entity in a UnifiedGraph.
No special cases. No exceptions.

Entity types:
  - Repository, Module, Package, Class, Function, Protocol
  - Specification, Architecture, Decision, Experiment, Paper
  - Law, Pattern, Organization, Engineer, Team, Capability
  - And everything else: commits, issues, releases, dependencies, etc.
"""

from genesis.metamodel.entity import UnifiedEntity, EntityType, EntityRelation, EntityMetadata
from genesis.metamodel.graph import UnifiedGraph
from genesis.metamodel.registry import EntityTypeRegistry
from genesis.metamodel.query import EntityQuery, QueryResult

__all__ = [
    "UnifiedEntity", "EntityType", "EntityRelation", "EntityMetadata",
    "UnifiedGraph",
    "EntityTypeRegistry",
    "EntityQuery", "QueryResult",
]
