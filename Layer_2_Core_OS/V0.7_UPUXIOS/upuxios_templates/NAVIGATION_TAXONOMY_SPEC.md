# Navigation & Taxonomy Specification

## 1. Document Overview
This document specifies the navigation architecture, Information Architecture (IA) hierarchy, and metadata taxonomy standards for the application. It ensures a consistent, high-findability user experience across desktop and mobile, optimized for user cognitive limits and WCAG 2.2 accessibility guidelines.

---

## 2. Information Architecture Hierarchy
The application's structural depth is restricted to a maximum of three core levels to minimize search latency and user navigation errors.

```
[Level 1: Global Workspace]
        |
        +---> [Level 2: Section Hubs]
                    |
                    +---> [Level 3: Contextual Tools & Detail Views]
                                |
                                +---> (Level 4: Inline Actions & Page Controls)
```

| Level | IA Category | Structural Purpose | Max Items | Navigation Control |
| :--- | :--- | :--- | :--- | :--- |
| **L1** | Global Workspace | High-level workspace switching and core modules. | 5 | Primary vertical sidebar / Global header |
| **L2** | Section Hubs | Main category dashboards and object indexes. | 7 | Secondary horizontal navigation bar |
| **L3** | Contextual Views | Specific task execution, editing, and analytics. | Unlimited | Tabs, list-details, side sheets |
| **L4** | Inline Actions | Operations on objects (Edit, Delete, Export). | 5 per group | Contextual button bars, overflow menus |

---

## 3. Navigation Menus & Behaviors

### 3.1. Hover Intent & Delay Tolerances
To prevent accidental menu triggers when moving the cursor across the screen, all hover-triggered dropdowns must implement a **Hover Intent** delay:

$$T_{\text{hover}} = 250\text{ ms}$$

If the user cursor remains over the target area for less than $T_{\text{hover}}$, the dropdown menu will not open. Once open, a mouseout buffer of $300\text{ ms}$ must elapse before the menu closes, allowing users to move their cursor diagonally toward menu options without triggering close events.

### 3.2. Menu States & Interactions
*   **Active State:** The active menu item must match the URL path. It must be styled with high-contrast accenting ($4.5:1$ ratio) and include an `aria-current="page"` attribute.
*   **Focus State:** Keyboard focus must display a visible outline (`2px solid var(--focus-color)`) with an offset of `2px`.
*   **Disabled State:** Inaccessible paths must have `opacity: 0.4`, `pointer-events: none`, and `aria-disabled="true"`.

---

## 4. Search Taxonomy & Metadata Tagging
High search findability is supported by a structured, faceted metadata schema applied to all content entities.

| Facet Attribute | Data Type | UI Input Control | Facet Hierarchy | Search Priority |
| :--- | :--- | :--- | :--- | :--- |
| `workspace_id` | UUID | Single-Select Dropdown | Level 1 (Global) | Critical |
| `entity_type` | Enum | Multi-Select Chips | Level 2 (Section) | High |
| `owner_id` | UUID | User Combo-box Search | Level 3 (Context) | Medium |
| `status_state` | Enum | Toggle Button Group | Level 3 (Context) | High |
| `created_at` | DateTime | Date Range Picker | Level 3 (Context) | Low |

---

## 5. URL Routing & Breadcrumb Syntax
All application paths must correspond directly to the Information Architecture.

### 5.1. URL Structure Template
```
https://{domain}/workspaces/{workspace_slug}/{section_slug}/{entity_id}
```
*   *Correct:* `https://app.platform.com/workspaces/billing-ops/invoices/inv-90812`
*   *Incorrect:* `https://app.platform.com/invoices.php?id=90812&ws=billing-ops`

### 5.2. Breadcrumb Navigation
Breadcrumbs must be generated dynamically from the active URL path.
*   **Syntax:** `Workspace > Section Hub > Contextual View`
*   **Truncation Rule:** If a label exceeds $24$ characters, truncate with an ellipsis (`...`) but retain the full label in the `title` attribute. The active page item must be plain text (non-clickable) and have `aria-current="page"`.

---

## 6. Interaction & Keyboard Accessibility
Keyboard accessibility for navigation must comply with WAI-ARIA standards.

### 6.1. Keyboard Navigation Path
*   **`Tab` Key:** Traverse main L1 and L2 menu targets sequentially.
*   **`Right/Left Arrows`:** Traverse horizontal lists.
*   **`Down/Up Arrows`:** Open and traverse vertical dropdown menus.
*   **`Space` or `Enter`:** Activate selected menu item.
*   **`Esc`:** Close active dropdown menu and return focus to its parent trigger.

---

## 7. Verification Checklist
- [ ] Verify that all navigation links contain `aria-label` when utilizing icons only.
- [ ] Confirm hover intent timeout is set to $250\text{ ms}$ programmatically.
- [ ] Check keyboard focus ring visibility across all interactive states.
- [ ] Validate breadcrumb link targets against the active URL structure.

---

## 8. Revision History
*   **V1.0 (2026-06-26):** Initial Navigation & Taxonomy Specification template.\n