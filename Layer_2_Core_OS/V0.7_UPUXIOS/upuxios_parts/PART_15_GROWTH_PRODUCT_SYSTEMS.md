# Part 15 — Growth Product Systems

## 1. Context & Strategy

### 1.1 Purpose
The Growth Product Systems Part defines user acquisition, onboarding, activation, and monetization patterns. It establishes self-serve conversion mechanisms, viral loops, and contextual upgrade gates.

### 1.2 PLG Economics & Virality
To achieve self-sustaining growth, we monitor the Viral Coefficient ($K$):

$$K = i \times c$$

Where:
*   $i$ is the average number of invitations sent per active user.
*   $c$ is the conversion rate of invites to active accounts.
*   *Requirement*: Systems must aim for $K > 1.0$ by placing low-friction sharing triggers within natural user success pathways.

---

## 2. Onboarding & Activation Flows

Onboarding must minimize time-to-value (TTV) and guide users toward their activation milestone ("Aha!" moment).

### 2.1 The Progressive Profiling Onboarding Wizard
*   **Split Steps**: Maximize completion rates by splitting setup forms into $\le 3$ steps.
*   **Skip Option**: Allow users to bypass onboarding steps and land directly in the workspace.
*   **Progress Indicators**: Render a linear step tracker showing: `[1: Setup Profile] ──► [2: Invite Team] ──► [3: Connect Workspace]`.

### 2.2 Reusable Dynamic Product Tours
*   **Interactive Spotlights**: Highlight key UI controls sequentially using high-contrast tooltip backdrops.
*   **Dismissal Bounds**: Product tours must feature a clear `[Dismiss Tour]` link at every stage to avoid user frustration.

```
+--------------------------------------+
|  Tool Spotlight Banner               |
|  "This is your primary analytics dashboard..."
|  [Dismiss]          [Next Step (1/3)]|
+--------------------------------------+
```

---

## 3. Pricing Layout & Conversion Mechanics

Monetization layouts must clarify pricing value differentials and simplify checkouts.

### 3.1 Tiered Feature Comparison Grid
*   **Billing Frequency Toggle**: Present an obvious slider to swap between Monthly and Annual billing (displaying a clear `"Save 20%"` tag for annual billing).
*   **Visual Highlights**: The target enterprise tier card should be highlighted with a distinctive border color and labeled with a `"Most Popular"` badge.
*   **Visual Checkmarks**: Active features are marked with green checkmarks, while unavailable features are grayed out or left out entirely.

### 3.2 Contextual Upgrade Paywalls (Gating)
Upgrade triggers must appear when usage limits approach exhaustion.
*   **Quota Progress Indicators**: In-app usage graphs must show warning colors (Orange at 80% usage, Red at 100% usage).
*   **Contextual Upgrade Modal**: When usage exceeds 100%, block write actions and launch a slide-in drawer showing:
    *   *Headline*: `"You have reached your 50 free report generation limit."`
    *   *Value Prop*: `"Upgrade to Pro for unlimited generation, team exports, and historical tracking."`
    *   *Primary Action*: `[Upgrade to Pro]` (takes user directly to the credit card input page).

---

## 4. Growth Product Systems Checklist
*   [ ] Checked onboarding sequence TTV (Time-To-Value) benchmarks.
*   [ ] Configured viral invite triggers in primary workflows.
*   [ ] Designed pricing grid with a Monthly/Annual toggle and discount tags.
*   [ ] Verified progress gauges trigger warning colors at 80% usage.
*   [ ] Implemented non-obtrusive upgrade modals when usage thresholds are reached.
