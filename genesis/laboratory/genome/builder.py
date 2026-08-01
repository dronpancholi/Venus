"""
Genome Builder — constructs a SoftwareGenome from DigitalTwin + USIR.

Pipeline:
  1. Create genome for repository
  2. For each file/module → create chromosome
  3. For each class/protocol/interface/function → create gene
  4. Extract traits from repository metrics
  5. Compute fitness from quality attributes
  6. Classify species from architectural signature
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id
from genesis.laboratory.genome.model import (
    SoftwareGenome, GenomeChromosome, GenomeGene, GenomeGene as Gene,
    GenomeGene as GeneNode,  # alias for readability
    ChromosomeType, GeneType, TraitCategory, FitnessScore,
    MutationRecord, MutationType, Species, EvolutionaryLineage,
)

# trait extraction helpers

TRAIT_EXTRACTORS: dict[str, callable] = {}


def register_trait(name: str):
    def decorator(fn):
        TRAIT_EXTRACTORS[name] = fn
        return fn
    return decorator


class GenomeBuilder:
    """Build a SoftwareGenome from repository analysis."""

    def __init__(self, metrics: dict[str, Any] | None = None):
        self.metrics = metrics or {}

    def build_from_twin(self, twin, repo_id: str, repo_name: str,
                         language: str = "python") -> SoftwareGenome:
        """Build genome from a DigitalTwin."""
        genome = SoftwareGenome(
            id=f"genome::{repo_id}",
            repository_id=repo_id,
            repository_name=repo_name,
            language=language,
            created_at=time.time(),
            updated_at=time.time(),
        )

        # — Extract files as chromosomes —
        file_nodes = twin.find_nodes(kind="file") if hasattr(twin, 'find_nodes') else []
        for fn in file_nodes:
            chrom_id = f"chrom_{fn.id}" if hasattr(fn, 'id') else generate_id()
            chrom = GenomeChromosome(
                id=chrom_id,
                name=getattr(fn, 'label', getattr(fn, 'name', 'unknown')),
                chromosome_type=ChromosomeType.MODULE,
                file_path=getattr(fn, 'file_path', getattr(fn, 'source_file', '')),
                lines_of_code=getattr(fn, 'last_line', 0) or getattr(fn, 'lines_of_code', 0) or 0,
            )

            # — Extract classes/functions as genes —
            for node in twin.find_nodes(kind="class"):
                gid = genome.generate_gene_id()
                gene = GenomeGene(
                    id=gid,
                    name=getattr(node, 'label', getattr(node, 'name', 'Unknown')),
                    gene_type=GeneType.CLASS,
                    file_path=getattr(node, 'file_path', ''),
                    complexity=float(getattr(node, 'complexity', 0) or 0),
                )
                if hasattr(node, 'base_classes') and node.base_classes:
                    gene.dependencies = list(node.base_classes)
                chrom.add_gene(gene)

            for node in twin.find_nodes(kind="function"):
                gid = genome.generate_gene_id()
                gene = GenomeGene(
                    id=gid,
                    name=getattr(node, 'label', getattr(node, 'name', 'Unknown')),
                    gene_type=GeneType.FUNCTION_GENE,
                    file_path=getattr(node, 'file_path', ''),
                    complexity=float(getattr(node, 'complexity', 0) or 0),
                )
                chrom.add_gene(gene)

            for node in twin.find_nodes(kind="protocol") if hasattr(twin, 'find_nodes') else []:
                gid = genome.generate_gene_id()
                gene = GenomeGene(
                    id=gid,
                    name=getattr(node, 'label', 'Unknown'),
                    gene_type=GeneType.PROTOCOL,
                    file_path=getattr(node, 'file_path', ''),
                )
                chrom.add_gene(gene)

            genome.add_chromosome(chrom)

        # — Extract traits from metrics —
        genome.traits = self._extract_traits(genome)

        # — Compute fitness —
        genome.fitness = self._compute_fitness(genome)

        # — Classify species —
        genome.species = self._classify_species(genome)

        return genome

    def build_from_usir(self, usir, repo_id: str, repo_name: str,
                         language: str = "python", repo_url: str = "") -> SoftwareGenome:
        """Build genome from a USIR graph."""
        genome = SoftwareGenome(
            id=f"genome::{repo_id}",
            repository_id=repo_id,
            repository_name=repo_name,
            repository_url=repo_url,
            language=language,
            created_at=time.time(),
            updated_at=time.time(),
        )

        # — Group USIR nodes by source file → chromosomes —
        file_map: dict[str, GenomeChromosome] = {}

        for node in usir.nodes:
            src = getattr(node, 'source_file', '') or 'unknown'
            if src not in file_map:
                chrom_id = genome.generate_gene_id()
                file_map[src] = GenomeChromosome(
                    id=f"chrom_{chrom_id}",
                    name=Path(src).stem if src != 'unknown' else 'unknown',
                    chromosome_type=ChromosomeType.MODULE,
                    file_path=src,
                    lines_of_code=getattr(node, 'lines_of_code', 0) or 0,
                )

            gene_type = self._usir_kind_to_gene_type(getattr(node, 'kind', None))
            gid = genome.generate_gene_id()
            gene = GenomeGene(
                id=gid,
                name=getattr(node, 'name', 'Unnamed'),
                gene_type=gene_type,
                file_path=src,
                line_start=getattr(node, 'source_line', 0) or 0,
                complexity=float(getattr(node, 'complexity', 0) or 0),
            )
            file_map[src].add_gene(gene)

        for chrom in file_map.values():
            genome.add_chromosome(chrom)

        # — Extract traits —
        genome.traits = self._extract_traits(genome)

        # — Compute fitness —
        genome.fitness = self._compute_fitness(genome)

        # — Species classification —
        genome.species = self._classify_species(genome)

        return genome

    def _usir_kind_to_gene_type(self, kind) -> GeneType:
        if kind is None:
            return GeneType.CLASS
        name = kind.name.lower() if hasattr(kind, 'name') else str(kind).lower()
        mapping = {
            'class': GeneType.CLASS,
            'protocol': GeneType.PROTOCOL,
            'interface': GeneType.INTERFACE_GENE,
            'trait': GeneType.ABSTRACTION,
            'function': GeneType.FUNCTION_GENE,
            'api': GeneType.API,
            'event': GeneType.EVENT,
            'command': GeneType.COMMAND,
            'query': GeneType.QUERY,
            'test': GeneType.TEST,
            'config': GeneType.CONFIG,
            'migration': GeneType.MIGRATION,
        }
        return mapping.get(name, GeneType.CLASS)

    def _extract_traits(self, genome: SoftwareGenome) -> dict[str, float]:
        traits: dict[str, float] = {}

        # — Size traits —
        traits['gene_count'] = float(genome.gene_count)
        traits['chromosome_count'] = float(genome.chromosome_count)
        traits['gene_density'] = round(
            genome.gene_count / max(genome.chromosome_count, 1), 4
        )

        # — Complexity traits —
        complexities = [g.complexity for g in genome.all_genes if g.complexity > 0]
        traits['avg_complexity'] = round(
            sum(complexities) / max(len(complexities), 1), 4
        )
        traits['max_complexity'] = round(max(complexities) if complexities else 0, 4)

        # — Dependency traits —
        dep_counts = [len(g.dependencies) for g in genome.all_genes]
        traits['avg_dependencies'] = round(
            sum(dep_counts) / max(len(dep_counts), 1), 4
        )
        traits['total_dependencies'] = float(genome.total_dependencies)
        traits['dependency_density'] = round(
            genome.total_dependencies / max(genome.chromosome_count, 1), 4
        )

        # — Gene type distribution —
        type_counts: dict[str, int] = {}
        for g in genome.all_genes:
            type_counts[g.gene_type.name.lower()] = type_counts.get(g.gene_type.name.lower(), 0) + 1
        for t, c in type_counts.items():
            if c > 0:
                traits[f'gene_type_{t}'] = float(c)

        # — Protocol richness —
        protocol_count = type_counts.get('protocol', 0) + type_counts.get('interface_gene', 0)
        traits['protocol_richness'] = round(
            protocol_count / max(genome.gene_count, 1), 4
        )

        # — Conserved gene ratio —
        conserved = [g for g in genome.all_genes if g.conserved]
        traits['conserved_ratio'] = round(
            len(conserved) / max(genome.gene_count, 1), 4
        )

        # — Add metric-derived traits if available —
        if self.metrics:
            for k in ('architectural_entropy', 'maintainability_index',
                       'subsystem_cohesion', 'contract_coverage',
                       'information_density', 'graph_diameter',
                       'duplication_index', 'volatility'):
                if k in self.metrics:
                    traits[k] = float(self.metrics[k])

        return traits

    def _compute_fitness(self, genome: SoftwareGenome) -> FitnessScore:
        fitness = FitnessScore()

        # — Maintainability: inverse of avg complexity, normalized —
        avg_c = genome.traits.get('avg_complexity', 0)
        fitness.maintainability = round(1.0 / (1.0 + avg_c), 4)

        # — Test coverage: ratio of test genes to total genes —
        test_genes = [g for g in genome.all_genes if g.gene_type == GeneType.TEST]
        fitness.test_coverage = round(
            len(test_genes) / max(genome.gene_count, 1), 4
        )

        # — Coupling: inverse of dependency density, normalized —
        dep_den = genome.traits.get('dependency_density', 0)
        fitness.coupling = round(1.0 / (1.0 + dep_den), 4)

        # — Complexity: normalized —
        max_c = genome.traits.get('max_complexity', 0)
        fitness.complexity = round(1.0 / (1.0 + max_c), 4)

        # — Maturity: based on conserved genes and chromosome count —
        cons_ratio = genome.traits.get('conserved_ratio', 0)
        fitness.maturity = round(
            min(1.0, cons_ratio + min(genome.chromosome_count / 50, 0.5)), 4
        )

        # — Security: placeholder (requires security analysis) —
        fitness.security = 0.5

        # — Spec coverage: from metrics —
        spec_cov = self.metrics.get('specification_completeness', 0) if self.metrics else 0
        fitness.spec_coverage = round(float(spec_cov), 4)

        # — Overall: weighted average —
        weights = {
            'maintainability': 0.20,
            'test_coverage': 0.20,
            'coupling': 0.15,
            'complexity': 0.15,
            'maturity': 0.10,
            'security': 0.10,
            'spec_coverage': 0.10,
        }
        fitness.overall = round(sum(
            getattr(fitness, k, 0) * w for k, w in weights.items()
        ), 4)

        return fitness

    def _classify_species(self, genome: SoftwareGenome) -> str:
        """Classify genome into an architectural species based on traits.

        Species categories:
          - microservice: high chromosome count, low coupling, many interfaces
          - monolith: low chromosome count, high coupling, few interfaces
          - framework: many abstract genes, protocols
          - library: high gene count, low chromosome count, few protocols
          - data_pipeline: high event/command count
          - api_gateway: high protocol count, many interfaces
          - unknown
        """
        traits = genome.traits
        gene_count = traits.get('gene_count', 0)
        chrom_count = traits.get('chromosome_count', 0)
        protocol_richness = traits.get('protocol_richness', 0)
        dep_density = traits.get('dependency_density', 0)

        interfaces = traits.get('gene_type_interface_gene', 0) + traits.get('gene_type_protocol', 0)
        events = traits.get('gene_type_event', 0)
        commands = traits.get('gene_type_command', 0)

        if chrom_count >= 20 and dep_density < 2 and interfaces >= 5:
            return "microservice"
        elif chrom_count < 10 and dep_density > 3:
            return "monolith"
        elif protocol_richness > 0.2 or interfaces >= 10:
            return "framework"
        elif gene_count > 50 and chrom_count < 10 and interfaces < 3:
            return "library"
        elif events + commands > 10:
            return "data_pipeline"
        elif interfaces >= 5 and protocol_richness > 0.1:
            return "api_gateway"
        return "unknown"
