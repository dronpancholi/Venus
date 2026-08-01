# Venus Integration Contract (M185)

**File:** `genesis/contracts/__init__.py`

Defines exactly which Genesis capabilities Venus consumes.

### Consumed APIs (20)
fabric.kernel.instance(), fabric.kernel.emit(), fabric.kernel.query_events(),
fabric.kernel.search(), fabric.kernel.registry, fabric.kernel.engineering,
ai.registry, ai.router, knowledge.search, memory.institutional,
graph_v2.query, lifecycle.state, resources.monitor, performance.monitor,
query.engine, runtime.apps, terminal.commands, workspace.manager

### Constraints
1. Venus MUST use Genesis Fabric for all inter-subsystem communication
2. Venus MUST NOT import internal genesis modules directly
3. Venus MUST register all services with FabricKernel
4. Venus MUST use AIRouter for all AI operations
5. Venus MUST emit events for all significant state changes
