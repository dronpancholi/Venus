# Part 14 — Mobile Intelligence

## 1. Context & Strategy

### 1.1 Purpose
The Mobile Intelligence Part defines behavioral rules, physical ergonomics, offline-first mechanisms, and gesture-driven interaction patterns for touch-screen interfaces.

### 1.2 Ergonomic Thumb-Zone Mapping
To facilitate one-handed mobile usage, interactive zones are prioritized by physical reach:
*   **Green Zone (Natural)**: Bottom 60% of the screen. Place primary actions, tab navigation, and search bars here.
*   **Yellow Zone (Stretched)**: Middle 20% of the screen. Place secondary options and intermediate selections.
*   **Red Zone (Hard to Reach)**: Top 20% of the screen. Place status indicators, close buttons, and settings icons.

```
+---------------------------+
|      [ Red Zone ]         |  <-- Hard to reach: Settings, Back
+---------------------------+
|    [ Yellow Zone ]        |  <-- Requires stretching
+---------------------------+
|                           |
|     [ Green Zone ]        |  <-- Natural: Primary buttons, Tab bars
+---------------------------+
```

---

## 2. Touch Targets & Responsive Grids

Mobile interfaces require physical space to prevent input errors.

### 2.1 Spatial and Target Rules
*   **Touch Targets**: Minimum interactive dimensions must be $48\text{px} \times 48\text{px}$ to prevent accidental activation.
*   **Tap Spacing**: Interactive elements must maintain a minimum buffer of $8\text{px}$ between bounds.
*   **Grid Layout**: A 4-column fluid layout with $16\text{px}$ margins and $12\text{px}$ vertical gutters. Columns scale dynamically while horizontal scrolls are restricted to card decks.

---

## 3. Gestures & Physical Feedbacks

Mobile devices leverage sensory feedback to build interactive confidence.

### 3.1 Standard Swipe Actions
Swipe gestures on list rows must display clear underlying actions and match system defaults:
*   **Swipe Right (Action: Pin/Mark Read)**: Teal container slides in, exposing an eye or pin icon.
*   **Swipe Left (Action: Delete/Archive)**: Red container slides in, exposing a trash or archive icon.
*   **Visual Release Threshold**: Swiping past 35% of the row width commits the action automatically with a velocity filter ($>0.5\text{px/ms}$).

### 3.2 Bottom Sheet & Modal Controls
*   **Drag Handle**: Bottom sheets must include a visible drag bar ($36\text{px} \times 4\text{px}$) with rounded corners, centered at the top edge.
*   **Flick Physics**: Fast upward swipes expand sheets to full screen, while downward swipes close sheets.

---

## 4. Offline State & Optimistic UI

Interfaces must handle intermittent network connections gracefully.

### 4.1 Sync States & Visual Cues
*   **Connectivity Toast**: A subtle banner appears when connection drops: `"Offline — changes will sync when online"`.
*   **Optimistic UI Updates**: When a user marks an item completed, toggle the checkbox immediately. Run background sync retry loops. If the retry loop fails after 3 attempts, rollback the toggle state and display an error icon.

### 4.2 Sync Conflict Resolution UX
When local and remote changes conflict, display a modal showing:
*   *Option A*: Keep Local Version (showing timestamp of last local edit).
*   *Option B*: Keep Cloud Version (showing editor name and timestamp).
*   *Action*: `[Resolve Conflict]`.

---

## 5. Mobile Intelligence Checklist
*   [ ] Placed primary interactive targets inside the ergonomic Green Zone.
*   [ ] Checked touch targets are at least $48\text{px} \times 48\text{px}$.
*   [ ] Configured logical swipe-action thresholds (35% row width, haptic triggers).
*   [ ] Verified offline state indicator banners display during disconnects.
*   [ ] Implemented optimistic state transition models with local storage caching.
