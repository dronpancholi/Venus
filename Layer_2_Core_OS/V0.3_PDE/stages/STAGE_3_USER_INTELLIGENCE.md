# Stage 3 — User Intelligence

## 1. Governance & Rationale

### 1.1 Why It Exists
Software is operated by human beings within organizational frameworks. Researching user personas, cognitive workflows, frustrations, and buying habits prevents building technically correct systems that fail in practice due to poor user adoption. It establishes the design requirements for UI/UX, access privileges, and workflow triggers.

### 1.2 What Questions It Answers
*   Who is the operator, who is the buyer, and who is the internal supervisor?
*   What is the exact sequence of cognitive and manual steps in the user's current workflow?
*   What are the psychological frustrations and cognitive load peaks in their daily tasks?
*   How do purchase decisions occur in their organization, and what are the barriers to switching from legacy tools?

### 1.3 What Decisions Depend on It
*   **User Interface & Experience (UI/UX) Design**: CLI vs. Web Console vs. API-first; density of information layout.
*   **Authentication & Access Structure**: RBAC (Role-Based Access Control) scopes (operator, viewer, auditor).
*   **Integrations & Notification Hubs**: Where do alert signals route (Slack, email, SMS, push)?

### 1.4 What Happens if It Is Skipped
Skipping Stage 3 results in **Product-User Mismatch**. The team will build an advanced command-line tool for non-technical agency marketers, or a complex UI dashboard for system administrators who prefer APIs. This mismatch leads to poor user retention and immediate churn.

### 1.5 What Evidence Is Required Before Proceeding
*   Detailed user journey map detailing current daily step-by-step actions.
*   A minimum of 5 mapped enterprise buying committee profiles (for B2B software).
*   A documented profile of switching cost barriers.

---

## 2. Operational Methodology

### 2.1 The User Cognitive Load Mapping Method
We profile the user's workflow to identify where cognitive friction occurs. Every high-friction step must be targeted for automation:

```
[Step 1: Open Ahrefs] ──► [Step 2: Copy domains] ──► [Step 3: Paste to sheet] ──► [Step 4: Manual search emails]
      Low load                 Low load                  Low load                      HIGH COGNITIVE LOAD
                                                                                     (Point of Churn/Error)
                                                                                               │
                                                                                               ▼
                                                                                   [Target for Automation]
```

### 2.2 Reusable User Profiling Frameworks

#### 2.2.1 The B2B Buying Committee Matrix
B2B software must satisfy multiple profiles inside a single tenant customer:

| Role | Motivations | Primary Blocker | Key UI/UX Target |
|---|---|---|---|
| **Operator** (End User) | Speed, automation, error reduction | High cognitive load, complexity | Simple queue views, keyboard shortcuts |
| **Manager** (Supervisor) | Team performance, reporting, audit | Lack of visibility, data silos | Dashboard views, CSV exports, approval screens |
| **IT/Security** (Buyer Gate) | Compliance, security, data residency | Data leaks, open ports | SAML SSO, Row-Level Security, audit logs |
| **Financial Buyer** (Exec) | Return on investment (ROI), low TCO | Cost overruns, seat inflation | Clear pricing models, usage-to-value reports |

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Verified Problem Statement (from Stage 1).
*   Market Sizing and Segments (from Stage 2).
*   User interview video logs and transcripts.

### 3.2 Outputs
*   **User Persona Dossiers**: Mapped profiles for each buying committee role.
*   **User Journey Worksheets**: Current state workflows with cognitive load ratings.
*   **UX/UI Guardrails**: Concrete specifications for the application interface.

---

## 4. Reusable Checklists & Templates

### 4.1 User Research Checklist
*   [ ] Interviewed target end-operators and supervisors.
*   [ ] Documented the exact manual workflows of target users.
*   [ ] Calculated the switching cost (time to export, train, and deploy) for legacy tools.
*   [ ] Mapped the organizational buying committee structure.
*   [ ] Identified the primary retention drivers (what makes them return daily).

### 4.2 Template: User Journey Workflow Map
```markdown
### 1. Persona Profile
*   **Title**: [e.g., SEO Specialist]
*   **Domain Context**: [e.g., Digital Agency, 20 active clients]
*   **Tech Literacy**: [Low / Medium / High]

### 2. Current Workflow Step-by-Step
1.  **Step 1**: [Action] | *Tool*: [Tool name] | *Friction*: [1-5]
2.  **Step 2**: [Action] | *Tool*: [Tool name] | *Friction*: [1-5]
3.  **Step 3**: [Action] | *Tool*: [Tool name] | *Friction*: [1-5]

### 3. Key Frustrations & Opportunities
*   *Bottleneck*: [State the step where the user spends the most manual hours or makes errors]
*   *Requirement*: [State how our system will automate or secure this step]
```

---

## 5. Scoring & Decision Gates

### 5.1 Scorecard: User Alignment Index (UAI)
Evaluate user alignment on a 1-5 scale:

| Vector | Scoring Criteria | Score (1-5) |
|---|---|---|
| **Pain Urgency** | 1: Users don't care. 5: Users are actively looking for solutions. | |
| **Switching Viability** | 1: High database migration locks. 5: Low migration friction. | |
| **Adoption Ease** | 1: Requires months of training. 5: Intuitive/auto-onboarding. | |
| **Retention Strength** | 1: One-off utility. 5: Enforces daily operational habits. | |

### 5.2 Decision Gate
*   **Exit Criteria**: User Alignment Index score **≥ 15 / 20**, with no single vector scoring below 3.
*   **Pass**: Proceed to **Stage 4: Competitive Intelligence**.
*   **Fail**: Return to user discovery or adjust target ICP.
