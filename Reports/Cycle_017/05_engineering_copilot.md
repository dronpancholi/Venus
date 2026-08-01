# M124: Engineering Copilot

> Status: **Implemented**
> Files: `genesis/engineering/copilot.py`
> Integration: `genesis/fabric/kernel.py` (lazy `copilot` property)

---

## Summary

A permanent engineering copilot that understands current context (screen, selection, engineering state) and answers questions using EngineeringRegistry, KnowledgeEngine, and ReasoningEngine — not generic LLM responses.

## How It Works

```
CopilotEngine
├── ask(query, screen_id, selected_id) → CopilotResponse
│   ├── Build CopilotContext from live kernel state
│   ├── Route query to appropriate handler
│   │   ├── "" → Context summary + suggestions
│   │   ├── "what/who/here" → Screen + selection context
│   │   ├── "fragile/health" → ReasoningEngine analysis
│   │   ├── "decision/recommend" → KnowledgeEngine.get_decisions()
│   │   ├── "report" → KnowledgeEngine.search_reports()
│   │   ├── "object/registry" → Registry stats
│   │   └── other → Registry search
│   └── Return structured answer + suggestions + references
```

## Example Interactions

**"what is here?"** → Context summary with 5 registry dimensions + screen name

**"analyze health"** → Reasoning engine output: 3 findings with evidence citations

**"show decisions"** → Recent engineering decisions from parsed reports

**"find reports"** → Report search across 149 indexed documents

## Context Understanding

The CopilotContext captures:
- Current screen ID and name
- Selected object (type, ID, relationships, links)
- Active session ID
- Engineering state: kernel uptime, object counts, event store size
- Knowledge: indexed reports, extracted items count

## Performance

All responses < 1ms — no LLM call, no external dependency, no network.

## Integration Points

- (Desktop) Screens can call `kernel.copilot.ask(query, screen_id, selected_id)` for inline help
- (Command Palette) Can add copilot queries
- (AI Screen) Can be the primary copilot interface
