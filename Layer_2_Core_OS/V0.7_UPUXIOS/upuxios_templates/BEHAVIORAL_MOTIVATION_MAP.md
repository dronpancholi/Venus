# Behavioral Motivation Map

## 1. Document Overview
This document maps user behaviors, motivators, and triggers using established behavioral science models. Its goal is to design workflows that drive habit formation, increase engagement, and eliminate user friction.

---

## 2. Behavioral Framework: Fogg Behavior Model (FBM)
We analyze and predict user action using the Fogg Behavior Model:

$$B = MAP$$

Where:
*   $B$ = Behavior (the target action we want the user to perform).
*   $M$ = Motivation (the user's drive to act).
*   $A$ = Ability (the user's capacity to perform the behavior).
*   $P$ = Prompt (the trigger or cue that calls the user to action).

All three elements ($M, A, P$) must converge at the same moment for a behavior to occur. If any element is below the activation threshold, the behavior fails.

```
 MOTIVATION
    High ^
         |          * Behavior Occurs (Above Action Line)
         |        .
         |       .  Action Line
         |      .
         |     .
         |    .
     Low |--------------------------------------->
         Low (Hard to do)              High (Easy to do)
                               ABILITY
```

---

## 3. Motivation Factors ($M$)
To evaluate the user's emotional and strategic drives, we assess three pairs of core motivators:

1.  **Pleasure / Pain:** Immediate sensory reactions.
2.  **Hope / Fear:** Anticipation of good or bad outcomes (e.g., hope of growth, fear of missing out).
3.  **Social Acceptance / Rejection:** Desire to belong, fit in, and be valued by peers.

---

## 4. Ability Factors ($A$)
Ability represents the simplicity of the action. We analyze ability across the 6 Simplicity Factors:

| Simplicity Factor | Description | Score (1-5)* | Friction Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Time** | How long does it take to do this? | | Streamline clicks, auto-fill fields. |
| **Money** | What is the financial cost? | | Provide free tiers or transparent pricing. |
| **Physical Effort** | What physical actions are required? | | Optimize tap targets; reduce typing. |
| **Brain Cycles** | How much mental focus is required? | | Reduce cognitive load ($7 \pm 2$ chunks). |
| **Social Deviance** | Does it go against social norms? | | Provide social proof and clear permissions. |
| **Non-Routine** | How much does it disrupt their routine? | | Align with existing native habits. |

*\*Score: 1 = Extremely Difficult / High Friction, 5 = Extremely Simple / Frictionless*

---

## 5. Prompt Types ($P$)
Prompts initiate the behavior. We classify prompts into three categories:

1.  **Spark:** For users with high Ability but low Motivation. Combines a prompt with an emotional motivator (e.g., "Unlock a free credit now!").
2.  **Facilitator:** For users with high Motivation but low Ability. Combines a prompt with an action simplifier (e.g., "Install in 1-click").
3.  **Signal:** For users who have both high Motivation and high Ability. Serves as a pure reminder (e.g., "Your report is ready").

---

## 6. Behavioral Motivation Mapping Table
Use this table to map out specific user actions in the product.

| Target Behavior ($B$) | User Segment | Motivation Drivers ($M$) | Ability Barriers ($A$) | Applied Prompt ($P$) | Success Metric |
| :--- | :--- | :--- | :--- | :--- | :--- |
| *e.g., Complete onboarding* | *New sign-ups* | *Hope: Career advancement* | *Brain Cycles: Complex form fields* | *Facilitator: Single Sign-On (SSO)* | *Activation rate (> 75%)* |
| | | | | | |
| | | | | | |
| | | | | | |

---

## 7. Habit Loop Design (Hooked Model)
To build self-sustaining user engagement, define the habit loop for the primary feature:

```
               [1] TRIGGER (Internal/External)
                       |
                       v
   [4] INVESTMENT  <--------->  [2] ACTION (B = MAP)
         |                              |
         +------- [3] VARIABLE REWARD <--+
```

1.  **Trigger:**
    *   *External Trigger:* (e.g., push notification, email, UI badge)
    *   *Internal Trigger:* (e.g., anxiety, boredom, desire to connect)
2.  **Action:** The simplest physical behavior done in anticipation of a reward (e.g., scrolling, pulling to refresh).
3.  **Variable Reward:** The satisfaction of the user's craving that leaves them wanting more. Must include variable outcomes (e.g., social validation, new content, self-achievement).
4.  **Investment:** The user puts something of value back into the system (e.g., data, reputation, time, money) that makes the next cycle easier and more compelling.

---

## 8. Revision History
*   **V1.0 (2026-06-26):** Initial template design based on Fogg's Behavior Model and Hooked framework.
