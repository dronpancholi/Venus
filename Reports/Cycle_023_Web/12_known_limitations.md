# Known Limitations

## Technical
1. **No LLM integration** — AI Copilot uses search API, not an LLM
2. **No real web terminal** — Terminal page is a visual mockup; xterm.js removed due to peer dependency conflict
3. **No authentication** — API is unauthenticated by default (`require_auth=False`)
4. **No PWA service worker** — manifest exists but no offline support
5. **No responsive mobile layout** — Sidebar collapse not adaptive to viewport
6. **No server-side rendering** — SPA has empty initial HTML (SEO impact)
7. **No error boundaries** — React error boundaries not implemented
8. **No loading skeletons** — Pages use text placeholders instead of skeleton loaders
9. **No visualizations** — Knowledge graph, task graph, charts not implemented
10. **No file browser** — Project view doesn't show file tree
11. **No conversation persistence** — Copilot conversations not saved to workspace
12. **SearchDialog doesn't handle empty results gracefully on first load**
13. **WebSocket URL assumes `/v1/ws` without configurable path**
14. **No HTTPS support** — HTTP only
15. **No CORS configuration** — Works for same-origin only

## Design Gaps
16. **No dark/light mode toggle** — Dark mode only
17. **No custom theming** — Uses hardcoded Genesis blue
18. **No accessibility audit** — ARIA labels incomplete
19. **No keyboard navigation** — Tab order not verified
20. **Font loading** — System fonts only, no custom font loading

## Build/Delivery
21. **Frontend not in Python package** — `web/dist/` must exist at runtime
22. **No automated frontend build** — Must run `npm run build` manually
23. **No version synchronization** — Frontend/backend versions independent
24. **No CI/CD integration** — No build pipeline for the frontend
25. **Large JS bundle** — 482KB total (147KB gzip) — Framer Motion is the largest at 129KB
