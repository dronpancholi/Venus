# Product-Led Growth (PLG) Upgrade & Pricing UX

## 1. Document Overview
This document specifies layout grids, upgrade trigger criteria, checkout forms, and subscription settings panels to support a product-led growth (PLG) model.

---

## 2. Pricing Page & Plan Grid
The primary pricing page presents plan options side-by-side.

### 2.1. Pricing Layout
```
+---------------------------------------------------------------------------------+
|                        [Billing Cycle]:  ( ) Monthly  (*) Annual (Save 20%)     |
+---------------------------------------------------------------------------------+
|  [Free Plan]               [Pro Plan - Popular]        [Enterprise Plan]        |
|  $0                        $29 / month                 Contact Us               |
|                            (Billed annually)                                    |
|  * 1 User                  * Unlimited Users           * Advanced Security      |
|  * 2 Workspaces            * 10 Workspaces             * SSO Integrations       |
|                                                                                 |
|  [Get Started]             [Upgrade Now]               [Contact Sales]          |
+---------------------------------------------------------------------------------+
```

### 2.2. Visual Highlights
*   **Recommended Plan Badge:** Highlight the target tier using a contrasting color outline and a "Most Popular" label.
*   **Pricing Toggles:** Toggle switches let users compare monthly and annual pricing options easily.

---

## 3. Inline Upgrade Triggers
Display upgrade alerts at logical points when users hit plan limits.

| Plan Limit Event | Trigger Point | Visual Banner Pattern | Target Call-to-Action |
| :--- | :--- | :--- | :--- |
| **Workspace Limit** | User clicks "Create Workspace" when at plan capacity. | Modal: "You have reached your limit of 2 workspaces." | "Upgrade to Pro for more workspaces" |
| **Seats Limit** | User invites a team member when seats are full. | Warning Alert Banner in Team Management settings. | "Buy 1 additional seat for $5/mo" |
| **Export Limit** | User attempts an export on a restricted plan. | Locked indicator icon next to button options. | "Unlock CSV export with Pro" |

---

## 4. Checkout & Payment Forms
Keep checkout forms simple to reduce purchase drop-offs.
*   **Input Fields:** Collect Card Number, Expiration Date, CVV, and Billing Zip Code in a single line if possible.
*   **Real-time Validation:** Validate card numbers and Zip codes dynamically as the user types.
*   **Total Summary:** Show an itemized summary listing prices, active discounts, taxes, and final totals.

---

## 5. Subscription Management
The settings panel lets users manage their plans easily.
*   **Seat Controls:** Add or remove team seats with a count selector.
*   **Plan Swaps:** Switch plans with a "Change Plan" wizard.
*   **Cancellation Options:** Before canceling, show a mitigation page offering discounts or account pauses.

---

## 6. Verification Checklist
- [ ] Confirm pricing page contrast ratios meet WCAG AA requirements.
- [ ] Verify checkout input validation detects invalid card details correctly.
- [ ] Test the annual billing toggle to ensure prices update instantly.
- [ ] Ensure cancellation surveys load correctly before final changes.

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial PLG Upgrade & Pricing UX template.\n