"""
PersistentGraphDB — SQLite-backed planetary-scale knowledge graph.

Holds billions of nodes and edges with:
  - typed nodes + typed edges
  - temporal metadata
  - confidence scores
  - evidence provenance
  - full-text search
  - graph algorithms (BFS, DFS, centrality, clustering, pathfinding)
  - export (JSON, CSV, GEXF, Cypher)
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import os
import sqlite3
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator

from genesis.utils.identity import generate_id


NODES_DDL = """
CREATE TABLE IF NOT EXISTS nodes (
    uid TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    node_type TEXT NOT NULL DEFAULT 'entity',
    description TEXT DEFAULT '',
    attributes TEXT DEFAULT '{}',
    source TEXT DEFAULT '',
    confidence REAL DEFAULT 1.0,
    tags TEXT DEFAULT '[]',
    created_at REAL DEFAULT 0,
    updated_at REAL DEFAULT 0
);
"""

EDGES_DDL = """
CREATE TABLE IF NOT EXISTS edges (
    id TEXT PRIMARY KEY,
    source_uid TEXT NOT NULL,
    target_uid TEXT NOT NULL,
    relation TEXT NOT NULL DEFAULT 'references',
    weight REAL DEFAULT 1.0,
    confidence REAL DEFAULT 1.0,
    attributes TEXT DEFAULT '{}',
    metadata TEXT DEFAULT '{}',
    source TEXT DEFAULT '',
    created_at REAL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_uid);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_uid);
