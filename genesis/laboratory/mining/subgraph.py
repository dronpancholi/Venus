"""
Universal Pattern Mining (Program D) — discover patterns at scale.

Subsystems:
  - FrequentSubgraphMiner: discover frequent architectural subgraphs
  - MotifDetector: detect recurring architectural motifs
  - PatternCluster: cluster similar patterns
  - PatternEvolutionTracker: track pattern evolution over time
"""

from __future__ import annotations

import math
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Any

from genesis.laboratory.genome.model import SoftwareGenome, GenomeGene


# ── Data Model ──


@dataclass
class MinedPattern:
    """A discovered architectural pattern."""
    id: str = ""
    name: str = ""
    pattern_type: str = ""  # subgraph, motif, architectural, dependency
    structure: dict[str, Any] = field(default_factory=dict)
    genes: list[str] = field(default_factory=list)
    repositories: list[str] = field(default_factory=list)
    frequency: int = 0
    confidence: float = 0.0
    entropy: float = 0.0
    canonical_form: str = ""


@dataclass
class ArchitecturalMotif:
    """A recurring architectural motif (small recurring pattern)."""
    id: str = ""
    name: str = ""
    genes: list[str] = field(default_factory=list)
    gene_types: list[str] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)
    repository_count: int = 0
    frequency: int = 0
    significance: float = 0.0


@dataclass
class PatternCluster:
    """A cluster of similar patterns."""
    id: str = ""
    patterns: list[str] = field(default_factory=list)
    centroid: str = ""
    size: int = 0
    cohesion: float = 0.0
    representative: str = ""


# ── Frequent Subgraph Miner ──


class FrequentSubgraphMiner:
    """Mine frequent subgraph patterns across genome gene dependency graphs."""

    MIN_SUPPORT = 2  # minimum genomes a pattern must appear in

    def mine(self, genomes: list[SoftwareGenome], min_support: int = 2) -> list[MinedPattern]:
        """Discover frequent patterns across genomes."""
        patterns: list[MinedPattern] = []
        support_count: dict[str, set[str]] = defaultdict(set)  # pattern_key → set of genome_ids

        # — Build gene-type bigram patterns —
        for genome in genomes:
            genes = genome.all_genes
            # For each gene, look at its type paired with dependency types
            for gene in genes:
                for dep_id in gene.dependencies:
                    dep_gene = self._find_gene(genome, dep_id)
                    if dep_gene:
                        key = f"{gene.gene_type.name.lower()}->{dep_gene.gene_type.name.lower()}"
                        support_count[key].add(genome.id)

        # — Convert to patterns —
        for key, genome_ids in support_count.items():
            if len(genome_ids) >= min_support:
                types = key.split("->")
                patterns.append(MinedPattern(
                    id=f"subgraph_{len(patterns)}",
                    name=key,
                    pattern_type="dependency_edge_type",
                    structure={"source_type": types[0], "target_type": types[1]},
                    repositories=sorted(genome_ids),
                    frequency=len(genome_ids),
                    confidence=round(len(genome_ids) / max(len(genomes), 1), 4),
                ))

        # — Mine gene co-occurrence patterns —
        cooccurrence: dict[tuple[str, str], set[str]] = defaultdict(set)
        for genome in genomes:
            genes = genome.all_genes
            # Group by chromosome then look at gene type co-occurrences
            for chrom in genome.chromosomes.values():
                gene_types = [g.gene_type.name.lower() for g in chrom.genes.values()]
                for i, t1 in enumerate(gene_types):
                    for j, t2 in enumerate(gene_types):
                        if i < j:
                            key = tuple(sorted([t1, t2]))
                            cooccurrence[key].add(genome.id)

        for (t1, t2), genome_ids in sorted(cooccurrence.items(), key=lambda x: -len(x[1])):
            if len(genome_ids) >= min_support:
                patterns.append(MinedPattern(
                    id=f"subgraph_co_{len(patterns)}",
                    name=f"{t1}+{t2}",
                    pattern_type="gene_cooccurrence",
                    structure={"type_a": t1, "type_b": t2},
                    repositories=sorted(genome_ids),
                    frequency=len(genome_ids),
                    confidence=round(len(genome_ids) / max(len(genomes), 1), 4),
                ))

        return sorted(patterns, key=lambda p: -p.frequency)

    def _find_gene(self, genome: SoftwareGenome, gene_id: str) -> GenomeGene | None:
        for chrom in genome.chromosomes.values():
            if gene_id in chrom.genes:
                return chrom.genes[gene_id]
        return None


# ── Motif Detector ──


