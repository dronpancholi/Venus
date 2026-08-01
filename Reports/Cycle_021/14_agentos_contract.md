# AgentOS Integration Contract (M187)

**File:** `genesis/contracts/__init__.py`

Defines exactly which Genesis capabilities AgentOS consumes.

### Consumed APIs (20)
fabric.kernel.instance(), fabric.kernel.emit(), fabric.kernel.agent_runtime,
fabric.kernel.task_graph, fabric.kernel.execution_engine,
ai.registry, ai.router, knowledge.engine, memory.engineering,
graph_v2.query, lifecycle.state, performance.monitor, query.engine, runtime.apps

### Constraints
1. AgentOS MUST interact only through FabricKernel APIs
2. AgentOS MUST NOT import genesis internals directly
3. AgentOS MUST use AIRouter for all AI operations
4. AgentOS MUST be provider-neutral (no hardcoded AI provider)
5. AgentOS MUST emit events for all agent lifecycle changes
6. AgentOS MUST NOT duplicate Fabric event infrastructure
