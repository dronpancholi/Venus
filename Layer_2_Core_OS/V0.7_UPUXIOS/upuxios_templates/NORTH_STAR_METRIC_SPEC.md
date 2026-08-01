# North Star Metric Specification

## 1. Document Overview
This specification defines the product's North Star Metric (NSM)—the key measure of customer value and long-term business success. It establishes the mathematical relationships, input drivers, and telemetry schema required to align product development with real customer utility.

---

## 2. North Star Metric Definition
*   **The North Star Metric:** `[Name of NSM, e.g., Weekly Query volume completed successfully]`
*   **Plain English Definition:** `[Describe what the metric measures and why it matters]`
*   **Core Value Exchanged:** `[Describe the value the customer receives and the value the business retains when this metric grows]`

---

## 3. Mathematical Formula & Composition
We model the North Star Metric mathematically as a function of key leading indicators:

$$NSM = \text{Reach} \times \text{Depth} \times \text{Frequency}$$

Where:
*   **Reach ($R$):** The number of active users taking the core action in a period.
*   **Depth ($D$):** The value or volume generated per session/user (e.g., number of documents processed).
*   **Frequency ($F$):** How often the user returns to perform the core action within the timeframe.

### 3.1. Mathematical Representation
$$\text{NSM}_t = \sum_{i=1}^{U_t} \left( A_{i,t} \times V_{i,t} \right)$$

Where:
*   $U_t$ = Active Users in period $t$.
*   $A_{i,t}$ = Action frequency of user $i$ in period $t$.
*   $V_{i,t}$ = Average value metric (e.g., accuracy, volume) of action for user $i$ in period $t$.

---

## 4. Metric Hierarchy & Driver Tree
Use the table below to detail the input metrics that feed the North Star Metric.

```
                  [ NORTH STAR METRIC ]
                            |
         +------------------+------------------+
         |                  |                  |
    [ REACH ]           [ DEPTH ]        [ FREQUENCY ]
   (Input L1)           (Input L2)         (Input L3)
```

| Metric Level | Metric Name | Metric Type | Target Value | Data Source | Measurement Frequency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **North Star** | `[NSM Name]` | Volume/Retention | | Mixpanel / SQL | Weekly |
| **Input L1 (Reach)** | *e.g., Monthly Active Creators* | Quantity | | Segment | Monthly |
| **Input L2 (Depth)** | *e.g., Average tracks published*| Intensity | | Segment | Weekly |
| **Input L3 (Freq)** | *e.g., Average sessions per user* | Speed/Rate | | Segment | Daily |
| **Output (Business)**| *e.g., Monthly Recurring Revenue*| Lagging (Financial)| | Stripe | Monthly |

---

## 5. Downstream Impact & Business Value
Explain how changes in the North Star Metric impact lagging business metrics.

*   **Impact on Retention:** An increase in the NSM should lead to a corresponding [decrease/increase] in [Churn/Retention].
*   **Impact on Expansion:** A high NSM indicates [expansion opportunities, e.g., seat expansion, upsell].
*   **Impact on LTV:** Every unit increase in the NSM is correlated with a `$` [value] increase in Customer Lifetime Value.

---

## 6. Event Instrumentation & Telemetry Schema
To ensure precise calculation of the NSM and its drivers, developer teams must implement the following tracking schema.

| Event Name | Trigger Condition | Parameter Key | Data Type | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `core_job_completed` | User successfully executes the primary action. | `job_id` | String | `job_9281a8` |
| | | `duration_ms` | Integer | `450` |
| | | `payload_size` | Float | `2.4` |
| `session_started` | Application is brought into the foreground. | `session_id` | String | `sess_82173` |
| | | `platform` | String | `ios` |

---

## 7. Dashboard & Reporting Requirements
The operational dashboard must monitor:
1.  **Weekly Trend:** A rolling 12-week view of the NSM with standard deviation bands.
2.  **Cohort Breakdown:** Cohort performance grouped by signup week (to verify that newer cohorts are achieving NSM milestones faster than older cohorts).
3.  **Anomalous Drop Alerts:** Trigger slack alert if the NSM drops by $> 15\%$ week-over-week.

---

## 8. Revision History
*   **V1.0 (2026-06-26):** Initial North Star Metric Specification template.
