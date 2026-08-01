"""
Tests for the Global Repository Observatory.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from genesis.observatory.graph import (
    ObservatoryGraph, ObservedNode, CrossRepoEdge, ObservatorySnapshot,
)
from genesis.observatory.registry import RepositoryRegistry, RepositoryRecord
from genesis.observatory.miner import RepositoryMiner
from genesis.usir import USIRGraph, USIRNode, USIRKind
from genesis.usir.parsers.typescript import TypeScriptAdapter, JavaScriptAdapter


# ── Registry Tests ──

class TestRepositoryRegistry:
    def test_create_and_get(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            reg = RepositoryRegistry(db_path)
            record = reg.register("test/repo", "https://example.com", "github")
            assert record.id == "github::test/repo"
            assert record.name == "test/repo"
            assert record.status == "pending"

            fetched = reg.get("github::test/repo")
            assert fetched is not None
            assert fetched.name == "test/repo"
            assert fetched.url == "https://example.com"
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_update(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            reg = RepositoryRegistry(db_path)
            reg.register("test/repo", source="local")
            reg.update("local::test/repo", status="ready", file_count=42)
            r = reg.get("local::test/repo")
            assert r is not None
            assert r.status == "ready"
            assert r.file_count == 42
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_list_and_count(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            reg = RepositoryRegistry(db_path)
            reg.register("a", source="local")
            reg.register("b", source="github")
            reg.register("c", source="local")

            assert reg.count() == 3
            local_repos = reg.list_repos(source="local")
            assert len(local_repos) == 2

            reg.update("local::a", status="ready")
            ready = reg.list_repos(status="ready")
            assert len(ready) == 1
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_summary(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            reg = RepositoryRegistry(db_path)
            reg.register("x", source="local")
            reg.update("local::x", status="ready", file_count=10, line_count=100,
                       usir_node_count=50)
            s = reg.summary()
            assert s["total_repos"] == 1
            assert s["ready"] == 1
            assert s["total_files"] == 10
            assert s["total_lines"] == 100
            assert s["total_usir_nodes"] == 50
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_log(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            reg = RepositoryRegistry(db_path)
            reg.register("test/repo")
            reg._log("local::test/repo", "test_action", "test details")
            log = reg.get_log("local::test/repo")
            assert len(log) == 2  # register + log
            assert log[0]["action"] == "test_action"
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_metadata(self):
        rec = RepositoryRecord(id="t", name="test")
        rec.metadata = {"key": "value"}
        assert rec.metadata == {"key": "value"}
        d = rec.to_dict()
        assert d["metadata"] == {"key": "value"}
        assert d["name"] == "test"


# ── ObservatoryGraph Tests ──

class TestObservatoryGraph:
    def test_add_repo_graph(self):
        graph = ObservatoryGraph()
        usir = USIRGraph()
        c1 = USIRNode(id="class1", kind=USIRKind.CLASS, name="TestClass")
        c2 = USIRNode(id="class2", kind=USIRKind.INTERFACE, name="TestInterface")
        usir.add_node(c1)
        usir.add_node(c2)
        usir.add_edge("class1", "class2", "implements")
        usir.add_edge("class2", "class1", "dependency")

        count = graph.add_repo_graph("repo1", "python", usir)
        assert count == 2
        assert graph.summary()["nodes"] == 2
        assert graph.summary()["edges"] == 2
        assert graph.summary()["repositories"] == 1

    def test_find_by_name(self):
        graph = ObservatoryGraph()
        usir = USIRGraph()
        usir.add_node(USIRNode(id="f1", kind=USIRKind.FUNCTION, name="hello"))
        graph.add_repo_graph("r1", "python", usir)

        found = graph.find_by_name("hello")
        assert len(found) == 1
        assert found[0].name == "hello"

        not_found = graph.find_by_name("nonexistent")
        assert len(not_found) == 0

    def test_find_by_kind(self):
        graph = ObservatoryGraph()
        usir1 = USIRGraph()
        usir1.add_node(USIRNode(id="c1", kind=USIRKind.CLASS, name="A"))
        usir1.add_node(USIRNode(id="c2", kind=USIRKind.CLASS, name="B"))
        usir1.add_node(USIRNode(id="f1", kind=USIRKind.FUNCTION, name="f"))

        graph.add_repo_graph("r1", "python", usir1)
        classes = graph.find_by_kind("class")
        assert len(classes) == 2
        funcs = graph.find_by_kind("function")
        assert len(funcs) == 1

    def test_find_by_repo(self):
        graph = ObservatoryGraph()
        usir1 = USIRGraph()
        usir1.add_node(USIRNode(id="c1", kind=USIRKind.CLASS, name="A"))
        usir2 = USIRGraph()
        usir2.add_node(USIRNode(id="c2", kind=USIRKind.CLASS, name="B"))

        graph.add_repo_graph("repo1", "python", usir1)
        graph.add_repo_graph("repo2", "python", usir2)

        assert len(graph.find_by_repo("repo1")) == 1
        assert len(graph.find_by_repo("repo2")) == 1

    def test_find_similar(self):
        graph = ObservatoryGraph()
        usir = USIRGraph()
        usir.add_node(USIRNode(id="n1", kind=USIRKind.CLASS, name="SameName"))
        graph.add_repo_graph("repo1", "python", usir)
        usir2 = USIRGraph()
        usir2.add_node(USIRNode(id="n2", kind=USIRKind.CLASS, name="SameName"))
        graph.add_repo_graph("repo2", "python", usir2)

        similar = graph.find_similar("repo1::n1", threshold=0.4)
        assert len(similar) == 1
        assert similar[0][0] == "repo2::n2"

    def test_cross_repo_edge(self):
        graph = ObservatoryGraph()
        usir1 = USIRGraph()
        usir1.add_node(USIRNode(id="a", kind=USIRKind.CLASS, name="A"))
        usir2 = USIRGraph()
        usir2.add_node(USIRNode(id="b", kind=USIRKind.CLASS, name="B"))
        graph.add_repo_graph("r1", "python", usir1)
        graph.add_repo_graph("r2", "python", usir2)

        graph.add_cross_repo_edge("r1::a", "r2::b", "protocol_match", 0.8)
        cross = graph.cross_repo_dependencies()
        assert len(cross) == 1
        assert cross[0].kind == "protocol_match"
        assert cross[0].weight == 0.8

    def test_common_patterns(self):
        graph = ObservatoryGraph()
        usir = USIRGraph()
        usir.add_node(USIRNode(id="x", kind=USIRKind.CLASS, name="Common"))
        graph.add_repo_graph("r1", "python", usir)
        usir2 = USIRGraph()
        usir2.add_node(USIRNode(id="y", kind=USIRKind.CLASS, name="Common"))
        graph.add_repo_graph("r2", "python", usir2)

        patterns = graph.common_patterns()
        assert patterns["total"] >= 1
        assert any(p["name"] == "Common" for p in patterns["patterns"])

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            graph = ObservatoryGraph(storage_path=tmp)
            usir = USIRGraph()
            usir.add_node(USIRNode(id="s1", kind=USIRKind.CLASS, name="SaveTest"))
            graph.add_repo_graph("repo_save", "python", usir)
            graph.save("test_save")

            graph2 = ObservatoryGraph(storage_path=tmp)
            graph2.load("test_save")
            assert graph2.summary()["nodes"] == 1
            assert graph2.summary()["repositories"] == 1
            found = graph2.find_by_name("SaveTest")
            assert len(found) == 1

    def test_snapshot(self):
        graph = ObservatoryGraph()
        usir = USIRGraph()
        usir.add_node(USIRNode(id="n1", kind=USIRKind.CLASS, name="N"))
        graph.add_repo_graph("r1", "python", usir)
        snap = graph.snapshot(ris_score=0.75)
        assert snap.repo_count == 1
        assert snap.node_count >= 1
        assert snap.ris_score == 0.75

    def test_empty_graph(self):
        graph = ObservatoryGraph()
        s = graph.summary()
        assert s["nodes"] == 0
        assert s["repositories"] == 0
        assert s["edges"] == 0
        assert s["patterns_available"] == 0

    def test_multiple_languages(self):
        graph = ObservatoryGraph()
        usir1 = USIRGraph()
        usir1.add_node(USIRNode(id="p", kind=USIRKind.CLASS, name="Py"))
        graph.add_repo_graph("r1", "python", usir1)
        usir2 = USIRGraph()
        usir2.add_node(USIRNode(id="t", kind=USIRKind.CLASS, name="Ts"))
        graph.add_repo_graph("r2", "typescript", usir2)

        langs = graph.summary()["languages"]
        assert langs.get("python") == 1
        assert langs.get("typescript") == 1


# ── TypeScript Adapter Tests ──

SAMPLE_TS = """
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

