# ENGINE — Architecture Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
The Architecture Generator is an AI-executable engine that produces complete, production-grade system architecture designs for any software product. It synthesizes inputs from V0.3 (problem discovery), V0.4 (decisions), and V0.5 (systems thinking) into concrete architecture blueprints.

---

## Input Requirements
```
Required:
  - Product description and primary use cases
  - Expected user scale (MAU, peak RPS)
  - Team size and structure
  - Technology constraints (existing stack, cloud provider preference)
  - Non-functional requirements (latency, availability, compliance)

Optional:
  - Budget constraints
  - Timeline requirements
  - Existing system to integrate with
```

---

## Generation Process

### Step 1: Domain Analysis
- Identify bounded contexts from use case analysis
- Map context relationships (context map)
- Define data ownership per context
- Identify cross-cutting concerns

### Step 2: Architecture Selection
Apply Part 18 decision tree:
- < 15 engineers + new product → Modular Monolith
- Multiple teams + proven domains → Microservices
- High read/write imbalance → CQRS + Event Sourcing

### Step 3: Component Decomposition
For each bounded context, generate:
- Service/module definition
- API surface area
- Data model
- External dependencies
- Communication patterns (sync/async)

### Step 4: Infrastructure Topology
- Cloud provider and region selection
- Compute tier selection (Kubernetes, Lambda, VM)
- Network topology (VPC, subnets, security groups)
- Data tier (primary DB, read replicas, cache, message broker)
- CDN and edge configuration

### Step 5: Documentation Output
Generate C4 model diagrams (L1 through L4):
- System Context diagram
- Container diagram
- Component diagrams per service
- Deployment diagram

---

## Output Templates
Produces: [HLD](../usedpos_templates/HLD_HIGH_LEVEL_DESIGN.md), [C4 L1](../usedpos_templates/C4_ARCHITECTURE_L1_SYSTEM_CONTEXT.md), [C4 L2](../usedpos_templates/C4_ARCHITECTURE_L2_CONTAINER.md)

---

## Validation Checklist
- [ ] All bounded contexts have clear ownership
- [ ] No shared databases across service boundaries
- [ ] All external dependencies have circuit breakers
- [ ] SLO targets achievable with selected architecture
- [ ] Security boundaries enforced at network and application layer
- [ ] Cost estimate within acceptable range at target scale
