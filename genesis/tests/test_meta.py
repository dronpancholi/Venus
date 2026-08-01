"""Tests for GENESIS XI Meta Compiler."""

import pytest
from genesis.meta.workspace import (
    Workspace, WorkspaceManifest, Repository, RepositoryType, WorkspaceScope,
)
from genesis.meta.irep import WorkspaceIR, WorkspaceIRNode, IRBuilder, IRNodeType, IREdgeType
from genesis.meta.graph import (
    WorkspaceDependencyGraph, WorkspaceCapabilityMap, WorkspaceGraph,
)
from genesis.meta.resolution import SymbolResolver, Symbol, CapabilityLinker, CapabilityBinding
from genesis.meta.federation import RepositoryFederation, FederationLink
from genesis.meta.optimization import WorkspaceOptimizer
from genesis.meta.build_graph import (
    BuildGraph, BuildNode, BuildNodeType, BuildStatus, BuildArtifact,
)
from genesis.meta.twin import WorkspaceTwin, TwinEntity
from genesis.meta.meta_compiler import MetaCompiler


# ── Fixtures ──

@pytest.fixture
def sample_repos():
    return [
        Repository(id="repo_a", name="core-lib", language="python",
                     repo_type=RepositoryType.LIBRARY,
                     capabilities_provided=["auth", "logging"],
                     file_count=50, module_count=10),
        Repository(id="repo_b", name="api-service", language="python",
                     repo_type=RepositoryType.SERVICE,
                     dependencies=["repo_a"],
                     capabilities_consumed=["auth"],
                     capabilities_provided=["rest-api"],
                     file_count=100, module_count=20),
        Repository(id="repo_c", name="worker", language="go",
                     repo_type=RepositoryType.SERVICE,
                     dependencies=["repo_a"],
                     capabilities_consumed=["logging"],
                     file_count=30, module_count=8),
    ]


@pytest.fixture
def sample_workspace(sample_repos):
    ws = Workspace(WorkspaceManifest(name="test-ws"), name="test-ws")
    for repo in sample_repos:
        ws.add_repository(repo)
    return ws


# ── Workspace Tests ──

class TestRepository:
    def test_defaults(self):
        r = Repository(name="test-repo")
        assert r.repo_type == RepositoryType.SOURCE
        assert r.default_branch == "main"
        assert r.healthy
        assert r.id

    def test_summary(self, sample_repos):
        s = sample_repos[0].summary()
        assert s["name"] == "core-lib"
        assert s["capabilities"]["provided"] == 2


class TestWorkspaceManifest:
    def test_create(self):
        m = WorkspaceManifest(name="my-ws", version="2.0.0")
        assert m.scope == WorkspaceScope.LOCAL
        assert m.version == "2.0.0"

    def test_add_remove_repository(self, sample_repos):
        m = WorkspaceManifest(name="test")
        m.add_repository(sample_repos[0])
        assert len(m.repositories) == 1
        m.add_repository(sample_repos[0])
        assert len(m.repositories) == 1
        assert m.remove_repository(sample_repos[0].id)
        assert len(m.repositories) == 0

    def test_find_by_name(self, sample_repos):
        m = WorkspaceManifest(name="test")
        for r in sample_repos:
            m.add_repository(r)
        results = m.find_by_name("core")
        assert len(results) == 1


