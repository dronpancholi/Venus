# Part 05 — AI Architecture

## 1. Topologies of Agentic Systems
AI Architecture models agent collaboration networks, memory layout, tool calling protocols, Model Context Protocol (MCP) integrations, and RAG pipelines.

---

## 2. Agent Patterns Directory

### 2.1 Single Agent
*   *Definition*: One LLM loop executing a task with simple tools.
*   *Usecase*: Code formatting, text summarization, data mapping.

### 2.2 Swarms & Multi-Agent Networks
*   *Definition*: Cooperating specialized agents executing parallel subtasks.
*   *Protocol*: Message passing schemas (e.g. JSON-RPC over websockets).

```
                  +----------------------------------+
                  |  [Agent A] Planning Coordinator  |
                  +----------------------------------+
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
            +----------------+           +----------------+
            |  [Agent B] Dev |           | [Agent C] SRE  |
            +----------------+           +----------------+
```

---

## 3. Memory Architectures

### 3.1 Long Term Memory
*   *Mechanism*: Vector DB semantic storage, Hierarchical GraphRAG nodes.
*   *Purpose*: Persisting user preferences, system guidelines.

### 3.2 Short Term Memory
*   *Mechanism*: Redis caching session lists, token context windows.
*   *Purpose*: Storing active chat transaction payloads.

---

## 4. AI Architecture Checklist
*   [ ] Checked LLM task routing parameters.
*   [ ] Configured long-term vector memory caches.
*   [ ] Defined JSON schemas for all tool calls.
*   [ ] Written system instructions ensuring agent safety.
