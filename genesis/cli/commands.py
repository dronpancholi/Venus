"""
CORE-12: Package Manager — VenusPM

Commands:
  venus install, remove, update, compile, validate, certify,
  graph, search, package, publish, deploy

CORE-13: Studio Backend — workspace, projects, explorer APIs
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from genesis.compiler.compiler import Compiler
from genesis.validation.engine import ValidationEngine
from genesis.graph.engine import KnowledgeGraphEngine
from genesis.indexer.indexer import RepositoryIndexer
from genesis.runtime.executor import ExecutionEngine, Workflow, Task
from genesis.capability.registry import CapabilityRegistry, CapabilityDefinition


class CLI:
    """Venus Command Line Interface."""

    def __init__(self):
        self.compiler = Compiler()
        self.validator = ValidationEngine()
        self.graph = KnowledgeGraphEngine()
        self.runtime = ExecutionEngine()
        self.capabilities = CapabilityRegistry()

    def run(self, args: list[str] | None = None):
        parser = argparse.ArgumentParser(
            prog="venus",
            description="Venus Genesis-I Platform CLI",
        )
        sub = parser.add_subparsers(dest="command", help="Available commands")

        # install
        p_install = sub.add_parser("install", help="Install a package/plugin")
        p_install.add_argument("package", help="Package name or path")

        # remove
        p_remove = sub.add_parser("remove", help="Remove a package/plugin")
        p_remove.add_argument("package", help="Package name")

        # update
        p_update = sub.add_parser("update", help="Update packages")
        p_update.add_argument("packages", nargs="*", help="Package names (empty = all)")

        # compile
        p_compile = sub.add_parser("compile", help="Compile source files")
        p_compile.add_argument("source", nargs="+", help="Source file(s) to compile")
        p_compile.add_argument("--output", "-o", default="_build", help="Output directory")
        p_compile.add_argument("--passes", nargs="*", help="Compiler passes to run")

        # validate
        p_validate = sub.add_parser("validate", help="Validate artifacts")
        p_validate.add_argument("targets", nargs="+", help="Files or directories to validate")
        p_validate.add_argument("--categories", nargs="*", help="Validation categories")

        # certify
        p_certify = sub.add_parser("certify", help="Certify an artifact")
        p_certify.add_argument("path", help="Artifact path")
        p_certify.add_argument("--level", default="standard", help="Certification level")

        # graph
        p_graph = sub.add_parser("graph", help="Manage knowledge graph")
        p_graph.add_argument("action", choices=["build", "export", "stats", "query"])
        p_graph.add_argument("--format", default="cypher", choices=["cypher", "graphml", "json"])
        p_graph.add_argument("--query", "-q", help="Graph query string")

        # search
        p_search = sub.add_parser("search", help="Search across artifacts")
        p_search.add_argument("query", help="Search query")
        p_search.add_argument("--type", help="Filter by semantic type")
        p_search.add_argument("--max", type=int, default=10, help="Max results")

        # package
        p_package = sub.add_parser("package", help="Package artifacts")
        p_package.add_argument("name", help="Package name")
        p_package.add_argument("--version", default="0.1.0", help="Package version")
        p_package.add_argument("--include", nargs="+", help="Files to include")

        # publish
        p_publish = sub.add_parser("publish", help="Publish a package")
        p_publish.add_argument("package", help="Package path")

        # deploy
        p_deploy = sub.add_parser("deploy", help="Deploy artifacts")
        p_deploy.add_argument("source", help="Source to deploy")
        p_deploy.add_argument("--target", help="Deployment target")

        # index
        p_index = sub.add_parser("index", help="Index the repository")
        p_index.add_argument("--path", default=".", help="Repository root path")
        p_index.add_argument("--output", default="_catalog.json", help="Output file")

        # diagnose
        p_diag = sub.add_parser("diagnose", help="Run self-diagnostics")
        p_diag.add_argument("--mode", choices=["quick", "full"], default="quick")

        # run
        p_run = sub.add_parser("run", help="Execute a workflow")
        p_run.add_argument("workflow", help="Workflow definition file")

        # info
        sub.add_parser("info", help="Platform information")

        parsed = parser.parse_args(args)

        if not parsed.command:
            parser.print_help()
            return

        handler = getattr(self, f"cmd_{parsed.command}", None)
        if handler:
            handler(parsed)
        else:
            print(f"Unknown command: {parsed.command}")

    def cmd_compile(self, args):
        for source in args.source:
            source_path = Path(source)
            if not source_path.exists():
                print(f"  [ERROR] Source not found: {source}")
                continue
            try:
                passes = args.passes
                cu, artifacts = self.compiler.compile_and_generate(
                    source_path, args.output, passes
                )
                print(f"  Compiled: {source}")
                print(f"    AST nodes: {len(cu.ast.nodes)}")
                print(f"    Dependencies: {len(cu.dependencies.edges)}")
                print(f"    Generated: {len(artifacts)} artifact types")
                for gen_name, gen_files in artifacts.items():
                    print(f"      {gen_name}: {len(gen_files)} files")
            except Exception as e:
                print(f"  [ERROR] Compilation failed: {e}")

    def cmd_validate(self, args):
        for target in args.targets:
            results = self.validator.validate_path(target, args.categories)
            summary = self.validator.summary(results)
            print(f"  Validated: {target}")
            print(f"    Total: {summary['total']}, Passed: {summary['passed']}, Failed: {summary['failed']}")
            for r in results:
                if not r.passed:
                    print(f"    [{r.severity.upper()}] {r.validator_name}: {r.message}")

    def cmd_graph(self, args):
        if args.action == "build":
            print("  Knowledge graph built (use `create_node`/`add_edge` APIs)")
        elif args.action == "export":
            if args.format == "cypher":
                print(self.graph.export_cypher())
            elif args.format == "graphml":
                print(self.graph.export_graphml())
        elif args.action == "stats":
            s = self.graph.summary()
            print(f"  Nodes: {s['total_nodes']}")
            print(f"  Edges: {s['total_edges']}")
            print(f"  By type: {s['by_type']}")
            print(f"  Orphans: {s['orphans']}")
            print(f"  Cycles: {s['cycles']}")

    def cmd_search(self, args):
        results = self.graph.find_nodes(
            node_type=args.type,
            label_contains=args.query,
        )[:args.max]
        print(f"  Found: {len(results)} results")
        for node in results:
            print(f"    {node.node_id}: {node.label} ({node.semantic_type})")

    def cmd_index(self, args):
        indexer = RepositoryIndexer(Path(args.path))
        summary = indexer.scan()
        print(f"  Scanned: {summary['total_files']} files")
        print(f"  Duplicates: {summary['duplicates']}")
        print(f"  Broken links: {summary['broken_links']}")
        if args.output:
            indexer.save_catalog(args.output)
            print(f"  Saved to: {args.output}")

    def cmd_run(self, args):
        wf_path = Path(args.workflow)
        if not wf_path.exists():
            print(f"  [ERROR] Workflow not found: {args.workflow}")
            return
        try:
            wf_data = json.loads(wf_path.read_text())
            wf = Workflow(
                workflow_id=wf_data.get("id", ""),
                name=wf_data.get("name", args.workflow),
            )
            for tdata in wf_data.get("tasks", []):
                task = Task(
                    task_id=tdata.get("id"),
                    name=tdata.get("name"),
                    timeout=tdata.get("timeout", 300),
                )
                for dep in tdata.get("dependencies", []):
                    task.depends_on(dep)
                wf.add_task(task)
            self.runtime.register_workflow(wf)
            results = self.runtime.execute(wf.workflow_id)
            print(f"  Workflow executed: {wf.name}")
            for r in results:
                print(f"    {r['name']}: {r['status']}")
        except Exception as e:
            print(f"  [ERROR] Workflow execution failed: {e}")

    def cmd_info(self, args):
        from genesis.core.types import type_registry
        print("  Venus Genesis-I Platform")
        print(f"  Ontology types: {len(type_registry.all_types())}")
        print(f"  Capabilities: {len(self.capabilities.all())}")
        print(f"  Compiler passes: {len(self.compiler.pass_registry.all())}")
        print(f"  Code generators: {len(self.compiler.codegen_registry.all())}")
        print(f"  API routes: {len(self._get_api_routes())}")
        print(f"  Validators: {len(self.validator.all_validators())}")

    def cmd_install(self, args):
        print(f"  Installing: {args.package}")
        print("  (Package manager backend pending registry implementation)")

    def cmd_remove(self, args):
        print(f"  Removing: {args.package}")

    def cmd_update(self, args):
        targets = args.packages or ["all"]
        print(f"  Updating: {', '.join(targets)}")

    def cmd_certify(self, args):
        print(f"  Certifying: {args.path} at level {args.level}")

    def cmd_package(self, args):
        print(f"  Packaging: {args.name} v{args.version}")

    def cmd_publish(self, args):
        print(f"  Publishing: {args.package}")

    def cmd_deploy(self, args):
        print(f"  Deploying: {args.source} to {args.target or 'default'}")

    def cmd_diagnose(self, args):
        from genesis.diagnostics.diagnostics import Diagnostics
        diag = Diagnostics()
        results = diag.run(mode=args.mode)
        print(f"  Diagnostics ({args.mode} mode):")
        for check in results:
            status = "✓" if check["passed"] else "✗"
            print(f"    [{status}] {check['name']}: {check['message']}")

    def _get_api_routes(self):
        from genesis.api.router import APIRouter
        router = APIRouter()
        return router.list_routes()
