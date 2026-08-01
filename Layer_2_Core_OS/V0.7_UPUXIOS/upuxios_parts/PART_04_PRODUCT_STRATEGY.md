# Part 04: Product Strategy & Prioritization

## 1. Context & Strategy
Product Strategy is the bridge between validated discovery opportunities and the engineering execution pipeline. This manual establishes structural models for feature prioritization, value classification, and roadmap construction, ensuring that resource allocation is optimized for business viability, technical feasibility, and customer impact.

---

## 2. RICE Prioritization Engine
To eliminate subjective arguments during feature selection, we evaluate all product requirements using the RICE framework.

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

### 2.1 Parameter Scaling Definitions

#### Reach (R)
Estimated number of users or organizations affected per quarter:
*   *Scale*: Actual numeric count based on telemetry data (e.g., $15,000$ active users).

#### Impact (I)
Estimated increase in user value or conversion lift:
*   $3.0$: Massive impact (critical value/revenue driver).
*   $2.0$: High impact (dramatic workflow improvement).
*   $1.0$: Medium impact (incremental improvement).
*   $0.5$: Low impact (minor refinement).
*   $0.25$: Minimal/Negligible impact.

#### Confidence (C)
Percentage metric reflecting evidence supporting our Reach, Impact, and Effort estimations:
*   $1.0$ ($100\%$): High confidence; backed by direct customer research, analytics data, and technical prototype trials.
*   $0.8$ ($80\%$): Medium confidence; backed by qualitative research or comparable competitor data.
*   $0.5$ ($50\%$): Low confidence; based on anecdotal feedback or assumptions.
*   $0.2$ ($20\%$): Speculative; high estimation variance.

#### Effort (E)
Person-months required to design, develop, test, and release the capability:
*   *Scale*: Real numeric value (e.g., $3.5$ developer-months). Minimum effort value is $0.5$.

---

## 3. Kano Model Satisfaction Index
We classify features into five categories to balance customer expectations and resource investment:

```
[Delighter/Attractive] ──► (Drives delight beyond expectations)
[One-Dimensional]      ──► (Linear satisfaction: more is better)
[Must-Be/Basic]        ──► (Expected features: absence causes failure)
[Indifferent]          ──► (No impact on customer satisfaction)
[Reverse]              ──► (Presence causes customer dissatisfaction)
```

### 3.1 Kano Coefficients
We map customer responses to functional and dysfunctional questions to calculate two metrics:

$$\text{Satisfaction Coefficient (CS)} = \frac{A + O}{A + O + M + I}$$

$$\text{Dissatisfaction Coefficient (DS)} = \frac{O + M}{A + O + M + I} \times (-1)$$

Where:
*   $A$: Attractive responses (delighters).
*   $O$: One-dimensional responses.
*   $M$: Must-be responses.
*   $I$: Indifferent responses.

#### Action Thresholds:
*   If $|DS| \to 1.0$ and $CS \to 0$, prioritize immediately. This is a baseline expectation (Must-be).
*   If $CS \to 1.0$ and $DS \to 0$, schedule strategically to differentiate our product (Delighters).

---

## 4. Capability Mapping & Roadmapping
We structure our product roadmap across three levels:
1.  **Core Capabilities**: Fundamental systems that run the business (e.g., database scaling, security architecture).
2.  **Enablers**: Subsystems that allow other capabilities to operate faster (e.g., internal APIs, developer CLI).
3.  **Strategic Capabilities**: New value-adds that open new customer segments or increase market share.

---

## 5. Product Strategy Checklist
*   [ ] Checked RICE scores for all items in the current backlog.
*   [ ] Ensured all effort estimations are approved by engineering.
*   [ ] Classified candidate features using the Kano functional/dysfunctional survey structure.
*   [ ] Map the feature to the capability catalog (Core / Enabler / Strategic).
*   [ ] Validated that the final roadmap contains a balanced mix of 60% Core, 30% Strategic, and 10% Delighter capabilities.
