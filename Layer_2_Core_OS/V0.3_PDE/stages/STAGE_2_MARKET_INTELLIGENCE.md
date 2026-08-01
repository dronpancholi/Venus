# Stage 2 — Market Intelligence

## 1. Governance & Rationale

### 1.1 Why It Exists
Markets determine the economic scale, life expectancy, and deployment constraints of software. Researching TAM, SAM, and SOM prevents building systems for markets too small to yield enterprise value. Understanding regulatory, regional, and macro trends ensures the engineering architecture is compatible with legal frameworks and macroeconomic realities before development capital is deployed.

### 1.2 What Questions It Answers
*   What is the addressable financial size of the market (TAM, SAM, SOM)?
*   What macro trends (economic cycles, high interest rates) and regulatory shifts (GDPR, EU AI Act) will impact system operations?
*   How do regional variations impact deployment models?
*   What technological changes (such as LLM cost deflation or deprecation of legacy protocols) will occur during the system's development cycle?

### 1.3 What Decisions Depend on It
*   **Infrastructure Strategy**: Single-region vs. Multi-region data residency architecture.
*   **Engineering Capacity & Capital Allocation**: How much capital can be rationally invested in the code based on SOM returns.
*   **Data Models**: Structural mapping of localized privacy boundaries.

### 1.4 What Happens if It Is Skipped
Skipping Stage 2 results in **Regulatory or Scalability Collisions**. The company might build a centralized cloud database for a market that legally mandates local data residency (e.g., Germany/healthcare), leading to a complete rebuild. Or it may build an expensive system for a market too small to support the infrastructure operating cost.

### 1.5 What Evidence Is Required Before Proceeding
*   Authenticated market reports (Gartner, IDC, primary regulatory publications).
*   Signed-off regulatory roadmap outlining geographical restrictions.
*   A unit economic projection showing target customer density and cost tolerance.

---

## 2. Operational Methodology

### 2.1 Translating Market Datasets to Engineering Decisions

To keep market intelligence actionable, every market data point must map directly to an architectural choice:

```
┌────────────────────────────────────────────────────────┐
│  MARKET DATA POINT                                     │
│  "EU AI Act imposes transparency on inference chains"  │
└───────────────────────────┬────────────────────────────┘
                            │ (Maps to)
                            ▼
┌────────────────────────────────────────────────────────┐
│  ARCHITECTURAL CONSEQUENCE                             │
│  "Every LLM generation prompt, temperature, and output  │
│   must be written to an immutable DB audit log"        │
└────────────────────────────────────────────────────────┘
```

| Market Dataset | Technical Impact Vector | Engineering Action |
|---|---|---|
| **TAM / SAM / SOM** | Scale & Concurrency Targets | Determines whether we build single-instance monoliths or horizontal microservices. |
| **Geographic Density** | Latency & Ingress Strategy | Maps CDN, edge computing, and region-binding configurations. |
| **Regulatory Frameworks** | Data Architecture | Enforces RLS, client-side encryption keys, and region isolation. |
| **Technological Lifecycles** | Third-Party Dependencies | Determines whether we integrate APIs or compile proprietary local models. |

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Verified Problem Statement (from Stage 1).
*   Target geographic scope (e.g., US only, global, EU-compliant).
*   Industry sector reports.

### 3.2 Outputs
*   **Market Intelligence Dossier**: Comprehensive quantitative sizing.
*   **Regulatory Constraint Matrix**: Mapped list of compliance targets.
*   **Architectural Mandates Document**: Derived list of database and infrastructure requirements.

---

## 4. Reusable Checklists & Templates

### 4.1 Market Intelligence Checklist
*   [ ] Calculated TAM, SAM, and SOM using bottom-up transactional data.
*   [ ] Documented all applicable regulations in the target regions.
*   [ ] Charted competitor regional concentrations.
*   [ ] Mapped technological lifecycles of all core platform dependencies.
*   [ ] Modeled economic cycle sensitivities (recession impact on customer churn).

### 4.2 Template: Market-to-Architecture Mapping Matrix
```markdown
### 1. Market Sizing Summary
* Bottom-up TAM: $[Value] | SAM: $[Value] | SOM: $[Value]
* Target Customer Count (SOM): [Count]

### 2. Regulatory & Compliance Constraints
* **Regulation**: [e.g., GDPR Article 25]
  * *Impact*: [e.g., Data deletion rights]
  * *Architectural Mitigation*: [e.g., Cascade delete triggers on User UUID]

### 3. Technological Lifeshifts
* **Trend**: [e.g., Third-party API cost decay]
  * *Impact*: [e.g., Direct provider integration becomes cheaper than host building]
  * *Architectural Mitigation*: [e.g., Decouple provider client interfaces behind registry pattern]
```

---

## 5. Scoring & Decision Gates

### 5.1 Scorecard: Market Viability Score (MVS)
Evaluate the market space on a 1-5 scale:

| Vector | Scoring Criteria | Score (1-5) |
|---|---|---|
| **Sufficient Scale** | 1: SOM < $1M ARR. 5: SOM > $50M ARR. | |
| **Regulatory Safety** | 1: Incompatible / high risk of ban. 5: Clean compliance path. | |
| **Margin Room** | 1: High API/Compute costs vs. pricing. 5: 80%+ gross margin target. | |
| **Market Velocity** | 1: Shrinking market. 5: Rapidly expanding target sector. | |

### 5.2 Decision Gate
*   **Exit Criteria**: Market Viability Score **≥ 15 / 20**, with no single vector scoring below 3.
*   **Pass**: Proceed to **Stage 3: User Intelligence**.
*   **Fail**: Return to market identification or abort.
