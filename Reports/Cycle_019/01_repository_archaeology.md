# Cycle 019 — Repository Archaeology

## Full System Audit Results

### Package Inventory
- **81 packages** under genesis/
- **494 Python files** (115,643 lines)
- **93 test files** (2,999 test functions)
- **44 top-level modules**
- **12 documentation files**

### EngineeringObjectType Analysis
- **35 types defined**, only **16 used** (19 unused — 54% dead surface area)
- Unused: EVENT, AGENT_TASK, MESSAGE, MEMORY, AUDIT_ENTRY, DECISION, PLUGIN, PROJECT, PIPELINE, PROVIDER, WORKSPACE, TIMELINE, ARCHITECTURE_DELTA, COMPONENT, PACKAGE, WORKFLOW, METRIC, ARCH_NODE, ARCH_EDGE, EVIDENCE

### Event Architecture
- **38 unique event types** emitted
- Only **8 on_event subscriptions** — massive fire-and-forget asymmetry
- **3 competing event bus systems** (EventBus, EventRouter, FabricKernel)
- **3 competing workflow systems** (automation/engine, execution/workflow, runtime/executor)

### Desktop
- **11 screens**, **11 widgets**, **2 modal screens**
- **77 keyboard shortcuts**
- **21 set_interval calls** (polling, though _DRIVEN_INTERVAL=9999)

### AI Providers
- **3 providers**: NvidiaNIM, Ollama, OpenAICompatible
- All auto-register on boot via AIOrchestrationEngine
- **6 CLI entry points** using argparse

### Dependencies
- **1,018 from genesis imports** across 330 files
- High coupling risk in fabric/kernel.py (imports from 12 packages)

### Key Findings
1. Events are fire-and-forget with minimal subscribers
2. 19 unused EngineeringObjectTypes indicate dead design surface
3. Three competing workflow systems need unification
4. Desktop still has 21 polling calls despite event infrastructure
5. No unified state — each subsystem keeps independent state
