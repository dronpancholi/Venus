# Phase 0 Delta: Conversation Engine

**File:** `genesis/fabric/conversations.py` — 271 lines  
**Tests:** Via `test_kernel.py`

## Architecture

```
ConversationEngine
  ├── _conversations: dict[str, Conversation]
  ├── _by_tag: dict[str, list[str]]
  ├── _by_participant: dict[str, list[str]]
  └── _by_link: dict[str, list[str]]
```

**Design philosophy:** "Conversations as first-class engineering objects" — every discussion links to architecture, knowledge, memory, reports, tasks, benchmarks, simulations, governance, commits, and decisions.

## Conversation Data Model

```python
Conversation:
  id, title, objective, participants: list[str]
  messages: list[ConversationMessage]
  links: dict[str, str]  # type -> target_id
  tags, summary, decisions: list[str]
  parent_id, branch_of (for forking)
  created_at, updated_at

ConversationMessage:
  id, conversation_id, role (user/agent/system)
  content, citations, links, timestamp
```

## Key Methods

| Method | Purpose |
|--------|---------|
| `create(title, objective, participants, tags)` | Create and index conversation |
| `add_message(id, role, content, citations, links)` | Append message, emit event, persist |
| `search(query, tags, participant, linked_to, limit)` | Multi-filter search |
| `extract_decisions(id)` | Scan messages for decision/approved/rejected/selected |
| `branch(id, new_title)` | Fork conversation with copied participants/tags |
| `summarize(id)` | Text summary with title, participants, count, decisions |

## Findings

1. **No LLM integration for summarization** — `summarize()` just concatenates metadata, doesn't call AI
2. **`extract_decisions` uses naive string matching** — looks for lines starting with "decision:", "approved:", "rejected:", "selected:" — no NLP
3. **Search is purely text-based** — no semantic search, no embedding similarity
4. **No conversation deletion** — `create()` only, no `delete()` or `archive()` method
5. **Conversations not exposed in desktop as full screen** — only as a sub-view in Memory/Timeline
6. **No conversation export** — no markdown/JSON export method

## Recommendations

1. Add `summarize_with_ai()` method that calls `AIRouter.chat()` with conversation messages
2. Add LLM-based decision extraction using structured output
3. Add embedding-based semantic search to `search()`
4. Add `archive()` / `delete()` conversation lifecycle methods
5. Create dedicated `ConversationScreen` in desktop with full message view
6. Add `export_markdown()` / `export_json()` serialization
