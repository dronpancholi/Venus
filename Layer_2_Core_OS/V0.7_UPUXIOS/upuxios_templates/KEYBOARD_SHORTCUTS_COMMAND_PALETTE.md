# Keyboard Shortcuts & Command Palette Specification

## 1. Document Overview
This document specifies keyboard shortcuts and the UX behavior of the search command palette. It ensures power-user efficiency, clear discoverability, and WAI-ARIA-compliant keyboard accessibility.

---

## 2. Global Keyboard Shortcut Registry
Key combinations are defined using platform-specific modifiers. For Mac OS, `Cmd` maps to `Ctrl` on Windows/Linux.

| Modifier Key (Win) | Modifier Key (Mac) | Key | Target Action | Scope | Avoid Conflict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Ctrl` | `Cmd` | `K` | Open Command Palette | Global | Browser search box |
| `Ctrl` | `Cmd` | `/` | Show Shortcuts Cheat Sheet | Global | Browser help guides |
| `Esc` | `Esc` | - | Cancel / Close Panel | Contextual | System overlays |
| `Ctrl` | `Cmd` | `S` | Save Progress | Active View | Browser save page |
| `Shift` | `Shift` | `?` | Help Center Documentation | Global | System help triggers |

---

## 3. Command Palette UX & Interaction Model

### 3.1. Autocomplete & Fuzzy Search Ranking
The Command Palette filters results dynamically. Search results are ranked using a scoring system:

$$\text{Score} = w_1 \cdot P_{\text{match}} + w_2 \cdot R_{\text{recency}} + w_3 \cdot F_{\text{frequency}}$$

Where:
*   $P_{\text{match}}$ = Proximity of query string match (e.g. prefix match has higher weight than middle match).
*   $R_{\text{recency}}$ = Recency of item activation ($1$ if clicked in last 24h, $0$ otherwise).
*   $F_{\text{frequency}}$ = Normalized frequency of use by user.
*   $w_1, w_2, w_3$ = Weight coefficients ($0.6, 0.25, 0.15$ respectively).

### 3.2. Decision Time Limits (Hick's Law)
To prevent cognitive paralysis within the Command Palette, the result list is capped at:

$$n = 7 \pm 2\text{ items}$$

Results are categorized into distinct sections (Actions, Navigation, Help) to help users scan options quickly.

---

## 4. Accessibility Implementation
WAI-ARIA specifications for the Command Palette:
*   The text input must have `role="combobox"`, `aria-autocomplete="list"`, and `aria-expanded="true"` when visible.
*   The results container must have `role="listbox"`.
*   Active options must be announced dynamically to screen readers using `aria-activedescendant="option-id"`.
*   Focus must remain in the input box while keyboard arrow keys traverse the option list.

---

## 5. Configuration & Customization
Users can customize keyboard shortcuts through a settings panel. Remappings are saved as a JSON schema in user settings:

```json
{
  "shortcuts": [
    {
      "action": "open_palette",
      "default_keys": ["Control", "k"],
      "custom_keys": ["Control", "p"]
    }
  ]
}
```

---

## 6. Verification Checklist
- [ ] Verify that search inputs clear correctly when the Command Palette is closed.
- [ ] Confirm screen readers read active items on Up/Down arrow selection.
- [ ] Ensure that custom shortcuts do not override critical screen reader system controls (e.g., JAWS or VoiceOver commands).
- [ ] Test the search matching algorithm with typos and partial strings.

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial Command Palette & Keyboard spec template.\n