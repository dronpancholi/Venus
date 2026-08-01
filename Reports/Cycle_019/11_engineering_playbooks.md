# M155 — Engineering Playbooks

## File
`genesis/playbooks/engine.py`, `genesis/playbooks/__init__.py`

## Purpose
Reusable institutional playbooks capturing 19 cycles of engineering learning. Each playbook includes prerequisites, required tools, engineering workflow, validation, rollback, expected outputs, common mistakes, and historical examples.

## Key Components

### Playbook
- `name`, `description`, `prerequisites`, `tools`, `steps`
- `validation`, `rollback`, `expected_outputs`, `common_mistakes`
- `historical_examples`, `tags`

### EngineeringPlaybooks
- `get(name)`, `list()`, `search(query)`, `stats()`

### Built-in Playbooks
1. **large_refactoring** — Safe module/package refactoring (8 steps, 4 validations)
2. **ai_provider_integration** — Register and deploy AI providers (5 steps)
3. **knowledge_consolidation** — Consolidate and optimize knowledge base (4 steps)

## Integration
- **kernel.playbooks** — lazy-loaded, auto-booted
- **EngineeringState** — stores playbook count
- **EngineeringRegistry** — playbooks registered as PLAYBOOK objects
