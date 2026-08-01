# M137 — Engineering Planner

## File
`genesis/planner/engine.py`, `genesis/planner/__init__.py`

## Purpose
Autonomous engineering plan generation based on repository analysis. Analyzes DigitalTwin data, ReasoningEngine findings, and KnowledgeEngine decisions to produce prioritized action plans.

## Key Components

### EngineeringPlanner
- `generate_plan(name)` — produces a plan with items from:
  - **DigitalTwin**: large modules → refactoring suggestions; poor function/class ratios → design improvements
  - **ReasoningEngine**: high-risk findings (fragility, coupling, decay, duplication, debt) → prioritized remediation
  - **KnowledgeEngine**: pending decisions → follow-up items
- `list_plans()` — all generated plans
- `get_plan(name)` — specific plan by name

### PlanItem
- `title`, `description`, `priority` (high/medium/low), `effort` (large/medium/small), `source`, `tags`

## Integration
- **FabricKernel.planner** — lazy-loaded, auto-booted
- **EngineeringRegistry** — plan + items registered as PLAN objects
- **DigitalTwin** — source of module/code metrics
- **ReasoningEngine** — source of risk analysis
- **KnowledgeEngine** — source of decisions and recommendations
