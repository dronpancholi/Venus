# Interaction States Blueprint

## 1. Document Overview
This blueprint defines the interaction state lifecycle, styling tokens, transition parameters, and accessibility requirements for interactive elements. It guarantees visual and behavioral consistency for every user touchpoint, minimizing user friction and cognitive load.

---

## 2. State Lifecycle Model
Interactive elements (buttons, form fields, cards) progress through a standardized interaction lifecycle.

```
       +--------------+
       |   Default    |
       +-------+------+
               |
      (Hover / Focus / Active)
               |
               v
       +--------------+
  +--->|   Loading    |<---+
  |    +-------+------+    |
  |            |           |
(Error)     (Success)   (Reset)
  |            |           |
  |            v           |
  |    +--------------+    |
  +----+   Success    +----+
  |    +--------------+    |
  |                        |
  |    +--------------+    |
  +----+    Error     +----+
       +--------------+
```

---

## 3. Timing & Animation Curves
All visual transitions must utilize standardized timing tokens and easing functions to ensure responsiveness.

| Speed Token | Value | CSS Easing Function | Best Use Case |
| :--- | :--- | :--- | :--- |
| `--transition-instant` | $50\text{ ms}$ | `linear` | Tooltip visibility, minor toggle checks. |
| `--transition-fast` | $150\text{ ms}$ | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Hover states, button clicks, tab transitions. |
| `--transition-normal` | $250\text{ ms}$ | `cubic-bezier(0.4, 0, 0.2, 1)` | Accordions, select dropdown open/close. |
| `--transition-slow` | $400\text{ ms}$ | `cubic-bezier(0.4, 0, 1, 1)` | Modals, slide-in sheets, page transitions. |

---

## 4. State Transition Matrix
Track how elements transition between states, specifying triggers, styles, and accessibility rules.

| Trigger Event | Source State | Target State | CSS Transitions | ARIA / Accessibility |
| :--- | :--- | :--- | :--- | :--- |
| `mouseenter` | Default | Hover | `background-color 150ms ease-out` | None required. |
| `focusin` | Default | Focus | `outline 150ms ease-out` | `aria-selected` or active focus. |
| `mousedown` | Hover/Focus | Active | `transform 50ms linear` | None. |
| `click` (async) | Active | Loading | `opacity 150ms linear` | `aria-busy="true"`, screen reader alert. |
| `resolve` (success) | Loading | Success | `border-color 250ms ease-in-out` | `aria-live="polite"` announcing success. |
| `reject` (error) | Loading | Error | `border-color 250ms ease-in-out` | `aria-invalid="true"`, focus shifted to error. |

---

## 5. Component State Definitions

### 5.1. Buttons
*   **Default:** Bold visual boundary; minimum size of $44 \times 44\text{ px}$ for touch compatibility (Fitts' Law target sizing).
*   **Hover:** Background color shifts by $10\%$ depth. Cursor style: `pointer`.
*   **Focus:** Outline `3px solid var(--focus-ring)` with `2px` offset.
*   **Active:** Transform scale shifts to $0.98$ to simulate mechanical press.
*   **Disabled:** Background opacity reduced to $35\%$, cursor: `not-allowed`.

### 5.2. Form Inputs
*   **Default:** `1px solid var(--border-neutral)`.
*   **Focus:** Outline `2px solid var(--primary-accent)`, label shifts to floating active state.
*   **Error:** Outline `2px solid var(--error-red)`, supporting helper text displays with matching red color.

---

## 6. Accessibility & Focus Trapping
*   **Contrast Ratio:** Every state (except disabled) must maintain a contrast ratio of $\ge 4.5:1$ against the background.
*   **Focus Trapping:** When overlay panels (modals, sheets) are open, keyboard focus must be trapped within the overlay. Pressing `Tab` at the last focusable element must wrap around to the first focusable element.

---

## 7. Verification Checklist
- [ ] Test focus outline visibility in high-contrast operating system settings.
- [ ] Measure CSS transition timing parameters against spec tokens.
- [ ] Ensure `aria-busy="true"` is added dynamically during async operations.
- [ ] Verify that hover states are not triggered on touch screens during scrolling.

---

## 8. Revision History
*   **V1.0 (2026-06-26):** Initial creation of Interaction States Blueprint template.\n