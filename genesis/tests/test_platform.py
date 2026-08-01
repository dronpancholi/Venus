"""
GENESIS-I Platform Test Suite

Covers all 15 CORE modules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import tempfile
import os
from pathlib import Path

# ── CORE-05: Universal Object Model ──
from genesis.core.base import BaseEntity, BaseCapability, BaseArtifact
from genesis.core.types import type_registry, SemanticType
from genesis.core.exceptions import GenesisError

def test_base_entity():
    e = BaseEntity(entity_id="test:1", name="test", semantic_type="test_type", version="1.0.0")
    assert e.entity_id == "test:1"
    assert e.name == "test"
    assert e.semantic_type == "test_type"
    assert e.validate() == []
    d = e.to_dict()
    assert d["entity_id"] == "test:1"
    assert d["name"] == "test"
    assert d["version"] == "1.0.0"
    # Roundtrip
    e2 = BaseEntity.from_dict(d)
    assert e2.entity_id == "test:1"
    assert e2.name == "test"

    # Touch
    old = e.updated_at
    e.touch()
    assert e.updated_at >= old

def test_base_capability():
    cap = BaseCapability(capability_id="cap:test:1", name="test-cap", version="2.0.0")
    assert cap.semantic_type == "capability"
    cap.interfaces.append({"name": "api", "method": "GET", "path": "/test"})
    d = cap.to_dict()
    assert "interfaces" in d
    assert len(d["interfaces"]) == 1

def test_base_artifact():
    art = BaseArtifact(artifact_id="art:test:1", name="test-art", artifact_type="schema", version="1.0.0")
    assert art.semantic_type == "artifact.schema"
    assert art.validation_state == "unvalidated"

def test_type_registry():
    assert type_registry.get("entity") is not None
    assert type_registry.get("base_entity") is not None
    assert type_registry.get("artifact") is not None
    assert type_registry.get("operating_system") is not None
    assert type_registry.get("nonexistent") is None
    assert type_registry.is_subtype_of("operating_system", "artifact")
    assert type_registry.is_subtype_of("artifact", "entity")
    chain = type_registry.resolve_hierarchy("operating_system")
    assert len(chain) >= 2


# ── CORE-01: UIR ──
from genesis.core.uir import (
    UIRNode, UIREdge, UIRGraph,
    DependencyGraph, CapabilityGraph, ValidationGraph,
    ExecutionGraph, CompilationUnit,
)

def test_uir_node():
    n = UIRNode("node:1", "Test Node", "test_type")
    assert n.node_id == "node:1"
    assert n.label == "Test Node"
    n.set("key", "value")
    assert n.get("key") == "value"
    h = n.compute_hash()
    assert len(h) == 16
    d = n.to_dict()
    assert d["node_id"] == "node:1"
    n2 = UIRNode.from_dict(d)
    assert n2.node_id == "node:1"

def test_uir_graph():
    g = UIRGraph("test-graph", "test")
    n1 = UIRNode("a", "A", "type_a")
    n2 = UIRNode("b", "B", "type_b")
    g.add_node(n1)
    g.add_node(n2)
    g.add_edge_raw("a", "b", "depends_on", weight=1)
    assert len(g.nodes) == 2
    assert len(g.edges) == 1
    assert g.get_node("a") is n1
    neigh = g.neighbors("a")
    assert ("b", "depends_on") in neigh

    sub = g.subgraph("a", depth=1)
    assert len(sub.nodes) == 2
    assert len(sub.edges) == 1

    found = g.find(semantic_type="type_a")
    assert len(found) == 1

    g2 = UIRGraph.from_dict(g.to_dict())
    assert len(g2.nodes) == 2

    g.merge(g2)
    assert len(g.nodes) == 2  # no duplicates

def test_dependency_graph():
    dg = DependencyGraph()
    dg.add_dependency("A", "B")
    dg.add_dependency("B", "C")
    dg.add_dependency("C", "D")
    order = dg.resolve_order()
    assert order.index("A") < order.index("D")
    assert len(dg.find_cycles()) == 0
    # Test cycle detection
    dg.add_dependency("D", "A")
    cycles = dg.find_cycles()
    assert len(cycles) > 0

def test_execution_graph():
    eg = ExecutionGraph()
    eg.add_task("t1", "Task 1")
    eg.add_task("t2", "Task 2")
    eg.add_task("t3", "Task 3")
    eg.add_sequence(["t1", "t2", "t3"])
    order = eg.top_sort()
    assert order[0] == "t1"
    assert order[-1] == "t3"

def test_compilation_unit():
    cu = CompilationUnit("test.json", "json")
    assert cu.source_path == "test.json"
    assert all(name in cu.all_graphs() for name in ["ast", "dependencies", "capabilities", "validation", "execution", "metadata"])


# ── CORE-08: Metadata Engine ──
from genesis.core.metadata import MetadataEngine

def test_metadata_engine():
    engine = MetadataEngine()
    rec = engine.create_record("/path/to/file.md", "document", "1.0.0")
    assert rec.artifact_id.startswith("ven:meta:")
    assert engine.get_record("/path/to/file.md") is rec
    engine.set_validation_state("/path/to/file.md", "validated")
    assert rec.validation_state == "validated"
    engine.set_certification("/path/to/file.md", "certified")
    assert rec.certification == "certified"
    results = engine.search(semantic_type="document")
    assert len(results) == 1
    assert engine.count() == 1
    engine.delete_record("/path/to/file.md")
    assert engine.count() == 0


# ── CORE-04: Capability Registry ──
from genesis.capability.registry import CapabilityDefinition, CapabilityRegistry

def test_capability_registry():
    reg = CapabilityRegistry()
    assert len(reg.all()) == 18  # core capabilities
    assert reg.get("compiler") is not None
    assert reg.get("nonexistent") is None

    custom = CapabilityDefinition("custom-test", "Test capability", "0.1.0", "tester")
    custom.add_interface("exec", "POST", "/v1/custom/exec")
    custom.add_contract("output", "Must return JSON")
    custom.add_dependency("compiler")
    reg.register(custom)
    assert len(reg.all()) == 19

    chain = reg.dependency_chain("custom-test")
    assert "custom-test" in chain


# ── CORE-03: Plugin Architecture ──
from genesis.plugin.manifest import PluginManifest
from genesis.plugin.manager import PluginManager

def test_plugin_manifest():
    m = PluginManifest("my-plugin", "1.0.0", "plugin.py", "A test plugin", "dev")
    m.add_hook("runtime", "on_start")
    m.add_hook("validation", "on_validate")
    m.add_dependency("compiler", ">=1.0")
    m.add_command("greet", "handler.greet", "Say hello")
    assert m.validate() == []
    assert "on_start" in m.hooks["runtime"]
    yaml_str = m.to_yaml()
    assert "name: my-plugin" in yaml_str
    assert "version: 1.0.0" in yaml_str
    # Roundtrip
    m2 = PluginManifest.from_dict(m.to_dict())
    assert m2.name == "my-plugin"

def test_plugin_manager():
    mgr = PluginManager()
    m = PluginManifest("test-p", "1.0.0", "test.py", "Test", "dev")
    mgr.register_plugin(m)
    assert mgr.get("test-p") is not None


# ── CORE-02: Compiler Framework ──
from genesis.compiler.compiler import Compiler
from genesis.compiler.parser import Parser
from genesis.compiler.ast import AST, ASTNode

def test_ast():
    ast = AST("test.json", "json")
    root = ASTNode("program", name="root")
    child = ASTNode("function", name="main")
    child.value = "hello"
    root.add_child(child)
    ast.root = root
    assert len(root.children) == 1
    assert len(ast.find("function")) == 1

def test_parser_json():
    ast = Parser.parse_string('{"key": "value", "num": 42}', "json", "test.json")
    assert ast.source_format == "json"
    assert ast.root.node_type == "json_document"

def test_parser_markdown():
    md = "# Title\n\nSome text\n- item 1\n- item 2"
    ast = Parser.parse_string(md, "markdown", "test.md")
    assert ast.source_format == "markdown"
    assert len(ast.find("heading")) > 0

def test_parser_dsl():
    dsl = "OperatingSystem UniversalSecurityOS {\n  version: 1.0.0\n}"
    ast = Parser.parse_string(dsl, "dsl", "test.venus")
    assert ast.source_format == "dsl"

def test_compiler_basic():
    comp = Compiler()
    cu = comp.compile_string('{"key": "value"}', "json", "test")
    assert len(cu.ast.nodes) > 0
    assert "dead_code_elimination" in cu.passes_applied
    assert "dependency_pruning" in cu.passes_applied
    assert "metadata_normalization" in cu.passes_applied

def test_compiler_generate():
    import tempfile
    comp = Compiler()
    cu = comp.compile_string('{"name": "test"}', "json", "test")
    out_dir = os.path.join(tempfile.gettempdir(), "genesis-test")
    artifacts = comp.generate(cu, out_dir)
    assert len(artifacts) > 0
    for gen_name, files in artifacts.items():
        for f in files:
            assert Path(f).exists()

def test_compiler_cache():
    import tempfile
    comp = Compiler()
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
        f.write('{"a": 1}')
        f.flush()
        cu1 = comp.compile(f.name)
        cu2 = comp.incremental_compile(f.name)
        assert cu2 is cu1  # from cache
        comp.invalidate_cache(f.name)
        cu3 = comp.compile(f.name)
        assert cu3 is not cu1  # new compilation after cache eviction
        os.unlink(f.name)


# ── CORE-10: Validation Engine ──
from genesis.validation.engine import ValidationEngine
from genesis.validation.base import ValidationResult, BaseValidator

def test_validation_result():
    r = ValidationResult("test", "schema", True, "OK", "info", "file.json")
    assert r.passed
    assert r.validator_name == "test"
    assert r.category == "schema"

def test_custom_validator():
    engine = ValidationEngine()
    engine.register_func("custom_check", "quality", lambda t: ValidationResult("custom_check", "quality", True, "Custom OK"))
    assert engine.get("custom_check") is not None
    results = engine.validate({"path": "test.json"})
    assert len(results) >= 4  # 3 built-in + 1 custom

def test_validation_summary():
    engine = ValidationEngine()
    results = [ValidationResult("a", "schema", True, "OK"), ValidationResult("b", "schema", False, "FAIL")]
    s = engine.summary(results)
    assert s["total"] == 2
    assert s["passed"] == 1
    assert s["failed"] == 1


# ── CORE-07: Knowledge Graph Engine ──
from genesis.graph.engine import KnowledgeGraphEngine

def test_knowledge_graph():
    kg = KnowledgeGraphEngine()
    kg.add_node("os:1", "UniversalSecurityOS", "operating_system")
    kg.add_node("part:1", "Kernel", "part")
    kg.add_edge("part:1", "os:1", "composes")
    assert kg.summary()["total_nodes"] == 2
    assert kg.summary()["total_edges"] == 1

    assert kg.get_node("os:1") is not None
    assert kg.get_node("UniversalSecurityOS") is not None
    assert len(kg.find_nodes(node_type="part")) == 1
    assert len(kg.find_nodes(label_contains="Kernel")) == 1

    cypher = kg.export_cypher()
    assert "MERGE" not in cypher
    assert "CREATE" in cypher

    kg2 = KnowledgeGraphEngine()
    kg2.load_from_dict({"nodes": {"x": {"label": "X", "semantic_type": "test"}}, "edges": []})
    assert kg2.summary()["total_nodes"] == 1


# ── CORE-09: Repository Indexer ──
from genesis.indexer.indexer import RepositoryIndexer

def test_indexer():
    indexer = RepositoryIndexer("/tmp")
    summary = indexer.scan()
    assert "total_files" in summary


# ── CORE-11: Execution Engine ──
from genesis.runtime.executor import ExecutionEngine, Workflow, Task, TaskStatus

def test_workflow():
    wf = Workflow(name="test-wf")
    t1 = Task(name="step1")
    t2 = Task(name="step2")
    wf.add_task(t1)
    wf.add_task(t2)
    wf.add_sequence("step1", "step2")
    order = wf.top_sort()
    assert [t.name for t in order] == ["step1", "step2"]

def test_execution_engine():
    engine = ExecutionEngine()
    wf = engine.create_workflow("test-exec")
    t1 = Task(name="a")
    t2 = Task(name="b")
    wf.add_task(t1)
    wf.add_task(t2)
    wf.add_sequence("a", "b")

    results = engine.execute(wf.workflow_id)
    assert len(results) == 2
    assert results[0]["status"] == "completed"


# ── CORE-06: API ──
from genesis.api.router import APIRouter, Request

def test_api_router():
    router = APIRouter()
    routes = router.list_routes()
    assert len(routes) == 34

    def health_handler(req):
        return {"status": "ok"}

    router.register_handler("GET", "/v1/health", health_handler)
    resp = router.handle(Request("GET", "/v1/health"))
    assert resp.status == 200
    assert resp.data["status"] == "ok"

    resp = router.handle(Request("GET", "/nonexistent"))
    assert resp.status == 404

    health = router.health_check()
    assert health["status"] == "healthy"


# ── CORE-13: Studio Backend ──
from genesis.studio.backend import StudioBackend

def test_studio_backend():
    studio = StudioBackend()
    ws = studio.get_workspace()
    assert "name" in ws

    proj = studio.create_project("test-proj", "A test project")
    assert proj["name"] == "test-proj"

    caps = studio.get_capabilities()
    assert len(caps) >= 18

    types = studio.get_ontology_types()
    assert len(types) >= 20

    health = studio.health()
    assert health["status"] == "healthy"


# ── CORE-14: Project 31A Integration ──
from genesis.integration.project31a import Project31AIntegration

def test_project31a():
    import tempfile
    p31 = Project31AIntegration()
    review = p31.architecture_review()
    assert "node_types" in review
    assert "recommendations" in review
    out_docs = os.path.join(tempfile.gettempdir(), "p31-docs")
    docs = p31.generate_documentation(out_docs)
    assert len(docs) >= 2
    risks = p31.risk_analysis()
    assert "total_risks" in risks
    auto = p31.autonomous_review()
    assert "architecture" in auto
    assert "capabilities" in auto
    assert "risks" in auto


# ── CORE-15: Self Diagnostics ──
from genesis.diagnostics.diagnostics import Diagnostics

def test_diagnostics():
    diag = Diagnostics()
    results = diag.run("quick")
    assert len(results) >= 5
    s = diag.summary()
    assert "total_checks" in s
    assert "health_score" in s


# ── CORE-12: CLI — test via programmatic API ──
from genesis.cli.commands import CLI

def test_cli_info():
    cli = CLI()
    cli.run(["info"])

def test_cli_diagnose():
    cli = CLI()
    cli.run(["diagnose", "--mode", "quick"])

def test_cli_graph_stats():
    cli = CLI()
    cli.run(["graph", "stats"])


if __name__ == "__main__":
    # Run all tests and report
    test_fns = [fn for fn in dir() if fn.startswith("test_")]
    passed = 0
    failed = 0
    for fn_name in sorted(test_fns):
        fn = globals()[fn_name]
        try:
            fn()
            print(f"  ✓ {fn_name}")
            passed += 1
        except Exception as e:
            import traceback
            print(f"  ✗ {fn_name}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\nResults: {passed} passed, {failed} failed, {len(test_fns)} total")
