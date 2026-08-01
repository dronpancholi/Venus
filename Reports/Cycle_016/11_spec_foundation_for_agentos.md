# Cycle 016 — Foundation for AgentOS (M120)

## Vision
Genesis should become the runtime that AgentOS builds upon. Not by implementing AgentOS now, but by preparing stable, versioned APIs that AgentOS can consume without modification.

## Stable API Surface (Target)

| API | Current Form | Target Form | Status |
|-----|-------------|-------------|--------|
| Agent Runtime | `FabricKernel.instance().agent_runtime` | `agentos.agent.Runtime` | 🔄 |
| Execution | `FabricKernel.instance().task_executor` | `agentos.execution.Executor` | 🔄 |
| Workspace | `app.navigate_to()` | `agentos.workspace.Workspace` | 🔄 |
| Memory | `UniversalMemorySystem(kernel)` | `agentos.memory.MemorySystem` | 🔄 |
| Knowledge | `UnifiedGraph(kernel)` | `agentos.knowledge.Graph` | 🔄 |
| Conversation | `ConversationEngine` | `agentos.conversation.Engine` | 🔄 |
| Plugin | `PluginManager` | `agentos.plugin.Manager` | 🔄 |
| Provider | `AIProvider` ABC | `agentos.provider.Provider` | 🔄 |
| Observability | `kernel.metrics` | `agentos.observability.Metrics` | 🔄 |
| Task | `TaskGraph` | `agentos.task.Graph` | 🔄 |
| Storage | `StorageEngine` | `agentos.storage.Engine` | 🔄 |
| Desktop | `GenesisDesktop` | `agentos.desktop.App` | 🔄 |
| Server | `GenesisAPI` | `agentos.api.Server` | 🔄 |
| SDK | `genesis/sdk/` | `agentos.sdk.SDK` | 🔄 |

## Principles
1. Every API must be versioned (v1, v2, etc.)
2. Every API must have comprehensive documentation
3. Every API must be tested independently
4. Every API must be backwards-compatible for at least one major version
5. No direct access to private (`_`) members across API boundaries
6. All APIs must be importable from `agentos.*` namespace

## Current Violations
- `screens.py` accesses `kernel._contexts`, `kernel._conversation_engine`, `kernel._continuous_engineering`
- `widgets.py` accesses `kernel._contexts`, `a._outbox`, `a._inbox`
- `palette.py` accesses `kernel._continuous_engineering`
- `app.py` accesses `kernel._threads`

## Migration Strategy
1. Add public properties to FabricKernel for all private members currently accessed
2. Create `genesis/interfaces/` package with abstract base classes
3. Extract `genesis/sdk/` with stable wrapper APIs
4. Document all APIs with OpenAPI/Sphinx
5. Version all APIs at `agentos/v1/`

## Deferred to Cycle 017-018
All extraction work deferred. Current priority is stabilizing the existing API surface.
