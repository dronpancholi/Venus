# Phase 0 Delta: Command Palette & Universal Search

**File:** `genesis/desktop/palette.py` — 281 lines, 2 modal screens  
**Tests:** 0

## CommandPalette

- **Trigger:** `ctrl+k`
- **Commands:** 22 (reduced from 25 — 3 dead commands removed in Cycle 014)
- **Execution:** `on_list_view_selected` routes each command to `navigate_to()`, `app.exit()`, or custom handler

**Command categories:**
- 11 screen navigation commands (home, inspector, agents, memory, repository, timeline, graph, ai, ce, reports, settings)
- 5 action commands (search, refresh, palette, quit, tasks)
- 3 CE commands (start_ce, stop_ce)
- 3 inspector sub-commands (kernel_stats, emit_event, inspector_metrics, inspector_sessions)

## SearchEverywhere

- **Trigger:** `ctrl+p`
- **Sources:** All (default), Events, Agents, Tasks, Services, Audit, Conversations, Commands, Reports
- **Ranking:** TF-IDF-style relevance score across 10+ data sources

**Search sources:**
1. `FabricKernel.instance().query_events(limit=50)` — recent events
2. `agent_runtime.list_agents()` — agent names
3. `task_graph.get_by_status("ready")` — ready tasks
4. `registry.list_services()` — registered services
5. `kernel.audit.query(limit=50)` — audit entries
6. `conversation_engine.search()` — conversations
7. `COMMANDS` list — palette commands by name/description
8. `Reports/{cycle}/*.md` — report files from disk

## Findings

1. **Shortcut claims mismatched** (fixed in Cycle 014): `repository` claimed `ctrl+p` (was search), `ai` claimed `ctrl+shift+i` (was ctrl+1), `ce` claimed `ctrl+shift+e` (was ctrl+2), `reports` claimed `ctrl+shift+r` (no binding), `settings` claimed `ctrl++` (no binding)
2. **Search refreshes on every keystroke** — no debounce, high-frequency requery on long input
3. **Search sources read from disk** — `Reports` source uses `Path.cwd()` which breaks outside project root
4. **No keyboard shortcut for search results** — must use arrow keys + enter (no ctrl+number for top-5)
5. **Palette doesn't surface emitter_test or other debug commands** — they're hidden with no feedback
6. **No plugin command integration** — palette has no mechanism for plugins to register commands

## Recommendations

1. Add 200ms debounce to SearchEverywhere input handler
2. Add `reports_dir` parameter or resolve via `Path(__file__).parent.parent`
3. Add `ctrl+1` through `ctrl+5` shortcuts for top-5 search results
4. Show "No results" message instead of empty list in palette
5. Design plugin command registration API for Palette