class TestWorkspace:
    def test_create(self):
        ws = Workspace(name="my-ws")
        assert ws.name == "my-ws"
        assert ws.repository_count == 0

    def test_add_repository(self, sample_repos):
        ws = Workspace(name="test")
        ws.add_repository(sample_repos[0])
        ws.add_repository(sample_repos[0])
        assert ws.repository_count == 1

    def test_remove_repository(self, sample_repos):
        ws = Workspace(name="test")
        ws.add_repository(sample_repos[0])
        assert ws.remove_repository(sample_repos[0].id)
        assert not ws.remove_repository("nonexistent")

    def test_find_by_name(self, sample_workspace):
        results = sample_workspace.find_by_name("core")
        assert len(results) == 1

    def test_find_by_type(self, sample_workspace):
        libs = sample_workspace.find_by_type(RepositoryType.LIBRARY)
        assert len(libs) == 1
        services = sample_workspace.find_by_type(RepositoryType.SERVICE)
        assert len(services) == 2

    def test_find_by_language(self, sample_workspace):
        py = sample_workspace.find_by_language("python")
        assert len(py) == 2
        go = sample_workspace.find_by_language("go")
        assert len(go) == 1

    def test_dependency_graph(self, sample_workspace):
        dg = sample_workspace.dependency_graph()
        assert "repo_a" in dg
        assert dg["repo_b"] == ["repo_a"]

    def test_capability_map(self, sample_workspace):
        cm = sample_workspace.capability_map()
        assert "auth" in cm
        assert "repo_a" in cm["auth"]

    def test_total_files(self, sample_workspace):
        assert sample_workspace.total_files() == 180

    def test_languages(self, sample_workspace):
        langs = sample_workspace.languages()
        assert "python" in langs
        assert "go" in langs

    def test_summary(self, sample_workspace):
        s = sample_workspace.summary()
        assert s["repositories"] == 3
        assert s["languages"] == ["python", "go"] or s["languages"] == ["go", "python"]


# ── Workspace IR Tests ──

class TestWorkspaceIR:
    def test_create(self):
        ir = WorkspaceIR(workspace_id="ws_1", workspace_name="test")
        assert ir.node_count() == 0
        assert ir.edge_count() == 0

    def test_add_node(self):
        ir = WorkspaceIR()
        node = ir.add_node(WorkspaceIRNode(name="root", node_type=IRNodeType.WORKSPACE))
        assert ir.node_count() == 1
        assert ir.get_node(node.id).name == "root"

    def test_add_edge(self):
        ir = WorkspaceIR()
        n1 = ir.add_node(WorkspaceIRNode(name="a", node_type=IRNodeType.REPOSITORY))
        n2 = ir.add_node(WorkspaceIRNode(name="b", node_type=IRNodeType.CAPABILITY))
        edge = ir.add_edge(n1.id, n2.id, IREdgeType.PROVIDES)
        assert ir.edge_count() == 1

    def test_add_edge_missing_node(self):
        ir = WorkspaceIR()
        n1 = ir.add_node(WorkspaceIRNode(name="a", node_type=IRNodeType.REPOSITORY))
        with pytest.raises(ValueError):
            ir.add_edge(n1.id, "nonexistent", IREdgeType.CONTAINS)

    def test_nodes_by_type(self):
        ir = WorkspaceIR()
        ir.add_node(WorkspaceIRNode(name="ws", node_type=IRNodeType.WORKSPACE))
        ir.add_node(WorkspaceIRNode(name="repo", node_type=IRNodeType.REPOSITORY))
        assert len(ir.nodes_by_type(IRNodeType.WORKSPACE)) == 1
        assert len(ir.nodes_by_type(IRNodeType.REPOSITORY)) == 1

    def test_nodes_for_repo(self):
        ir = WorkspaceIR()
        n = ir.add_node(WorkspaceIRNode(name="r1", node_type=IRNodeType.REPOSITORY,
                                          repository_id="repo_x"))
        assert len(ir.nodes_for_repo("repo_x")) == 1

    def test_successors_predecessors(self):
        ir = WorkspaceIR()
        n1 = ir.add_node(WorkspaceIRNode(name="a"))
        n2 = ir.add_node(WorkspaceIRNode(name="b"))
        n3 = ir.add_node(WorkspaceIRNode(name="c"))
        ir.add_edge(n1.id, n2.id, IREdgeType.CONTAINS)
        ir.add_edge(n1.id, n3.id, IREdgeType.CONTAINS)
        succ = ir.successors(n1.id)
        assert len(succ) == 2
        pred = ir.predecessors(n2.id)
        assert len(pred) == 1

    def test_subgraph(self):
        ir = WorkspaceIR()
        n_ws = ir.add_node(WorkspaceIRNode(name="ws", node_type=IRNodeType.WORKSPACE))
        n_r1 = ir.add_node(WorkspaceIRNode(name="r1", node_type=IRNodeType.REPOSITORY,
                                             repository_id="r1"))
        n_r2 = ir.add_node(WorkspaceIRNode(name="r2", node_type=IRNodeType.REPOSITORY,
                                             repository_id="r2"))
        ir.add_edge(n_ws.id, n_r1.id)
        ir.add_edge(n_ws.id, n_r2.id)
        sub = ir.subgraph("r1")
        assert sub.node_count() == 1

    def test_finalize(self):
        ir = WorkspaceIR()
        ir.add_node(WorkspaceIRNode(name="n1"))
        ir.finalize()
        assert ir._built_at > 0

    def test_to_dict(self):
        ir = WorkspaceIR(workspace_id="ws_test")
        ir.add_node(WorkspaceIRNode(name="n1"))
        d = ir.to_dict()
        assert d["workspace_id"] == "ws_test"
        assert d["nodes"] == 1


