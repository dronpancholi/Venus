# Cycle 006 — Multi-Agent Engineering Organization

## From Single Agent to Engineering Company

Currently, Genesis operates as a single intelligence — the autonomous engineering pipeline
runs analyzer→planner→codegen sequentially. This is fine for simple tasks but cannot
scale to complex engineering decisions that require multiple perspectives.

A single AI makes mistakes it cannot detect. A single AI has blind spots. A single AI
cannot review its own work.

An engineering organization of specialized agents can debate, challenge, review, and
improve collectively — producing higher-quality outcomes than any single agent.

## Agent Roles

| Role | Responsibilities | Tools |
|------|-----------------|-------|
| **Chief Engineer** | Overall direction, priority, approval | All read, plan approve |
| **Principal Architect** | Architecture decisions, layer compliance | Graph, governance, simulation |
| **Repository Scientist** | Repository analysis, knowledge extraction | Scanner, indexer, graph |
| **Engineering Researcher** | Research patterns, best practices | Web search, memory, knowledge |
| **Planner** | Task decomposition, implementation plans | Analyzer, proof, simulation |
| **Product Manager** | Requirements, acceptance criteria | Memory, communication |
| **Backend Engineer** | Python implementation, kernel changes | Analyzer, codegen, test |
| **Frontend Engineer** | UI implementation, design system | N/A (frontend tools) |
| **Knowledge Engineer** | Knowledge graph, engineering memory | Graph, memory, institutional |
| **Documentation Engineer** | Documentation, reports | Report generator |
| **Security Engineer** | Security review, vulnerability detection | Security tools |
| **Performance Engineer** | Benchmarking, optimization | Mathematics, profiler |
| **Quality Engineer** | Test coverage, quality metrics | Test runner, mathematics |
| **Testing Engineer** | Test writing, test execution | Test runner |
| **Governance Auditor** | Policy compliance, layer violations | Governance, architecture |
| **Migration Specialist** | Migration planning, execution | Simulation, graph, diff |
| **Simulation Scientist** | Impact simulation, what-if analysis | Simulation engine |
| **Economics Analyst** | Cost analysis, ROI calculation | Mathematics |
| **Reviewer** | Code review, architecture review | Diff, governance, test |
| **Release Engineer** | Versioning, changelog, release | Package, git |

## Agent Specification

```python
@dataclass
class AgentSpec:
    agent_id: str
    role: AgentRole
    name: str
    description: str
    capabilities: list[AgentCapability]
    tools: list[ToolSpec]
    decision_boundaries: list[str]     # what this agent can decide
    requires_approval: list[str]       # what needs human/chief approval
    confidence_model: ConfidenceModel
    planning_strategy: PlanningStrategy
    evaluation_criteria: list[str]
    max_concurrent_tasks: int
    system_prompt: str
```

## Collaboration Protocol

Agents communicate through a shared event bus:

1. **Chief Engineer** publishes an objective
2. **Planner** decomposes into tasks
3. Tasks are assigned to appropriate agents
4. Agents work in parallel, publishing progress events
5. **Reviewer** reviews deliverables
6. **Governance Auditor** checks compliance
7. **Chief Engineer** approves or requests changes
8. **Knowledge Engineer** updates engineering memory
9. **Documentation Engineer** updates reports

### Debate Protocol

For high-risk decisions:
1. Two or more agents with different roles analyze the same problem
2. Each produces a recommendation with confidence
3. **Chief Engineer** or **Principal Architect** reconciles
4. If disagreement persists, run simulation (Mission 24)
5. Document both positions and resolution in engineering memory

## Task Lifecycle

```
PENDING → ASSIGNED → IN_PROGRESS → REVIEW → APPROVED → COMPLETED
                                         ↘ REJECTED → REASSIGNED
```

Each state transition is logged to engineering memory.

## Implementation

```
genesis/agents/
  __init__.py        — AgentSpec, AgentRole, AgentCapability
  registry.py        — AgentRegistry
  bus.py             — Agent communication bus
  roles/
    chief_engineer.py
    principal_architect.py
    repository_scientist.py
    planner.py
    backend_engineer.py
    ...
  protocols/
    debate.py
    review.py
    approval.py
```

Start with 5 core roles, expand as the system matures.
