# Part 24: QA Automation

## 1. Context & Strategy
QA Automation under Project Venus governs the end-to-end (E2E) verification of user-facing systems and complex workflow integrations. This manual defines visual regression models, browser automation patterns, test suite orchestration, and flakiness containment strategies. All user-interface code must pass automated QA gates before target promotion.

---

## 2. Test Flakiness & Reliability Metrics

### 2.1 Test Flakiness Index
A flaky test passes and fails under the same codebase state. The Flakiness Index ($FI$) is calculated over a tracking window to prioritize remediation:

$$FI = \frac{T_{flaky}}{T_{total}}$$

Where:
*   $T_{flaky}$: Number of tests exhibiting unstable run history (both pass and fail outcomes on the same Git commit).
*   $T_{total}$: Total active tests in the automated QA suite.
*   *Threshold*: The E2E suite must maintain an $FI \le 2\%$. Any test exceeding this threshold must be automatically quarantined.

### 2.2 Visual Shift Tolerance (Structural Similarity Index - SSIM)
Visual regression tests utilize the SSIM model to compare screenshots ($x$ and $y$) and identify layout shifts, ignoring minor subpixel rendering differences:

$$\text{SSIM}(x, y) = \frac{(2\mu_x\mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}$$

Where $\mu$ and $\sigma$ denote brightness and variance statistics, and $C_1, C_2$ stabilize the division.
*   *Requirement*: Deployments must verify $\text{SSIM}(x, y) \ge 0.99$.

---

## 3. Automation Implementation Standards

### 3.1 Playwright E2E Test Setup
E2E browser automation must utilize the Page Object Model (POM) pattern to isolate UI selectors from assertions.

```typescript
// pages/order-page.ts
import { Page, Locator } from '@playwright/test';

export class OrderPage {
  readonly page: Page;
  readonly checkoutBtn: Locator;
  readonly orderSuccessAlert: Locator;

  constructor(page: Page) {
    this.page = page;
    this.checkoutBtn = page.locator('[data-testid="checkout-button"]');
    this.orderSuccessAlert = page.locator('[data-testid="success-alert"]');
  }

  async proceedToCheckout() {
    await this.checkoutBtn.click();
  }
}
```

```typescript
// specs/order-flow.spec.ts
import { test, expect } from '@playwright/test';
import { OrderPage } from '../pages/order-page';

test.describe('Order Lifecycle', () => {
  test('should complete standard checkout successfully', async ({ page }) => {
    const orderPage = new OrderPage(page);
    await page.goto('/checkout');
    await orderPage.proceedToCheckout();
    await expect(orderPage.orderSuccessAlert).toBeVisible({ timeout: 5000 });
  });
});
```

### 3.2 Visual Regression Comparison Schema
Every visual validation task must output a metrics file matching this structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VisualRegressionReport",
  "type": "object",
  "properties": {
    "viewport": {
      "type": "string"
    },
    "ssimScore": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "mismatchedPixels": {
      "type": "integer"
    },
    "diffImagePath": {
      "type": "string"
    }
  },
  "required": ["viewport", "ssimScore", "mismatchedPixels", "diffImagePath"]
}
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that all selectors use unique data attributes (e.g., `data-testid="button-submit"`).
*   [ ] Ensured no hardcoded wait/sleep calls exist; all operations wait for specific selectors or API responses.
*   [ ] Checked that flaky tests are identified, quarantined, and tracked as Jira tasks.
*   [ ] Verified visual regression checks execute on both mobile viewport and desktop viewport.
*   [ ] Confirmed test executions clean up seed data after browser close.
