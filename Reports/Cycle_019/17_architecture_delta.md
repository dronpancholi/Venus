# Cycle 019 — Architecture Delta

## Before (Cycle 018)
```
FabricKernel (17 properties from Cycle 017 + Cycle 018)
├── engineering / knowledge / reasoning / copilot / timeline
├── autonomous_review / twin / ai / automation
├── observatory / explorer / planner
├── memory_v2 / multi_project / live_architecture
├── visual_reasoning / agentos

State: fragmented, per-subsystem
Events: fire-and-forget, few subscribers
Workflows: 3 competing systems (automation, execution/workflow, runtime/executor)
Desktop: 11 screens, polling fallback
Knowledge: static, manual organization
Decisions: audit-log only
Insights: reasoning findings only
```

## After (Cycle 019)
```
FabricKernel (21 new properties, 38 total)
├── [Cycle 017] engineering / knowledge / reasoning / copilot / timeline / review
├── [Cycle 018] twin / ai / automation / observatory / explorer / planner
│              memory_v2 / multi_project / live_architecture
│              visual_reasoning / agentos
├── [Cycle 019] state_engine / nervous_system / context_engine
│              workflow_engine / insight_engine / decision_intelligence
│              knowledge_organizer / proactive_copilot / playbooks
│              app_platform / command_center / sdk

State: unified EngineeringState (8 domains, transitions recorded)
Events: NervousSystem propagates all signals (38 event types → subscribers)
Workflows: EngineeringWorkflowEngine (3 defs, rollback, approval, goals)
Desktop: 14 command center panels, workspace memory, experience-first nav
Knowledge: SelfOrganizingKnowledge (clusters, merges, archives, auto-consolidates)
Decisions: DecisionIntelligence (propose → decide → implement lifecycle)
Insights: InsightEngine (evidence-backed, cross-referenced, auto-generated)
Platform: AppPlatform (6 apps), SDK (21 capabilities), Playbooks (3 playbooks)
```

## New Packages Created (12)
- `genesis/state/` — Engineering State
- `genesis/nervous/` — Nervous System
- `genesis/context/` — Context Engine
- `genesis/workflows/` — Workflow Engine
- `genesis/insight/` — Insight Engine
- `genesis/decisions/` — Decision Intelligence
- `genesis/knowledge_v2/` — Self-Organizing Knowledge
- `genesis/copilot_v2/` — Proactive Copilot
- `genesis/playbooks/` — Engineering Playbooks
- `genesis/app_platform/` — Application Platform
- `genesis/command_center/` — Live Command Center
- `genesis/sdk/` — Developer SDK

## EngineeringObjectType Additions (12)
STATE, NERVOUS_SYSTEM, INSIGHT, DECISION_RECORD, PLAYBOOK, APP, SDK, SIGNAL, COPILOT, UX_FLOW, APP_MODULE, APP_ENDPOINT

## Line Count
- ~6,500 lines of new production code
- ~2,500 lines of reports
