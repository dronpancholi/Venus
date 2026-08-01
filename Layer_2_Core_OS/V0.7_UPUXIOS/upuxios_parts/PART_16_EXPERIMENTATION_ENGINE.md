# Part 16 — Experimentation Engine

## 1. Context & Strategy

### 1.1 Purpose
The Experimentation Engine Part defines standard operating procedures for continuous testing, feature flagging, conversion tracking, and session audits. It establishes rigorous statistical protocols to validate experience hypotheses before launching updates to 100% of the customer base.

---

## 2. A/B Testing & Statistical Rigor

All user interface experiments must run with adequate cohort sizing to prevent false positives (Type I errors).

### 2.1 Sample Size Calculation
We calculate the required sample size ($N$) per variation using:

$$N = \frac{16 \sigma^2}{\Delta^2}$$

Where:
*   $\sigma^2$ is the baseline variance of the metric (for a binary conversion rate $p$, $\sigma^2 = p(1-p)$).
*   $\Delta$ is the Minimum Detectable Effect (MDE) in absolute terms.
*   *Assumption*: Represents a standard $95\%$ confidence level ($\alpha = 0.05$) and $80\%$ power ($\beta = 0.20$) on a two-tailed hypothesis test.

### 2.2 Cohort Randomization and Routing
*   **User Hash Partitioning**: Cohort routing is determined at request time by hashing the User UUID concatenated with the Experiment Key:
    $$\text{Bucket} = \text{MurmurHash3}(\text{UserUUID} + \text{ExperimentKey}) \pmod{100}$$
    *   $\text{Bucket} < 50 \rightarrow$ Treatment A (Control).
    *   $\text{Bucket} \ge 50 \rightarrow$ Treatment B (Variant).

---

## 3. Feature Flag Architecture

Feature flags isolate changes, decoupling code deployments from feature releases.

### 3.1 Flags & Rollouts Control Flow
```
                           [Feature Key Check]
                                    │
                         [Is Globally Disabled?]
                          ├── Yes ──► [Fallback Version]
                          └── No  ──► [Targeting Rules Match?]
                                            ├── Yes ──► [Rollout % Check]
                                            └── No  ──► [Fallback Version]
```

### 3.2 Dynamic Targeting Parameters
*   **Internal Testing**: Enforced 100% release to `@projectvenus.ai` email domains.
*   **Canary Rollouts**: Incremental traffic routing ($1\% \rightarrow 5\% \rightarrow 20\% \rightarrow 100\%$) backed by active latency and error-rate monitoring.
*   **Fallback Config**: If client-side SDK check times out or network drops, default to the safe fallback state (`isActive = false`) within $100\text{ms}$.

---

## 4. Conversion Funnel Tracking

Funnels monitor drop-off rates across critical product conversion steps.

### 4.1 Funnel Visual Mapping
Funnels are represented visually in analytics views, highlighting drop-off metrics between stages:

```
[Stage 1: Landing (100%)]
   │
   ▼  Drop-off: 40% (Time-on-step: 14s)
[Stage 2: Sign-up (60%)]
   │
   ▼  Drop-off: 25% (Time-on-step: 85s)
[Stage 3: Workspace Created (45%)]
   │
   ▼  Drop-off: 10% (Time-on-step: 30s)
[Stage 4: Activation Milestone (35%)]
```

---

## 5. Session Replay & Privacy Masking

Session replays help diagnose usability blockers, but require strict privacy rules.

### 5.1 Privacy & PII Masking Standards
To comply with GDPR, HIPAA, and CCPA:
*   **Default Masking**: All input elements (`<input>`, `<textarea>`, `<select>`) must be masked by default at the browser client level before transmission. Text characters are replaced with asterisk symbols (`***`).
*   **Explicit Excludes**: Add the custom attribute `data-private` to exclude sensitive containers, charts, or payment details from recording grids.
*   **Explicit Consent**: Replays are active only for users who have consented to analytical tracking via cookie banners.

---

## 6. Experimentation Checklist
*   [ ] Checked sample size requirements using baseline conversion rates and target MDE.
*   [ ] Ensured user hash assignment logic prevents cohort crossover.
*   [ ] Configured feature flags with fallback variables.
*   [ ] Designed conversion funnel tracking coordinates.
*   [ ] Audited recording scripts to verify PII masking on input fields.
