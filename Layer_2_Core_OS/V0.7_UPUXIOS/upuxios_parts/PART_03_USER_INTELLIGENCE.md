# Part 03: User Intelligence & ICP Personas

## 1. Context & Strategy
User Intelligence defines the operational attributes, behaviors, environments, and motivations of our target users. Under Project Venus, design does not happen in a vacuum; every screen layout, system speed target, and terminology set must align with the validated Ideal Customer Profile (ICP) dossier of the user who will operate the application.

---

## 2. Ideal Customer Profile (ICP) Personas

We categorize users by three operational dimensions:

| Attribute Dimension | Key Variables | Enterprise Metric |
| :--- | :--- | :--- |
| **Domain Expertise** | High regulatory training vs. general office staff | Operational Error Rate |
| **Technical Capacity** | Advanced query writers, average GUI operators, or mobile-only | Time-to-Task Completion |
| **System Environment** | High-speed multi-monitor setups vs. slow latency mobile links | Max Page Load Weight |

### 2.1 Persona Templates
For every user archetype, we document:
*   **Role & Title**: E.g., Lead Systems Admin.
*   **Primary Job**: E.g., Maintain 99.99% service availability.
*   **Tool Stack**: E.g., Datadog, AWS Console, Slack, JIRA.
*   **Hardware Profile**: E.g., dual-monitor, high-spec macOS, low-latency broadband.

---

## 3. Empathy Mapping Model

An empathy map splits user behaviors and observations into four sectors:

```
+-----------------------------------+-----------------------------------+
|               SAYS                |              THINKS               |
| E.g., "I need this audit data     | E.g., "If I make one mistake here,|
| export to be faster."             | I could get the team audited."    |
+-----------------------------------+-----------------------------------+
|               DOES                |              FEELS                |
| E.g., Copies values manually from | E.g., Anxious about security keys |
| one terminal window to another.   | exposure during onboarding.       |
+-----------------------------------+-----------------------------------+
```

---

## 4. User Journey Mapping & Touchpoints
User Journeys map steps over time, noting:
1.  **Stage**: Discovery, Onboarding, Daily Use, Recovery, Upgrade.
2.  **User Action**: Specific steps the user takes.
3.  **Touchpoints**: GUI pages, command line inputs, email alerts, slack integrations.
4.  **Customer Pain Points**: Points of high friction or delay.
5.  **Emotional Curve**: A scale from $+5$ (highly motivated) to $-5$ (frustrated/ready to churn).
6.  **System Dependency**: Supporting backend databases, caching nodes, or third-party APIs.

### 4.1 Emotional Curve Audit
Any stage of the user journey that drops below an emotional score of $0$ must have a corresponding "Friction Resolution Epic" scheduled in the next sprint cycle to stabilize user retention.

---

## 5. User Intelligence Checklist
*   [ ] Persona attributes are validated against at least $5$ real customer interviews.
*   [ ] Hardware and networking constraints of the target user are documented.
*   [ ] Empathy map fields (Says, Thinks, Does, Feels) have been updated post-user interviews.
*   [ ] Emotional curves of the User Journey Map contain no stages with negative scores.
