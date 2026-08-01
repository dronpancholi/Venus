# Executive KPI Dashboard Design Spec

## 1. Document Overview
This document specifies grid structures, metric layouts, data refreshing states, and export mechanisms for executive dashboards. It ensures key business metrics are readable and clear for decision-makers.

---

## 2. Dashboard Grid & Layout Systems
The executive dashboard utilizes a flexible 12-column grid layout. The visual structure is divided into three tiers based on importance:

```
+---------------------------------------------------------------------------------+
|                               [Tier 1: Global Filters]                           |
+---------------------------------------------------------------------------------+
|  [Tier 2: Primary KPI Cards] (3 Columns per Card)                                |
|  +--------------------+  +--------------------+  +--------------------+  +---+  |
|  | Card 1             |  | Card 2             |  | Card 3             |  |...|  |
|  +--------------------+  +--------------------+  +--------------------+  +---+  |
+---------------------------------------------------------------------------------+
|  [Tier 3: Analytical Trends & Chart Panels] (6 Columns per Chart)               |
|  +----------------------------------------+  +--------------------------------+ |
|  | Chart A                                |  | Chart B                        | |
|  +----------------------------------------+  +--------------------------------+ |
+---------------------------------------------------------------------------------+
```

| Responsive Breakpoint | Width (px) | Grid Columns | Padding / Margins | Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Desktop UltraWide** | $\ge 1440$ | 12 | Outer: $24\text{px}$, Gaps: $16\text{px}$ | Center aligned container, max width $1600\text{px}$. |
| **Desktop Standard** | $1024 - 1439$ | 12 | Outer: $20\text{px}$, Gaps: $12\text{px}$ | Fluid columns adjust width automatically. |
| **Tablet Portrait** | $768 - 1023$ | 6 | Outer: $16\text{px}$, Gaps: $12\text{px}$ | Cards wrap to 2-column or 3-column rows. |
| **Mobile Standard** | $< 768$ | 2 | Outer: $12\text{px}$, Gaps: $8\text{px}$ | Vertical stack; L1 cards stack sequentially. |

---

## 3. Primary KPI Metric Cards
KPI cards display critical metrics at a glance using a standard format.

### 3.1. Metric Card Anatomy
```
+----------------------------------------------------------+
|  Metric Title                                 [Tooltip]  |
|  $1,248,500                                              |
|  [Trend Icon] +14.2% vs previous period                  |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ [Sparkline]  |
+----------------------------------------------------------+
```

### 3.2. Visual Hierarchy Rules
*   **Metric Value Typography:** Bold, high-contrast, display sans-serif font face.
*   **Comparison Trends:**
    *   *Positive trend (Green):* Color `--success-text` (contrast $\ge 4.5:1$).
    *   *Negative trend (Red):* Color `--error-text` (contrast $\ge 4.5:1$).
*   **Sparklines:** Simple trend line without axes, colored to match the direction of the trend.

---

## 4. Data Refresh & Latency UX
Dashboards display data status indicators to show how fresh the metrics are.
*   **Real-time Stream:** Small pulsing green dot labeled "Live".
*   **Scheduled Batch:** Plain text label: "Refreshed $X$ minutes ago".
*   **Manual Refresh:** Inline action button with rotation state animation on click.
*   **Loading State:** Show gray skeleton boxes matching actual chart heights instead of blank screens to keep layout shifting minimal.

---

## 5. Personalization & Exporting

### 5.1. Dashboard Customization
*   **Drag-and-Drop:** Drag handles on widgets allow users to reorganize layout order. Positions are saved in local storage.
*   **Widget Library:** A side panel lets users search, toggle, and add/remove metrics from their view.

### 5.2. Export Options
*   **PDF Report:** Combines active cards into a multi-page PDF optimized for printing.
*   **CSV/Excel:** Exports underlying chart data with formatted column names.

---

## 6. Verification Checklist
- [ ] Confirm screen readers read both metric values and trend direction details.
- [ ] Check contrast ratios for positive (green) and negative (red) text.
- [ ] Test widget drag-and-drop mechanics with keyboard controls.
- [ ] Verify loading skeleton dimensions match final chart sizes to prevent layout shifts.

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial Executive KPI Dashboard specification template.\n