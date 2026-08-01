# Typography & Color System Specification

## 1. Document Overview
This document defines font hierarchies, typographic scales, color swatches, contrast targets, and theme-switching behaviors to ensure all elements are legible and consistent.

---

## 2. Typography Scale & Hierarchies
Our typographic scale uses the **Major Third** ratio ($1.25$) to scale font sizes consistently from body text up to page headings.

| Element | Tag | Desktop Size (rem) | Mobile Size (rem) | Line Height | Font Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hero Title** | `h1` | $2.441\text{ rem}$ | $1.953\text{ rem}$ | $1.15$ | Bold ($700$) |
| **Section Header** | `h2` | $1.953\text{ rem}$ | $1.563\text{ rem}$ | $1.20$ | Semi-Bold ($600$) |
| **Subsection** | `h3` | $1.563\text{ rem}$ | $1.250\text{ rem}$ | $1.25$ | Medium ($500$) |
| **Primary Body** | `p` | $1.000\text{ rem}$ | $1.000\text{ rem}$ | $1.50$ | Regular ($400$) |
| **Secondary Body**| `span` | $0.800\text{ rem}$ | $0.800\text{ rem}$ | $1.40$ | Regular ($400$) |
| **Small Caption** | `small` | $0.640\text{ rem}$ | $0.640\text{ rem}$ | $1.30$ | Medium ($500$) |

*   **Line Length Guideline:** Body copy width should stay between $45$ and $75$ characters per line to optimize reading comfort.

---

## 3. Color Palette & Contrast Standards
All combinations of text and background colors must comply with the WCAG 2.2 contrast ratio formulas:

$$CR = \frac{L_1 + 0.05}{L_2 + 0.05}$$

Where:
*   $L_1$ = Relative luminance of the lighter color.
*   $L_2$ = Relative luminance of the darker color.

| Context | Text Category | Required Ratio (AA) | Target Ratio (AAA) | Example Combination |
| :--- | :--- | :--- | :--- | :--- |
| **Normal Text** | Body Copy ($< 18\text{pt}$) | $\ge 4.5:1$ | $\ge 7.0:1$ | `#374151` on `#FFFFFF` ($9.1:1$) |
| **Large Text** | Titles / Large Text | $\ge 3.0:1$ | $\ge 4.5:1$ | `#1E3A8A` on `#F3F4F6` ($8.2:1$) |
| **UI Components** | Focus rings, inputs | $\ge 3.0:1$ | $\ge 4.5:1$ | `#3B82F6` on `#FFFFFF` ($4.6:1$) |

---

## 4. Dark Theme & High Contrast Adaptations
Dark theme is activated by applying a `.dark` class to the `html` element. Color tokens map to darker alternatives:

| Light Theme Variable | Light Hex | Dark Theme Variable | Dark Hex |
| :--- | :--- | :--- | :--- |
| `--bg-default` | `#FFFFFF` | `--bg-default-dark` | `#111827` |
| `--text-primary` | `#111827` | `--text-primary-dark`| `#F9FAFB` |
| `--border-neutral` | `#E5E7EB` | `--border-neutral-dark`| `#374151` |
| `--primary-accent` | `#3B82F6` | `--primary-accent-dark`| `#60A5FA` |

---

## 5. Verification Checklist
- [ ] Verify that all text-on-color combinations pass WCAG contrast checks.
- [ ] Ensure line lengths are capped at $75$ characters for long paragraphs.
- [ ] Verify font fallback configurations function correctly across different devices.
- [ ] Confirm dark mode styles activate without visual glitches or unreadable text.

---

## 6. Revision History
*   **V1.0 (2026-06-26):** Initial Typography & Color System template.\n