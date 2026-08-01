# Part 10 — Design Systems

## 1. Context & Strategy

### 1.1 Purpose
The Design Systems Part defines the unified visual, spatial, and functional building blocks of the Project Venus product ecosystem. It establishes a single source of truth for UI patterns, decoupling design intent from hardcoded frontend implementations via structured design tokens and layout rules.

### 1.2 Cognitive and Physical Principles
To optimize interaction speed and reduce visual search time, the system incorporates:
*   **Fitts' Law**: Minimizes movement time ($MT$) to interactive elements by optimizing distance ($D$) and target size ($W$):
    $$MT = a + b \log_2\left(\frac{2D}{W}\right)$$
    *Target sizing rules enforce $W \ge 48\text{px}$ for all touch and click targets to prevent high error rates ($>5\%$).*
*   **Hick's Law**: Accelerates choice time ($T$) by minimizing the number of options ($n$) in navigation and configuration panels:
    $$T = b \log_2(n + 1)$$
*   **Miller's Law (7 ± 2)**: Visual layouts partition configuration fields and controls into semantic clusters of no more than $7 \pm 2$ items to align with working memory constraints.

---

## 2. Design Token Architecture

Design tokens are structured in a three-tier hierarchy: Global (Reference) Tokens $\rightarrow$ Alias (Semantic) Tokens $\rightarrow$ Component Tokens.

```
[Global Tokens: #0066CC] ──► [Semantic Tokens: sys.color.primary] ──► [Component Tokens: btn.bg.primary]
```

### 2.1 JSON Schema for Design Tokens
Tokens are serialized in a standard JSON format ready for automated compilation:

```json
{
  "color": {
    "brand": {
      "blue": { "value": "#0066CC", "type": "color" }
    },
    "neutral": {
      "900": { "value": "#0F172A", "type": "color" },
      "100": { "value": "#F1F5F9", "type": "color" }
    },
    "sys": {
      "primary": { "value": "{color.brand.blue}", "type": "color" },
      "background": { "value": "{color.neutral.100}", "type": "color" },
      "text": { "value": "{color.neutral.900}", "type": "color" }
    }
  },
  "spacing": {
    "base": { "value": "8px", "type": "dimension" },
    "xs": { "value": "calc({spacing.base} * 0.5)", "type": "dimension" },
    "sm": { "value": "{spacing.base}", "type": "dimension" },
    "md": { "value": "calc({spacing.base} * 2)", "type": "dimension" },
    "lg": { "value": "calc({spacing.base} * 3)", "type": "dimension" }
  }
}
```

---

## 3. Spacing & Breakpoint Grids

All layouts conform to an 8px spatial grid system. Margins, paddings, gap spacing, and dimension increments must be multiples of 8px (or 4px for fine-grained micro-interactions).

### 3.1 Breakpoint Grid Specifications
| Breakpoint | Range (Width) | Columns | Margin | Gap | Target Layout Strategy |
|---|---|---|---|---|---|
| **Mobile** | $320\text{px} - 599\text{px}$ | 4 | $16\text{px}$ | $12\text{px}$ | Full-width stacked modules, persistent bottom action bar |
| **Tablet** | $600\text{px} - 1023\text{px}$ | 8 | $24\text{px}$ | $16\text{px}$ | Dual-column grids, collapsible side navigation panel |
| **Desktop** | $1024\text{px} - 1439\text{px}$ | 12 | $32\text{px}$ | $24\text{px}$ | Multi-pane workspace layouts, permanent nav rail |
| **Wide Desktop** | $\ge 1440\text{px}$ | 12 | Max content width $1440\text{px}$ | $24\text{px}$ | Centered grid with outer margins expanding dynamically |

---

## 4. Typographic System

The typographic scale uses a **Perfect Fourth** ($1.333$ ratio) modular scale with fluid sizing calculations based on viewport width:

$$\text{FontSize} = \text{Clamp}\left(\text{MinSize}, \text{ScaleFactor} \times \text{ViewportWidth}, \text{MaxSize}\right)$$

### 4.1 Type Scale Definition
*   **Hero (Display)**: $2.369\text{rem}$ ($37.9\text{px}$) | Line Height: $1.15$ | Letter Spacing: $-0.02\text{em}$
*   **H1 (Header 1)**: $1.777\text{rem}$ ($28.4\text{px}$) | Line Height: $1.2$ | Letter Spacing: $-0.015\text{em}$
*   **H2 (Header 2)**: $1.333\text{rem}$ ($21.3\text{px}$) | Line Height: $1.25$ | Letter Spacing: $-0.01\text{em}$
*   **Body (Regular)**: $1.000\text{rem}$ ($16.0\text{px}$) | Line Height: $1.5$ | Letter Spacing: $0.0\text{em}$
*   **Caption/Label**: $0.750\text{rem}$ ($12.0\text{px}$) | Line Height: $1.4$ | Letter Spacing: $0.02\text{em}$

---

## 5. Component Hierarchies & States

We structure components according to atomic hierarchy:
1.  **Atoms**: Raw elements (Buttons, Input Fields, Checkboxes, Icons).
2.  **Molecules**: Combinations of atoms (Search Bars, Input Fields with Validation Labels, Card Headers).
3.  **Organisms**: Self-contained functional blocks (Navbar, Multi-metric Chart Card, Data Table with Filters).
4.  **Templates**: Structural grid page layouts.

### 5.1 Interactive Component States
All interactive components must explicitly define styling for:
*   `Default`: Baseline state.
*   `Hover`: Visual cue of interactivity (+10% lightness or subtle shift).
*   `Focus`: Enforced $2\text{px}$ high-contrast ring with $2\text{px}$ offset (`outline-offset: 2px`).
*   `Active/Pressed`: Visual representation of actuation (-10% lightness or deep press shadow).
*   `Disabled`: Opacity $40\%$, cursor set to `not-allowed`, removed from keyboard tab index (`tabindex="-1"`).
*   `Loading`: Skeleton pulse animation or progress spinner, preserving layout size.

---

## 6. Design Systems Checklist
*   [ ] Checked target size of all interactive elements matches Fitts' Law requirements ($W \ge 48\text{px}$).
*   [ ] Validated layout against desktop (12-column) and mobile (4-column) breakpoint rules.
*   [ ] Resolved fluid typographic calculations.
*   [ ] Structured and exported all design tokens using the standard schema.
*   [ ] Documented default, hover, focus, active, disabled, and loading states for new components.
