"""Base compiler pass infrastructure."""

from abc import ABC, abstractmethod
from typing import Any

from genesis.core.uir import CompilationUnit


class CompilerPass(ABC):
    """A single compiler pass that transforms a CompilationUnit."""

    def __init__(self, name: str = ""):
        self.name = name or self.__class__.__name__

    @abstractmethod
    def run(self, cu: CompilationUnit) -> CompilationUnit:
        ...

    def __repr__(self) -> str:
        return f"<Pass:{self.name}>"


class PassRegistry:
    """Registry of named compiler passes."""

    def __init__(self):
        self._passes: dict[str, CompilerPass] = {}

    def register(self, pass_instance: CompilerPass):
        self._passes[pass_instance.name] = pass_instance

    def get(self, name: str) -> CompilerPass | None:
        return self._passes.get(name)

    def all(self) -> list[CompilerPass]:
        return list(self._passes.values())

    def run_sequence(self, cu: CompilationUnit, pass_names: list[str] | None = None) -> CompilationUnit:
        targets = pass_names or list(self._passes.keys())
        for name in targets:
            pass_instance = self._passes.get(name)
            if pass_instance:
                cu = pass_instance.run(cu)
                cu.passes_applied.append(name)
        return cu
