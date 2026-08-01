# ENGINE — Frontend Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates complete, production-grade frontend applications from design specifications and API contracts. Applies Feature-Sliced Design, state management best practices, accessibility standards, and all VENUS frontend standards.

---

## Input Requirements
```
Required:
  - Application type (SPA, SSR, Static, Micro-frontend)
  - User flows and page specifications
  - Design system tokens (colors, typography, spacing)
  - API contracts (OpenAPI spec or GraphQL SDL)
  - Authentication requirements

Optional:
  - Performance targets (Core Web Vitals)
  - Accessibility level (WCAG AA / AAA)
  - i18n requirements
  - Target devices and browsers
```

---

## Generation Process

### Step 1: Project Scaffold
Generate framework-appropriate structure:
```
Framework Selection:
  SEO-critical → Next.js (App Router)
  Pure SPA → React + Vite
  Content-heavy → Astro
  Enterprise → Angular

Structure: Feature-Sliced Design (Part 10)
```

### Step 2: Design System Generation
- CSS custom properties for all design tokens
- Typography scale with Google Fonts integration
- Color system with semantic naming
- Spacing scale
- Component variants

### Step 3: Atomic Component Generation
For each required UI element:
- Component implementation (TypeScript + JSX)
- Storybook story (all variants)
- Unit test (render, interactions, accessibility)
- CSS Module styles

### Step 4: Feature Implementation
For each user flow:
- Page component with data fetching
- Feature-level state management
- API integration (Tanstack Query)
- Form validation (React Hook Form + Zod)
- Error boundary and loading states

### Step 5: Performance Optimization
- Route-level code splitting
- Image optimization configuration
- Font preloading
- Critical CSS extraction
- Bundle analysis and tree-shaking verification

---

## Core Web Vitals Compliance
Every generated frontend must pass:
- LCP < 2.5s
- INP < 200ms
- CLS < 0.1
- Bundle size audit (initial JS < 200KB gzipped)

---

## Accessibility Compliance
- WCAG 2.1 AA by default
- Semantic HTML for all interactive elements
- Keyboard navigation fully functional
- ARIA attributes on all custom components
- Color contrast validation automated in CI
