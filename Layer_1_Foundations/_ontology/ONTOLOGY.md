# PROJECT VENUS — UNIVERSAL ONTOLOGY

**Version**: 1.0  
**Purpose**: Complete semantic model of every entity in Venus.

All objects in Venus inherit from a single root entity type through a strict single-inheritance hierarchy. The ontology defines what exists; the entity model defines the structure of each type.

---

## Type Hierarchy

```
Entity
├── Artifact          — Any persisted Venus object
│   ├── OperatingSystem  — V0.X OS definition
│   ├── Part             — Knowledge domain component
│   ├── Module           — Operational unit
│   ├── Engine           — Executable / verification logic
│   ├── Template         — Output artifact blueprint
│   ├── Stage            — Process stage
│   ├── Certificate      — Validation output
│   ├── Schema           — Type definition
│   ├── Document         — Generated output (markdown, etc.)
│   ├── Workflow         — Executable process definition
│   └── Configuration    — Runtime configuration
├── Knowledge         — Institutional knowledge
│   ├── Concept          — Abstract idea
│   ├── Principle        — Design/operating principle
│   ├── Rule             — Formal rule statement
│   ├── Pattern          — Reusable pattern
│   ├── Constraint       — Boundary condition
│   ├── Metric           — Measurable quantity
│   ├── Observation      — Recorded observation
│   └── Taxonomy         — Classification system
├── Capability        — Functional ability
│   ├── Function         — Atomic capability
│   ├── Service          — Composed capability
│   ├── Endpoint         — External interface
│   └── Protocol         — Communication standard
├── Decision          — Recorded decision
│   ├── ArchitectureDecision
│   ├── TechnicalDecision
│   ├── ProductDecision
│   └── StrategicDecision
├── Validation        — Validation artifacts
│   ├── Check            — Single validation rule
│   ├── Gate             — Validation gate
│   ├── Score            — Scoring result
│   ├── Audit            — Audit record
│   └── Certification    — Certification result
├── Execution         — Runtime execution
│   ├── Task             — Atomic execution unit
│   ├── Job              — Composed execution
│   ├── Pipeline         — CI/CD pipeline
│   ├── Runtime          — Execution environment
│   └── WorkflowRun      — Workflow instance
├── Relationship      — Named relationship
│   ├── Dependency       — Source depends on target
│   ├── Inheritance      — Source inherits from target
│   ├── Reference        — Source references target
│   ├── Validation       — Source validates target
│   ├── Production       — Source produces target
│   └── Composition      — Source contains target
├── Memory            — Persistent memory
│   ├── SemanticMemory   — Fact/knowledge memory
│   ├── ProceduralMemory — How-to memory
│   ├── DecisionMemory   — Decision history
│   ├── EvolutionMemory  — Evolution history
│   ├── ResearchMemory   — Research findings
│   └── ProjectMemory    — Per-project context
├── Agent             — Autonomous agent
│   ├── Planner          — Planning agent
│   ├── Executor         — Execution agent
│   ├── Validator        — Validation agent
│   ├── Learner          — Learning agent
│   ├── Evolver          — Self-improvement agent
│   └── Router           — Routing agent
├── Context           — Execution context
│   ├── SystemContext    — System state
│   ├── ExecutionContext — Execution state
│   ├── SecurityContext  — Security state
│   └── BusinessContext  — Business state
├── Policy            — Policy definition
│   ├── SecurityPolicy   — Security rules
│   ├── GovernancePolicy — Governance rules
│   ├── QualityPolicy    — Quality rules
│   └── CompliancePolicy — Compliance rules
├── Event             — Occurred event
│   ├── Trigger          — Event that triggers action
│   ├── Notification     — Event notification
│   ├── Error            — Error event
│   └── MetricEvent      — Metric event
├── Prompt            — AI prompt definition
│   ├── SystemPrompt     — System-level prompt
│   ├── AgentPrompt      — Agent-level prompt
│   ├── ValidationPrompt — Validation prompt
│   └── GenerationPrompt — Generation prompt
├── Goal              — Objective or target
│   ├── Objective        — High-level goal
│   ├── Requirement      — Formal requirement
│   ├── KeyResult        — Measurable result
│   └── Milestone        — Temporal marker
├── WorkflowDef       — Workflow definition
│   ├── Step             — Workflow step
│   ├── Transition       — State transition
│   └── DecisionNode     — Decision point
├── Interface         — External interface
│   ├── API              — API definition
│   ├── EventStream      — Event stream
│   └── Contract         — Interface contract
└── Language          — Language definition
    ├── Vocabulary        — Vocabulary term
    ├── Grammar           — Grammar rule
    └── Expression        — Expression definition
```

---

## Top-Level Categories

| Category | Role | Persistence | Executable |
|----------|------|-------------|------------|
| Artifact | Frozen definition | Yes | No |
| Knowledge | Learnable fact | Yes | No |
| Capability | Functional ability | Yes | Yes |
| Decision | Historical record | Yes | No |
| Validation | Quality assurance | Yes | Yes |
| Execution | Runtime action | No (transient) | Yes |
| Relationship | Connector | Yes | No |
| Memory | Learned state | Yes | No |
| Agent | Autonomous actor | Yes | Yes |
| Context | Execution snapshot | No (transient) | No |
| Policy | Governing rule | Yes | Yes |
| Event | Occurrence signal | No (stream) | No |
| Prompt | AI instruction | Yes | Yes |
| Goal | Target state | Yes | No |
| Interface | External boundary | Yes | Yes |

---

## Relationship Types

| Relationship | Source Types | Target Types | Semantics |
|-------------|--------------|--------------|-----------|
| `depends_on` | Any | Any | Source requires target |
| `inherits` | Artifact | Artifact | Source extends target |
| `references` | Any | Any | Source mentions target |
| `validates` | Validation | Any | Source validates target |
| `produces` | Engine | Template, Certificate | Source generates target |
| `contains` | OperatingSystem | Part, Engine, Template | Source contains target |
| `implements` | Engine | Policy, Rule | Source implements target |
| `satisfies` | Artifact | Goal, Requirement | Source satisfies target |
| `triggers` | Event | Execution, Workflow | Source triggers target |
| `composes` | Any | Any | Source is composed of target |
| `governs` | Policy | Any | Source governs target |
| `maps_to` | Artifact | Concept | Source represents concept |
| `evolves_to` | Any | Any | Source becomes target |
| `observes` | Agent | Event, Metric | Source observes target |
| `learns` | Memory | Knowledge | Source learns target |
