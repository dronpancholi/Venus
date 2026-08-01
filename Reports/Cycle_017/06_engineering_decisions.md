# M126: Engineering Decision System

> Status: **Designed** (foundation built)
> Enablers: M121 (EngineeringObject), M122 (KnowledgeEngine)

---

## Architecture

Every major engineering change records:
- **Problem** — what needed to be solved
- **Context** — what systems were affected
- **Alternatives considered** — what was rejected
- **Decision** — what was chosen and why
- **Evidence** — concrete data supporting the decision
- **Trade-offs** — what was sacrificed
- **Affected objects** — which EngineeringObjects are impacted
- **Rollback** — how to undo
- **Validation** — how to verify it worked

## Implementation Path

1. Extend `EngineeringObjectType.DECISION` with structured decision fields
2. `DecisionEngine` wraps `ConversationEngine.extract_decisions()` + report parsing
3. Auto-detection: reports with "Decision:" or "ADR-" sections auto-converted
4. Desktop: dedicated Decision view in Memory/Knowledge screens

## Existing Foundation

- KnowledgeEngine already extracts 39 decisions from reports
- ConversationEngine has `extract_decisions()` and `get_decisions()` methods
- EngineeringObject already supports relationships and links
- Copilot can already answer "show decisions" from existing extractions
