# Accessibility & Compliance Checklist (WCAG 2.2 AA)

## 1. Document Overview
This checklist defines the accessibility rules, screen reader scripts, and auditing guidelines required to meet WCAG 2.2 AA compliance. It ensures the application is accessible to all users, regardless of ability.

---

## 2. Perceivable Guidelines

### 2.1. Non-Text Content (Alt Text)
- [ ] Every image must include a descriptive `alt` attribute. If an image is purely decorative, use `alt=""` so screen readers skip it.
- [ ] Form controls and buttons with icons must include an `aria-label` or `title` attribute.

### 2.2. Visual Contrast Rates
- [ ] Text and interactive elements must meet the minimum contrast ratios specified below:

| Target Element | Minimum Contrast Ratio | Auditing Tool |
| :--- | :--- | :--- |
| Normal text | $4.5:1$ | Chrome DevTools Contrast Checker |
| Large text ($> 18\text{pt}$) | $3.0:1$ | Chrome DevTools Contrast Checker |
| Graphic icons & boundaries | $3.0:1$ | Axe DevTools |

---

## 3. Operable Guidelines

### 3.1. Keyboard Navigation
- [ ] All interactive elements must be accessible via the keyboard alone (without using a mouse).
- [ ] Focus indicators must be clearly visible (`outline` property should never be styled as `none`).
- [ ] Use skip links (`href="#main-content"`) at the top of the page to let keyboard users bypass navigation menus.

### 3.2. Focus Order & Keyboard Traps
- [ ] Interactive focus must move in a logical order (left-to-right, top-to-bottom).
- [ ] Ensure modal dialogs implement focus trapping to prevent keyboard users from focusing on elements behind the modal.

---

## 4. Understandable Guidelines

### 4.1. Text & Layout Clarity
- [ ] Set the primary page language on the document root: `<html lang="en">`.
- [ ] Keep language simple; explain acronyms and technical terms on first use.

### 4.2. Input Assistance
- [ ] Form fields must feature visible, descriptive labels (`<label for="id">`).
- [ ] Error messages must describe what is wrong and how to fix it, using `aria-describedby` to link the message to its input field.

---

## 5. Robust Guidelines
- [ ] Write valid semantic HTML: close tags correctly and nesting elements in the proper order.
- [ ] Interactive widgets must include descriptive WAI-ARIA role and state attributes (`role="dialog"`, `aria-expanded`).

---

## 6. Auditing & Testing Workflow
1.  **Automated Audit:** Run an Axe DevTools or Google Lighthouse scan to find common compliance issues.
2.  **Keyboard Walkthrough:** Navigate the application using only the `Tab`, `Arrow`, and `Enter` keys to verify that focus behaves logically.
3.  **Screen Reader Check:** Test the interface with a screen reader (VoiceOver on Mac, NVDA on Windows) to verify that headings and menus are announced correctly.

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial WCAG 2.2 AA Compliance Checklist.\n