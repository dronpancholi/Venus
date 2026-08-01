# Part 13 — Enterprise UX

## 1. Context & Strategy

### 1.1 Purpose
The Enterprise UX Part outlines layout, security, and administrative patterns necessary to satisfy high-security, multi-tenant B2B customer requirements. It details permission matrices, workspace contexts, and compliance-grade audit logging.

### 1.2 The Enterprise Principle
Do not treat enterprise software as single-user consumer applications. Layouts must balance high-density data tables, granular security indicators, administrative configuration panels, and complex permission hierarchies without cluttering the user interface.

---

## 2. Multi-Tenant Layout Architectures

B2B applications must prevent data contamination and clarify user scoping.

### 2.1 Workspace & Tenant Context Switcher
*   **Workspace Indicator**: A persistent badge or dropdown at the top-left of the sidebar display shows the active company tenant.
*   **Preventing Cross-Tenant Leaks**: Any navigation action that crosses tenant lines must trigger a blocking authorization check.
*   **White-Label Boundaries**: Layout styles must define theme configurations using semantic design tokens (`sys.theme.primary`) to allow company branding overrides without breaking layout alignments.

```
+-------------------------------------------------------+
|  [Company Tenant Dropdown v]                          |
|  ├─ Workspace Alpha (ID: WS-1002)                    |
|  └─ Workspace Beta (ID: WS-1003)                      |
+-------------------------------------------------------+
```

---

## 3. RBAC (Role-Based Access Control) Interfaces

RBAC UI prevents unauthorized operations and makes permissions transparent.

### 3.1 Visual Treatment of Restricted Features
*   **Disabled vs. Hidden**:
    *   *Hide*: If a user does not have permission to view a page or tab, remove it from the sidebar or tab list.
    *   *Disable with Context*: If a button or configuration control is disabled due to missing permissions, do not simply make it unclickable. Render a lock icon and show a tooltip explanation: `"Requires Admin Role (Permission: write:billing)"`.

### 3.2 Dynamic Permission Matrix
Roles must be configured via an interactive matrix interface:

| Permission Name | Administrator | Editor | Reader | custom_role |
|---|:---:|:---:|:---:|:---:|
| `billing:write` | Checkbox (Checked) | Checkbox (Unchecked) | Checkbox (Unchecked) | Checkbox (Unchecked) |
| `member:invite` | Checkbox (Checked) | Checkbox (Checked) | Checkbox (Unchecked) | Checkbox (Unchecked) |
| `data:export` | Checkbox (Checked) | Checkbox (Unchecked) | Checkbox (Unchecked) | Checkbox (Checked) |

---

## 4. Impersonation UX Flow

Admin impersonation is critical for debugging customer accounts but poses high compliance risk.

### 4.1 Enforcing Security Alerts
*   **Persistent Banner**: When an administrator is impersonating a tenant user, a high-contrast banner must lock to the top of the interface:
    *   *Text*: `"You are currently impersonating [User Name] ([User Email]). All actions are logged under Admin ID [Admin ID]."`
    *   *Action*: Prominent button: `[Exit Impersonation]`.
*   **Session Boundary**: Impersonation sessions must auto-terminate after 30 minutes of inactivity.

---

## 5. Audit Log & Governance UX

All administrative mutations require human-scannable audit tracking.

### 5.1 Audit Log Table Specifications
Audit logs must render as a dense grid containing:
*   **Timestamp**: ISO 8601 UTC format (`YYYY-MM-DD HH:mm:ss Z`).
*   **User/Actor**: Profile avatar, email, and IP address.
*   **Action Category**: Color-coded badges for CRUD operations (`CREATE` = green, `UPDATE` = yellow, `DELETE` = red).
*   **Object Type**: Link to the modified entity.
*   **Visual Changes Diff**: Toggle dropdown displaying the exact changes:

```diff
- "billing_address": "123 Old St"
+ "billing_address": "456 New Ave"
```

---

## 6. Enterprise UX Checklist
*   [ ] Ensured active workspace/tenant is clearly displayed in the navigation sidebar.
*   [ ] Checked that disabled controls provide helpful explanations on permission requirements.
*   [ ] Audited system layouts to verify they adapt to tenant theme injections.
*   [ ] Configured top-level impersonation banner and auto-exit functions.
*   [ ] Designed compliance-ready audit tables with explicit filter capabilities.
