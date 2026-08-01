# Cycle 016 — Visual Engineering (M113)

## Historical Context
The KnowledgeGraphScreen was the most misleading screen name in the app. Its docstring claimed "Interactive knowledge graph with search, filtering, relationship explorer, overlays" — zero of these existed. It was a system statistics browser with hardcoded text descriptions.

## Design
Replace text-only views with Textual's Tree widget for hierarchical entity browsing. Each entity type (Services, Agents, Tasks, Conversations) gets a tree with expandable nodes showing relationships and metadata.

## Implementation

### Rebuilt `KnowledgeGraphScreen` (`screens.py`)

**Old**: 5 views (Nodes, Edges, Types, Dependencies, Agent Overlay) — all text in ListView + RichLog
**New**: 5 views (Services, Agents, Tasks, Conversations, Dependencies) — all Tree-based with RichLog details

**View Structure:**
| View | Tree Root | Children | Detail Panel |
|------|-----------|----------|--------------|
| Services | Services | Each service + versions | Capabilities via child nodes |
| Agents | Agents | Each agent name + role | Status, model, tasks, recent tasks via children |
| Tasks | Tasks | Each task + status | Dependencies via child tree |
| Conversations | Conversations | Each conversation | Participants via child nodes |
| Dependencies | Dependency Graph | Summary stats + task deps | Expandable dep chains |

**Color System:**
- Agent status: `AGENT_STATUS_COLOR` (green/cyan/red/yellow/dim)
- Task status: `TASK_STATUS_COLOR` (dim/yellow/cyan/green/red)
- Services: magenta
- Conversations: blue

**Filtering**: Input field at top, filter applied on Submit (Enter). Filters across all entities by name/role/label.

## Files Changed
- `genesis/desktop/screens.py` — complete rewrite of `KnowledgeGraphScreen`
- `genesis/desktop/app.py` — CSS updated (kg-search, kg-entity-tree, kg-inspect)

## Key Decisions
- **Tree over ListView**: Tree is the closest Textual gets to a graph visualization — hierarchical, expandable, and visually structured
- **5 focused views**: Narrowed from vague "graph" to specific entity types that actually have data
- **No real graph library**: Textual doesn't support D3-style graph rendering; Tree is the pragmatic middle ground
- **Screen renamed**: "Entity Explorer" in title, "graph" route retained for backward compat
