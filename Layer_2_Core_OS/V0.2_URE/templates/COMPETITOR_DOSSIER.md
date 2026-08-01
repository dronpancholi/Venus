# Template: Competitor Dossier

## 1. Document Context
*   **Project Name**: [Project Name]
*   **Target Competitor**: [Competitor Name]
*   **Date Compiled**: [Date]

---

## 2. Competitive Profile

### 2.1 Commercial Strategy
*   *Pricing Model*: [e.g., Seat-based pricing starting at $199/mo]
*   *Estimated COGS/Margins*: [Describe where they leak margin, e.g., heavy manual support]
*   *Target Audience*: [e.g., SMBs, Enterprise]

### 2.2 Technical Deficiencies
*   *Architecture*: [e.g., Monolith without durable queue worker queues]
*   *Inference Stack*: [e.g., GPT-3.5 static prompts, no grounding checks]
*   *Security Isolation*: [e.g., Shared Postgres database, no Row-Level Security]

---

## 3. Product Comparison Grid

| Feature | Competitor [Name] | Our System | Differentiator |
|---|---|---|---|
| Workflow Durability | Fragile (runs on cron/Celery) | Durable (Temporal Saga) | Survives worker crashes |
| Personalization Quality | Generic placeholders | Grounded LLM + web scrapers | High-converting outreach |
| Data Isolation | Standard logic checks | PostgreSQL RLS Enforced | Zero cross-tenant leaks |

---

## 4. Competitive Verdict
*   **What to Copy**: [Proven interface components or data pipelines]
*   **What to Reject**: [Overly complex setups or seat-based billing loops]
*   **What to Improve**: [Introduce durability, security, or outcome-based billing]
