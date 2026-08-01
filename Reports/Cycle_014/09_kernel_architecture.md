# Phase 0 Delta: Kernel Architecture

**Files:** `genesis/kernel/` — 15 files, ~1,800 lines  
**Tests:** 159 in `test_kernel.py`, 2,862 across all kernel tests

## Layered Kernel Architecture

```
Layer 4: FabricKernel         — Full event-sourced communications hub
Layer 3: EngineeringOS        — Service lifecycle with DAG boot ordering
Layer 2: PlatformV2           — Service-oriented management (health, metrics, telemetry)
Layer 1: PlatformAdapter      — Migration bridge from VenusPlatform → ServiceKernel
Layer 0: Platform (Venus)     — Original 725-line god-object platform
         UniversalKernel      — 15 sub-managers (process, task, memory, storage, etc.)
```

## UniversalKernel Sub-Managers

| Manager | Lines | Purpose |
|---------|-------|---------|
| `ProcessManager` | 118 | Process lifecycle |
| `TaskScheduler` | 155 | Task scheduling |
| `MemoryManager` | 105 | Memory management |
| `StorageManager` | 93 | Abstract volume manager |
| `CheckpointManager` | 107 | State snapshots |
| `RecoveryManager` | 117 | Failure recovery |
| `EventRouter` | 103 | Lightweight event pub/sub |
| `IPC` | 121 | Inter-process communication |
| `PluginLoader` | 105 | Module discovery |
| `DIKernel` | 96 | Dependency injection |
| `ResourceManager` | 127 | Resource allocation |
| `ExecutionManager` | 128 | Execution lifecycle |
| `HealthManager` | 99 | Health monitoring |
| `SecurityManager` | 123 | Auth, tokens, policies |
| `CapabilityLoader` | 97 | Capability discovery |

## Findings

1. **No consumers of UniversalKernel** — created in `VenusPlatform.boot()` and `PlatformAdapter.boot()` but never used for runtime operations; all runtime code uses FabricKernel
2. **VenusPlatform is a god-object** — 725 lines, 50+ service attributes, monolithic `boot()` method that sequentially boots GENESIS VIII through XIII programs
3. **PlatformAdapter duplicated VenusPlatform** — 728 lines, same 50+ services but wrapped in ServiceDef objects
4. **3 competing platform frameworks** — `platform.py`, `platform_v2.py`, `platform_adapter.py` all solve the same problem differently
5. **EngineeringOS has no runtime purpose** — declares service roles and DAG but isn't used by any running system
6. **`UniversalKernel.shutdown()` never called** — no current code path invokes it

## Recommendations

1. Designate FabricKernel as the ONE kernel — deprecate UniversalKernel for runtime use
2. Keep UniversalKernel's sub-managers (SecurityManager, HealthManager, etc.) as composable utilities
3. Consolidate 3 platform files into one — `platform.py` as the boot orchestrator
4. Remove EngineeringOS or merge into platform_v2
5. Wire `UniversalKernel.shutdown()` into FabricKernel.shutdown() for graceful cleanup of sub-managers
