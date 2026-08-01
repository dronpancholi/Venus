"""Genesis-I Core — Universal Object Model, UIR, Metadata, Type System."""

from .base import BaseEntity, BaseCapability, BaseArtifact
from .uir import (
    UIRNode, UIRGraph, CompilationUnit,
    DependencyGraph, CapabilityGraph, ValidationGraph,
    ExecutionGraph, MetadataGraph
)
from .types import SemanticType, TypeRegistry, TypeConstraint
from .metadata import MetadataEngine, MetadataRecord
from .exceptions import (
    GenesisError, ValidationError, CompilationError,
    PluginError, CapabilityError, GraphError,
    MetadataError, IndexerError, RuntimeError
)

__all__ = [
    "BaseEntity", "BaseCapability", "BaseArtifact",
    "UIRNode", "UIRGraph", "CompilationUnit",
    "DependencyGraph", "CapabilityGraph", "ValidationGraph",
    "ExecutionGraph", "MetadataGraph",
    "SemanticType", "TypeRegistry", "TypeConstraint",
    "MetadataEngine", "MetadataRecord",
    "GenesisError", "ValidationError", "CompilationError",
    "PluginError", "CapabilityError", "GraphError",
    "MetadataError", "IndexerError", "RuntimeError",
]