class TestIRBuilder:
    def test_build(self, sample_workspace):
        builder = IRBuilder()
        ir = builder.build(sample_workspace)
        assert ir.node_count() >= 3
        assert ir.edge_count() >= 2

    def test_incremental_build(self, sample_workspace):
        builder = IRBuilder()
        ir1 = builder.build(sample_workspace)
        ir2 = builder.incremental_build(sample_workspace, ir1)
        assert ir2.node_count() >= ir1.node_count()

    def test_build_history(self, sample_workspace):
        builder = IRBuilder()
        builder.build(sample_workspace)
        assert len(builder.build_history()) >= 1


# ── Graph Tests ──

class TestWorkspaceDependencyGraph:
    def test_edges(self, sample_workspace):
        g = WorkspaceDependencyGraph(sample_workspace)
        assert len(g.edges()) >= 1

    def test_no_cycles(self, sample_workspace):
        g = WorkspaceDependencyGraph(sample_workspace)
        assert not g.has_cycles()

    def test_fan_in_fan_out(self, sample_workspace):
        g = WorkspaceDependencyGraph(sample_workspace)
        assert g.fan_in("repo_a") == 2
        assert g.fan_out("repo_a") == 0

    def test_topological_order(self, sample_workspace):
        g = WorkspaceDependencyGraph(sample_workspace)
        order = g.topological_order()
        assert order.index("repo_a") < order.index("repo_b")

    def test_transitive_dependencies(self, sample_workspace):
        g = WorkspaceDependencyGraph(sample_workspace)
        deps = g.transitive_dependencies("repo_b")
        assert "repo_a" in deps

    def test_leaf_root_repos(self, sample_workspace):
        g = WorkspaceDependencyGraph(sample_workspace)
        leaves = g.leaf_repositories()
        assert any(r.id == "repo_a" for r in leaves)
        roots = g.root_repositories()
        assert any(r.id == "repo_b" for r in roots)

    def test_upstream_downstream(self, sample_workspace):
        g = WorkspaceDependencyGraph(sample_workspace)
        up = g.upstream("repo_b")
        assert "repo_a" in up
        down = g.downstream("repo_a")
        assert "repo_b" in down
        assert "repo_c" in down

    def test_summary(self, sample_workspace):
        g = WorkspaceDependencyGraph(sample_workspace)
        s = g.summary()
        assert s["total_repos"] == 3


