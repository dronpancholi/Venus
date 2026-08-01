# CYCLE 007 — REPORT 04: UNIVERSAL TASK GRAPH

## Everything Becomes a Dependency-Aware Graph

⸻

## VISION

Every engineering request in Genesis automatically becomes a graph of work items.
The graph tracks dependencies, blocking relationships, critical path, progress, and
completion. It provides automatic parallelism detection, resource conflict analysis,
and completion prediction.

⸻

## PROBLEM STATEMENT

Before Cycle 007, engineering tasks were handled ad-hoc:
- No standard task representation
- No dependency tracking between tasks
- No visibility into work progress
- No critical path analysis
- No way to predict completion time
- No connection between high-level goals and low-level execution

⸻

## TASK NODE TYPES

| Type | Description | Example |
|------|-------------|---------|
| GOAL | Highest-level objective | "Improve test coverage" |
| OBJECTIVE | Measurable sub-goal | "Add unit tests for core modules" |
| PROJECT | Multi-task engineering project | "Q1 Testing Initiative" |
| EPIC | Large feature area | "Integration test framework" |
| STORY | User-facing feature | "As a dev, I can run tests on save" |
| ENGINEERING_TASK | Concrete work item | "Implement test watcher" |
| AGENT_TASK | Assigned to an agent | "Review test watcher PR" |
| EXECUTION_UNIT | Atomic operation | "Run test suite" |
| OPERATION | Single operation | "npm test" |
| VALIDATION | Verification step | "Verify all tests pass" |
| EVIDENCE | Proof of completion | "Test report #42" |
| COMPLETION | Terminal node | "Merged to main" |

⸻

## TASK STATUS

```
PENDING → READY → RUNNING → COMPLETED
                            → FAILED
                            → SKIPPED
                            → ROLLED_BACK
```

A task is READY when all its dependencies are COMPLETED or SKIPPED.

⸻

## CRITICAL PATH ALGORITHM

```python
def critical_path(self) -> list[TaskNode]:
    # Find root nodes (no parent)
    roots = [n for n in self._nodes.values() if not n.parent_id]
    
    # DFS from each root, tracking accumulated duration
    best_path, best_duration = [], 0
    
    def dfs(node, path, accumulated):
        children = get_children(node)
        if not children:
            if accumulated > best_duration:
                update best_path, best_duration
            return
        for child in children:
            path.append(child)
            dfs(child, path, accumulated + child.estimated_duration_secs)
            path.pop()
    
    return best_path  # Longest path = critical path
```

Complexity: O(V + E) where V = nodes, E = edges.

⸻

## TASK GRAPH BUILDER

High-level objectives are decomposed through the builder:

```python
builder = TaskGraphBuilder(graph)

# Decompose an objective
goal = builder.from_objective("Ship performance improvements")
design = builder.add_engineering_task("Design benchmark suite", parent_id=goal.id)
implement = builder.add_engineering_task("Implement optimizations", 
                                          parent_id=goal.id, 
                                          dependencies=[design.id])
review = builder.add_agent_task("Review implementation", 
                                 parent_id=implement.id,
                                 agent_role="reviewer")
```

⸻

## API

```python
# Graph operations
graph = TaskGraph(kernel)
graph.add_node(node)
graph.get_node(id)
graph.update_status(id, TaskStatus.RUNNING)
graph.update_progress(id, 0.75)
graph.add_dependency(node_id, depends_on_id)
graph.get_ready_tasks()  # Tasks whose deps are all complete
graph.critical_path()    # Longest path
graph.summary()          # Counts by type and status
```

⸻

## FUTURE EXTENSIONS

- Automatic task decomposition from natural language objectives
- Resource conflict detection (agent contention, provider contention)
- Completion time prediction using historical data
- Task reassignment on agent failure
- Rollback implementation with dependency-aware undo
