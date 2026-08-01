# Frontend Architecture

## Stack
| Layer | Choice | Rationale |
|-------|--------|-----------|
| Framework | React 19 | Industry standard, large ecosystem |
| Build | Vite 6 | Fast, modern, TypeScript-native |
| Language | TypeScript 5.8 | Type safety |
| Styling | Tailwind CSS 3.4 | Utility-first, consistent design |
| Routing | React Router 7 | Declarative, client-side SPA routing |
| Data Fetching | TanStack Query 5 | Caching, dedup, background refetch |
| Animation | Framer Motion 12 | Declarative, performant animations |
| State | Zustand 5 | Minimal global state |
| Icons | Lucide React | Consistent, tree-shakeable icon set |

## Directory Structure
```
web/
├── index.html                    # SPA entry point
├── package.json                  # Dependencies
├── vite.config.ts                # Build config, proxy, chunking
├── tsconfig.json                 # TypeScript config
├── tailwind.config.js            # Custom colors, fonts, animations
├── postcss.config.js             # PostCSS with Tailwind
├── public/
│   ├── favicon.svg               # SVG favicon
│   └── manifest.json             # PWA manifest
└── src/
    ├── main.tsx                  # React entry, QueryClient, Router
    ├── App.tsx                   # Route definitions
    ├── index.css                 # Tailwind directives, globals
    ├── lib/
    │   ├── api.ts                # REST API client (18 endpoints)
    │   ├── websocket.ts          # WebSocket client with reconnect
    │   ├── store.ts              # Zustand UI state store
    │   └── types.ts              # TypeScript interfaces
    ├── components/
    │   ├── Layout.tsx            # App shell (sidebar + statusbar + outlet)
    │   ├── Sidebar.tsx           # Navigation sidebar
    │   ├── StatusBar.tsx         # Bottom status bar (WS, health)
    │   ├── SearchDialog.tsx      # Universal search (⌘K)
    │   └── CopilotPanel.tsx      # AI Copilot chat panel
    └── pages/
        ├── Home.tsx              # Landing page with stats
        ├── Dashboard.tsx         # Full system dashboard
        ├── Project.tsx           # Single project view
        ├── Knowledge.tsx         # Knowledge catalog + search
        ├── Timeline.tsx          # Event + audit timeline
        ├── Terminal.tsx          # Engineering terminal
        ├── Copilot.tsx           # Full AI Copilot page
        ├── Search.tsx            # Dedicated search page
        └── Settings.tsx          # Settings/configuration
```

## Build Output
```
dist/
├── index.html                    # 0.98 KB (gzip: 0.47 KB)
├── favicon.svg
├── manifest.json
└── assets/
    ├── index-CNkJLB7s.css        # 17 KB (gzip: 4 KB)
    ├── vendor-D48Dyvk0.js        # 43 KB (gzip: 15 KB) — React/ReactDOM/Router
    ├── query-D_FLdHVE.js         # 47 KB (gzip: 15 KB) — TanStack Query
    ├── motion-BnduLcn5.js        # 129 KB (gzip: 42 KB) — Framer Motion
    └── index-pCHG8_9P.js         # 245 KB (gzip: 71 KB) — App code
Total: 482 KB (gzip: 147 KB)
```
