# UAIEOS Engine Specification: Workflow Orchestration

This engine specification details the software architecture, state-machine execution code patterns, and interface models for the Workflow Orchestration Engine of the UAIEOS.

---

## 1. Engine Architecture

The Workflow Orchestration Engine is divided into two primary processing units: the **DAG Executor** (for deterministic, structured tasks) and the **Reactive Agent Broker** (for dynamic, non-deterministic agent workflows).

```
+-----------------------------------------------------------------------------------+
|                           Workflow Orchestration Gateway                          |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
                +---------------------------------------------------+
                |            Task Routing & Parser Engine           |
                +---------------------------------------------------+
                     /                                         \
                    v                                           v
      +---------------------------+               +---------------------------+
      |       DAG Executor        |               |   Reactive Agent Broker   |
      |   (Deterministic Steps)   |               |   (Dynamic Event-Loop)    |
      +---------------------------+               +---------------------------+
                    |                                           |
                    +---------------------+---------------------+
                                          |
                                          v
                        +-----------------------------------+
                        |      State Persistence Layer      |
                        |        (Redis/Spanner Driver)     |
                        +-----------------------------------+
```

---

## 2. Interface Definitions (Python)

To ensure interoperability, the engine implements the following core class interfaces.

```python
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import datetime
import uuid

class WorkflowState:
    def __init__(self, workflow_id: str, initial_state: str):
        self.workflow_id: str = workflow_id
        self.current_state: str = initial_state
        self.version: int = 1
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.timestamp: datetime.datetime = datetime.datetime.utcnow()

    def transition_to(self, target_state: str, metadata: Dict[str, Any]) -> None:
        self.history.append({
            "from_state": self.current_state,
            "to_state": target_state,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "metadata": metadata
        })
        self.current_state = target_state
        self.version += 1
        self.timestamp = datetime.datetime.utcnow()

class IStatePersistence(ABC):
    @abstractmethod
    def save_state(self, state: WorkflowState) -> bool:
        """Serializes and writes the state to the persistent database."""
        pass

    @abstractmethod
    def load_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Loads and deserializes the state from the persistent database."""
        pass

class IWorkflowExecutor(ABC):
    @abstractmethod
    def execute(self, state: WorkflowState) -> WorkflowState:
        """Orchestrates execution logic based on the state machine schema."""
        pass
```

---

## 3. Implementation Patterns

### 3.1 Deterministic DAG Runner Implementation
The DAG runner implements a topological sort to resolve task dependency trees and execute independent branches concurrently using thread pools.

```python
import concurrent.futures

class DAGRunner(IWorkflowExecutor):
    def __init__(self, adjacency_list: Dict[str, List[str]], task_registry: Dict[str, Any]):
        self.adjacency_list = adjacency_list
        self.task_registry = task_registry
        self.in_degree = {u: 0 for u in adjacency_list}
        self._compute_in_degrees()

    def _compute_in_degrees(self):
        for u in self.adjacency_list:
            for v in self.adjacency_list[u]:
                self.in_degree[v] = self.in_degree.get(v, 0) + 1

    def execute(self, state: WorkflowState) -> WorkflowState:
        # Simple topological run execution
        resolved_order = self._topological_sort()
        state.transition_to("RUNNING", {"execution_path": resolved_order})
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for task_id in resolved_order:
                if task_id in self.task_registry:
                    # Retrieve prompt context and cost limits from state context
                    future = executor.submit(self.task_registry[task_id].run, state.context)
                    result = future.result()  # Blocking for demonstration
                    state.context[f"result_{task_id}"] = result
                    
        state.transition_to("COMPLETED", {"success": True})
        return state

    def _topological_sort(self) -> List[str]:
        # Implementation of Kahn's Algorithm
        in_deg = self.in_degree.copy()
        queue = [u for u in in_deg if in_deg[u] == 0]
        order = []
        while queue:
            u = queue.pop(0)
            order.append(u)
            for v in self.adjacency_list.get(u, []):
                in_deg[v] -= 1
                if in_deg[v] == 0:
                    queue.append(v)
        return order
```

### 3.2 Reactive Multi-Agent Event Broker
For dynamic agent execution, routing decisions are triggered by parsing messages emitted onto the shared event-bus. If the Z-score calculation (specified in [PART_09_WORKFLOW_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_09_WORKFLOW_ORCHESTRATION.md#L60-L75)) indicates that an alternative agent channel has significantly outperformed the default path, the broker adjusts its route handler weights.

```python
class ReactiveAgentBroker:
    def __init__(self, persistence: IStatePersistence):
        self.persistence = persistence
        self.handlers: Dict[str, Any] = {}

    def register_agent(self, topic: str, agent: Any) -> None:
        self.handlers[topic] = agent

    def dispatch_message(self, envelope: Dict[str, Any]) -> None:
        # Validate message formatting against structural schema
        topic = envelope["recipient"]
        if topic in self.handlers:
            # Load transaction execution context
            workflow_id = envelope["payload"]["structured_data"].get("workflow_id")
            state = self.persistence.load_state(workflow_id)
            if not state:
                state = WorkflowState(workflow_id, "INIT")
                
            state.transition_to("PROCESSING", {"sender": envelope["sender"]})
            self.persistence.save_state(state)
            
            # Execute agent callback
            response = self.handlers[topic].process(envelope["payload"]["content"])
            
            state.transition_to("IDLE", {"response_status": "success"})
            self.persistence.save_state(state)
```

---

## 4. System Cross-References
*   For the operational manuals and Z-score equations, see [PART_09_WORKFLOW_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_09_WORKFLOW_ORCHESTRATION.md).
*   For cost-effective rate-limiting of execution loops, see [ENGINE_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_AI_ECONOMICS.md).
*   For logging trace state metrics, see [ENGINE_OBSERVABILITY_TELEMETRY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_OBSERVABILITY_TELEMETRY.md).
