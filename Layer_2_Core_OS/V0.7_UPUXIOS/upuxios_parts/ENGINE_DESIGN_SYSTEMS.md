# Engine: Design Systems

## 1. Context & Strategy

### 1.1 Purpose
The Design Systems Engine automates the ingestion, validation, and transformation of design tokens (defined in JSON format) into platform-specific styling configurations, such as CSS Custom Properties, Tailwind CSS configs, and Swift/XML assets.

### 1.2 Philosophy
Manual translation of styling rules is a major source of design drift and visual regression. Visual attributes must be declared once in a single token repository, compiled automatically, and distributed programmatically across all codebases.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Input**: JSON design token payload conforming to the design token schema (defined in [Part 10](file:///Users/dronpancholi/Developer/01_Strategic/Venus/upuxios_parts/PART_10_DESIGN_SYSTEMS.md)).
*   **Outputs**:
    *   `variables.css`: Standard CSS custom properties block.
    *   `tailwind.config.js`: Tailwind theme expansion override object.
    *   `tokens.swift`: Swift UI theme structure mapping.

### 2.2 Compilation Pipeline
```
               [Raw JSON Tokens Ingest]
                          │
            [Validation & Schema Matcher]
                          │
            [Calculations & Scaling Engine]
             ├── Compute fluid typography bounds
             └── Resolve alias/semantic tokens
                          │
            [Code Exporter (Style Dictionary)]
             ├── CSS Variables Exporter
             ├── Tailwind Config Exporter
             └── Swift UI Exporter
```

---

## 3. Mathematical Token Computations

The engine dynamically generates scaled attributes:

### 3.1 Fluid Font-Size Calculation
For any text class, the engine computes the fluid font-size mapping:

$$\text{CSS Clamp} = \text{clamp}\left(P_{min}, P_{min} + \left(P_{max} - P_{min}\right) \times \frac{V_w - V_{min}}{V_{max} - V_{min}}, P_{max}\right)$$

Where:
*   $P_{min}$ is the minimum font size in rems (e.g. $1\text{rem}$ at desktop break).
*   $P_{max}$ is the maximum font size in rems (e.g. $1.333\text{rem}$).
*   $V_w$ is the viewport width indicator (`100vw`).
*   $V_{min}$ and $V_{max}$ are the viewport range limits (typically $375\text{px}$ to $1440\text{px}$).

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that JSON tokens follow the semantic naming hierarchy.
*   [ ] Verified contrast compliance of target colors prior to compiling token exports.
*   [ ] Validated fluid scale clamps against mobile viewport min/max constraints.
*   [ ] Confirmed export templates generate valid syntax for Tailwind CSS and CSS Custom Properties.
*   *Exit Criteria*: Style variables successfully compiled and tests passed without visual regression.
