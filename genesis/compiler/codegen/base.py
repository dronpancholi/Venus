"""Base code generator infrastructure."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from genesis.core.uir import CompilationUnit


class CodeGenerator(ABC):
    """Generates output artifacts from a CompilationUnit."""

    def __init__(self, name: str = "", output_format: str = ""):
        self.name = name or self.__class__.__name__
        self.output_format = output_format

    @abstractmethod
    def generate(self, cu: CompilationUnit, output_dir: str | Path) -> list[Path]:
        ...


class CodeGenRegistry:
    """Registry of code generators."""

    def __init__(self):
        self._generators: dict[str, CodeGenerator] = {}

    def register(self, generator: CodeGenerator):
        self._generators[generator.name] = generator

    def get(self, name: str) -> CodeGenerator | None:
        return self._generators.get(name)

    def all(self) -> list[CodeGenerator]:
        return list(self._generators.values())

    def generate_all(self, cu: CompilationUnit, output_dir: str | Path) -> dict[str, list[Path]]:
        results = {}
        for name, gen in self._generators.items():
            results[name] = gen.generate(cu, output_dir)
        return results
