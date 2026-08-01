# CYCLE 009 — AGENT EXECUTION ENGINE REPORT

## Agent-to-AI Provider Wiring (Mission 74)

---

## Overview

The AgentExecutionEngine bridges AgentRuntime and AI providers. Agents no longer
simulate work. When assigned a task, the engine constructs role-specific system
prompts, routes through AIRouter to the best available provider, executes the
task, and returns the result.

## Architecture

```
AgentInstance.assign_task(objective)
  ↓
AgentExecutionEngine.execute(agent, task)
  ├── _build_system_prompt(agent, task)
  │     ├── ROLE_PROMPTS[agent.spec.role]  (18 role-specific prompts)
  │     ├── agent.spec.system_prompt        (custom override)
  │     └── task context                    (capabilities, constraints)
  │
  ├── AIRouter.chat(messages)
  │     ├── ProviderRegistry.healthy_providers()
  │     ├── _rank_providers(capability)
  │     └── provider.chat(messages, model)
  │
  └── return result
```

## Role Prompts

18 agent roles with specialized system prompts:

| Role | Prompt Focus |
|------|-------------|
| CHIEF_ENGINEER | Architectural decisions, quality standards |
| PRINCIPAL_ARCHITECT | System design, tech debt, migrations |
| REPOSITORY_SCIENTIST | Repository analysis, structural reports |
| ENGINEERING_RESEARCHER | Investigation, evidence-backed recommendations |
| PLANNER | Task decomposition, effort estimation |
| PRODUCT_MANAGER | Requirements, prioritization, stakeholder mgmt |
| BACKEND_ENGINEER | Python code, APIs, business logic |
| FRONTEND_ENGINEER | UI/UX, TypeScript, CSS, accessibility |
| KNOWLEDGE_ENGINEER | Graphs, ontologies, knowledge bases |
| DOCUMENTATION_ENGINEER | Technical writing, API docs, guides |
| SECURITY_ENGINEER | Vulnerability audits, security architecture |
| PERFORMANCE_ENGINEER | Profiling, optimization, benchmarking |
| QUALITY_ENGINEER | Code quality, standards, tech debt prevention |
| TESTING_ENGINEER | Test strategies, coverage, reliability |
| GOVERNANCE_AUDITOR | Compliance, policy enforcement |
| MIGRATION_SPECIALIST | Refactoring, backward compatibility |
| SIMULATION_SCIENTIST | Modeling, simulation, predictive analysis |
| REVIEWER | Code review, actionable feedback |
| RELEASE_ENGINEER | Versioning, build pipelines, deployments |
| ECONOMICS_ANALYST | ROI analysis, cost-benefit, resource optimization |

## Execution Flow

1. **Agent receives task** via AgentScheduler or direct assignment
2. **AgentExecutionEngine.execute()** is called
3. **System prompt** is built from role + custom prompt + context
4. **Message array** is constructed (system + user + optional context)
5. **AIRouter** finds best provider using capability-based routing
6. **Provider executes** chat completion
7. **Result** is returned to agent
8. **Event emitted** with provider, model, duration, usage stats
9. **Agent calls complete_task() or fail_task()**

## Usage

```python
from genesis.fabric.kernel import FabricKernel
from genesis.fabric.execution import AgentExecutionEngine
from genesis.fabric.agents import AgentRuntime, AgentSpec, AgentRole

kernel = FabricKernel.instance()
kernel.boot()

runtime = AgentRuntime(kernel)
engine = AgentExecutionEngine(kernel)

agent_id = runtime.spawn(AgentSpec(
    name="Architect",
    role=AgentRole.PRINCIPAL_ARCHITECT,
))

agent = runtime.get_agent(agent_id)
task = agent.assign_task("Analyze the repository architecture")

# Execute via AI provider
result = engine.execute_sync(agent, task)
print(result)
```

## Stats

```python
stats = engine.stats
# {
#   "execution_count": 42,
#   "total_duration_ms": 125000.0,
#   "avg_duration_ms": 2976.19
# }
```

## Provider Selection

Provider selection uses AIRouter's capability-based routing:
- Route by capability (chat, code_generation, streaming)
- Rank by benchmark score (success rate, latency)
- Prefer providers with required capability
- Fallback chain to next healthy provider
