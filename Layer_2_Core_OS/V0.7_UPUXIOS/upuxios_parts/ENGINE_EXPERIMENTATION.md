# Engine: Experimentation

## 1. Context & Strategy

### 1.1 Purpose
The Experimentation Engine processes user interaction data, conversion events, and cohort identifiers to compute conversion lift, track p-values, evaluate statistical power, and audit privacy masking compliance for all ongoing tests.

### 1.2 Philosophy
Never ship design modifications based on subjective opinions. Decisions must be backed by statistically significant test cohorts, clean control distributions, and strict compliance with privacy laws.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Control and variant event streams, user consent states, session logs, custom experiment identifiers, MDE goals as defined in [Part 16](file:///Users/dronpancholi/Developer/01_Strategic/Venus/upuxios_parts/PART_16_EXPERIMENTATION_ENGINE.md).
*   **Outputs**: A/B Test Significance Report, details on conversion lift, p-value, statistical power, and privacy audit status.

### 2.2 Auditing Pipeline
```
               [Ingest Experiment Cohort Events]
                              │
               [Validate Hash Assignment Rules]
                └── Verify user bucket distribution
                              │
               [Compute Conversion Lift & Math]
                └── Calculate z-scores and p-values
                              │
               [Evaluate Statistical Significance]
                └── Check power level and sample bounds
                              │
                [PII Masking Privacy Audit]
```

---

## 3. Algorithmic Checks & Statistical Protocol

### 3.1 Z-Score & Significance Verification
For a binary conversion rate check, the engine calculates the pooled standard error ($SE_{pooled}$) and $Z$-score:

$$p_{pooled} = \frac{x_A + x_B}{n_A + n_B}$$

$$SE_{pooled} = \sqrt{p_{pooled}(1 - p_{pooled}) \left( \frac{1}{n_A} + \frac{1}{n_B} \right)}$$

$$Z = \frac{p_B - p_A}{SE_{pooled}}$$

Where:
*   $p_A, p_B$ are the conversion rates of Control and Variant cohorts.
*   $n_A, n_B$ are the sample sizes.
*   $x_A, x_B$ are the number of conversions.

The engine verifies if $p$-value $< 0.05$ (equivalent to $|Z| > 1.96$ for a two-tailed test). If statistical significance is achieved, the variant is flagged as ready for rollout.

### 3.2 Sample Size Gate
The engine compares the current sample size against the calculated minimum ($N_{min}$). If $n_i < N_{min}$, it flags the test as underpowered and prevents early termination.

### 3.3 Privacy & PII Masking Verification
*   Audits dynamic recording logs to ensure that fields with inputs did not transmit sensitive characters (e.g. checks that all recorded input content is replaced by asterisks `***` or omitted via `data-private` tags).

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that user assignment hashes prevent cohort crossover.
*   [ ] Verified the experiment has reached the required sample size ($N_{min}$).
*   [ ] Calculated the $Z$-score and $p$-value for the target metric.
*   [ ] Checked that statistical power exceeds the $80\%$ minimum threshold.
*   [ ] Confirmed PII masking rules are active and verified on session logs.
*   *Exit Criteria*: Experiment calculations verified and signed off for product release.
