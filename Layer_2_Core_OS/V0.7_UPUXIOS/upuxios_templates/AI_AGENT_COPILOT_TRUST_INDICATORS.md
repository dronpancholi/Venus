# AI Agent & Copilot Trust Indicators Spec

## 1. Document Overview
This document specifies trust indicators, status alerts, confidence metrics, and reference guidelines for AI interfaces. It ensures users understand what the AI is doing, increasing transparency and trust.

---

## 2. Trust Lifecycle & States
The AI assistant displays its current processing status using standardized states.

| Trust State | Indicator Label | Visual Icon / Style | ARIA Live Role |
| :--- | :--- | :--- | :--- |
| **Planning** | "Analyzing request..." | Pulsing brain icon / Neutral blue theme | `aria-live="polite"` |
| **Reasoning** | "Checking data sources..."| Clock spinner / Info blue | `aria-live="polite"` |
| **Action** | "Generating results..." | Rotating gears icon / Active teal | `aria-live="assertive"` |
| **Validating** | "Verifying accuracy..." | Safe check animation / Emerald | `aria-live="polite"` |
| **Completed** | "Ready" | Solid checkmark / Standard theme | None |

---

## 3. Transparency & Reference UX
Users must be able to inspect and verify the data sources the AI used to generate its response.

### 3.1. Inline Citations & Reference Cards
*   **Format:** Insert numbered inline links `[1]`, `[2]` next to facts or figures.
*   **Source Cards:** Clicking a citation card opens a detailed side panel showing the original text, document name, date updated, and matching confidence score.

### 3.2. Confidence Score Thresholds
When displaying automated insights or suggestions, indicate confidence using visual color tokens.

$$\text{Confidence Score} = \text{Model Score} \times 100$$

*   **High Confidence** ($\ge 85\%$): Display emerald indicator dot (`--color-success`).
*   **Medium Confidence** ($50\% - 84\%$): Display amber indicator dot (`--color-warning`).
*   **Low Confidence** ($< 50\%$): Display gray indicator dot. Require human approval before proceeding.

---

## 4. User Feedback & Model Calibration
Help users correct AI actions when confidence is low or errors occur.
*   **Edit Steps:** Users can click edit buttons next to individual planning steps to change search criteria before the AI continues.
*   **Calibration Control:** A settings slider lets users adjust confidence filters. Items below the chosen threshold will require manual approval.

---

## 5. System Failures & Recovery Modes
If the AI cannot complete a request, show a clear recovery message.
*   **Helpful Error Messages:** Avoid generic error codes. State what went wrong: "Unable to retrieve the billing database."
*   **Alternative Options:** Suggest alternative actions, such as rephrasing the question or checking connection settings.

---

## 6. Verification Checklist
- [ ] Verify that citations link to the correct source documents.
- [ ] Confirm screen readers read trust states and updates correctly.
- [ ] Test the confidence meter's response to changing threshold scores.
- [ ] Validate manual override workflows when confidence drops below $50\%$.

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial AI Trust Indicators Specification template.\n