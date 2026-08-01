# Part 09: Dashboard Intelligence & Data Visualization

## 1. Context & Strategy
Dashboard Intelligence sets the layout, widget structures, and visualization rules for our data-rich screens. By matching dashboard designs to the user's operational objectives (executive monitoring vs. deep analytical querying), we ensure critical business metrics remain digestible, accurate, and performant.

---

## 2. Dashboard Archetypes

We support three operational dashboard styles:

### 2.1 Executive Dashboard
*   *Purpose*: High-level performance tracking, business health monitoring, and long-term planning.
*   *ICP Persona*: C-Suite, VP of Operations.
*   *Refresh Cycle*: Daily / Weekly.
*   *Key Visuals*: High-level KPI callout blocks, trend lines, sparklines.
*   *Constraint*: No scrollbars allowed. The dashboard must fit on a single standard viewport.

### 2.2 Operational Dashboard
*   *Purpose*: Real-time incident detection, queue management, and service health monitoring.
*   *ICP Persona*: Systems Operators, Lead Engineers.
*   *Refresh Cycle*: Near-real-time ($5\text{s} - 60\text{s}$ polling).
*   *Key Visuals*: Large status indicators, error counters, event logs, current queue heights.
*   *Constraint*: Audio-visual alerts for critical threshold crossings.

### 2.3 Analytical Dashboard
*   *Purpose*: Root-cause analysis, custom query building, and database exploration.
*   *ICP Persona*: Data Analysts, Compliance Officers.
*   *Refresh Cycle*: On-demand.
*   *Key Visuals*: Interactive heatmaps, scatterplots, filter sidebars, nested data tables.
*   *Constraint*: Support data exports to CSV/JSON format.

---

## 3. Widget System & Layout Grid

We layout dashboard screens using a flexible $12$-column grid system.

```
+───────────────────────────────────────────────────────────────────────────+
|                           Executive Header Widget (12 Col)                |
+───────────────────────────+───────────────────────────+───────────────────+
|    KPI Metric (4 Col)     |    KPI Metric (4 Col)     | KPI Metric (4 Col)|
+───────────────────────────+───────────────────────────+───────────────────+
|               Data Trend Chart (8 Col)                | Alert List (4 Col)|
+───────────────────────────────────────────────────────+───────────────────+
```

### 3.1 Widget Sizing Rules:
*   *Width Constraints*: Small KPI Cards ($3$ or $4$ cols), Medium Charts ($6$ or $8$ cols), Full Tables ($12$ cols).
*   *Height Constraints*: Keep card row heights uniform (e.g., $180\text{px}$, $360\text{px}$, or $540\text{px}$).

---

## 4. Data Visualization Guidelines
1.  **Chart Selection**:
    *   *Time-series*: Line charts only. Never use bar charts for time data.
    *   *Comparisons*: Bar charts.
    *   *Distribution*: Scatterplots or histograms.
    *   *Composition*: Stacked bar charts or donut charts (limit to $\le 5$ slices; never use pie charts).
2.  **Color Usage**:
    *   *Standard Colors*: Neutral dark slate for axes, bright primary blue for values.
    *   *Semantic Colors*: Green for positive status (`#2E7D32`), yellow for warnings (`#F57F17`), red for alerts (`#C62828`).
3.  **Tooltips**: Must show exact values, timestamps, and comparison offsets (e.g., "+12.3% vs last week") on hover.

---

## 5. Visual Widget Performance Budget
To maintain high responsiveness under heavy data loads, dashboards must satisfy these performance metrics:
*   **Largest Contentful Paint (LCP)**: $\le 1.5\text{s}$ for primary KPI data.
*   **Cumulative Layout Shift (CLS)**: $\approx 0$. Set fixed aspect-ratio placeholders for charts to prevent content jump.
*   **First Input Delay (FID)**: $\le 100\text{ms}$ during interactive widget filtering.

---

## 6. Dashboard Intelligence Checklist
*   [ ] Classified dashboard design into one of the three archetypes.
*   [ ] Checked that widgets conform to the 12-column grid layout rules.
*   [ ] Ensured no pie charts are used in the visualization modules.
*   [ ] Verified fixed-height placeholders are defined for all lazyloaded charts.
*   [ ] Confirmed data tables provide direct CSV/JSON export actions.