class TestWorkspaceCapabilityMap:
    def test_providers_of(self, sample_workspace):
        cm = WorkspaceCapabilityMap(sample_workspace)
        providers = cm.providers_of("auth")
        assert len(providers) == 1
        assert providers[0].id == "repo_a"

    def test_consumers_of(self, sample_workspace):
        cm = WorkspaceCapabilityMap(sample_workspace)
        consumers = cm.consumers_of("auth")
        assert len(consumers) == 1

    def test_all_capabilities(self, sample_workspace):
        cm = WorkspaceCapabilityMap(sample_workspace)
        caps = cm.all_capabilities()
        assert "auth" in caps
        assert "logging" in caps

    def test_unresolved_and_orphans(self, sample_workspace):
        cm = WorkspaceCapabilityMap(sample_workspace)
        unresolved = cm.unresolved_consumers()
        assert len(unresolved) == 0

    def test_coverage(self, sample_workspace):
        cm = WorkspaceCapabilityMap(sample_workspace)
        cov = cm.coverage()
        assert cov["coverage"] >= 1.0


class TestWorkspaceGraph:
    def test_summary(self, sample_workspace):
        g = WorkspaceGraph(sample_workspace)
        s = g.summary()
        assert "dependency_graph" in s
        assert "capability_map" in s


# ── Resolution Tests ──

class TestSymbolResolver:
    def test_register_and_resolve(self, sample_workspace):
        sr = SymbolResolver(sample_workspace)
        sym = Symbol(name="calculate", repository_id="repo_a",
                      symbol_type="function", visibility="public")
        sr.register_symbol(sym)
        results = sr.resolve("calculate", "repo_b")
        assert len(results) >= 1

    def test_unresolved_symbols(self, sample_workspace):
        sr = SymbolResolver(sample_workspace)
        sym = Symbol(name="missing_func", repository_id="repo_b",
                      symbol_type="reference")
        sr.register_symbol(sym)
        unresolved = sr.unresolved_symbols()
        assert len(unresolved) >= 1

    def test_public_symbols(self, sample_workspace):
        sr = SymbolResolver(sample_workspace)
        sr.register_symbol(Symbol(name="pub", repository_id="repo_a",
                                   visibility="public"))
        sr.register_symbol(Symbol(name="priv", repository_id="repo_a",
                                   visibility="private"))
        assert len(sr.public_symbols()) == 1

    def test_symbols_for_repo(self, sample_workspace):
        sr = SymbolResolver(sample_workspace)
        sr.register_symbol(Symbol(name="s1", repository_id="repo_a"))
        sr.register_symbol(Symbol(name="s2", repository_id="repo_a"))
        assert len(sr.symbols_for_repo("repo_a")) == 2

    def test_resolution_coverage(self, sample_workspace):
        sr = SymbolResolver(sample_workspace)
        assert sr.resolution_coverage() == 0.0
        sr.register_symbol(Symbol(name="ref", repository_id="repo_b",
                                   symbol_type="reference"))
        sr.resolve("ref", "repo_b")
        assert sr.resolution_coverage() >= 0

    def test_summary(self, sample_workspace):
        sr = SymbolResolver(sample_workspace)
        sr.register_symbol(Symbol(name="calc", repository_id="repo_a"))
        s = sr.summary()
        assert s["total_symbols"] >= 1


class TestCapabilityLinker:
    def test_link_success(self, sample_workspace):
        cl = CapabilityLinker(sample_workspace)
        binding = cl.link("auth", "repo_b")
        assert binding is not None
        assert binding.provider_repo_id == "repo_a"

    def test_link_missing_capability(self, sample_workspace):
        cl = CapabilityLinker(sample_workspace)
        binding = cl.link("nonexistent", "repo_b")
        assert binding is None

    def test_unlink(self, sample_workspace):
        cl = CapabilityLinker(sample_workspace)
        b = cl.link("auth", "repo_b")
        assert cl.unlink(b.id)
        assert not cl.unlink("missing")

    def test_bindings_for_repo(self, sample_workspace):
        cl = CapabilityLinker(sample_workspace)
        cl.link("auth", "repo_b")
        bindings = cl.bindings_for("repo_a")
        assert len(bindings) >= 1

    def test_consumers_and_providers(self, sample_workspace):
        cl = CapabilityLinker(sample_workspace)
        cl.link("auth", "repo_b")
        assert len(cl.consumers_of("repo_a")) >= 1
        assert len(cl.providers_for("repo_b")) >= 1

    def test_active_bindings(self, sample_workspace):
        cl = CapabilityLinker(sample_workspace)
        cl.link("auth", "repo_b")
        assert len(cl.active_bindings()) >= 1

    def test_summary(self, sample_workspace):
        cl = CapabilityLinker(sample_workspace)
        cl.link("auth", "repo_b")
        s = cl.summary()
        assert s["total_bindings"] >= 1


