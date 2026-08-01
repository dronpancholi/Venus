# BuildIT Integration Contract (M186)

**File:** `genesis/contracts/__init__.py`

Defines exactly which Genesis capabilities BuildIT consumes.

### Consumed APIs (12)
fabric.kernel.instance(), fabric.kernel.emit(), fabric.kernel.engineering,
fabric.kernel.search(), knowledge.engine, memory.engineering,
graph_v2.query, performance.monitor, query.engine, terminal.commands

### Constraints
1. BuildIT MUST consume Genesis knowledge for build optimization
2. BuildIT MUST NOT duplicate Genesis AI infrastructure
3. BuildIT MUST emit events for all build/test lifecycle changes
4. BuildIT MUST use Genesis performance monitoring for build benchmarks