class MotifDetector:
    """Detect recurring architectural motifs."""

    MOTIF_TEMPLATES: list[tuple[str, list[str], float]] = [
        ("factory_protocol", ["class", "protocol", "function"], 0.7),
        ("interface_implementation", ["interface", "class", "method"], 0.8),
        ("event_handler", ["event", "function", "method"], 0.7),
        ("repository_pattern", ["class", "method", "function"], 0.6),
        ("controller_service", ["class", "class", "function"], 0.6),
    ]

    def detect(self, genome: SoftwareGenome) -> list[ArchitecturalMotif]:
        """Detect motifs in a single genome."""
        motifs: list[ArchitecturalMotif] = []

        for chrom in genome.chromosomes.values():
            gene_types = [g.gene_type.name.lower() for g in chrom.genes.values()]
            gene_names = [g.name for g in chrom.genes.values()]
            gene_list = list(chrom.genes.values())

            # — Check motif templates —
            for motif_name, type_pattern, significance in self.MOTIF_TEMPLATES:
                # Try to find the pattern as a subsequence
                if self._is_subsequence(type_pattern, gene_types):
                    motif_genes = []
                    for t in type_pattern:
                        for g in gene_list:
                            if g.gene_type.name.lower() == t and g.name not in motif_genes:
                                motif_genes.append(g.name)
                                break

                    if motif_genes:
                        motif_id = f"motif_{len(motifs)}"
                        motifs.append(ArchitecturalMotif(
                            id=motif_id,
                            name=motif_name,
                            genes=motif_genes,
                            gene_types=type_pattern,
                            edges=[(motif_genes[i], motif_genes[i + 1])
                                   for i in range(len(motif_genes) - 1)],
                            frequency=1,
                            significance=significance,
                        ))

            # — Detect star motifs (hub with many connections) —
            for gene in gene_list:
                if len(gene.dependencies) >= 3:
                    hub_motif = ArchitecturalMotif(
                        id=f"motif_hub_{len(motifs)}",
                        name="hub_and_spoke",
                        genes=[gene.name] + [f"dep_{i}" for i in gene.dependencies[:3]],
                        gene_types=[gene.gene_type.name.lower()] + ["class"] * min(len(gene.dependencies), 3),
                        frequency=1,
                        significance=min(len(gene.dependencies) / 10, 0.9),
                    )
                    motifs.append(hub_motif)

        return motifs

    def _is_subsequence(self, pattern: list[str], sequence: list[str]) -> bool:
        """Check if pattern is a subsequence of sequence."""
        it = iter(sequence)
        return all(p in it for p in pattern)

    def cross_repo_motifs(self, genomes: list[SoftwareGenome],
                           min_repos: int = 2) -> list[ArchitecturalMotif]:
        """Detect motifs that appear across multiple repositories."""
        motif_counts: dict[str, set[str]] = defaultdict(set)  # motif_name → repo set
        all_motifs: dict[str, list[ArchitecturalMotif]] = defaultdict(list)

        for genome in genomes:
            motifs = self.detect(genome)
            for m in motifs:
                motif_counts[m.name].add(genome.id)
                all_motifs[m.name].append(m)

        cross_motifs = []
        for name, repo_ids in motif_counts.items():
            if len(repo_ids) >= min_repos:
                combined = all_motifs[name]
                avg_significance = sum(m.significance for m in combined) / len(combined)
                cross_motifs.append(ArchitecturalMotif(
                    id=f"cross_motif_{name}",
                    name=name,
                    repository_count=len(repo_ids),
                    frequency=len(combined),
                    significance=round(avg_significance, 4),
                ))

        return sorted(cross_motifs, key=lambda m: -m.repository_count)


# ── Pattern Cluster ──


class PatternCluster:
    """Cluster similar patterns across repositories."""

    def cluster_patterns(self, patterns: list[MinedPattern],
                          threshold: float = 0.5) -> list[PatternCluster]:
        """Cluster patterns by type and structure similarity."""
        if not patterns:
            return []

        clusters: list[PatternCluster] = []
        assigned: set[str] = set()
        cluster_id = 0

        for i, p in enumerate(patterns):
            if p.id in assigned:
                continue

            cluster_group = [p]
            assigned.add(p.id)

            for j, q in enumerate(patterns):
                if q.id in assigned:
                    continue
                sim = self._pattern_similarity(p, q)
                if sim >= threshold:
                    cluster_group.append(q)
                    assigned.add(q.id)

            if cluster_group:
                clusters.append(PatternCluster(
                    id=f"cluster_{cluster_id}",
                    patterns=[cp.id for cp in cluster_group],
                    centroid=cluster_group[0].id,
                    size=len(cluster_group),
                    cohesion=round(sum(
                        self._pattern_similarity(cluster_group[0], cp)
                        for cp in cluster_group
                    ) / len(cluster_group), 4),
                    representative=cluster_group[0].name,
                ))
                cluster_id += 1

        return sorted(clusters, key=lambda c: -c.size)

    def _pattern_similarity(self, a: MinedPattern, b: MinedPattern) -> float:
        score = 0.0
        if a.pattern_type == b.pattern_type:
            score += 0.4
        if a.structure.get("source_type") == b.structure.get("source_type"):
            score += 0.3
        if a.structure.get("target_type") == b.structure.get("target_type"):
            score += 0.3
        if a.structure.get("type_a") == b.structure.get("type_a"):
            score += 0.2
        if a.structure.get("type_b") == b.structure.get("type_b"):
            score += 0.2
        return min(score, 1.0)


# ── Pattern Evolution Tracker ──


@dataclass
class PatternEvolution:
    pattern_name: str
    first_seen: float = 0.0
    last_seen: float = 0.0
    frequency_history: list[tuple[float, int]] = field(default_factory=list)
    repo_history: list[tuple[float, str]] = field(default_factory=list)
    trend: str = "stable"  # growing, shrinking, stable


class PatternEvolutionTracker:
    """Track how patterns evolve across repository versions."""

    def track(self, patterns: list[MinedPattern]) -> list[PatternEvolution]:
        """Analyze pattern evolution from mined patterns."""
        evolution_map: dict[str, PatternEvolution] = {}

        for p in patterns:
            if p.name not in evolution_map:
                evolution_map[p.name] = PatternEvolution(pattern_name=p.name)
            pe = evolution_map[p.name]
            pe.frequency_history.append((0.0, p.frequency))
            pe.repo_history.append((0.0, str(p.repositories[:3])))

        for pe in evolution_map.values():
            if len(pe.frequency_history) >= 2:
                freqs = [f for _, f in pe.frequency_history]
                if freqs[-1] > freqs[0] * 1.2:
                    pe.trend = "growing"
                elif freqs[-1] < freqs[0] * 0.8:
                    pe.trend = "shrinking"
                else:
                    pe.trend = "stable"

        return list(evolution_map.values())
