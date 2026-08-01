# Growth Onboarding & Activation Flow UX

## 1. Document Overview
This document specifies registration steps, user profiling wizards, interactive walkthroughs, and activation metrics to ensure users find value quickly during onboarding.

---

## 2. Frictionless Sign-up Flow
Reduce registration drop-offs by keeping sign-up forms simple.
*   **Social Sign-On (SSO):** Put Google, Microsoft, and GitHub buttons at the top of the form.
*   **Single-Field Flow:** Only ask for Email and Password at first. Collect other details later during the wizard.
*   **Real-time Validation:** Check password strength and email availability dynamically as the user types.

---

## 3. Setup Wizard & User Profiling
Once registered, guide users through a brief, 3-step setup wizard:

```
[Step 1: Role Profile] ---> [Step 2: Workspace Setup] ---> [Step 3: Connect Team]
```

*   **Role Profiling:** Ask users to select their job role from clear options. This helps customize the default workspace layout.
*   **Setup Progress Bar:** Show a clear progress bar (e.g., "Step 2 of 3") at the top of the wizard view.

---

## 4. Progressive Walkthroughs & Guides
Use interactive guides to show key features as users explore the app.

### 4.1. Overlay Guides
*   **Tooltip Focus:** Dim the background except for the highlighted target element.
*   **Skip Tour Options:** Every step must include a "Skip Guide" button.

### 4.2. Action Checklist
Show a checklist of getting-started tasks on the dashboard home screen.
*   **Interactive Checklist:** Checking off a task updates the progress bar:

```
[Onboarding Progress: 2/4 Complete] ===================> [50%]
```

---

## 5. Measuring User Activation (Aha! Moment)
User activation occurs when they complete a key action that demonstrates the value of the platform.

$$\text{Activation Rate} = \frac{\text{Activated Users}}{\text{Total Registered Users}} \times 100$$

| Product Area | Milestone Action | Time Window | Success Celebration |
| :--- | :--- | :--- | :--- |
| **Workspace Creation**| Create first team workspace. | Within 24 hours | Success toast alert message. |
| **Team Invites** | Invite $2$ or more team members. | Within 7 days | "Team setup complete" progress badge. |
| **Active Integration**| Connect first third-party tool. | Within 14 days | Confetti animation on screen. |

---

## 6. Verification Checklist
- [ ] Verify that the setup wizard can be skipped or closed at any point.
- [ ] Confirm screen readers read all walkthrough tooltips and focus steps correctly.
- [ ] Test form fields to ensure auto-fill suggestions are supported.
- [ ] Verify that activation milestones trigger success events accurately.

---

## 7. Revision History
*   **V1.0 (2026-06-26):** Initial Growth Onboarding UX template.\n