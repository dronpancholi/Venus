"""
Observatory CLI — observe, ingest, status, graph commands.

Integrates into the VRIP CLI as subcommands.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

from genesis.observatory import RepositoryMiner, RepositoryRegistry, ObservatoryGraph
from genesis.usir.compiler import MultiLanguageCompiler


def register_subcommands(subparsers):
    """Register observatory subcommands."""
    obs = subparsers.add_parser("observe", help="Global Repository Observatory commands")
    obs_sub = obs.add_subparsers(dest="observe_command")

    # — observe ingest —
    ingest = obs_sub.add_parser("ingest", help="Ingest a repository")
    ingest.add_argument("path", nargs="?", help="Local path or owner/repo for GitHub")
    ingest.add_argument("--github", action="store_true", help="Ingest from GitHub")
    ingest.add_argument("--local", action="store_true", help="Ingest from local path")
    ingest.add_argument("--trending", type=int, nargs="?", const=5,
                        help="Ingest trending GitHub repos (optional: count)")

    # — observe status —
    status = obs_sub.add_parser("status", help="Show observatory status")
    status.add_argument("repo_id", nargs="?", help="Specific repo ID to inspect")
    status.add_argument("--summary", action="store_true", help="Show summary only")

    # — observe graph —
    graph_cmd = obs_sub.add_parser("graph", help="View the observatory graph")
    graph_cmd.add_argument("--summary", action="store_true", help="Graph summary")
    graph_cmd.add_argument("--patterns", action="store_true", help="Show cross-repo patterns")
    graph_cmd.add_argument("--repo", help="Filter by repo ID")
    graph_cmd.add_argument("--kind", help="Filter by node kind")
    graph_cmd.add_argument("--language", help="Filter by language")

    # — observe list —
    list_cmd = obs_sub.add_parser("list", help="List all repositories")
    list_cmd.add_argument("--status", help="Filter by status (ready/pending/failed)")
    list_cmd.add_argument("--source", help="Filter by source (github/local/postgres)")

    # — observe analyze —
    analyze = obs_sub.add_parser("analyze", help="Re-analyze repositories")
    analyze.add_argument("repo_id", nargs="?", help="Specific repo ID to analyze")
    analyze.add_argument("--all", action="store_true", help="Re-analyze all repos")

    return obs


def run_observe(args: argparse.Namespace) -> int:
    """Execute an observe subcommand."""
    miner = RepositoryMiner()
    registry = miner.registry
    graph = ObservatoryGraph()

    cmd = args.observe_command

    if cmd == "ingest":
        return _ingest(miner, args)
    elif cmd == "status":
        return _status(registry, args)
    elif cmd == "graph":
        return _graph_cmd(graph, registry, miner, args)
    elif cmd == "list":
        return _list_repos(registry, args)
    elif cmd == "analyze":
        return _analyze(miner, args)
    else:
        print(f"Unknown command: {cmd}")
        return 1


def _ingest(miner: RepositoryMiner, args: argparse.Namespace) -> int:
    if args.trending:
        print(f"🌍 Ingesting {args.trending} trending repositories...")
        ingested = miner.ingest_github_trending(args.trending)
        for rid in ingested:
            r = miner.registry.get(rid)
            status_char = "✓" if r and r.status == "ready" else "✗"
            lang = r.language if r else "?"
            print(f"  {status_char} {rid} ({lang}, {r.file_count if r else 0} files)")
        print(f"Ingested {len(ingested)} repos")
        return 0

    if args.github:
        if not args.path or "/" not in args.path:
            print("Error: --github requires owner/repo format")
            return 1
        parts = args.path.split("/")
        owner, repo = parts[-2], parts[-1]
        rid = miner.ingest_github(owner, repo)
        r = miner.registry.get(rid)
        if r and r.status == "ready":
            print(f"✓ {rid} — {r.language}, {r.file_count} files, {r.line_count} lines")
        else:
            print(f"✗ {rid} — failed")
        return 0

    if args.local or args.path:
        path = args.path or "."
        rid = miner.ingest_local(path)
        r = miner.registry.get(rid)
        if r and r.status == "ready":
            print(f"✓ {rid} — {r.language}, {r.file_count} files, {r.line_count} lines")
        else:
            print(f"✗ {rid} — failed")
        return 0

    print("Specify --github owner/repo, --local path, or --trending")
    return 1


def _status(registry: RepositoryRegistry, args: argparse.Namespace) -> int:
    if args.repo_id:
        record = registry.get(args.repo_id)
        if not record:
            print(f"Repository not found: {args.repo_id}")
            return 1
        print(f"Repository: {record.name}")
        print(f"  ID:       {record.id}")
        print(f"  Source:   {record.source}")
        print(f"  URL:      {record.url or '(local)'}")
        print(f"  Status:   {record.status}")
        print(f"  Language: {record.language}")
        print(f"  Files:    {record.file_count}")
        print(f"  Lines:    {record.line_count}")
        print(f"  USIR:     {record.usir_node_count} nodes, {record.usir_edge_count} edges")
        print(f"  Commit:   {record.last_commit or '(unknown)'}")
        print(f"  Analyzed: {record.last_analyzed}")
        log = registry.get_log(record.id)
        if log:
            print(f"  Log:")
            for entry in log[:5]:
                print(f"    {entry['action']} — {entry.get('details', '')[:80]}")
        return 0

    s = registry.summary()
    print(f"Repository Observatory  ({Path(registry.db_path).parent})")
    print(f"  Total:     {s['total_repos']}")
    print(f"  Ready:     {s['ready']}")
    print(f"  Pending:   {s['pending']}")
    print(f"  Failed:    {s['failed']}")
    print(f"  Files:     {s['total_files']}")
    print(f"  Lines:     {s['total_lines']}")
    print(f"  USIR:      {s['total_usir_nodes']} nodes")

    if args.summary:
        return 0

    repos = registry.list_repos(limit=20)
    if repos:
        print(f"\n  Recent:")
        for r in repos:
            print(f"    {r.status:8s} {r.name:40s} {r.language:12s} {r.file_count:5d} files")
    return 0


def _graph_cmd(graph: ObservatoryGraph, registry: RepositoryRegistry,
               miner: RepositoryMiner, args: argparse.Namespace) -> int:
    # — load the graph from disk —
    graph.load()

    if args.summary or not any([args.patterns, args.repo, args.kind, args.language]):
        s = graph.summary()
        print(f"Observatory Graph")
        print(f"  Repos:     {s['repositories']}")
        print(f"  Nodes:     {s['nodes']}")
        print(f"  Edges:     {s['edges']}")
        print(f"  Cross-repo: {s['cross_repo_edges']}")
        print(f"  Languages: {s['languages']}")
        print(f"  Patterns:  {s['patterns_available']}")
        return 0

    if args.patterns:
        patterns = graph.common_patterns()
        print(f"Common Cross-Repository Patterns ({patterns['total']}):")
        for p in patterns['patterns'][:20]:
            print(f"  {p['name']:30s} ({p['kind']:12s}) in {p['repos']} repos: {', '.join(p['repo_list'][:5])}")
        return 0

    if args.repo:
        nodes = graph.find_by_repo(args.repo)
        print(f"Nodes in {args.repo} ({len(nodes)}):")
        # group by kind
        by_kind: dict[str, int] = {}
        for n in nodes:
            by_kind[n.kind] = by_kind.get(n.kind, 0) + 1
        for kind, count in sorted(by_kind.items(), key=lambda x: -x[1]):
            print(f"  {kind:20s} {count}")
        return 0

    if args.kind:
        nodes = graph.find_by_kind(args.kind)
        print(f"Nodes of kind {args.kind} ({len(nodes)}):")
        for n in nodes[:30]:
            print(f"  {n.name:30s} in {n.repo_id}")
        return 0

    if args.language:
        nodes = graph.find_by_language(args.language)
        print(f"Nodes in language {args.language} ({len(nodes)}):")
        by_repo: dict[str, int] = {}
        for n in nodes:
            by_repo[n.repo_id] = by_repo.get(n.repo_id, 0) + 1
        for repo, count in sorted(by_repo.items(), key=lambda x: -x[1]):
            print(f"  {repo:40s} {count}")
        return 0

    return 0


def _list_repos(registry: RepositoryRegistry, args: argparse.Namespace) -> int:
    repos = registry.list_repos(status=args.status, source=args.source)
    if not repos:
        print("No repositories found.")
        return 0
    for r in repos:
        print(f"{r.status:8s} {r.name:50s} {r.language:12s} {r.file_count:5d} files  {r.usir_node_count:5d} usir")
    return 0


def _analyze(miner: RepositoryMiner, args: argparse.Namespace) -> int:
    if args.all:
        count = miner.analyze_existing()
        print(f"Re-analyzed {count} repositories")
        return 0
    if args.repo_id:
        count = miner.analyze_existing(args.repo_id)
        print(f"Re-analyzed {count} repositories")
        return 0
    print("Specify --all or a repo_id")
    return 1
