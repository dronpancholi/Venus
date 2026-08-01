# Localization & RTL Global Specification

## 1. Document Overview
This document specifies translation architectures, layout mirroring for Right-to-Left (RTL) languages, text wrapping limits, and global font fallbacks. It ensures the application adapts cleanly to different locales and languages.

---

## 2. Translation key Architecture & Pluralization
All user-facing strings must use structured translation keys. Hard-coded text strings are not allowed in the codebase.

### 2.1. String JSON Schema Example
```json
{
  "billing": {
    "invoice_count": {
      "one": "You have one unpaid invoice.",
      "other": "You have {count} unpaid invoices."
    },
    "payment_placeholder": "Enter card ending in {digits}"
  }
}
```

### 2.2. Dynamic Text Expansion Buffer
Translate layouts to support dynamic text length changes. Short English labels often expand in other languages.

$$\text{Target Space} = L_{\text{English}} \times F_{\text{expansion}}$$

| Original English String Length | Expansion Factor ($F_{\text{expansion}}$) | Target Layout Buffer Required |
| :--- | :--- | :--- |
| **Short labels** ($< 10$ chars) | $1.40$ | Allow $40\%$ extra horizontal space for translation. |
| **Sentences** ($10 - 50$ chars) | $1.25$ | Allow $25\%$ extra layout space. |
| **Paragraphs** ($> 50$ chars) | $1.15$ | Allow $15\%$ vertical growth capacity. |

---

## 3. Right-to-Left (RTL) Layout Standards
When an RTL language (e.g., Arabic, Hebrew) is active, set `<html dir="rtl">` on the root element.

### 3.1. Logical CSS Properties
Do not use physical properties like left/right margin or padding. Use logical CSS properties to ensure layouts mirror automatically.

| Standard CSS Property | Localization CSS Property | Behavior in RTL |
| :--- | :--- | :--- |
| `margin-left: 12px;` | `margin-inline-start: 12px;` | Applies space on the right side. |
| `padding-right: 8px;` | `padding-inline-end: 8px;` | Applies padding on the left side. |
| `left: 0;` | `inset-inline-start: 0;` | Positions element relative to the start edge. |
| `border-top-left-radius:` | `border-start-start-radius:` | Mirrors top corners automatically. |

### 3.2. Icon Mirroring Guidelines
*   **Directional Icons:** Arrows, back buttons, and progress indicators must flip direction in RTL.
*   **Neutral Icons:** Brand logos, search icons, and checkmarks remain in their default orientation.

---

## 4. Font Selection for Global Scripts
To prevent layout breaks, use fallbacks that match regional font families.

```css
/* Global CSS Font Stack Fallbacks */
.global-text {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
               /* CJK Fallbacks */
               "Segoe UI Emoji", "PingFang SC", "Hiragino Kaku Gothic ProN", "Noto Sans CJK", 
               /* Arabic Fallbacks */
               "Noto Sans Arabic", "Geeza Pro",
               sans-serif;
}
```

---

## 5. Verification Checklist
- [ ] Confirm layout mirrors correctly without overlapping elements when `dir="rtl"` is applied.
- [ ] Verify that localized text does not overflow containers or trigger unexpected wrapping.
- [ ] Check date, time, and currency formats update correctly based on the active locale.
- [ ] Ensure translation files do not contain missing keys or empty values.

---

## 6. Revision History
*   **V1.0 (2026-06-26):** Initial Localization & RTL Specification template.\n