# ── Federation Tests ──

class TestRepositoryFederation:
    def test_register_workspace(self):
        rf = RepositoryFederation()
        ws = Workspace(name="ws_a")
        rf.register_workspace(ws)
        assert rf.get_workspace(ws.id).name == "ws_a"

    def test_unregister(self):
        rf = RepositoryFederation()
        ws = Workspace(name="ws_a")
        rf.register_workspace(ws)
        assert rf.unregister_workspace(ws.id)
        assert not rf.unregister_workspace("nonexistent")

    def test_link(self):
        rf = RepositoryFederation()
        ws1 = Workspace(name="ws1")
        ws2 = Workspace(name="ws2")
        rf.register_workspace(ws1)
        rf.register_workspace(ws2)
        link = rf.link(ws1.id, ws2.id, "repo_a", "repo_b")
        assert link is not None

    def test_link_missing_workspace(self):
        rf = RepositoryFederation()
        ws = Workspace(name="ws")
        rf.register_workspace(ws)
        assert rf.link(ws.id, "missing", "r1", "r2") is None

    def test_unlink(self):
        rf = RepositoryFederation()
        ws1 = Workspace(name="ws1")
        ws2 = Workspace(name="ws2")
        rf.register_workspace(ws1)
        rf.register_workspace(ws2)
        link = rf.link(ws1.id, ws2.id, "r1", "r2")
        assert rf.unlink(link.id)
        assert not rf.unlink("missing")

    def test_sync(self):
        rf = RepositoryFederation()
        ws1 = Workspace(name="ws1")
        ws2 = Workspace(name="ws2")
        rf.register_workspace(ws1)
        rf.register_workspace(ws2)
        link = rf.link(ws1.id, ws2.id, "r1", "r2")
        assert rf.sync(link.id)
        assert not rf.sync("missing")

    def test_links_for_workspace_and_repo(self):
        rf = RepositoryFederation()
        ws1 = Workspace(name="ws1")
        ws2 = Workspace(name="ws2")
        rf.register_workspace(ws1)
        rf.register_workspace(ws2)
        rf.link(ws1.id, ws2.id, "r1", "r2")
        assert len(rf.links_for_workspace(ws1.id)) >= 1
        assert len(rf.links_for_repo("r1")) >= 1

    def test_federated_graph(self):
        rf = RepositoryFederation()
        ws1 = Workspace(name="ws1")
        ws2 = Workspace(name="ws2")
        rf.register_workspace(ws1)
        rf.register_workspace(ws2)
        rf.link(ws1.id, ws2.id, "r1", "r2")
        g = rf.federated_graph()
        assert len(g) >= 1

    def test_summary(self):
        rf = RepositoryFederation()
        ws1 = Workspace(name="ws1")
        ws2 = Workspace(name="ws2")
        rf.register_workspace(ws1)
        rf.register_workspace(ws2)
        rf.link(ws1.id, ws2.id, "r1", "r2")
        s = rf.summary()
        assert s["workspaces"] == 2


# ── Optimization Tests ──

