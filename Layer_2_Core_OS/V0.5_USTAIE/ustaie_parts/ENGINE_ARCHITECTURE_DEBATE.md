# Engine: Architecture Debate

## 1. Context & Strategy

### 1.1 Purpose
The Architecture Debate Engine challenges proposed systems designs by running simulated debate loops between ten specialized distinguished architect personas, identifying structural risks before coding.

### 1.2 Philosophy
Perfect consensus is rare; structured critique is mandatory. Force opposing roles to debate, resolving latency, cost, and reliability bottlenecks prior to merging blueprints.

---

## 2. Personas Mappings & Core Focus

1.  **Principal Backend**: Focuses on code modularity, library footprint, interfaces.
2.  **Distinguished Architect**: Focuses on system coupling, bounded contexts, DDD standards.
3.  **Security**: Focuses on zero-trust borders, tenant data isolation, secrets.
4.  **Performance**: Focuses on thread blocking, memory footprint, p99 latencies.
5.  **DevOps**: Focuses on deployment configurations, CI/CD pipeline speeds.
6.  **Database**: Focuses on lock contentions, sharding limits, query scaling.
7.  **AI**: Focuses on context token overhead, prompt injections, hallucination rates.
8.  **Product**: Focuses on developer velocity, release deadlines.
9.  **SRE**: Focuses on MTTR, redundancy fallback playbooks.
10. **CTO**: Focuses on gross margins, enterprise SLAs, strategic alignment.

---

## 3. Operational Algorithm & Debate Protocol

### 3.1 The Consensus Loop
```
                          [Ingest Draft Topology]
                                     │
                        [Persona Review Critiques]
                                     │
                        [Consensus Voting Round]
                                     ├── Score >= 7/10 ──► [Approve Blueprint]
                                     └── Score < 7/10  ──► [Trigger Design Revision]
```

### 3.2 Required Evidence
Persona rejections must cite specific constraint IDs or historical failure logs (from V0.4 Module 21) to be valid.

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked proposal against all 10 persona roles.
*   [ ] Logged specific objections.
*   [ ] Calculated consensus score.
*   *Exit Criteria*: Consensus score >= 7/10 achieved.
*   Proceed to **Automatic Architecture Verification**.
