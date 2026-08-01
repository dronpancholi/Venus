"""
Software Genome Atlas — biological representation of software repositories.

Model:
  Genome → Chromosomes → Genes → Traits
  Species → Families → Evolutionary Lineage
  Fitness, Dominance, Inheritance, Mutations

Every repository is a genome.
Every module/file is a chromosome.
Every class/protocol is a gene.
Every architectural property is a trait.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class ChromosomeType(Enum):
    MODULE = auto()
    PACKAGE = auto()
    SERVICE = auto()
    LIBRARY = auto()
    INTERFACE = auto()


class GeneType(Enum):
    CLASS = auto()
    PROTOCOL = auto()
    INTERFACE_GENE = auto()
    ABSTRACTION = auto()
    FUNCTION_GENE = auto()
    DATA_MODEL = auto()
    API = auto()
    EVENT = auto()
    COMMAND = auto()
    QUERY = auto()
    TEST = auto()
    CONFIG = auto()
    MIGRATION = auto()


class TraitCategory(Enum):
    ARCHITECTURE = auto()
    QUALITY = auto()
    SECURITY = auto()
    PERFORMANCE = auto()
    MAINTAINABILITY = auto()
    EVOLVABILITY = auto()
    COMPLEXITY = auto()
    COUPLING = auto()
    COHESION = auto()
    MATURITY = auto()


class MutationType(Enum):
    REFACTOR = auto()
    DEPENDENCY_ADD = auto()
    DEPENDENCY_REMOVE = auto()
    INTERFACE_CHANGE = auto()
    API_BREAK = auto()
    ABSTRACTION_INTRODUCE = auto()
    ABSTRACTION_REMOVE = auto()
    PATTERN_INSTRODUCE = auto()
    PATTERN_REMOVE = auto()
    SCALE_CHANGE = auto()


@dataclass
class GenomeGene:
    """A gene — one unit of software behavior.

    Maps to: class, protocol, interface, function, command, event, query.
    """
    id: str = ""
    name: str = ""
    gene_type: GeneType = GeneType.CLASS
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    complexity: float = 0.0
    dependencies: list[str] = field(default_factory=list)  # gene IDs
    dependents: list[str] = field(default_factory=list)
    traits: dict[str, float] = field(default_factory=dict)
    mutations: list[MutationRecord] = field(default_factory=list)
    conserved: bool = False  # appears across species/repos
    orthologs: list[str] = field(default_factory=list)  # same gene in other genomes

    def __hash__(self):
        return hash(self.id)


@dataclass
class MutationRecord:
    type: MutationType
    timestamp: float
    description: str = ""
    impact: float = 0.0  # -1.0 to 1.0


@dataclass
class GenomeChromosome:
    """A chromosome — one file or module.

    Maps to: Python module, TypeScript file, package, service boundary.
    """
    id: str = ""
    name: str = ""
    chromosome_type: ChromosomeType = ChromosomeType.MODULE
    file_path: str = ""
    genes: dict[str, GenomeGene] = field(default_factory=dict)
    lines_of_code: int = 0
    cohesion: float = 0.0
    coupling: float = 0.0
    traits: dict[str, float] = field(default_factory=dict)

    def add_gene(self, gene: GenomeGene):
        self.genes[gene.id] = gene

    @property
    def gene_count(self) -> int:
        return len(self.genes)

    @property
    def dominant_traits(self) -> list[tuple[str, float]]:
        return sorted(self.traits.items(), key=lambda x: -x[1])[:5]


@dataclass
class FitnessScore:
    overall: float = 0.0
    maintainability: float = 0.0
    test_coverage: float = 0.0
    spec_coverage: float = 0.0
    coupling: float = 0.0
    complexity: float = 0.0
    security: float = 0.0
    maturity: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {k: v for k, v in self.__dict__.items() if isinstance(v, float)}


@dataclass
class Species:
    """A species — a family of architecturally similar repositories."""
    id: str = ""
    name: str = ""
    description: str = ""
    member_genomes: list[str] = field(default_factory=list)
    common_traits: dict[str, float] = field(default_factory=dict)
    signature_patterns: list[str] = field(default_factory=list)
    fitness_range: tuple[float, float] = (0.0, 0.0)

    @property
    def population(self) -> int:
        return len(self.member_genomes)


@dataclass
class EvolutionaryLineage:
    """Evolutionary lineage tracking for a genome."""
    genome_id: str
    ancestor_id: str = ""
    branch: str = "main"
    generation: int = 0
    mutations: list[MutationRecord] = field(default_factory=list)
    fitness_history: list[tuple[float, float]] = field(default_factory=list)  # (timestamp, score)
    fork_point: str = ""
    species_id: str = ""


@dataclass
class SoftwareGenome:
    """Complete software genome for one repository.

    A genome represents the entire architectural DNA of a repository:
    - Chromosomes: modules/files
    - Genes: classes, protocols, interfaces, functions
    - Traits: measurable properties
    - Species: taxonomic classification
    - Fitness: overall quality score
    """
    id: str = ""
    repository_id: str = ""
    repository_name: str = ""
    repository_url: str = ""
    language: str = ""
    chromosomes: dict[str, GenomeChromosome] = field(default_factory=dict)
    traits: dict[str, float] = field(default_factory=dict)
    fitness: FitnessScore = field(default_factory=FitnessScore)
    species: str = ""
    lineage: EvolutionaryLineage | None = None
    created_at: float = 0.0
    updated_at: float = 0.0
    version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    _id_counter: int = 0

    def add_chromosome(self, chromosome: GenomeChromosome):
        self.chromosomes[chromosome.id] = chromosome

    def add_gene(self, chromosome_id: str, gene: GenomeGene) -> bool:
        chrom = self.chromosomes.get(chromosome_id)
        if chrom:
            chrom.add_gene(gene)
            return True
        return False

    @property
    def chromosome_count(self) -> int:
        return len(self.chromosomes)

    @property
    def gene_count(self) -> int:
        return sum(c.gene_count for c in self.chromosomes.values())

    @property
    def total_dependencies(self) -> int:
        deps: set[str] = set()
        for c in self.chromosomes.values():
            for g in c.genes.values():
                deps.update(g.dependencies)
        return len(deps)

    @property
    def all_genes(self) -> list[GenomeGene]:
        genes = []
        for c in self.chromosomes.values():
            genes.extend(c.genes.values())
        return genes

    @property
    def conserved_genes(self) -> list[GenomeGene]:
        return [g for g in self.all_genes if g.conserved]

    @property
    def dominant_traits(self) -> list[tuple[str, float]]:
        return sorted(self.traits.items(), key=lambda x: -x[1])[:10]

    def generate_gene_id(self) -> str:
        self._id_counter += 1
        return f"gene_{self._id_counter}"

    def summary(self) -> dict[str, Any]:
        return {
            "repository": self.repository_name,
            "language": self.language,
            "chromosomes": self.chromosome_count,
            "genes": self.gene_count,
            "total_dependencies": self.total_dependencies,
            "conserved_genes": len(self.conserved_genes),
            "fitness": round(self.fitness.overall, 4),
            "species": self.species,
            "traits": dict(sorted(self.traits.items(), key=lambda x: -x[1])[:5]),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "repository_name": self.repository_name,
            "language": self.language,
            "chromosome_count": self.chromosome_count,
            "gene_count": self.gene_count,
            "traits": self.traits,
            "fitness": self.fitness.to_dict(),
            "species": self.species,
            "version": self.version,
        }