class TestWorkspaceOptimizer:
    def test_register_pass(self, sample_workspace):
        opt = WorkspaceOptimizer(sample_workspace)
        opt.register_pass("test", lambda ws: {"done": True})
        assert len(opt.available_passes()) == 1

    def test_execute_pass(self, sample_workspace):
        opt = WorkspaceOptimizer(sample_workspace)
        opt.register_pass("test", lambda ws: {"done": True})
        results = opt.optimize("test")
        assert results["test"]["status"] == "completed"
        assert results["test"]["result"]["done"]

    def test_execute_all(self, sample_workspace):
        opt = WorkspaceOptimizer(sample_workspace)
        opt.register_pass("a", lambda ws: {})
        opt.register_pass("b", lambda ws: {})
        results = opt.optimize()
        assert len(results) == 2

    def test_pass_failure(self, sample_workspace):
        opt = WorkspaceOptimizer(sample_workspace)
        opt.register_pass("failing", lambda ws: (_ for _ in ()).throw(ValueError("bad")))
        results = opt.optimize("failing")
        assert results["failing"]["status"] == "failed"

    def test_default_passes(self, sample_workspace):
        opt = WorkspaceOptimizer(sample_workspace)
        opt.register_default_passes()
        assert len(opt.available_passes()) >= 3

    def test_history(self, sample_workspace):
        opt = WorkspaceOptimizer(sample_workspace)
        opt.register_pass("t", lambda ws: {})
        opt.optimize("t")
        assert len(opt.optimization_history()) >= 1

    def test_summary(self, sample_workspace):
        opt = WorkspaceOptimizer(sample_workspace)
        s = opt.summary()
        assert s["registered_passes"] == 0
        opt.register_pass("t", lambda ws: {})
        s = opt.summary()
        assert s["registered_passes"] == 1


# ── Build Graph Tests ──

class TestBuildGraph:
    def test_add_node(self):
        bg = BuildGraph()
        n = bg.add_node(BuildNode(name="compile", node_type=BuildNodeType.REPOSITORY_COMPILE))
        assert bg.get_node(n.id).name == "compile"

    def test_remove_node(self):
        bg = BuildGraph()
        n = bg.add_node(BuildNode(name="n1"))
        assert bg.remove_node(n.id)
        assert not bg.remove_node("nonexistent")

    def test_nodes_by_type(self):
        bg = BuildGraph()
        bg.add_node(BuildNode(name="c1", node_type=BuildNodeType.REPOSITORY_COMPILE))
        bg.add_node(BuildNode(name="c2", node_type=BuildNodeType.REPOSITORY_COMPILE))
        bg.add_node(BuildNode(name="t1", node_type=BuildNodeType.TEST))
        assert len(bg.nodes_by_type(BuildNodeType.REPOSITORY_COMPILE)) == 2

    def test_execution_order(self):
        bg = BuildGraph()
        n1 = bg.add_node(BuildNode(name="root"))
        n2 = bg.add_node(BuildNode(name="dep", dependencies=[n1.id]))
        n3 = bg.add_node(BuildNode(name="leaf", dependencies=[n2.id]))
        order = bg.execution_order()
        ids = [n.id for n in order]
        assert ids.index(n1.id) < ids.index(n2.id)
        assert ids.index(n2.id) < ids.index(n3.id)

    def test_build(self):
        bg = BuildGraph()
        n = bg.add_node(BuildNode(name="test"))
        result = bg.build(n.id)
        assert result == BuildStatus.SUCCESS

    def test_build_with_handler(self):
        bg = BuildGraph()
        n = bg.add_node(BuildNode(name="test"))
        result = bg.build(n.id, handler=lambda node: {"output": 42})
        assert result == BuildStatus.SUCCESS
        assert n.output.get("output") == 42

    def test_build_failure(self):
        bg = BuildGraph()
        n = bg.add_node(BuildNode(name="test"))
        result = bg.build(n.id, handler=lambda node: (_ for _ in ()).throw(RuntimeError("crash")))
        assert result == BuildStatus.FAILURE

    def test_build_dependency_failure(self):
        bg = BuildGraph()
        n1 = bg.add_node(BuildNode(name="root"))
        n2 = bg.add_node(BuildNode(name="dep", dependencies=[n1.id]))
        assert bg.build(n2.id) == BuildStatus.FAILURE

    def test_build_all(self):
        bg = BuildGraph()
        bg.add_node(BuildNode(name="a"))
        bg.add_node(BuildNode(name="b"))
        results = bg.build_all(lambda n: {"compiled": True})
        assert all(s == BuildStatus.SUCCESS for s in results.values())

    def test_artifacts(self):
        bg = BuildGraph()
        n = bg.add_node(BuildNode(name="build"))
        art = BuildArtifact(name="output.bin", build_node_id=n.id,
                             artifact_type="binary", path="/tmp/out")
        bg.add_artifact(art)
        assert bg.get_artifact(art.id).name == "output.bin"
        assert len(bg.artifacts_for_build(n.id)) == 1

    def test_failed_and_completed(self):
        bg = BuildGraph()
        n1 = bg.add_node(BuildNode(name="ok"))
        n2 = bg.add_node(BuildNode(name="fail"))
        bg.build(n1.id)
        bg.build(n2.id, handler=lambda n: (_ for _ in ()).throw(Exception("bad")))
        assert len(bg.completed_nodes()) == 1
        assert len(bg.failed_nodes()) == 1

    def test_critical_path(self):
        bg = BuildGraph()
        n1 = bg.add_node(BuildNode(name="root"))
        n2 = bg.add_node(BuildNode(name="mid", dependencies=[n1.id]))
        n3 = bg.add_node(BuildNode(name="leaf", dependencies=[n2.id]))
        critical = bg.critical_path()
        assert len(critical) >= 1

    def test_summary(self):
        bg = BuildGraph()
        bg.add_node(BuildNode(name="a"))
        bg.add_node(BuildNode(name="b"))
        s = bg.summary()
        assert s["total_nodes"] == 2


