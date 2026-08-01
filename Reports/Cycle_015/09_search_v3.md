# Cycle 015 — Engineering Search 3.0 (M106)

## Current State

`SearchEverywhere` modal screen (ctrl+p):
- 10 sources: Events, Agents, Tasks, Services, Audit, Conversations, Commands, Reports
- TF-IDF-style text relevance ranking
- Filter buttons for source type
- No debounce (requeries on every keystroke)

## Target

Search becomes the PRIMARY navigation system. Search anything: repositories, files, classes, functions, events, knowledge, memory, reports, architecture, providers, agents, tasks, benchmarks, plugins, commands, conversations, timeline, settings.

## Search Sources

| Source | Current | Target | Backend |
|--------|---------|--------|---------|
| Events | ✅ | ✅ | EventStore query |
| Agents | ✅ | ✅ | AgentRuntime.list_agents() |
| Tasks | ✅ | ✅ | TaskGraph.get_by_status() |
| Services | ✅ | ✅ | ServiceRegistry |
| Audit | ✅ | ✅ | AuditLog.query() |
| Conversations | ✅ | ✅ | ConversationEngine.search() |
| Commands | ✅ | ✅ | COMMANDS list |
| Reports | ✅ | ✅ | Filesystem scan |
| Files | ❌ | ✅ | Git ls-files / glob |
| Classes | ❌ | ✅ | AST scanning |
| Functions | ❌ | ✅ | AST scanning |
| Knowledge | ❌ | ✅ | UnifiedGraph query |
| Memory | ❌ | ✅ | UniversalMemorySystem |
| Architecture | ❌ | ✅ | Repository graph |
| Providers | ❌ | ✅ | ProviderRegistry |
| Benchmarks | ❌ | ✅ | Benchmark data |
| Plugins | ❌ | ✅ | PluginManager |
| Settings | ❌ | ✅ | Config keys |
| Timeline | ❌ | ✅ | Event timeline |
| Recommendations | ❌ | ✅ | Rules engine |

## Features

| Feature | Current | Target |
|---------|---------|--------|
| Sources | 10 | 20+ |
| Ranking | TF-IDF | BM25 + recency + relevance |
| Debounce | None | 200ms |
| Semantic search | None | Embedding-based (via AI provider) |
| Relationship search | None | Graph neighborhood |
| Context search | None | Session-aware |
| Recent searches | None | Last 20 queries |
| Pinned searches | None | Save queries |
| Saved searches | None | Persistent storage |
| Preview | None | Inline preview pane |
| Quick actions | None | ctrl+enter → execute |
| Filters | Source buttons | Type + date + relevance |
| Grouping | None | By source + type |
| Keyboard nav | Arrow + enter | vim-style j/k, ctrl+num for top-5 |

## Implementation

1. Add 200ms debounce to input handler
2. Add class/function search via AST scanning of `genesis/` directory
3. Add semantic search via `AIRouter.embeddings()` + cosine similarity
4. Add relationship search via `UnifiedGraph.neighbors()` 
5. Add recent/pinned/saved search storage to UniversalMemorySystem
6. Add preview pane (right side) showing first N lines of result
7. Add quick action: ctrl+enter executes command or navigates to result