interface User {
  id: number;
  name: string;
  email: string;
}

type Status = 'active' | 'inactive';

enum Role {
  Admin,
  User,
  Guest
}

@Injectable({ providedIn: 'root' })
class UserService implements OnInit {
  private users: User[] = [];
  private apiUrl: string = '/api/users';

  constructor(private http: HttpClient) {}

  async getUsers(): Promise<User[]> {
    return this.users;
  }

  private validateUser(user: User): boolean {
    return user.id > 0;
  }
}

export default UserService;
"""

SAMPLE_JSX = """
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'https://api.example.com';

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    const result = await axios.get(API_BASE + '/users');
    setData(result.data);
  }

  return <div>{data ? data.name : 'Loading...'}</div>;
}

export default App;
"""

SAMPLE_COMMONJS = """
const express = require('express');
const { Router } = require('express');
const bodyParser = require('body-parser');
const app = express();
module.exports = app;
"""


class TestTypeScriptAdapter:
    def setup_method(self):
        self.adapter = TypeScriptAdapter()
        self.js_adapter = JavaScriptAdapter()

    def test_file_extensions(self):
        exts = self.adapter.file_extensions()
        assert '.ts' in exts
        assert '.tsx' in exts
        assert '.js' not in exts
        assert '.mjs' not in exts

        js_exts = self.js_adapter.file_extensions()
        assert '.js' in js_exts
        assert '.ts' not in js_exts
        assert '.jsx' in js_exts
        assert '.mjs' in js_exts

    def test_detect(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False, mode='w') as f:
            f.write("const x = 1;")
            ts_path = Path(f.name)
        try:
            assert self.adapter.can_parse(ts_path)
            assert not self.js_adapter.can_parse(ts_path)
        finally:
            ts_path.unlink(missing_ok=True)

    def test_parse_typescript(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False, mode='w') as f:
            f.write(SAMPLE_TS)
            ts_path = Path(f.name)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                graph = self.adapter.parse_file(ts_path, root)
                assert graph.node_count > 0
                # should detect class, interface, enum, type, imports
                kinds = {n.kind for n in graph.nodes}
                kind_names = {k.name.lower() for k in kinds}
                assert 'class' in kind_names or any(n.kind.name.lower() == 'class' for n in graph.nodes)
        finally:
            ts_path.unlink(missing_ok=True)

    def test_parse_javascript(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode='w') as f:
            f.write(SAMPLE_JSX)
            js_path = Path(f.name)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                graph = self.js_adapter.parse_file(js_path, root)
                assert graph.node_count > 0
        finally:
            js_path.unlink(missing_ok=True)

    def test_parse_commonjs(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode='w') as f:
            f.write(SAMPLE_COMMONJS)
            js_path = Path(f.name)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                graph = self.js_adapter.parse_file(js_path, root)
                assert graph.node_count > 0
                # should detect require imports
                module_node = graph.get_node(f"javascript::{Path(js_path.name).stem}")
                # check if any node has module-level ID or imports were detected
                assert graph.node_count >= 1
        finally:
            js_path.unlink(missing_ok=True)

    def test_parse_empty_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False, mode='w') as f:
            f.write("")
            ts_path = Path(f.name)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                graph = self.adapter.parse_file(ts_path, root)
                assert graph.node_count == 1  # just the module node
        finally:
            ts_path.unlink(missing_ok=True)

    def test_parse_simple_class(self):
        source = """
