# M158 — Developer Platform & SDK

## File
`genesis/sdk/engine.py`, `genesis/sdk/__init__.py`

## Purpose
Stable SDKs exposing every major Genesis capability. Python SDK, REST SDK, WebSocket SDK, CLI SDK.

## SDK Capabilities (21)

| Capability | Methods | Version |
|---|---|---|
| engineering_objects | get, search, register, get_by_type, get_by_tag, latest, stats | 1.0.0 |
| knowledge | search, get_decisions, get_recommendations, get_entities, summary | 1.0.0 |
| twin | summary, query, scan | 1.0.0 |
| reasoning | analyze_fragility, analyze_coupling, analyze_debt, analyze_duplication, analyze_architecture_decay, comprehensive_analysis | 1.0.0 |
| timeline | query, add | 1.0.0 |
| search | search | 1.0.0 |
| ai | chat, stream_chat, embeddings, tool_call, list_providers, routing_decision | 1.0.0 |
| automation | list_workflows, get_workflow, stats | 1.0.0 |
| workflows | register, run, get_execution, list_executions, list_defs | 1.0.0 |
| insights | list, create, stats | 1.0.0 |
| decisions | propose, decide, get, search, stats | 1.0.0 |
| memory | store, recall, search, promote, stats | 1.0.0 |
| projects | register_project, scan_project, list_projects, compare | 1.0.0 |
| architecture | scan, summary, get_dependents, get_dependencies | 1.0.0 |
| observatory | record, trend, snapshot | 1.0.0 |
| explorer | explore, explore_by_type, find_path | 1.0.0 |
| planner | generate_plan, list_plans, get_plan | 1.0.0 |
| copilot | suggestions, stats | 1.0.0 |
| playbooks | get, list, search, stats | 1.0.0 |
| agentos | list_capabilities, check_readiness, get_capability | 1.0.0 |
| state | get, set, get_domain, snapshot, domains, transitions | 1.0.0 |

## API Pattern
```python
# All capabilities accessible via kernel.<capability>.<method>()
kernel.engineering.search("query")
kernel.knowledge.search("query", limit=10)
kernel.twin.summary()
```

## Integration
- **kernel.sdk** — lazy-loaded, auto-booted
- **REST SDK** — all capabilities exposed via GET /v1/search and existing endpoints
- **All 21 capabilities** versioned and documented
