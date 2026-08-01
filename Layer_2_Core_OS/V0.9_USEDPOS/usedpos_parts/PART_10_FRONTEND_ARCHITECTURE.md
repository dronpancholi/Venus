# PART 10 — Frontend Architecture
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Frontend Architecture defines the structural patterns, state management philosophy, component design system, routing strategy, performance standards, and accessibility requirements for all frontend applications within the VENUS stack. Frontend is the point of human contact — quality here directly translates to user trust, adoption, and retention.

---

## 2. Architecture Patterns

### 2.1 Recommended Architectures

| Pattern | Use Case | Framework |
|---|---|---|
| **Feature-Sliced Design** | Large SPA with multiple teams | React, Vue |
| **Micro-Frontend** | Multiple independently deployed UIs | Module Federation |
| **Server Components** | Content-heavy, SEO-critical applications | Next.js, Remix |
| **Islands Architecture** | Mostly static with interactive zones | Astro |
| **BFF (Backend for Frontend)** | Mobile + web with distinct data needs | Node.js BFF layer |

### 2.2 Feature-Sliced Design (Default SPA Architecture)

```
src/
├── app/                 # App initialization, providers, routing
├── pages/               # Route-level page compositions
├── widgets/             # Complex autonomous UI blocks
├── features/            # User-scenario-based UI features
├── entities/            # Business domain UI representations
├── shared/              # Reusable utilities, UI kit, API client
│   ├── ui/              # Design system components
│   ├── api/             # Generated API clients
│   ├── lib/             # Utility functions
│   └── config/          # Environment config
```

**Import rules**:
- `app` can import any layer
- `pages` can import `widgets`, `features`, `entities`, `shared`
- `widgets` can import `features`, `entities`, `shared`
- `features` can import `entities`, `shared`
- `entities` can import `shared`
- `shared` cannot import any upper layer (no circular deps)

---

## 3. State Management Strategy

### 3.1 State Classification
| Type | Location | Tool |
|---|---|---|
| **Server state** (remote data) | React Query / SWR | Tanstack Query |
| **URL state** (navigation, filters) | URL params | Next.js router |
| **Global UI state** (auth, theme) | Context + Zustand | Zustand |
| **Local component state** | useState / useReducer | React hooks |
| **Form state** | Form libraries | React Hook Form |

### 3.2 Server State Management (Tanstack Query)
All remote data fetched through React Query with:
- Automatic background refetching
- Stale-while-revalidate pattern
- Optimistic updates for mutations
- Cache invalidation strategies
- Error boundary integration

### 3.3 Global State Rules
- Global state must be minimal
- Never store derivable data in global state
- Authentication state: centralized auth context
- Theme/locale: context
- Everything else: co-locate with the component that uses it

---

## 4. Component Design Standards

### 4.1 Component Categories

| Category | Description | Example |
|---|---|---|
| **Atomic** | Single-purpose, no business logic | Button, Input, Badge |
| **Molecular** | Composition of atomic components | SearchBar, FormField |
| **Organism** | Business-context components | ProductCard, UserMenu |
| **Template** | Page layout without real data | DashboardLayout |
| **Page** | Full route with data fetching | OrdersPage |

### 4.2 Component Design Rules
- Maximum component responsibility: one concern
- Props: typed with TypeScript interfaces
- Default props: always defined for optional props
- Side effects: only in hooks, never in render
- No inline styles in production code
- Accessibility: ARIA roles, keyboard navigation, focus management

### 4.3 Component File Structure
```
components/
  OrderCard/
    OrderCard.tsx          # Component
    OrderCard.stories.tsx  # Storybook stories
    OrderCard.test.tsx     # Unit tests
    OrderCard.css          # Scoped styles (CSS Modules)
    index.ts               # Public export
```

---

## 5. Performance Standards

| Metric | Target | Critical Threshold |
|---|---|---|
| **LCP** (Largest Contentful Paint) | < 2.5s | < 4.0s |
| **INP** (Interaction to Next Paint) | < 200ms | < 500ms |
| **CLS** (Cumulative Layout Shift) | < 0.1 | < 0.25 |
| **Bundle size (initial)** | < 200KB gzipped | < 500KB |
| **Time to Interactive** | < 3.5s | < 7.5s |

### 5.1 Performance Implementation Standards
- Code splitting at route level (mandatory)
- Lazy loading for non-critical components
- Image optimization: next/image or equivalent
- Font optimization: font-display: swap, preload
- Critical CSS inlined
- Service Worker for repeat visitors
- Preconnect/prefetch for critical third-party origins

---

## 6. Accessibility (a11y) Standards

All VENUS frontends must meet **WCAG 2.1 AA** compliance:

- Semantic HTML for all interactive elements
- ARIA labels for non-descriptive elements
- Keyboard navigation for all user flows
- Color contrast ratio ≥ 4.5:1 for normal text
- Screen reader testing with VoiceOver / NVDA
- Focus management in modals and dynamic content
- Skip navigation links on all pages

---

## 7. Frontend Security Standards

- Content Security Policy (CSP) headers mandatory
- No `dangerouslySetInnerHTML` without sanitization
- All user inputs sanitized before rendering
- Authentication tokens stored in httpOnly cookies (not localStorage)
- CSRF protection on all mutation endpoints
- Third-party scripts reviewed and integrity-checked
- No PII logged to browser console or analytics