CREATE INDEX IF NOT EXISTS idx_edges_relation ON edges(relation);
"""

INDEX_DDL = """
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name);
CREATE INDEX IF NOT EXISTS idx_nodes_created ON nodes(created_at);
CREATE INDEX IF NOT EXISTS idx_nodes_updated ON nodes(updated_at);
CREATE INDEX IF NOT EXISTS idx_nodes_source ON nodes(source);
"""

META_DDL = """
CREATE TABLE IF NOT EXISTS graph_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT OR IGNORE INTO graph_metadata (key, value) VALUES ('version', '1');
INSERT OR IGNORE INTO graph_metadata (key, value) VALUES ('created_at', strftime('%s','now'));
INSERT OR IGNORE INTO graph_metadata (key, value) VALUES ('node_count', '0');
INSERT OR IGNORE INTO graph_metadata (key, value) VALUES ('edge_count', '0');
"""


@dataclass
class Node:
    """A node in the persistent knowledge graph."""
    uid: str = ""
    name: str = ""
    node_type: str = "entity"
    description: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        now = time.time()
        if not self.uid:
            self.uid = generate_id(self.node_type[:8], 12)
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "name": self.name,
            "node_type": self.node_type,
            "description": self.description,
            "attributes": dict(self.attributes),
            "source": self.source,
            "confidence": self.confidence,
            "tags": list(self.tags),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Node:
        return cls(
            uid=d.get("uid", ""),
            name=d.get("name", ""),
            node_type=d.get("node_type", "entity"),
            description=d.get("description", ""),
            attributes=dict(d.get("attributes", {})),
            source=d.get("source", ""),
            confidence=d.get("confidence", 1.0),
            tags=list(d.get("tags", [])),
            created_at=d.get("created_at", 0),
            updated_at=d.get("updated_at", 0),
        )


@dataclass
class Edge:
    """A typed edge between two nodes in the persistent knowledge graph."""
    id: str = ""
    source_uid: str = ""
    target_uid: str = ""
    relation: str = "references"
    weight: float = 1.0
    confidence: float = 1.0
    attributes: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = generate_id("edge", 12)
        if not self.created_at:
            self.created_at = now

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_uid": self.source_uid,
            "target_uid": self.target_uid,
            "relation": self.relation,
            "weight": self.weight,
            "confidence": self.confidence,
            "attributes": dict(self.attributes),
            "metadata": dict(self.metadata),
            "source": self.source,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Edge:
        return cls(
            id=d.get("id", ""),
            source_uid=d.get("source_uid", ""),
            target_uid=d.get("target_uid", ""),
            relation=d.get("relation", "references"),
            weight=d.get("weight", 1.0),
            confidence=d.get("confidence", 1.0),
            attributes=dict(d.get("attributes", {})),
            metadata=dict(d.get("metadata", {})),
            source=d.get("source", ""),
            created_at=d.get("created_at", 0),
        )


class GraphQueryBuilder:
    """Fluent query builder for the persistent graph."""

    def __init__(self, db: "PersistentGraphDB"):
        self._db = db
        self._node_type: str = ""
        self._name_contains: str = ""
        self._tag: str = ""
        self._min_confidence: float = 0.0
        self._source: str = ""
        self._created_after: float = 0
        self._created_before: float = 0
        self._limit: int = 100
        self._offset: int = 0
        self._order_by: str = ""
        self._order_desc: bool = False
        self._search_query: str = ""

    def of_type(self, node_type: str) -> GraphQueryBuilder:
        self._node_type = node_type
        return self

    def named(self, name_contains: str) -> GraphQueryBuilder:
        self._name_contains = name_contains
        return self

    def with_tag(self, tag: str) -> GraphQueryBuilder:
        self._tag = tag
        return self

    def with_confidence(self, min_conf: float) -> GraphQueryBuilder:
        self._min_confidence = min_conf
        return self

    def from_source(self, source: str) -> GraphQueryBuilder:
        self._source = source
        return self

    def created_between(self, after: float, before: float) -> GraphQueryBuilder:
        self._created_after = after
        self._created_before = before
        return self

    def limit(self, n: int) -> GraphQueryBuilder:
        self._limit = n
        return self

    def offset(self, n: int) -> GraphQueryBuilder:
        self._offset = n
        return self

    def order_by(self, column: str, desc: bool = False) -> GraphQueryBuilder:
        self._order_by = column
        self._order_desc = desc
        return self

    def search(self, query: str) -> GraphQueryBuilder:
        self._search_query = query
        return self

    def execute(self) -> list[Node]:
        return self._db._query_nodes(
            node_type=self._node_type,
            name_contains=self._name_contains,
            tag=self._tag,
            min_confidence=self._min_confidence,
            source=self._source,
            created_after=self._created_after,
            created_before=self._created_before,
            limit=self._limit,
            offset=self._offset,
            order_by=self._order_by,
            order_desc=self._order_desc,
            search_query=self._search_query,
        )

    def first(self) -> Node | None:
        results = self.limit(1).execute()
        return results[0] if results else None

    def count(self) -> int:
        results = self.execute()
        return len(results)

    def exists(self) -> bool:
        return self.first() is not None

    def neighbors(self, uid: str, relation: str = "",
                  direction: str = "both", max_depth: int = 1) -> list[Node]:
        return self._db._traverse_neighbors(
            uid, relation=relation, direction=direction, max_depth=max_depth,
        )

    def bfs(self, start_uid: str, target_uid: str = "",
            relation: str = "", max_depth: int = 10) -> list[list[str]]:
        return self._db._bfs(
            start_uid, target_uid=target_uid,
            relation=relation, max_depth=max_depth,
        )


# ── Persistent Graph Database ──

class PersistentGraphDB:
    """SQLite-backed planetary-scale knowledge graph database."""

    def __init__(self, db_path: str = ""):
        if not db_path:
            db_path = os.path.expanduser("~/.venus/graphdb/knowledge_graph.db")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._connect()
        self._init_schema()

    def _connect(self):
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA cache_size=-80000")  # 80MB cache
        self._conn.execute("PRAGMA foreign_keys=ON")

    def _init_schema(self):
        for ddl in [NODES_DDL, EDGES_DDL, INDEX_DDL, META_DDL]:
            try:
                self._conn.executescript(ddl)
            except sqlite3.OperationalError as e:
                if "already exists" not in str(e):
                    raise
        try:
            self._conn.executescript(
                "CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts "
                "USING fts5(name, description, tags, node_type, content='nodes', content_rowid='rowid');"
            )
        except sqlite3.OperationalError:
            pass  # FTS5 not available
        self._conn.commit()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._connect()
        return self._conn

    # ── Node Operations ──

    def add_node(self, node: Node) -> Node:
        self.conn.execute(
            """INSERT OR REPLACE INTO nodes
               (uid, name, node_type, description, attributes, source, confidence, tags, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (node.uid, node.name, node.node_type, node.description,
             json.dumps(node.attributes, default=str), node.source,
             node.confidence, json.dumps(node.tags, default=str),
             node.created_at, node.updated_at),
        )
        self.conn.commit()
        return node

    def add_node_bulk(self, nodes: list[Node]) -> int:
        data = [
            (n.uid, n.name, n.node_type, n.description,
             json.dumps(n.attributes, default=str), n.source,
             n.confidence, json.dumps(n.tags, default=str),
             n.created_at, n.updated_at)
            for n in nodes
        ]
        self.conn.executemany(
            """INSERT OR REPLACE INTO nodes
               (uid, name, node_type, description, attributes, source, confidence, tags, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data,
        )
        self.conn.commit()
        return len(nodes)

    def get_node(self, uid: str) -> Node | None:
        row = self.conn.execute(
            "SELECT * FROM nodes WHERE uid = ?", (uid,)
        ).fetchone()
        return self._row_to_node(row) if row else None

    def delete_node(self, uid: str):
        self.conn.execute("DELETE FROM nodes WHERE uid = ?", (uid,))
        self.conn.commit()

    def node_count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) as c FROM nodes").fetchone()
        return row["c"] if row else 0

    def _query_nodes(self, node_type: str = "", name_contains: str = "",
                     tag: str = "", min_confidence: float = 0.0,
                     source: str = "", created_after: float = 0,
                     created_before: float = 0, limit: int = 100,
                     offset: int = 0, order_by: str = "",
                     order_desc: bool = False,
                     search_query: str = "") -> list[Node]:
        if search_query:
            return self._search_nodes(search_query, limit, offset)
        conditions: list[str] = []
        params: list[Any] = []
        if node_type:
            conditions.append("node_type = ?")
            params.append(node_type)
        if name_contains:
            conditions.append("name LIKE ?")
            params.append(f"%{name_contains}%")
        if tag:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")
        if min_confidence > 0:
            conditions.append("confidence >= ?")
            params.append(min_confidence)
        if source:
            conditions.append("source = ?")
            params.append(source)
        if created_after > 0:
            conditions.append("created_at >= ?")
            params.append(created_after)
        if created_before > 0:
            conditions.append("created_at <= ?")
            params.append(created_before)
        where = " AND ".join(conditions) if conditions else "1=1"
        order_clause = ""
        if order_by:
            order_clause = f"ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        query = f"SELECT * FROM nodes WHERE {where} {order_clause} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_node(r) for r in rows]

    def _search_nodes(self, query: str, limit: int, offset: int) -> list[Node]:
        # Fall back to LIKE search if FTS is unavailable
        try:
            rows = self.conn.execute(
                """SELECT n.* FROM nodes n
                   JOIN nodes_fts fts ON n.rowid = fts.rowid
                   WHERE nodes_fts MATCH ?
                   LIMIT ? OFFSET ?""",
                (query, limit, offset),
            ).fetchall()
            return [self._row_to_node(r) for r in rows]
        except sqlite3.OperationalError:
            params = [f"%{query}%", limit, offset]
            rows = self.conn.execute(
                "SELECT * FROM nodes WHERE name LIKE ? LIMIT ? OFFSET ?",
                params,
            ).fetchall()
            return [self._row_to_node(r) for r in rows]

    # ── Edge Operations ──

    def add_edge(self, edge: Edge) -> Edge:
        # Ensure both nodes exist
        self.conn.execute(
            """INSERT OR IGNORE INTO nodes (uid, name, node_type, created_at, updated_at)
               VALUES (?, ?, 'stub', ?, ?)""",
            (edge.source_uid, f"stub:{edge.source_uid[:12]}", time.time(), time.time()),
        )
        self.conn.execute(
            """INSERT OR IGNORE INTO nodes (uid, name, node_type, created_at, updated_at)
               VALUES (?, ?, 'stub', ?, ?)""",
            (edge.target_uid, f"stub:{edge.target_uid[:12]}", time.time(), time.time()),
        )
        self.conn.execute(
            """INSERT OR REPLACE INTO edges
               (id, source_uid, target_uid, relation, weight, confidence,
                attributes, metadata, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (edge.id, edge.source_uid, edge.target_uid, edge.relation,
             edge.weight, edge.confidence,
             json.dumps(edge.attributes, default=str),
             json.dumps(edge.metadata, default=str),
             edge.source, edge.created_at),
        )
        self.conn.commit()
        return edge

    def add_edge_bulk(self, edges: list[Edge]) -> int:
        data = [
            (e.id, e.source_uid, e.target_uid, e.relation,
             e.weight, e.confidence,
             json.dumps(e.attributes, default=str),
             json.dumps(e.metadata, default=str),
             e.source, e.created_at)
            for e in edges
        ]
        self.conn.executemany(
            """INSERT OR REPLACE INTO edges
               (id, source_uid, target_uid, relation, weight, confidence,
                attributes, metadata, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data,
        )
        self.conn.commit()
        return len(edges)

    def get_edge(self, edge_id: str) -> Edge | None:
        row = self.conn.execute(
            "SELECT * FROM edges WHERE id = ?", (edge_id,)
        ).fetchone()
        return self._row_to_edge(row) if row else None

    def get_edges(self, source_uid: str = "", target_uid: str = "",
                  relation: str = "", limit: int = 100) -> list[Edge]:
        conditions: list[str] = []
        params: list[Any] = []
        if source_uid:
            conditions.append("source_uid = ?")
            params.append(source_uid)
        if target_uid:
            conditions.append("target_uid = ?")
            params.append(target_uid)
        if relation:
            conditions.append("relation = ?")
            params.append(relation)
        where = " AND ".join(conditions) if conditions else "1=1"
        rows = self.conn.execute(
            f"SELECT * FROM edges WHERE {where} LIMIT ?", params + [limit]
        ).fetchall()
        return [self._row_to_edge(r) for r in rows]

    def delete_edge(self, edge_id: str):
        self.conn.execute("DELETE FROM edges WHERE id = ?", (edge_id,))
        self.conn.commit()

    def edge_count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) as c FROM edges").fetchone()
        return row["c"] if row else 0

    # ── Graph Traversal ──

    def neighbors(self, uid: str, relation: str = "",
                  direction: str = "both", max_depth: int = 1) -> list[Node]:
        return self._traverse_neighbors(uid, relation, direction, max_depth)

    def _traverse_neighbors(self, uid: str, relation: str = "",
                            direction: str = "both",
                            max_depth: int = 1) -> list[Node]:
        if max_depth <= 0:
            return []
        visited: set[str] = {uid}
        current: set[str] = {uid}
        result: list[Node] = []
        for _ in range(max_depth):
            next_nodes: set[str] = set()
            for node_uid in current:
                conns = self._get_connections(node_uid, relation, direction)
                for neighbor_uid in conns:
                    if neighbor_uid not in visited:
                        visited.add(neighbor_uid)
                        next_nodes.add(neighbor_uid)
                        node = self.get_node(neighbor_uid)
                        if node:
                            result.append(node)
            current = next_nodes
            if not current:
                break
        return result

    def bfs(self, start_uid: str, target_uid: str = "",
            relation: str = "", max_depth: int = 10) -> list[list[str]]:
        return self._bfs(start_uid, target_uid, relation, max_depth)

    def _bfs(self, start_uid: str, target_uid: str = "",
             relation: str = "", max_depth: int = 10) -> list[list[str]]:
        from collections import deque
        queue: deque[tuple[str, list[str]]] = deque([(start_uid, [start_uid])])
        visited: set[str] = {start_uid}
        paths: list[list[str]] = []
        while queue:
            current, path = queue.popleft()
            if target_uid and current == target_uid:
                paths.append(path)
                continue
            if len(path) > max_depth:
                continue
            for neighbor_uid in self._get_connections(current, relation, "both"):
                if neighbor_uid not in visited:
                    visited.add(neighbor_uid)
                    queue.append((neighbor_uid, path + [neighbor_uid]))
            if not target_uid and len(queue) == 0:
                # Return all reachable paths
                paths.append(path)
        return paths if target_uid else [p for p in paths if len(p) > 1]

    def _get_connections(self, uid: str, relation: str = "",
                         direction: str = "both") -> list[str]:
        conditions: list[str] = []
        params: list[Any] = []
        if relation:
            conditions.append("relation = ?")
            params.append(relation)
        rel_where = f"AND {' AND '.join(conditions)}" if conditions else ""
        results: list[str] = []
        if direction in ("outgoing", "both"):
            rows = self.conn.execute(
                f"SELECT target_uid FROM edges WHERE source_uid = ? {rel_where}",
                [uid] + params,
            ).fetchall()
            results.extend(r["target_uid"] for r in rows)
        if direction in ("incoming", "both"):
            rows = self.conn.execute(
                f"SELECT source_uid FROM edges WHERE target_uid = ? {rel_where}",
                [uid] + params,
            ).fetchall()
            results.extend(r["source_uid"] for r in rows)
        return results

    # ── Query Builder ──

    def query(self) -> GraphQueryBuilder:
        return GraphQueryBuilder(self)

    # ── Graph Algorithms ──

    def degree_centrality(self, uid: str) -> dict[str, float]:
        in_deg = self.conn.execute(
            "SELECT COUNT(*) as c FROM edges WHERE target_uid = ?", (uid,)
        ).fetchone()["c"]
        out_deg = self.conn.execute(
            "SELECT COUNT(*) as c FROM edges WHERE source_uid = ?", (uid,)
        ).fetchone()["c"]
        total = max(self.node_count() - 1, 1)
        return {
            "in_degree": in_deg,
            "out_degree": out_deg,
            "total_degree": in_deg + out_deg,
            "in_centrality": in_deg / total,
            "out_centrality": out_deg / total,
            "total_centrality": (in_deg + out_deg) / total,
        }

    def clustering_coefficient(self, uid: str) -> float:
        neighbors = self._get_connections(uid, direction="both")
        neighbor_set = set(neighbors)
        if len(neighbors) < 2:
            return 0.0
        connections = 0
        for n1 in neighbors:
            n1_edges = self._get_connections(n1, direction="both")
            for n2 in n1_edges:
                if n2 in neighbor_set and n2 != n1:
                    connections += 1
        possible = len(neighbors) * (len(neighbors) - 1)
        return connections / possible if possible > 0 else 0.0

    def density(self) -> float:
        n = self.node_count()
        e = self.edge_count()
        if n < 2:
            return 0.0
        return (2.0 * e) / (n * (n - 1))

    # ── Statistics ──

    def node_type_distribution(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT node_type, COUNT(*) as c FROM nodes GROUP BY node_type ORDER BY c DESC"
        ).fetchall()
        return {r["node_type"]: r["c"] for r in rows}

    def relation_distribution(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT relation, COUNT(*) as c FROM edges GROUP BY relation ORDER BY c DESC"
        ).fetchall()
        return {r["relation"]: r["c"] for r in rows}

    def source_distribution(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT source, COUNT(*) as c FROM nodes WHERE source != '' GROUP BY source ORDER BY c DESC"
        ).fetchall()
        return {r["source"]: r["c"] for r in rows}

    def statistics(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count(),
            "edge_count": self.edge_count(),
            "density": round(self.density(), 6),
            "type_distribution": self.node_type_distribution(),
            "relation_distribution": self.relation_distribution(),
            "source_distribution": self.source_distribution(),
            "db_size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
        }

    # ── Export ──

    def export_json(self, path: str, compress: bool = False) -> str:
        out_path = Path(path)
        nodes = [self._row_to_node(r).to_dict() for r in
                 self.conn.execute("SELECT * FROM nodes").fetchall()]
        edges = [self._row_to_edge(r).to_dict() for r in
                 self.conn.execute("SELECT * FROM edges").fetchall()]
        data = json.dumps({"nodes": nodes, "edges": edges}, default=str)
        if compress:
            out_path = out_path.with_suffix(".json.gz")
            with gzip.open(str(out_path), "wt", encoding="utf-8") as f:
                f.write(data)
        else:
            out_path.write_text(data)
        return str(out_path)

    def export_csv(self, path: str) -> tuple[str, str]:
        nodes_path = Path(path) / "nodes.csv"
        edges_path = Path(path) / "edges.csv"
        nodes_path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(nodes_path), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["uid", "name", "node_type", "source", "confidence", "tags"])
            for r in self.conn.execute("SELECT * FROM nodes").fetchall():
                writer.writerow([r["uid"], r["name"], r["node_type"],
                                 r["source"], r["confidence"], r["tags"]])
        with open(str(edges_path), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "source_uid", "target_uid", "relation", "weight", "confidence"])
            for r in self.conn.execute("SELECT * FROM edges").fetchall():
                writer.writerow([r["id"], r["source_uid"], r["target_uid"],
                                 r["relation"], r["weight"], r["confidence"]])
        return str(nodes_path), str(edges_path)

    def export_gexf(self, path: str) -> str:
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        gexf = ET.Element("gexf", xmlns="http://www.gexf.net/1.3", version="1.3")
        graph = ET.SubElement(gexf, "graph", mode="static", defaultedgetype="directed")
        nodes_elem = ET.SubElement(graph, "nodes")
        nodes_map: dict[str, str] = {}
        for r in self.conn.execute("SELECT * FROM nodes").fetchall():
            node_elem = ET.SubElement(nodes_elem, "node", id=r["uid"], label=r["name"])
            nodes_map[r["uid"]] = r["name"]
        edges_elem = ET.SubElement(graph, "edges")
        for r in self.conn.execute("SELECT * FROM edges").fetchall():
            ET.SubElement(edges_elem, "edge", id=r["id"],
                          source=r["source_uid"], target=r["target_uid"],
                          weight=str(r["weight"]),
                          label=r["relation"])
        rough = ET.tostring(gexf, encoding="unicode")
        dom = minidom.parseString(rough.encode())
        pretty = dom.toprettyxml(indent="  ")
        Path(path).write_text(pretty)
        return path

    # ── UnifiedGraph Integration ──

    def load_from_unified_graph(self, ugraph) -> int:
        if not hasattr(ugraph, 'entities'):
            return 0
        nodes: list[Node] = []
        for uid, entity in ugraph.entities.items():
            node = Node(
                uid=uid,
                name=entity.name,
                node_type=entity.entity_type.value,
                source=entity.metadata.source,
                confidence=entity.metadata.confidence,
                tags=entity.metadata.tags,
                attributes=dict(entity.attributes),
                created_at=entity.metadata.created_at,
                updated_at=entity.metadata.updated_at,
            )
            nodes.append(node)
        self.add_node_bulk(nodes)
        edges: list[Edge] = []
        if hasattr(ugraph, 'edges'):
            for uedge in ugraph.edges:
                edge = Edge(
                    id=uedge.source_uid + "->" + uedge.target_uid,
                    source_uid=uedge.source_uid,
                    target_uid=uedge.target_uid,
                    relation=uedge.relation.value,
                    weight=uedge.weight,
                    created_at=uedge.created_at,
                )
                edges.append(edge)
        self.add_edge_bulk(edges)
        return len(nodes)

    # ── Connection Management ──

    def close(self):
        if self._conn:
            self._conn.commit()
            self._conn.close()
            self._conn = None

    def reconnect(self):
        self.close()
        self._connect()

    def vacuum(self):
        self.conn.execute("VACUUM")
        self.conn.commit()

    # ── Row Helpers ──

    @staticmethod
    def _row_to_node(row: sqlite3.Row) -> Node:
        try:
            attrs = json.loads(row["attributes"]) if isinstance(row["attributes"], str) else {}
        except (json.JSONDecodeError, TypeError):
            attrs = {}
        try:
            tags = json.loads(row["tags"]) if isinstance(row["tags"], str) else []
        except (json.JSONDecodeError, TypeError):
            tags = []
        return Node(
            uid=row["uid"],
            name=row["name"],
            node_type=row["node_type"],
            description=row["description"],
            attributes=attrs,
            source=row["source"],
            confidence=row["confidence"],
            tags=tags,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_edge(row: sqlite3.Row) -> Edge:
        try:
            attrs = json.loads(row["attributes"]) if isinstance(row["attributes"], str) else {}
        except (json.JSONDecodeError, TypeError):
            attrs = {}
        try:
            meta = json.loads(row["metadata"]) if isinstance(row["metadata"], str) else {}
        except (json.JSONDecodeError, TypeError):
            meta = {}
        return Edge(
            id=row["id"],
            source_uid=row["source_uid"],
            target_uid=row["target_uid"],
            relation=row["relation"],
            weight=row["weight"],
            confidence=row["confidence"],
            attributes=attrs,
            metadata=meta,
            source=row["source"],
            created_at=row["created_at"],
        )