# ── Workspace Twin Tests ──

class TestWorkspaceTwin:
    def test_create(self, sample_workspace):
        twin = WorkspaceTwin(sample_workspace)
        assert twin.workspace.name == "test-ws"

    def test_build_entities(self, sample_workspace):
        twin = WorkspaceTwin(sample_workspace)
        twin.build_entities()
        assert len(twin._entities) > 0

    def test_find_by_repo(self, sample_workspace):
        twin = WorkspaceTwin(sample_workspace)
        twin.build_entities()
        entity = twin.find_by_repo("repo_a")
        assert entity is not None
        assert entity.name == "core-lib"

    def test_aggregate_health(self, sample_workspace):
        twin = WorkspaceTwin(sample_workspace)
        twin.build_entities()
        health = twin.aggregate_health()
        assert health["average"] == 1.0

    def test_snapshot(self, sample_workspace):
        twin = WorkspaceTwin(sample_workspace)
        twin.build_entities()
        snap = twin.snapshot()
        assert "workspace" in snap
        assert "entities" in snap

    def test_update_repo(self, sample_workspace):
        twin = WorkspaceTwin(sample_workspace)
        twin.build_entities()
        sample_workspace.get_repository("repo_a").head_commit = "abc123"
        twin.update_repo("repo_a")
        entity = twin.find_by_repo("repo_a")
        assert entity.state["head_commit"] == "abc123"

    def test_compare(self, sample_workspace):
        twin1 = WorkspaceTwin(sample_workspace)
        twin1.build_entities()
        twin2 = WorkspaceTwin(sample_workspace)
        twin2.build_entities()
        result = twin1.compare(twin2)
        assert "changes" in result

    def test_attach_ir_and_graph(self, sample_workspace):
        twin = WorkspaceTwin(sample_workspace)
        ir = WorkspaceIR(workspace_id="ws1")
        ir.add_node(WorkspaceIRNode(name="n1", node_type=IRNodeType.WORKSPACE))
        twin.attach_ir(ir)
        twin.attach_graph(None)
        s = twin.summary()
        assert s["has_ir"]


