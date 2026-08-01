"""Compiler optimization passes."""

from .base import CompilerPass, PassRegistry
from .optimization import (
    DeadCodeEliminationPass,
    DependencyPruningPass,
    MetadataNormalizationPass,
)

__all__ = [
    "CompilerPass", "PassRegistry",
    "DeadCodeEliminationPass", "DependencyPruningPass",
    "MetadataNormalizationPass",
]
