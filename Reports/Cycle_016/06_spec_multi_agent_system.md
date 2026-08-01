# Cycle 016 — Multi-Agent System Design (M115)

## Current State
Genesis has an `AgentRuntime` with basic agent lifecycle, an `EngineeringBrain` with 10 cognitive subsystems (BeliefSystem, GoalHierarchy, ReasoningEngine, WorkingMemory, EpisodicMemory, AttentionMechanism, ReflectionEngine, StrategyEngine, DecisionEngine, Orchestrator), and an `Orchestrator` with multi-agent lifecycle (IDLE/BUSY/BLOCKED/ERROR/TERMINATED).

## Target Architecture
10 specialized agents, each with memory, goals, permissions, tools, reasoning history, metrics, health, conversations, relationships, and ownership:

1. **Planner Agent** — decomposes goals into action sequences
2. **Architect Agent** — designs system architecture and validates patterns
3. **Reviewer Agent** — reviews code, architecture, and decisions
4. **Research Agent** — gathers information from external sources
5. **Implementation Agent** — writes code based on specifications
6. **Testing Agent** — writes and runs tests
7. **Documentation Agent** — generates and maintains documentation
8. **Security Agent** — audits code for vulnerabilities
9. **Performance Agent** — profiles and optimizes performance
10. **Infrastructure Agent** — manages deployment and infrastructure

## Agent Interface
```python
class EngineeringAgent:
    name: str
    role: str
    status: AgentStatus
    memory: AgentMemory
    goals: list[Goal]
    permissions: set[str]
    tools: list[ToolSpec]
    reasoning_history: list[ReasoningStep]
    metrics: AgentMetrics
    health: AgentHealth
    conversations: list[Conversation]
    relationships: list[AgentRelationship]
```

## Desktop Integration
- Agent detail screen shows per-agent memory, goals, reasoning history
- Agent collaboration graph shows real relationships (not text tree)
- Pause/resume/terminate with confirmation dialogs
- Agent metrics and health dashboard

## Deferred to Cycle 017
Full implementation deferred. The architecture exists in `genesis/brain/cognition/` but desktop integration, specialized agents, and permission enforcement are not yet built.