# ── MetaCompiler Facade Tests ──

class TestMetaCompiler:
    def test_create(self):
        mc = MetaCompiler()
        assert mc.name == "MetaCompiler"

    def test_create_workspace(self):
        mc = MetaCompiler()
        ws = mc.create_workspace("test-ws")
        assert ws.name == "test-ws"
        assert mc.get_workspace(ws.id).name == "test-ws"

    def test_remove_workspace(self):
        mc = MetaCompiler()
        ws = mc.create_workspace("test")
        assert mc.remove_workspace(ws.id)
        assert not mc.remove_workspace("nonexistent")

    def test_add_remove_repository(self, sample_repos):
        mc = MetaCompiler()
        ws = mc.create_workspace("test")
        assert mc.add_repository(ws.id, sample_repos[0])
        assert mc.get_workspace(ws.id).repository_count == 1
        assert mc.remove_repository(ws.id, sample_repos[0].id)

    def test_add_repo_missing_workspace(self, sample_repos):
        mc = MetaCompiler()
        assert not mc.add_repository("missing", sample_repos[0])

    def test_compile_workspace(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        ir = mc.compile_workspace(sample_workspace.id)
        assert ir is not None
        assert ir.node_count() > 0

    def test_compile_missing_workspace(self):
        mc = MetaCompiler()
        assert mc.compile_workspace("nonexistent") is None

    def test_get_ir(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        mc.compile_workspace(sample_workspace.id)
        assert mc.get_ir(sample_workspace.id) is not None

    def test_build_workspace_graph(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        g = mc.build_workspace_graph(sample_workspace.id)
        assert g is not None

    def test_dep_graph_and_cap_map(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        assert mc.dep_graph(sample_workspace.id) is not None
        assert mc.cap_map(sample_workspace.id) is not None

    def test_create_twin(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        ir = mc.compile_workspace(sample_workspace.id)
        twin = mc.create_twin(sample_workspace.id)
        assert twin is not None
        assert mc.get_twin(sample_workspace.id) is not None

    def test_create_build_graph(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        bg = mc.create_build_graph(sample_workspace.id)
        assert bg is not None
        assert bg.summary()["total_nodes"] == 3

    def test_execute_build(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        results = mc.execute_build(sample_workspace.id)
        assert results is not None
        assert all(s == "success" for s in results.values())

    def test_create_symbol_resolver(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        sr = mc.create_symbol_resolver(sample_workspace.id)
        assert sr is not None

    def test_create_capability_linker(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        cl = mc.create_capability_linker(sample_workspace.id)
        assert cl is not None

    def test_create_optimizer(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        opt = mc.create_optimizer(sample_workspace.id)
        assert opt is not None
        assert len(opt.available_passes()) >= 3

    def test_federation(self):
        mc = MetaCompiler()
        assert mc.federation().summary()["workspaces"] == 0

    def test_history(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        mc.compile_workspace(sample_workspace.id)
        assert len(mc.history()) >= 1

    def test_overview(self, sample_workspace):
        mc = MetaCompiler()
        mc._workspaces[sample_workspace.id] = sample_workspace
        mc.compile_workspace(sample_workspace.id)
        o = mc.overview()
        assert o["workspaces"] >= 1


# ── TwinEntity Tests ──

class TestTwinEntity:
    def test_defaults(self):
        e = TwinEntity(name="test", entity_type="repository", repository_id="r1")
        assert e.health == 1.0
        assert e.id

    def test_state_metrics(self):
        e = TwinEntity(name="test", entity_type="service", repository_id="r1",
                        state={"branch": "main"}, metrics={"files": 50.0})
        assert e.state["branch"] == "main"
        assert e.metrics["files"] == 50.0
