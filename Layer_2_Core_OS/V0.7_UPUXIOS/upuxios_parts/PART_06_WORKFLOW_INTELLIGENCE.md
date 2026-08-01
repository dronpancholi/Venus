# Part 06: Workflow Intelligence & Error States

## 1. Context & Strategy
Workflow Intelligence ensures that the interaction paths a user takes to complete a task are clean, linear, and highly resilient to system-level exceptions. This manual establishes standards for task flow design, edge case routing, fallback/recovery loops, and user-facing error communication under Project Venus.

---

## 2. Task Flow Specifications
Every user task must be mapped to a clean flow model showing the interaction node, business logic execution, and database state change.

```
                  [User Inputs Query]
                           │
                           ▼
                  {Query Validation}
                   /              \
         (Valid) /                  \ (Invalid)
               ▼                      ▼
        [Execute Query]         [Show Real-Time Inline Error]
               │                      │
               ▼                      ▼
      [Display Results]         [Request Revision]
```

### 2.1 Task Flow Rules:
*   **Linearity**: No workflow should branch more than $3$ times. If more branches exist, split the process into child tasks.
*   **Status Indicators**: Every asynchronous process taking longer than $500\text{ms}$ must show a progressive indicator (loader, progress bar, or percentage tracker).
*   **State Retention**: If an action fails mid-workflow, all user-entered data must be persisted in local storage or temporary database cache so the user does not have to re-enter details.

---

## 3. Edge Case & Failure Recovery Loops

### 3.1 Common Failure Categories & UX Requirements

#### Validation Failures
*   *Rule*: Validate inputs on focus loss (blur) and submit. Do not show error states before the user completes input.
*   *Display*: Place error text directly below the invalid input element. Set label color using WCAG AAA contrast standard (red base with adequate contrast, e.g., `#D32F2F`).

#### Timeout Scenarios
*   *Rule*: Set user interaction timeout to $30\text{s}$ for API calls. If the backend fails to respond, cancel connection and display a Retry action button.

#### Rate Limits
*   *Rule*: When rate limits are tripped, show a user-friendly timer window (e.g., "Too many requests. Please try again in 45 seconds").

#### Empty States
*   *Rule*: Never display a blank screen. Provide an illustration, a clear explanation of why the state is empty, and a primary action button (e.g., "Add First Asset").

---

## 4. Error Message Architecture & Code Schema
Error messages must help the user resolve the issue immediately, avoiding cryptic codes.

### 4.1 Message Syntax Structure:
```
[Context Flag] - [What happened] + [Why it happened] + [Action to resolve]
```

*   **Example (Bad)**: `Error 500: Database insertion failed.`
*   **Example (Good)**: `[UPLOAD-403] - File upload rejected because the document size exceeds the 10MB limit. Compress your image and try again.`

---

## 5. Workflow Intelligence Checklist
*   [ ] Checked that every workflow has a documented task flow diagram.
*   [ ] Ensured all asynchronous API calls display load state triggers at $\ge 500\text{ms}$.
*   [ ] Confirmed empty states for all lists contain a primary call-to-action button.
*   [ ] Audited error messages to conform to the context-action syntax.
*   [ ] Confirmed user input is cached during transaction failure states.
