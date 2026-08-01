# Performance Report

## Bundle Size
| Asset | Raw | Gzip |
|-------|-----|------|
| index.html | 0.98 KB | 0.47 KB |
| index.css | 17.03 KB | 4.10 KB |
| vendor.js (React/Router) | 42.55 KB | 15.25 KB |
| query.js (TanStack Query) | 47.43 KB | 14.79 KB |
| motion.js (Framer Motion) | 128.78 KB | 42.34 KB |
| index.js (App code) | 244.64 KB | 70.70 KB |
| **Total** | **481.41 KB** | **147.65 KB** |

## Code Splitting
- Vendor chunk: React, ReactDOM, React Router
- Query chunk: TanStack Query
- Motion chunk: Framer Motion
- App chunk: All application code, lazy loading not implemented

## Caching
- Static assets: Immutable content hashing via Vite
- TanStack Query: 10-second stale time, 2 retries, no window refocus
- Health endpoint: 5-second polling interval
- Events: 10-second polling interval

## Server Impact
- Static files: Served by FastAPI/uvicorn (no CDN)
- Single process: No worker parallelization
- WSGI: Async via uvicorn (single event loop)

## Recommendations
1. Add CDN for static assets
2. Implement lazy loading for pages (`React.lazy`)
3. Add HTTP caching headers (`Cache-Control: public, immutable`)
4. Consider moving to uvicorn workers for production
5. Add compression middleware if not already handled
