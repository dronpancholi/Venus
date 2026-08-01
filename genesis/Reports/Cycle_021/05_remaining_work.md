# Remaining Work — Cycle 021 & Beyond

---

## Priority Matrix

| Priority | Item | Effort | Dependencies |
|----------|------|--------|-------------|
| P1 | Split screens.py (1,431 lines) into per-screen files with .tcss | 3d | None |
| P1 | Desktop Textual pilot tests | 2d | screens.py split |
| P2 | Migrate studio/backend.py to accept CanonicalGraphAPI | 1h | None |
| P2 | Migrate integration/project31a.py to accept CanonicalGraphAPI | 1h | None |
| P2 | Migrate platform.py to use kernel.graph.primary | 2d | None |
| P2 | Add KnowledgeGraphEngine adapter (wraps graph.engine) | 1d | None |
| P3 | Import cycle resolution (fabric ↔ automation ↔ execution) | 3d | None |
| P3 | Intelligence KnowledgeGraph adapter | 2d | None |

---

## Screen Splitting

`screens.py` (1,431 lines) is the last monolithic file in the desktop subsystem. Plan:

```
desktop/
├── screens/
│   ├── __init__.py
│   ├── main_screen.py
│   ├── graph_screen.py
│   ├── health_screen.py
│   ├── observability_screen.py
│   ├── boot_screen.py
│   ├── workspace_screen.py
│   ├── ai_screen.py
│   └── command_center_screen.py
├── styles/
│   ├── main.tcss
│   ├── graph.tcss
│   ├── health.tcss
│   └── ...
├── app.py              # Main Textual App
└── screens.py          # Deprecated
```

---

## Desktop Textual Pilot Tests

No Textual test infrastructure exists yet. Need:

1. `tests/test_desktop/` directory
2. Textual test helpers (`from textual.testing import AppTest`)
3. Screenshot-based snapshot tests
4. Integration tests for panel actions

---

## Long-term: Complete Migration

Goal: No file imports a graph class directly — all graph access goes through `kernel.graph.primary`.

Blockers:
- KnowledgeGraphEngine has unique APIs (export_cypher, export_graphml) not in CanonicalGraphAPI
- intelligence.kgraph.KnowledgeGraph has `find_nodes(kind=...)` instead of `find_nodes(node_type=...)`
- platform.py instantiates 5 graphs during boot — needs strategic refactor
