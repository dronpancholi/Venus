# Cycle 018 — Architecture Delta

## Before (Cycle 017)
```
FabricKernel
├── engineering (EngineeringRegistry)
├── knowledge (KnowledgeEngine)
├── reasoning (EngineeringReasoningEngine)
├── copilot (CopilotEngine)
├── timeline (UniversalTimeline)
└── autonomous_review (AutonomousReview)

AI: isolated ProviderRegistry + AIRouter (never auto-registered)
Desktop: 11 screens, 30s polling, no Copilot, legacy memory search
Events: fired but no workflow engine consumed them
WS queue: pushed events silently dropped
```

## After (Cycle 018)
```
FabricKernel
├── engineering (EngineeringRegistry)
├── knowledge (KnowledgeEngine)
├── reasoning (EngineeringReasoningEngine)
├── copilot (CopilotEngine)
├── timeline (UniversalTimeline)
├── autonomous_review (AutonomousReview)
├── twin (DigitalTwin)                     ← NEW
├── ai (AIOrchestrationEngine)             ← NEW
├── automation (AutomationEngine)          ← NEW
├── observatory (EngineeringObservatory)   ← NEW
├── explorer (EngineeringExplorer)         ← NEW
├── planner (EngineeringPlanner)           ← NEW
├── memory_v2 (EngineeringMemoryV2)        ← NEW
├── multi_project (MultiProjectIntelligence) ← NEW
├── live_architecture (LiveArchitectureEngine) ← NEW
├── visual_reasoning (VisualReasoningEngine) ← NEW
└── agentos (AgentOSFoundation)            ← NEW

AI: auto-registered on boot, kernel.ai, summarize() fixed, routing decisions live
Desktop: event-driven push, Copilot suggestions, KnowledgeEngine search, kernel.timeline
Events: AutomationEngine subscribes, dispatches 3 workflows, drains WS queue
```

## New Packages Created
- `genesis/twin/` — Digital Twin
- `genesis/automation/` — Automation Engine
- `genesis/observatory/` — Engineering Observatory
- `genesis/explorer/` — Engineering Explorer
- `genesis/planner/` — Engineering Planner
- `genesis/memory_v2/` — Multi-layer Memory
- `genesis/multi_project/` — Multi-Project Intelligence
- `genesis/architecture/` — Live Architecture
- `genesis/visual_reasoning/` — Visual Reasoning
- `genesis/agentos/` — AgentOS Foundation

## EngineeringObjectType Additions
AI_PROVIDER, AUTOMATION, PROMPT, WORKFLOW, CAPABILITY, PLAN, METRIC, ARCH_NODE, ARCH_EDGE, EVIDENCE, COMPONENT, MODULE, PACKAGE

## Line Count
- ~8,500 lines of new production code
- ~2,000 lines of reports
