# Architecture Delta

## Module Changes

### New Modules (13)
- genesis.lifecycle — Platform Lifecycle Manager (L4)
- genesis.resources — Resource Monitor (L4)
- genesis.performance — Performance Monitor (L4)
- genesis.data — Data Model Registry (L4)
- genesis.query — Universal Query Engine (L4)
- genesis.runtime — App Runtime (L4)
- genesis.terminal — Engineering Terminal (L4)
- genesis.workspace — Workspace Manager (L4)
- genesis.marketplace — Marketplace Foundation (L4)
- genesis.studio — Genesis Studio (L4)
- genesis.contracts — Integration Contracts (L4)
- genesis.hardening — Production Hardening (L4)

### Moved Modules
- genesis.events: L3 → L4
- genesis.di: L3 → L4

### Previously Unassigned Now Registered (59 modules)
All engineering, automation, knowledge, boot, health, observability modules registered.

### Allowed Cycles (3)
1. fabric.kernel → knowledge.engine → fabric.kernel
2. fabric.kernel → automation.engine → fabric.execution → fabric.kernel
3. fabric.kernel → automation.engine → fabric.execution → fabric.agents → fabric.kernel

### UUID Violations Fixed (1)
genesis.desktop.activity: uuid.uuid4() → generate_id()
