# AI Conversational UX Specification

## 1. Document Overview
This document specifies user interface layout rules, conversational behavior patterns, streaming latency bounds, error mitigations, and accessibility targets for AI chat assistants and copilot panels.

---

## 2. Chat Interface Anatomy & Layout
AI assistant interactions are placed in a flexible side panel or full-screen conversation view.

```
+----------------------------------------------------+
|  [Copilot Panel]                               [X] |
+----------------------------------------------------+
|  [System Status]: Copilot is active                |
|                                                    |
|  (User)  "Draft an API schema for user metrics."   |
|                                                    |
|  (AI)    "Certainly. Here is the schema:"          |
|          +--------------------------------------+  |
|          | ```json                              |  |
|          | { "metrics": [] }                    |  |
|          | ```                                  |  |
|          +--------------------------------------+  |
|          [Thump Up] [Thumb Down] [Copy]            |
|                                                    |
+----------------------------------------------------+
|  [Type your prompt here...]                 [Send] |
+----------------------------------------------------+
```

---

## 3. Streaming Response Latency Bounds
To keep the AI assistant engaging, responses should stream text in real-time. The text generation streaming speed must match comfortable reading rates.

```
Comfortable Reading Speed: ~250 words/min ≈ 4 words/sec ≈ 5.3 tokens/sec
```

| Streaming Speed Limit | Target Rate | Visual Behavior |
| :--- | :--- | :--- |
| **Minimum Rate** | $\ge 5\text{ tokens/sec}$ | Slow output; display inline pulse dot to reassure user. |
| **Target Rate** | $10 - 15\text{ tokens/sec}$ | Smooth text flow; matches reading speed. |
| **Max Threshold** | $25\text{ tokens/sec}$ | High speed; show loading indicator and render in blocks to prevent visual flashing. |

---

## 4. Prompt Suggestions & Suggestions Chips
*   **Display Logic:** Show contextual suggestion chips when the input field is empty.
*   **Hick's Law Application:** Limit suggestions to $3$ or $4$ chips, focusing on high-utility actions based on the current page content.

---

## 5. Error Recovery Matrix
When AI pipelines or network requests fail, resolve them gracefully to maintain user trust.

| Error Class | Root Cause | Visual UX Pattern | Recovery Path |
| :--- | :--- | :--- | :--- |
| **Token Exhaustion** | Context length exceeded. | Amber warning alert banner inside chat panel. | Offer "Summarize previous chat" or "Reset Session" button. |
| **Rate Limit** | Too many queries. | Toast alert: "System busy. Retrying in $X$ seconds." | Automated retry with exponential backoff. |
| **Network Timeout** | Connection failure. | Red message box: "Message could not be sent." | "Resend Message" button with offline state check. |
| **Safety Block** | Inappropriate input. | System message: "Prompt blocked by safety filters." | Clear input field, suggest alternative query phrasing. |

---

## 6. Feedback & Reinforcement Mechanisms
Each AI response must include direct action triggers to help train the model and improve usability:
*   **Thumbs Up/Down:** Inline voting. Clicking thumbs down triggers a dialog with checkbox categories (Hallucination, Incorrect Formatting, Bad Quality).
*   **Copy Code:** Quick clipboard button for code snippets.
*   **Regenerate:** Button at the bottom of the last message block.

---

## 7. Accessibility
*   **Screen Readers:** Announce streaming responses periodically (e.g., every $50$ characters or at sentence endings) using an `aria-live="polite"` container, avoiding constant disruptions.
*   **Keyboard Access:** Use `Tab` to navigate code copy buttons. Pressing `Esc` shifts focus back to the primary prompt input field.

---

## 8. Verification Checklist
- [ ] Verify that code blocks include copy-to-clipboard buttons.
- [ ] Confirm screen readers read streaming text updates clearly.
- [ ] Test the chat layout's responsiveness at narrow breakpoints ($320\text{ px}$).
- [ ] Verify that clicking thumbs down prompts for useful feedback without disrupting user workflow.

---

## 9. Revision History
*   **V1.0 (2026-06-26):** Initial AI Conversational UX Specification template.\n