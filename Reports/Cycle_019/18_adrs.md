# Cycle 019 — Architecture Decision Records

## ADR-019-001: State Engine as Canonical Foundation

**Status**: Accepted
**Context**: Every subsystem maintained independent state. No centralized view, no replay, no cross-subsystem observation.
**Decision**: EngineeringState becomes the single source of truth. All subsystems read/write to the same state. Every mutation records a transition.
**Consequences**: + State is unified and observable + Every mutation is replayable - All subsystems must adopt state engine pattern
**Related**: M147, NervousSystem, all Cycle 019 subsystems

## ADR-019-002: Nervous System Replaces Polling

**Status**: Accepted
**Context**: 21 set_interval calls polled subsystems. Events fired but few subscribers listened.
**Decision**: NervousSystem propagates state changes as signals. On-signal listeners replace polling. Desktop _DRIVEN_INTERVAL set to 9999s (effectively disabled).
**Consequences**: + Real-time signal propagation + No polling overhead - All subsystems must emit to state engine instead of direct event emission

## ADR-019-003: Workflows as First-Class Objects

**Status**: Accepted
**Context**: Three competing workflow systems (automation/engine, execution/workflow, runtime/executor). None had stages, goals, retries, rollback, or approvals.
**Decision**: EngineeringWorkflowEngine replaces all three. Built-in workflows use the same engine. New workflows register as definitions.
**Consequences**: + Single workflow system + Full lifecycle management (stages, rollback, approval) - Existing workflow systems deprecated

## ADR-019-004: Context Auto-Assembled

**Status**: Accepted
**Context**: Every interaction required manual context building. No centralized context available.
**Decision**: ContextEngine.build() collects from 15+ sources automatically. Every request receives context without manual work.
**Consequences**: + Zero-effort context + Consistent context across all interactions - Context engine depends on all subsystems being booted

## ADR-019-005: Copilot Becomes Proactive

**Status**: Accepted
**Context**: Copilot only responded to prompts. Missed opportunities for proactive improvement suggestions.
**Decision**: ProactiveCopilot runs background watcher checking twin ratios, reasoning risks, knowledge clusters every 30s. Emits copilot.suggestion events.
**Consequences**: + Continuous improvement suggestions + No prompt required - Background thread overhead (~30s interval)

## ADR-019-006: Knowledge Self-Organizes

**Status**: Accepted
**Context**: Knowledge was static. Manual organization required. Duplicate concepts accumulated.
**Decision**: SelfOrganizingKnowledge clusters concepts, merges duplicates, archives stale items, auto-consolidates every 50 new concepts.
**Consequences**: + Living knowledge graph + No manual maintenance - Cluster thresholds need tuning

## ADR-019-007: All Subsystems Register as EngineeringObjects

**Status**: Accepted
**Context**: Some subsystems registered as EngineeringObjects, some didn't. No consistent discovery mechanism.
**Decision**: Every Cycle 019 subsystem registers itself in EngineeringRegistry with an appropriate EngineeringObjectType. All accessible via kernel.<name>.
**Consequences**: + Universal discovery + Consistent pattern - 12 new EngineeringObjectTypes added

## ADR-019-008: Genesis as Application Platform

**Status**: Accepted
**Context**: Applications had to rebuild Genesis infrastructure. No app hosting model existed.
**Decision**: GenesisAppPlatform provides app lifecycle (register → start → stop), dependency injection, permission model, and access to all Genesis capabilities.
**Consequences**: + Apps reuse full Genesis platform + 6 built-in apps demonstrate pattern - App isolation model needed for multi-tenant
