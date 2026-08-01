# Template: Bounded Context Document

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Bounded Context Name**: [e.g., Billing Context]
*   **Date**: [Date]

---

## 2. Context Boundaries & Responsibilities
*Define the core domain responsibilities of this specific context, outlining what is inside and what is outside.*

*   **Responsibilities (Inside)**:
    1.  [e.g., Processing client payments via Stripe API]
    2.  [e.g., Managing subscription tier allocations]
*   **Exclusions (Outside)**:
    1.  [e.g., Storing user password hashes (responsibility of Auth Context)]
    2.  [e.g., Dispatching transaction email notifications (handled by Mail Context)]

---

## 3. Bounded Context Ubiquitous Language
*Define domain-specific terms to ensure alignment across code and documentation.*

*   **Term 1: Subscriber**
    *   *Definition*: A user profile with an active, paid tier record in the billing table.
*   **Term 2: Transaction**
    *   *Definition*: A single payment ledger item representing an event processed on the Stripe API gateway.

---

## 4. Bounded Context Verification Checks
*   [ ] Schema isolation confirmed (Zero shared tables with other contexts).
*   [ ] Communication boundaries conform to the Context Map.
