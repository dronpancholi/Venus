# Design Tokens & CSS Variables System

## 1. Document Overview
This document defines the core tokens for spacing, typography, colors, shadows, and borders. These tokens are maintained as CSS Custom Properties to keep styles consistent across all platforms and themes.

---

## 2. Core Color Tokens

### 2.1. Brand & Neutral Palettes
```css
:root {
  /* Brand Colors */
  --color-primary: #1E3A8A;
  --color-primary-light: #3B82F6;
  --color-primary-dark: #1E3A8A;
  --color-accent: #10B981;

  /* Neutral Scales */
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-400: #9CA3AF;
  --color-gray-700: #374151;
  --color-gray-900: #111827;
}
```

### 2.2. Semantic Feedback Colors
```css
:root {
  --color-success: #10B981;
  --color-success-bg: #ECFDF5;
  --color-warning: #F59E0B;
  --color-warning-bg: #FEF3C7;
  --color-error: #EF4444;
  --color-error-bg: #FEF2F2;
  --color-info: #3B82F6;
  --color-info-bg: #EFF6FF;
}
```

---

## 3. Typography Tokens
Typography scales are built around standard size and line-height proportions to ensure readability.

| Token Name | Font Size Value | Line Height | CSS Mapping |
| :--- | :--- | :--- | :--- |
| `--text-xs` | $0.75\text{ rem } (12\text{px})$ | $1.00\text{ rem}$ | Small helper labels, captions |
| `--text-sm` | $0.875\text{ rem } (14\text{px})$ | $1.25\text{ rem}$ | Body copy secondary, table data |
| `--text-base` | $1.00\text{ rem } (16\text{px})$ | $1.50\text{ rem}$ | Primary body text, input labels |
| `--text-lg` | $1.125\text{ rem } (18\text{px})$ | $1.75\text{ rem}$ | Sub-headings, metric labels |
| `--text-xl` | $1.25\text{ rem } (20\text{px})$ | $1.875\text{ rem}$ | Secondary headers, card titles |
| `--text-2xl` | $1.50\text{ rem } (24\text{px})$ | $2.25\text{ rem}$ | Section headers, modal titles |
| `--text-3xl` | $1.875\text{ rem } (30\text{px})$ | $2.625\text{ rem}$ | Primary workspace titles, KPI values |

---

## 4. Spacing & Grid System
We use an 8px grid system to scale layout margins and padding consistently.

$$S(n) = 8 \times n\text{ px}$$

```css
:root {
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.50rem;  /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1.00rem;  /* 16px */
  --spacing-6: 1.50rem;  /* 24px */
  --spacing-8: 2.00rem;  /* 32px */
  --spacing-12: 3.00rem; /* 48px */
}
```

---

## 5. Elevation & Shadow Tokens
Elevation changes are represented by layered box-shadow styles.

```css
:root {
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
```

---

## 6. Border & Radius Tokens
```css
:root {
  --radius-sm: 0.125rem; /* 2px */
  --radius-md: 0.25rem;  /* 4px */
  --radius-lg: 0.375rem; /* 6px */
  --radius-xl: 0.50rem;  /* 8px */
  --radius-full: 9999px; /* Pill */
}
```

---

## 7. Verification Checklist
- [ ] Confirm all color tokens meet WCAG AA contrast ratio requirements.
- [ ] Verify that spacing parameters match the 8px grid system values.
- [ ] Ensure dark mode overrides adjust variables dynamically at the `:root` level.
- [ ] Check font size tokens translate correctly to root browser configurations.

---

## 8. Revision History
*   **V1.0 (2026-06-26):** Initial Design Tokens & CSS Variables template.\n