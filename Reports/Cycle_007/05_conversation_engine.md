# CYCLE 007 — REPORT 05: CONVERSATION ENGINE

## Conversations as Permanent Engineering Knowledge

⸻

## VISION

Every engineering discussion in Genesis is captured as a first-class engineering object.
Conversations are not ephemeral chat logs — they are permanent, queryable, linked
records that become part of the institutional knowledge base. Every conversation
connects to architecture, knowledge, memory, reports, tasks, benchmarks, simulations,
governance, and engineering decisions.

⸻

## PROBLEM STATEMENT

Before Cycle 007, engineering discussions happened outside Genesis:
- In CLI output that scrolls away
- In chat logs with no structure
- In README files that go stale
- In pull request comments with no cross-referencing
- In engineering memory (genesis/memory/) but without conversation structure

There was no way to:
- Search past engineering discussions
- Link a conversation to specific subsystems
- Trace the decision history of a design choice
- Branch an exploration into alternative approaches
- Extract decisions automatically

⸻

## CONVERSATION STRUCTURE

### Conversation
| Field | Type | Description |
|-------|------|-------------|
| id | str | Unique identity |
| title | str | Short description |
| objective | str | What the conversation aims to resolve |
| participants | list[str] | Agents or users involved |
| messages | list[Message] | Ordered discussion |
| links | dict[str,str] | Linked engineering objects (arch, task, etc.) |
| tags | list[str] | Categorical labels |
| summary | str | Auto-generated or manual summary |
| decisions | list[str] | Extracted decisions |
| parent_id | str | Parent conversation (for branching) |
| branch_of | str | Original conversation this branched from |

### Message
| Field | Type | Description |
|-------|------|-------------|
| id | str | Unique identity |
| role | str | user, agent, system |
| content | str | Message body |
| citations | list[str] | Referenced sources |
| links | dict[str,str] | Related engineering objects |
| timestamp | float | When sent |

⸻

## API

```python
engine = ConversationEngine(kernel)

# Create
conv = engine.create("Design Review: Caching Layer", 
                     objective="Choose caching strategy",
                     participants=["alice", "bob", "cache_agent"],
                     tags=["design", "performance"])

# Add messages
engine.add_message(conv.id, "user", "Should we use Redis?",
                   links={"architecture": "cache_layer"})
engine.add_message(conv.id, "agent", "Analysis: Redis vs Memcached...",
                   citations=["benchmark_report_42"])

# Link to engineering objects
engine.link_conversation(conv.id, "architecture", "arch_cache")
engine.link_conversation(conv.id, "task", "task_optimize_cache")

# Search
results = engine.search(query="caching", tags=["design"])

# Extract decisions
decisions = engine.extract_decisions(conv.id)
# -> ["Decision: Use Redis with LRU eviction"]

# Branch exploration
alternative = engine.branch(conv.id, "Alternative: Memcached approach")

# Summarize
summary = engine.summarize(conv.id)
```

⸻

## DECISION EXTRACTION

The engine scans messages for decision markers:
- Lines starting with "Decision:", "Approved:", "Rejected:", "Selected:"
- Extracted decisions are tracked in `conversation.decisions`
- Decisions persist across sessions

⸻

## BRANCHING

Engineering discussions naturally fork. The `branch()` method creates a new
conversation that inherits the original's participants, tags, and objective
but has its own message history. The `branch_of` field tracks the origin.

⸻

## SEARCH

Multi-dimensional search:
- Text search across title, objective, summary, and last 10 messages
- Tag filtering (AND logic)
- Participant filtering
- Linked-entity filtering
- Results sorted by `updated_at` descending

⸻

## FUTURE EXTENSIONS

- AI-powered summarization of long conversations
- Automatic contradiction detection between conversations
- Follow-up generation (suggesting next steps)
- Knowledge linking (extract key concepts into knowledge graph)
- Timeline view of all conversations for a subsystem