class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }
    subtract(a: number, b: number): number {
        return a - b;
    }
}
"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False, mode='w') as f:
            f.write(source)
            ts_path = Path(f.name)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                graph = self.adapter.parse_file(ts_path, root)
                class_nodes = [n for n in graph.nodes if n.kind == USIRKind.CLASS]
                assert len(class_nodes) >= 1
                assert class_nodes[0].name == "Calculator"
        finally:
            ts_path.unlink(missing_ok=True)

    def test_parse_interface(self):
        source = """
interface Animal {
    name: string;
    age: number;
    makeSound(): void;
}
"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False, mode='w') as f:
            f.write(source)
            ts_path = Path(f.name)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                graph = self.adapter.parse_file(ts_path, root)
                iface_nodes = [n for n in graph.nodes if n.kind == USIRKind.INTERFACE]
                assert len(iface_nodes) >= 1
                assert iface_nodes[0].name == "Animal"
        finally:
            ts_path.unlink(missing_ok=True)

    def test_parse_enum(self):
        source = """
enum Direction {
    Up,
    Down,
    Left,
    Right
}
"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False, mode='w') as f:
            f.write(source)
            ts_path = Path(f.name)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                graph = self.adapter.parse_file(ts_path, root)
                enum_nodes = [n for n in graph.nodes if n.kind == USIRKind.ENUM]
                assert len(enum_nodes) >= 1
        finally:
            ts_path.unlink(missing_ok=True)

    def test_parse_type_alias(self):
        source = """
type Point = {
    x: number;
    y: number;
};
"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False, mode='w') as f:
            f.write(source)
            ts_path = Path(f.name)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                graph = self.adapter.parse_file(ts_path, root)
                alias_nodes = [n for n in graph.nodes if n.kind == USIRKind.ALIAS]
                assert len(alias_nodes) >= 1
        finally:
            ts_path.unlink(missing_ok=True)

    def test_language_name(self):
        assert self.adapter.language_name() == "typescript"
        assert self.js_adapter.language_name() == "javascript"


# ── Integration: Registry + Graph combined ──

class TestRegistryGraphIntegration:
    def test_register_and_graph(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            reg = RepositoryRegistry(db_path)
            reg.register("integrated/repo", "https://example.com", "github")
            reg.update("github::integrated/repo", status="ready", file_count=5)

            graph = ObservatoryGraph()
            usir = USIRGraph()
            usir.add_node(USIRNode(id="c1", kind=USIRKind.CLASS, name="Integrated"))
            graph.add_repo_graph("github::integrated/repo", "python", usir)

            assert reg.count("ready") == 1
            assert graph.summary()["nodes"] == 1
            assert graph.find_by_name("Integrated")[0].repo_id == "github::integrated/repo"
        finally:
            Path(db_path).unlink(missing_ok=True)
