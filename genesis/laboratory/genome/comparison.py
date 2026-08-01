"""
Genome Comparator — cross-repository genome comparison.

Supports:
  - Gene-level similarity (name, type, structure)
  - Chromosome-level similarity (gene composition, cohesion)
  - Genome-level similarity (traits, fitness, species)
  - Ortholog detection (same gene across genomes)
  - Evolutionary distance computation
  - Phylogenetic tree construction
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from genesis.laboratory.genome.model import SoftwareGenome, GenomeGene


class GenomeComparator:
    """Compare software genomes across repositories."""

    # — Gene similarity —

    def gene_similarity(self, a: GenomeGene, b: GenomeGene) -> float:
        """Compute similarity between two genes (0.0 - 1.0)."""
        score = 0.0

        # Name exact match
        if a.name == b.name:
            score += 0.5
        elif a.name.lower() == b.name.lower():
            score += 0.3
        # Name partial match (common prefix)
        elif a.name[:4].lower() == b.name[:4].lower():
            score += 0.1

        # Same type
        if a.gene_type == b.gene_type:
            score += 0.2

        # Similar complexity
        if a.complexity > 0 and b.complexity > 0:
            ratio = min(a.complexity, b.complexity) / max(a.complexity, b.complexity)
            if ratio > 0.8:
                score += 0.1

        return min(score, 1.0)

    def find_orthologs(self, genome: SoftwareGenome,
                       others: list[SoftwareGenome],
                       threshold: float = 0.7) -> dict[str, list[tuple[str, str, float]]]:
        """Find orthologs: genes that are the same across different genomes.

        Returns: {gene_id: [(other_genome_id, other_gene_id, similarity), ...]}
        """
        orthologs: dict[str, list[tuple[str, str, float]]] = {}

        for gene in genome.all_genes:
            matches = []
            for other in others:
                for og in other.all_genes:
                    sim = self.gene_similarity(gene, og)
                    if sim >= threshold:
                        matches.append((other.id, og.id, sim))

                        # Mark both as conserved
                        gene.conserved = True
                        og.conserved = True
                        gene.orthologs.append(og.id)
                        og.orthologs.append(gene.id)

            if matches:
                orthologs[gene.id] = sorted(matches, key=lambda x: -x[2])

        return orthologs

    # — Genome similarity —

    def genome_similarity(self, a: SoftwareGenome, b: SoftwareGenome) -> float:
        """Overall similarity between two genomes (0.0 - 1.0)."""
        score = 0.0

        # Same language
        if a.language == b.language:
            score += 0.15

        # Same species
        if a.species == b.species:
            score += 0.15

        # Trait correlation
        trait_score = self._trait_correlation(a.traits, b.traits)
        score += trait_score * 0.3

        # Gene composition similarity
        comp_score = self._composition_similarity(a, b)
        score += comp_score * 0.2

        # Chromosome count similarity
        ratio = min(a.chromosome_count, b.chromosome_count) / max(a.chromosome_count, b.chromosome_count, 1)
        score += ratio * 0.1

        # Fitness similarity
        fitness_diff = abs(a.fitness.overall - b.fitness.overall)
        score += (1.0 - min(fitness_diff, 1.0)) * 0.1

        return min(score, 1.0)

    def _trait_correlation(self, ta: dict[str, float], tb: dict[str, float]) -> float:
        all_keys = set(ta.keys()) & set(tb.keys())
        if not all_keys:
            return 0.0

        diffs = []
        for k in all_keys:
            va = ta.get(k, 0)
            vb = tb.get(k, 0)
            diffs.append(abs(va - vb))

        avg_diff = sum(diffs) / len(diffs)
        return 1.0 - min(avg_diff, 1.0)

    def _composition_similarity(self, a: SoftwareGenome, b: SoftwareGenome) -> float:
        """Compare gene type distribution."""
        type_counts_a: dict[str, int] = defaultdict(int)
        type_counts_b: dict[str, int] = defaultdict(int)

        for g in a.all_genes:
            type_counts_a[g.gene_type.name.lower()] += 1
        for g in b.all_genes:
            type_counts_b[g.gene_type.name.lower()] += 1

        all_types = set(type_counts_a.keys()) | set(type_counts_b.keys())
        if not all_types:
            return 0.0

        total_a = sum(type_counts_a.values()) or 1
        total_b = sum(type_counts_b.values()) or 1

        diffs = []
        for t in all_types:
            pa = type_counts_a.get(t, 0) / total_a
            pb = type_counts_b.get(t, 0) / total_b
            diffs.append(abs(pa - pb))

        avg_diff = sum(diffs) / len(diffs)
        return 1.0 - min(avg_diff, 1.0)

    # — Distance matrix —

    def build_distance_matrix(self, genomes: list[SoftwareGenome]) -> dict[str, dict[str, float]]:
        """Build pairwise distance matrix: {genome_id: {other_id: distance}}."""
        matrix: dict[str, dict[str, float]] = {}

        for a in genomes:
            matrix[a.id] = {}
            for b in genomes:
                if a.id == b.id:
                    matrix[a.id][b.id] = 0.0
                else:
                    sim = self.genome_similarity(a, b)
                    matrix[a.id][b.id] = 1.0 - sim

        return matrix

    # — Phylogenetic tree (UPGMA) —

    def build_phylogenetic_tree(self, genomes: list[SoftwareGenome]) -> dict[str, Any]:
        """Build a simple phylogenetic tree from genome similarities.

        Returns a nested dict: {genome_id: children, distance, label}
        """
        matrix = self.build_distance_matrix(genomes)
        clusters = {g.id: {"label": g.repository_name, "children": [], "distance": 0.0}
                    for g in genomes}

        remaining = list(clusters.keys())

        while len(remaining) > 1:
            # Find closest pair
            min_dist = float('inf')
            min_pair = (None, None)

            for i in range(len(remaining)):
                for j in range(i + 1, len(remaining)):
                    a, b = remaining[i], remaining[j]
                    d = matrix.get(a, {}).get(b, 1.0)
                    if d < min_dist:
                        min_dist = d
                        min_pair = (a, b)

            if min_pair[0] is None:
                break

            a, b = min_pair
            new_id = f"cluster_{a}_{b}"

            clusters[new_id] = {
                "label": f"{clusters[a]['label']} + {clusters[b]['label']}",
                "children": [a, b],
                "distance": min_dist,
            }

            # Update distance matrix
            matrix[new_id] = {}
            for k in remaining:
                if k not in (a, b):
                    d = (matrix.get(a, {}).get(k, 1.0) + matrix.get(b, {}).get(k, 1.0)) / 2
                    matrix[new_id][k] = d
                    matrix[k][new_id] = d
            matrix[new_id][new_id] = 0.0

            remaining.remove(a)
            remaining.remove(b)
            remaining.append(new_id)

        root = remaining[0] if remaining else None
        return clusters.get(root, {"label": "root", "children": list(clusters.keys()), "distance": 0.0})

    # — Conserved pattern extraction —

    def extract_conserved_patterns(self, genomes: list[SoftwareGenome],
                                    threshold: float = 0.7) -> list[dict[str, Any]]:
        """Extract gene patterns that are conserved across multiple genomes."""
        # Build inverted index: (gene_name, gene_type) → list of genome_ids
        pattern_map: dict[tuple[str, str], set[str]] = defaultdict(set)

        for g in genomes:
            for gene in g.all_genes:
                key = (gene.name, gene.gene_type.name.lower())
                pattern_map[key].add(g.id)

        patterns = []
        for (name, gtype), genome_ids in sorted(pattern_map.items(), key=lambda x: -len(x[1])):
            if len(genome_ids) >= 2:
                patterns.append({
                    "name": name,
                    "type": gtype,
                    "genome_count": len(genome_ids),
                    "genomes": sorted(genome_ids),
                    "conservation_ratio": round(len(genome_ids) / max(len(genomes), 1), 4),
                })

        return patterns
