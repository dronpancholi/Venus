# Part 11 — Accessibility Engine

## 1. Context & Strategy

### 1.1 Purpose
The Accessibility Engine defines the standards required to ensure all Project Venus interfaces are fully usable by individuals with varying physical, sensory, cognitive, and situational capabilities. This part enforces strict WCAG 2.2 AA and AAA compliance, accessibility markup, and localized right-to-left (RTL) interface behavior.

---

## 2. WCAG 2.2 Compliance Framework

We target **WCAG 2.2 Level AA** as our mandatory baseline, and **Level AAA** for critical transactional and reading interfaces.

### 2.1 Contrast Ratios
*   **Normal Text (under 18pt/24px normal, 14pt/18.6px bold)**:
    *   *Level AA requirement*: $4.5:1$ minimum contrast ratio against background.
    *   *Level AAA requirement*: $7.0:1$ minimum contrast ratio.
*   **Large Text (18pt/24px normal or larger, 14pt/18.6px bold or larger)**:
    *   *Level AA requirement*: $3.0:1$ minimum contrast ratio.
    *   *Level AAA requirement*: $4.5:1$ minimum contrast ratio.
*   **UI Components & Graphical Objects**:
    *   Enforced $3.0:1$ contrast ratio for input boundaries, progress bars, and state indicator borders.

### 2.2 Formulas for Contrast Calculation
Contrast ($C$) is determined based on relative luminance ($L_1$ and $L_2$, where $L_1$ is the lighter color):

$$C = \frac{L_1 + 0.05}{L_2 + 0.05}$$

$$L = 0.2126 \times R + 0.7152 \times G + 0.0722 \times B$$

Where $R$, $G$, and $B$ are calculated as:
*   If $V_{sRGB} \le 0.04045$: $V = \frac{V_{sRGB}}{12.92}$
*   Else: $V = \left(\frac{V_{sRGB} + 0.055}{1.055}\right)^{2.4}$

---

## 3. Screen Readers & Semantic HTML

Interfaces must use semantic markup to expose structure to assistive technologies.

### 3.1 Landmark Elements
*   All layouts must employ standard tags: `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`.
*   A single `<h1>` tag must start the content hierarchy on every page.

### 3.2 ARIA Attributes & Live Regions
*   **Dynamic Announcements**: Enforce `aria-live="polite"` for non-disruptive notifications, and `aria-live="assertive"` for critical error banners.
*   **Interactive Controls**: Buttons that expand drawers or menus must include `aria-expanded="true|false"` and reference the target element's ID via `aria-controls`.
*   **Helper Text Relationships**: Form fields with instruction or validation text must link them using `aria-describedby="helper-text-id"`.
*   **Decorative Media**: Informational images require descriptive `alt="..."`. Decorative icons must carry `aria-hidden="true"` to prevent screen reader noise.

---

## 4. Keyboard Navigation Rules

Interfaces must be fully functional using only a keyboard.

### 4.1 Tab Order & Focus Control
*   **Natural Logical Sequence**: Focus order must match the visual reading order (left-to-right, top-to-bottom for LTR).
*   **Focus Ring Persistence**: Enforced high-contrast ring for all keyboard interactions. Global resets (`outline: none`) are strictly forbidden.
*   **Modal Focus Trapping**: Opening a modal must capture keypress loops within the modal limits. Esc key must exit the modal and return focus to the trigger element.

```
[Tab Out of Modal Footer] ──► Redirect Focus ──► [Modal Header Close Button]
```

---

## 5. Localization & RTL Layout Systems

We design for global adaptability, ensuring standard layouts support multi-lingual strings and Bidirectional (BiDi) text systems (e.g., Arabic, Hebrew).

### 5.1 RTL Mirroring Architecture
*   **CSS Logical Properties**: Always use logical properties instead of physical directions:
    *   `margin-inline-start` instead of `margin-left`
    *   `padding-inline-end` instead of `padding-right`
    *   `text-align: start` instead of `text-align: left`
*   **Layout Swapping**: Flex containers mirror layout axis direction based on document direction attribute: `<html dir="rtl">`.
*   **Visual Directional Elements**: Directional icons (e.g., arrows, page progress bars) must be mirrored in RTL mode, whereas branding, media play buttons, and clocks remain unmirrored.

---

## 6. Accessibility Compliance Checklist
*   [ ] Checked all text content passes contrast ratio checks ($4.5:1$ for AA, $7.0:1$ for AAA).
*   [ ] Ensured all form inputs are linked to visual labels using `<label for="...">`.
*   [ ] Verified focus trap mechanics are operating on all modal components.
*   [ ] Tested screen reader readouts of custom dynamic components using ARIA standards.
*   [ ] Verified layout stability and mirroring under RTL settings (`dir="rtl"`).
