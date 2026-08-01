# Template: Architecture Decision Record (ADR)

## ADR-[ID]: [Title, e.g., Migrate Session Store to Redis]

*   **Status**: Proposed / Accepted / Deprecated
*   **Intake ID**: DEC-[UUID]
*   **Audit Hash**: AUD-[HASH]
*   **Date**: YYYY-MM-DD

---

## 1. Context & Problem Statement
*Describe the technical context and problem setting. What are the constraints forcing this decision?*

---

## 2. Decision & Action
*Describe the selected action or technology solution. What are the implementation details?*

---

## 3. Consequences & Trade-offs
*Detail the downstream impacts of this decision.*

*   *Positive*: [e.g., Worker memory usage falls by ~40%]
*   *Negative*: [e.g., Latency increases by ~2ms due to network roundtrips]
*   *Security*: [e.g., Data is now encrypted at rest in Redis nodes]

---

## 4. Rejection History
*List alternative solutions that were evaluated and explain why they were rejected.*

*   *Option A (Local Memory)*: Rejected because concurrent storage exceeded node memory constraints.
*   *Option B (DynamoDB)*: Rejected due to higher latency overhead.
