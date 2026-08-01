# Cognitive Load Assessment

## 1. Document Overview
This assessment evaluates the mental effort required by users to interact with our digital interfaces. By quantifying and reducing cognitive load, we optimize user processing efficiency, decrease error rates, and improve completion times.

---

## 2. Theoretical Framework: Cognitive Load Theory (CLT)
Cognitive load is categorized into three distinct types. Our design goal is to minimize extraneous load, match intrinsic load to the user's skill level, and maximize germane load.

```
 TOTAL COGNITIVE LOAD = Intrinsic Load + Extraneous Load + Germane Load
                        |                |                 |
 [Domain Complexity] ---+                |                 +--- [Mental Schemas]
                                         |
 [Poor UI/Distractions] -----------------+ (Must be minimized)
```

1.  **Intrinsic Load:** The inherent difficulty of the task or information itself (e.g., executing a complex financial calculation). It cannot be removed but can be scaffolded.
2.  **Extraneous Load:** Mental effort wasted on poor UI design, cluttered layouts, confusing terminology, or inconsistent interactions. **This must be minimized.**
3.  **Germane Load:** The productive mental work used to construct mental schemas and process information (e.g., learning a new, efficient conceptual model).

---

## 3. Cognitive Capacity Constraints
To align with biological human memory limits, our designs enforce the following constraints:

### 3.1. Short-Term Memory Capacity (Miller's Law)
*   **Constraint:** Working memory can hold only $7 \pm 2$ chunks of information at a time.
*   **Design Rule:** Group information into distinct, labeled modules. Do not present unstructured lists larger than 7 items.

### 3.2. Attention Decay & Working Memory Duration
*   **Constraint:** Working memory decays in 10-15 seconds if not rehearsed.
*   **Design Rule:** Do not require users to remember information from a previous screen to complete a task on the current screen. Always provide visual persistence of inputs (e.g., review summaries).

---

## 4. Assessment Scorecard
Evaluate the target interface or user flow using the scorecard below.

*Score each item from 1 (Unacceptable / High Load) to 5 (Excellent / Low Load).*

### 4.1. Visual & Informational Hierarchy
| Criteria | Score (1-5) | Findings / Obsvervations | Required Mitigation |
| :--- | :--- | :--- | :--- |
| **Clutter Control:** No unnecessary visual elements, banners, or decorative flourishes. | | | |
| **Chunking:** Text and inputs are grouped logically (e.g., telephone numbers formatted as `XXX-XXX-XXXX`). | | | |
| **Information Density:** Page density doesn't overwhelm the eye. Screen white space is $\ge 30\%$. | | | |

### 4.2. Interaction Friction
| Criteria | Score (1-5) | Findings / Obsvervations | Required Mitigation |
| :--- | :--- | :--- | :--- |
| **Hick's Law Compliance:** Number of choice paths is minimized ($n \le 7$). | | | |
| **Input Effort:** Autofill, dropdowns, and smart defaults are used to reduce manual typing. | | | |
| **Error Prevention:** Input formats are validated inline; clear examples are shown. | | | |

### 4.3. Conceptual & Linguistic Clashes
| Criteria | Score (1-5) | Findings / Obsvervations | Required Mitigation |
| :--- | :--- | :--- | :--- |
| **Terminology Clarity:** No technical jargon or system errors are visible. Terminology matches user mental models. | | | |
| **Mental Model Alignment:** UI layout and flow mimic real-world activities or standard web conventions. | | | |
| **State Feedback:** The system explicitly states what is happening (loaders, toast notifications). | | | |

---

## 5. Quantitative Cognitive Load Formula (Index)
We calculate the **Cognitive Friction Index (CFI)** for a workflow as follows:

$$CFI = \frac{\sum(\text{Task Steps}) + \sum(\text{Decisions}) \times 1.5 + \sum(\text{Inputs}) \times 2}{\text{System Feedback Latency Factor}}$$

*Note: Latency Factor is 1.0 if sub-100ms; 0.8 if 100ms - 500ms; 0.5 if >500ms.*

| Workflow Evaluated | Task Steps | Decisions | Inputs | Latency Factor | CFI Score* |
| :--- | :--- | :--- | :--- | :--- | :--- |
| *Example: Account Creation* | *4* | *2* | *6* | *1.0* | *19.0* |
| | | | | | |

*\*CFI Target Scores:*
*   *Simple workflows (e.g., Login): $< 5.0$*
*   *Medium workflows (e.g., Checkout): $< 15.0$*
*   *Complex workflows (e.g., Configuration): $< 30.0$*

---

## 6. Action Plan & Mitigations
List the high-impact design modifications required to reduce the cognitive load based on the scorecard results.

1.  **Immediate (P0):**
    *   *Action:* [Describe change, e.g., Split the 12-field registration form into a 3-step wizard (Chunking).]
2.  **Short-term (P1):**
    *   *Action:* [Describe change, e.g., Replace text fields with dropdowns for selection choices.]
3.  **Long-term (P2):**
    *   *Action:* [Describe change, e.g., Build auto-save of draft state to prevent data loss anxiety.]

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Created standardized cognitive load assessment template.
