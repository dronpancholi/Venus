# End-to-End Playwright Specification
**Document ID:** VENUS-STD-064
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
End-to-End (E2E) testing verifies entire user workflows from UI interactions to database persistence. This document specifies the testing design and configurations using Microsoft Playwright.

## 2. Playwright Configuration (`playwright.config.ts`)
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: [['html', { outputFolder: 'playwright-report' }]],
  use: {
    baseURL: process.env.STAGING_URL || 'https://staging.venus.internal',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

## 3. Page Object Model (POM) Structure
To maintain robust test code, tests must use the POM design pattern.

### 3.1 Page Object Example (`LoginPage.ts`)
```typescript
import { Locator, Page } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('input[type="email"]');
    this.passwordInput = page.locator('input[type="password"]');
    this.loginButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-notification');
  }

  async navigate() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}
```

### 3.2 Test Script Example (`auth.spec.ts`)
```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';

test.describe('Authentication Journeys', () => {
  test('should display error message on invalid credentials', async ({ page }) => {
    // Arrange
    const loginPage = new LoginPage(page);
    await loginPage.navigate();

    // Act
    await loginPage.login('invalid@venus.org', 'WrongPassword123');

    // Assert
    await expect(loginPage.errorMessage).toBeVisible();
    await expect(loginPage.errorMessage).toContainText('Invalid email or password');
  });
});
```

## 4. Cross-References
- [Test Plan Strategy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TEST_PLAN_STRATEGY.md)
- [QA Automation Suite Runbook](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/QA_AUTOMATION_SUITE_RUNBOOK.md)
