# User Journey Map Template

## 1. Document Overview
This document maps a specific user persona's experience with the product over time. It documents their actions, thoughts, and emotional states across different stages of interaction, identifying opportunities to streamline workflows and drive user activation.

---

## 2. Journey Parameters
*   **Target User Persona:** `[Insert Persona Name, e.g., Data-driven Dave]`
*   **Journey Scenario:** `[e.g., Setting up a new automated data pipeline for the first time]`
*   **Primary Journey Goal:** `[e.g., Successfully connect a database and verify that data flows clean in < 10 mins]`

---

## 3. High-Level Journey Phases
```
  [1] DISCOVERY  -->  [2] ONBOARDING  -->  [3] VALUE REALIZATION  -->  [4] DEEP HABIT  -->  [5] EXPANSION
 (Awareness/Signup)   (First-run Setup)       ("Aha!" Moment)          (Daily Core Loop)   (Referral/Upgrade)
```

---

## 4. User Journey Matrix
Use the matrix below to document the user's steps, thoughts, emotional fluctuations, and optimization opportunities.

| Journey Phase | 1. Discovery / Signup | 2. Onboarding / Setup | 3. First Value ("Aha!") | 4. Daily Core Loop | 5. Retention / Advocacy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **User Action Steps** | *e.g., Clicks landing page ad; signs up with Google OAuth.* | *e.g., Guided onboarding tour; enters DB credentials.* | *e.g., Runs first query; sees populated dashboard.* | *e.g., Logs in daily to check reports; sets up alerts.* | *e.g., Recommends tool to colleagues; upgrades plan.* |
| **Touchpoints / Channels**| *Google Search, Landing Page, Auth flow.* | *Setup Wizard, Verification emails.* | *Main Dashboard, Success Modal, CSV export.* | *Web app, Slack notifications, email summaries.* | *Billing page, referral links, review sites.* |
| **User Thoughts / Quotes**| *"Will this connect to my Postgres database easily?"* | *"Why do they need my credit card details already?"* | *"Wow, that query ran in 300ms. That's fast!"* | *"I need to make sure this alerts me if a sync fails."*| *"This saved me 4 hours this week. I should share this."*|
| **Emotional State (1-5)** | `3 - Neutral` | `2 - Frustrated (Friction)` | `5 - Delighted ("Aha!")` | `4 - Satisfied` | `5 - Enthusiastic` |
| **Pain Points / Friction** | *Too much text on landing page.* | *Tough SQL configuration steps; security fears.* | *CSV output looks slightly unformatted.* | *Lack of bulk edit features.* | *Upgrade process has sales wall.* |
| **Opportunities / Fixes** | *Simplify headline; add instant video demo.* | *Add pre-filled DB templates; show SOC2 badge.* | *Auto-format columns on export.* | *Create keyboard shortcuts for bulk actions.* | *Self-serve upgrade paths.* |
| **Phase KPIs** | *Conversion rate (%)* | *Activation rate (%)* | *Time to value (TTV)* | *Daily Active Users (DAU)* | *Net Promoter Score (NPS)* |

---

## 5. Emotional Arc Visualization
Visualizing the user's emotional experience helps highlight where the "Valleys of Despair" (friction) and "Peaks of Delight" occur.

```
  5 - DELIGHT        .                       . (Aha!)                                            . (Referral)
                     .                     . .                                                 . .
  4 - SATISFIED      .                   .   .                                 . . . . . . . .
                     .  . (Discovery)  .     .                               .
  3 - NEUTRAL        ..              .       .                             .
                                   .         . (Friction Valley)         .
  2 - FRUSTRATED                 .           .                         .
                               .             .                       .
  1 - PAIN
                     +------------------------------------------------------------------------------------>
                         Discovery       Onboarding      First Value       Daily Loop        Expansion
```

---

## 6. Moments of Truth
Identify the single most critical actions in the journey map:

*   **The Activation Milestone (Aha! Moment):** The precise point where the user first experiences the product's core value proposition (e.g., *User sees active data sync on dashboard*).
*   **The Critical Friction Point:** The step where most drop-offs occur (e.g., *Connecting production databases before testing*).
*   **Strategic Fix:** [e.g., Provide a "Sandbox Database" button so users can test queries with dummy data without risk.]

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial creation of User Journey Map template.
