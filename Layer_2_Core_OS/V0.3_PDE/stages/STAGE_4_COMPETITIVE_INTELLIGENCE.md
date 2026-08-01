# Stage 4 — Competitive Intelligence

## 1. Governance & Rationale

### 1.1 Why It Exists
We do not build software in a vacuum. Competitive intelligence ensures we map the technical and commercial landscape of our competitors, identifying where they are weak, where their architecture fails, and how their pricing structure works. This prevents building copycat features and defines our engineering moat and differentiation strategy.

### 1.2 What Questions It Answers
*   Who are the direct, indirect, substitute, and open-source competitors?
*   What are their architectural limitations (e.g., lack of durable queuing, poor api scaling)?
*   How do they price their services, and what is their cost structure?
*   What parts of their product workflows are highly rated, and what parts cause user churn?

### 1.3 What Decisions Depend on It
*   **Architectural Moat**: Determining where we must over-engineer (e.g., using Temporal for durability when competitors use fragile scripts).
*   **Pricing Architecture**: Deciding on consumption-based, seat-based, or outcome-based database schemas.
*   **Interface Scope**: Deciding what legacy workflows to copy and what to reject.

### 1.4 What Happens if It Is Skipped
Skipping Stage 4 results in **Commoditization**. The company builds a product that lacks unique technical defensibility, forcing the commercial team to compete purely on price. Alternatively, the engineering team may spend months building features that competitors already offer in a superior or cheaper format.

### 1.5 What Evidence Is Required Before Proceeding
*   Completed feature grids comparing direct competitors.
*   Documented pricing schemes and cost structures for each competitor.
*   Technical teardowns (where possible) of competitor API responses, network payloads, or open-source repositories.

---

## 2. Operational Methodology

### 2.1 The Competitive Decomposition Grid
Every competitor is evaluated across technical, product, and commercial vectors:

```
                            ┌────────────────────────┐
                            │    COMPETITOR X        │
                            └───────────┬────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
   [Technical Teardown]          [Product Teardown]       [Commercial Teardown]
   - DB / Infrastructure         - User Workflow           - Pricing Multiple
   - API Performance             - UX / Speed              - Go-To-Market strategy
   - Scalability ceiling         - AI Integration          - Target ICP segment
```

### 2.2 Reusable Competitive Teardown Criteria

#### 2.2.1 Technical Evaluation
*   *Scale Limits*: How does their system handle high load? Do they experience performance degradation?
*   *Moat Assessment*: Is their core feature easily replicable, or does it require proprietary integrations?
*   *Security / Isolation*: Do they support enterprise-grade isolation (like RLS) or do they run shared-schema setups?

#### 2.2.2 Product & AI Evaluation
*   *AI Sophistication*: Is their AI a simple GPT wrapper, or do they run semantic models, RAG validation, and grounding checks?
*   *UX Deficiencies*: What are the main points of friction in their interfaces?

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   User Journey Map (from Stage 3).
*   List of competitor brand names (direct and indirect).
*   Public documentation, API reference pages, and price listings of competitors.

### 3.2 Outputs
*   **Competitor Dossier**: A structured breakdown of each competitor.
*   **Strategic Differentiation Matrix**: Map showing where our architecture is superior.
*   **Copy/Reject/Improve Blueprint**: Concrete engineering requirements.

---

## 4. Reusable Checklists & Templates

### 4.1 Competitive Research Checklist
*   [ ] Identified all direct, indirect, and substitute competitors.
*   [ ] Documented competitor pricing models and calculated their estimated gross margins.
*   [ ] Analyzed competitor user interfaces and documented usability flaws.
*   [ ] Teardown competitor API structures (analyzing network request payloads).
*   [ ] Isolated the competitor's structural moat.

### 4.2 Template: Competitor Technical Dossier
```markdown
### 1. Competitor Profile
*   **Name**: [Competitor Name]
*   **Target Segment**: [e.g., Enterprise SaaS, SMB]
*   **Estimated ARR**: $[Value]

### 2. Technical Architecture Assessment
*   *Infrastructure Stack*: [e.g., AWS, Serverless, Monolith]
*   *AI Capability*: [Wrapper vs. Fine-tuned vs. RAG]
*   *Key Technical Defect/Limit*: [e.g., API limits, slow background processing, lack of durability]

### 3. Copy / Reject / Improve Strategy
*   **Copy**: [What works well in their system that we must include]
*   **Reject**: [What is over-engineered or useless in their product]
*   **Improve**: [What structural feature we will build in a superior format]
```

---

## 5. Scoring & Decision Gates

### 5.1 Scorecard: Competitive Advantage Score (CAS)
Evaluate our prospective system against the competition on a 1-5 scale:

| Vector | Scoring Criteria | Score (1-5) |
|---|---|---|
| **Defensibility** | 1: Easy to copy. 5: Strong architectural/integration moat. | |
| **UX Superiority** | 1: Equivalent UX. 5: Complete removal of core workflow steps. | |
| **Economic Advantage**| 1: Competitor can underprice us. 5: Our unit costs are significantly lower. | |
| **AI Quality** | 1: Standard wrappers. 5: Grounded, high-trust agent outputs. | |

### 5.2 Decision Gate
*   **Exit Criteria**: Competitive Advantage Score **≥ 15 / 20**, with no single vector scoring below 3.
*   **Pass**: Proceed to **Stage 5: Technology Intelligence**.
*   **Fail**: Pivot the solution architecture or GTM differentiation.
