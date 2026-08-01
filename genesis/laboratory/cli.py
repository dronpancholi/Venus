"""
Laboratory CLI — commands for the Engineering Intelligence Laboratory.

Commands:
  lab analyze <path>    — Run full knowledge extraction on a repo
  lab genome <path>     — Build genome for a repo
  lab compare <a> <b>   — Compare two genomes
  lab mine              — Mine patterns across observed repos
  lab schedule          — Show scheduler status
  lab run               — Run scheduled ingestion
  lab experiment         — Show experiment history
  lab world             — Show world graph status
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from genesis.laboratory.extraction.pipeline import ExtractionPipeline
from genesis.laboratory.genome.builder import GenomeBuilder
from genesis.laboratory.genome.comparison import GenomeComparator
from genesis.laboratory.genome.model import SoftwareGenome, FitnessScore
from genesis.laboratory.mining.subgraph import (
    FrequentSubgraphMiner, MotifDetector, PatternCluster as PatternClustering,
)
from genesis.laboratory.scheduler import RepositoryScheduler
from genesis.laboratory.world_graph import WorldGraph
from genesis.laboratory.experiment import ExperimentPlatform, ExperimentDesign


def register_subcommands(subparsers):
    """Register laboratory subcommands."""
    lab = subparsers.add_parser("lab", help="Engineering Intelligence Laboratory")
    lab_sub = lab.add_subparsers(dest="lab_command")

    # — lab analyze —
    analyze = lab_sub.add_parser("analyze", help="Extract knowledge from a repository")
    analyze.add_argument("path", help="Repository path")

    # — lab genome —
    genome_cmd = lab_sub.add_parser("genome", help="Build software genome for a repository")
    genome_cmd.add_argument("path", help="Repository path")

    # — lab compare —
    compare = lab_sub.add_parser("compare", help="Compare two genomes")
    compare.add_argument("path_a", help="First repository path")
    compare.add_argument("path_b", help="Second repository path")

    # — lab mine —
    mine = lab_sub.add_parser("mine", help="Mine patterns across observed repositories")
    mine.add_argument("--min-support", type=int, default=2, help="Minimum repository support")
    mine.add_argument("--motifs", action="store_true", help="Detect architectural motifs")
    mine.add_argument("--patterns", action="store_true", help="Show mined patterns")

    # — lab schedule —
    lab_sub.add_parser("schedule", help="Show repository scheduler status")

    # — lab run —
    run = lab_sub.add_parser("run", help="Run scheduled ingestion")
    run.add_argument("--max", type=int, default=5, help="Max repos to ingest")
    run.add_argument("--continuous", action="store_true", help="Run continuously")
    run.add_argument("--iterations", type=int, default=1, help="Number of rounds")

    # — lab world —
    world = lab_sub.add_parser("world", help="World Engineering Graph status")
    world.add_argument("--graph", help="Graph type filter")
    world.add_argument("--node-type", help="Node type filter")

    # — lab experiment —
    lab_sub.add_parser("experiment", help="Show experiment history")

    return lab


def run_lab(args: argparse.Namespace) -> int:
    """Execute a laboratory subcommand."""
    cmd = args.lab_command

    if cmd == "analyze":
        return _analyze(args)
    elif cmd == "genome":
        return _genome(args)
    elif cmd == "compare":
        return _compare(args)
    elif cmd == "mine":
        return _mine(args)
    elif cmd == "schedule":
        return _schedule(args)
    elif cmd == "run":
        return _run_schedule(args)
    elif cmd == "world":
        return _world(args)
    elif cmd == "experiment":
        return _experiment(args)
    else:
        print(f"Unknown lab command: {cmd}")
        return 1


def _analyze(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Path not found: {path}")
        return 1

    print(f"Analyzing {path}...")
    pipeline = ExtractionPipeline()
    result = pipeline.extract(path, repo_id=f"local::{path.name}")

    print(f"\nKnowledge Extraction Results:")
    print(f"  Total knowledge pieces: {result.total}")
    print(f"  Architecture patterns:  {len(result.patterns)}")
    for p in result.patterns[:10]:
        print(f"    {p.pattern_type:12s} {p.name:30s} (prevalence: {p.prevalence:.2f})")
    print(f"  Protocols/APIs:         {len(result.protocols)}")
    for p in result.protocols[:10]:
        print(f"    {p['kind']:25s} {p['name']}")
    print(f"  Dependencies:           {len(result.dependencies)}")
    print(f"  Database schemas:       {len(result.database_schemas)}")
    for s in result.database_schemas[:5]:
        print(f"    model={s.get('model', '?')} table={s.get('table', '?')} cols={len(s.get('columns', []))}")
    print(f"  Security policies:      {len(result.security_policies)}")
    for s in result.security_policies[:5]:
        print(f"    {s['category']:25s} count={s['evidence_count']}")
    print(f"  CI/CD pipelines:        {len(result.ci_cd_pipelines)}")

    return 0


def _genome(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Path not found: {path}")
        return 1

    print(f"Building genome for {path}...")

    # Compile via USIR
    from genesis.usir.compiler import MultiLanguageCompiler
    compiler = MultiLanguageCompiler()
    usir = compiler.compile(path)

    builder = GenomeBuilder()
    genome = builder.build_from_usir(
        usir, repo_id=f"local::{path.name}",
        repo_name=path.name,
    )

    print(f"\nSoftware Genome: {genome.repository_name}")
    print(f"  Species:       {genome.species}")
    print(f"  Chromosomes:   {genome.chromosome_count}")
    print(f"  Genes:         {genome.gene_count}")
    print(f"  Dependencies:  {genome.total_dependencies}")
    print(f"  Conserved:     {len(genome.conserved_genes)}")

    print(f"\n  Fitness:")
    for k, v in genome.fitness.to_dict().items():
        print(f"    {k:20s} {v:.4f}")

    print(f"\n  Dominant Traits:")
    for name, val in genome.dominant_traits[:10]:
        print(f"    {name:30s} {val:.4f}")

    print(f"\n  Chromosomes:")
    for cid, chrom in genome.chromosomes.items():
        print(f"    {chrom.name:35s} genes={chrom.gene_count} files={chrom.file_path}")

    return 0


def _compare(args: argparse.Namespace) -> int:
    path_a = Path(args.path_a).resolve()
    path_b = Path(args.path_b).resolve()

    from genesis.usir.compiler import MultiLanguageCompiler
    compiler = MultiLanguageCompiler()

    print(f"Building genomes...")
    usir_a = compiler.compile(path_a)
    usir_b = compiler.compile(path_b)

    builder = GenomeBuilder()
    genome_a = builder.build_from_usir(usir_a, repo_id="a", repo_name=path_a.name)
    genome_b = builder.build_from_usir(usir_b, repo_id="b", repo_name=path_b.name)

    comparator = GenomeComparator()
    similarity = comparator.genome_similarity(genome_a, genome_b)

    print(f"\nGenome Comparison:")
    print(f"  {path_a.name:30s} vs {path_b.name}:")
    print(f"  Overall Similarity:     {similarity:.4f}")

    if similarity > 0.7:
        print(f"  Verdict: HIGHLY SIMILAR — likely same species")
    elif similarity > 0.4:
        print(f"  Verdict: MODERATELY SIMILAR — related architectures")
    else:
        print(f"  Verdict: DISTINCT — different architectural species")

    print(f"\n  Trait Correlation: {comparator._trait_correlation(genome_a.traits, genome_b.traits):.4f}")
    print(f"  Composition Similarity: {comparator._composition_similarity(genome_a, genome_b):.4f}")

    # Find orthologs
    orthologs = comparator.find_orthologs(genome_a, [genome_b], threshold=0.5)
    if orthologs:
        print(f"\n  Conserved Genes (orthologs): {len(orthologs)}")
        for gid, matches in list(orthologs.items())[:10]:
            ag = next((g for g in genome_a.all_genes if g.id == gid), None)
            if ag:
                print(f"    {ag.name:25s} → {matches[0][1]} (sim={matches[0][2]:.2f})")

    return 0


def _mine(args: argparse.Namespace) -> int:
    from genesis.observatory.miner import RepositoryMiner
    from genesis.usir.compiler import MultiLanguageCompiler
    import tempfile

    miner = RepositoryMiner()
    compiler = MultiLanguageCompiler()

    repos = miner.registry.list_repos(status="ready")[:20]
    if not repos:
        print("No ingested repos found. Run 'venus ... observe ingest' first.")
        print("Falling back to analyzing current repo...")

        # Analyze current repo
        root = Path.cwd()
        usir = compiler.compile(root)
        builder = GenomeBuilder()
        genome = builder.build_from_usir(usir, repo_id="local::venus", repo_name="venus")

        miner.registry.register("local::venus", source="local")
        genomes = [genome]
    else:
        genomes = []
        for r in repos:
            try:
                path = Path(r.clone_path) if r.clone_path else Path.cwd()
                usir = compiler.compile(path)
                builder = GenomeBuilder()
                genome = builder.build_from_usir(usir, repo_id=r.id, repo_name=r.name)
                genomes.append(genome)
            except Exception:
                continue

    print(f"Mining patterns across {len(genomes)} genomes...")

    # Frequent subgraph mining
    miner_pm = FrequentSubgraphMiner()
    patterns = miner_pm.mine(genomes, min_support=args.min_support)

    print(f"\nFrequent Patterns: {len(patterns)}")
    for p in patterns[:15]:
        print(f"  [freq={p.frequency}] {p.name:30s} ({p.pattern_type})")

    if args.motifs or not args.patterns:
        detector = MotifDetector()
        cross_motifs = detector.cross_repo_motifs(genomes, min_repos=args.min_support)
        print(f"\nCross-Repository Motifs: {len(cross_motifs)}")
        for m in cross_motifs[:10]:
            print(f"  [repos={m.repository_count}] {m.name:30s} (sig={m.significance:.3f})")

    if args.patterns:
        clusterer = PatternClustering()
        clusters = clusterer.cluster_patterns(patterns)
        print(f"\nPattern Clusters: {len(clusters)}")
        for c in clusters[:10]:
            print(f"  [size={c.size}] {c.representative:30s} cohesion={c.cohesion:.3f}")

    return 0


def _schedule(args: argparse.Namespace) -> int:
    scheduler = RepositoryScheduler()
    s = scheduler.summary()
    print(f"Repository Scheduler:")
    for k, v in s.items():
        print(f"  {k}: {v}")

    print(f"\nPending tasks:")
    pending = scheduler.pending_tasks()
    for t in pending[:10]:
        print(f"  {t.repo_id:50s} priority={t.priority} last={t.last_ingested:.0f}")

    if not pending:
        print(f"  (none — register repos or add trending)")

    return 0


def _run_schedule(args: argparse.Namespace) -> int:
    scheduler = RepositoryScheduler()

    if args.continuous:
        print(f"Running continuous ingestion ({args.iterations} rounds)...")
        scheduler.run_continuous(iterations=args.iterations)
    else:
        print(f"Running scheduled ingestion (max {args.max})...")
        results = scheduler.run_scheduled(max_repos=args.max)
        success = sum(1 for r in results if r.success)
        print(f"  {success}/{len(results)} succeeded")
        for r in results:
            status = "✓" if r.success else "✗"
            print(f"  {status} {r.repo_id} ({r.duration:.2f}s) {r.error}")

    return 0


def _world(args: argparse.Namespace) -> int:
    world = WorldGraph()
    world.load()
    s = world.summary()

    print(f"World Engineering Graph:")
    print(f"  Total nodes: {s['total_nodes']:,}")
    print(f"  Total edges: {s['total_edges']:,}")

    print(f"\n  By Graph Type:")
    for gt, count in sorted(s['graph_types'].items(), key=lambda x: -x[1]):
        print(f"    {gt:20s} {count}")

    if args.graph:
        nodes = world.find_by_type(args.graph, args.node_type or "")
        print(f"\n  Nodes in {args.graph}: {len(nodes)}")
        for n in nodes[:20]:
            print(f"    {n.id:40s} {n.label:30s} {n.node_type}")

    return 0


def _experiment(args: argparse.Namespace) -> int:
    platform = ExperimentPlatform()
    s = platform.history.summary()
    print(f"Experiment Platform:")
    print(f"  Total experiments:    {s['total']}")
    print(f"  Accepted:             {s['accepted']}")
    print(f"  Rejected:             {s['rejected']}")
    print(f"  Acceptance rate:      {s['acceptance_rate']:.2%}")
    print(f"  Avg effect size:      {s['avg_effect_size']:.4f}")

    if platform.history.experiments:
        print(f"\n  Recent experiments:")
        for e in platform.history.experiments[-5:]:
            status = "✓" if e.accepted else "✗"
            print(f"    {status} {e.hypothesis[:60]:60s} p={e.p_value:.4f} d={e.effect_size:.4f}")

    return 0
