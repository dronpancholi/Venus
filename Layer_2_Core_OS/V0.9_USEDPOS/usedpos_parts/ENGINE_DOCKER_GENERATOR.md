# ENGINE — Docker Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates optimized, security-hardened Dockerfiles and docker-compose configurations for any service. Applies multi-stage builds, minimal base images, layer caching, non-root execution, and all VENUS containerization standards.

---

## Input Requirements
```
Required:
  - Runtime language and version (Node 20, Python 3.12, Go 1.22)
  - Application entry point
  - Port configuration
  - Environment variables list

Optional:
  - Build tool requirements (pnpm, poetry, cargo)
  - Static asset serving requirements
  - Multi-arch requirements (amd64 + arm64)
  - Health check configuration
```

---

## Generated Dockerfile (TypeScript/Node.js)
```dockerfile
# syntax=docker/dockerfile:1.7
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
RUN apk add --no-cache libc6-compat
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile --prod=false

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# Stage 3: Production Dependencies Only
FROM node:20-alpine AS prod-deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile --prod=true

# Stage 4: Production Runner
FROM node:20-alpine AS runner
WORKDIR /app

# Security: non-root user
RUN addgroup --system --gid 1001 nodejs \
  && adduser --system --uid 1001 appuser

# Copy only production artifacts
COPY --from=builder --chown=appuser:nodejs /app/dist ./dist
COPY --from=prod-deps --chown=appuser:nodejs /app/node_modules ./node_modules
COPY --chown=appuser:nodejs package.json .

USER appuser

EXPOSE 3000
ENV NODE_ENV=production
ENV PORT=3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

ENTRYPOINT ["node", "dist/main.js"]
```

---

## Generated docker-compose.yml (Local Dev)
```yaml
# docker-compose.yml
version: "3.9"
services:
  app:
    build:
      context: .
      target: builder
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: pnpm dev

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
```

---

## Security Hardening Applied
- Non-root user execution (UID 1001)
- Minimal base image (Alpine Linux)
- Multi-stage build (no dev dependencies in final image)
- No secrets in image layers
- Read-only filesystem where possible
- HEALTHCHECK instruction always present
- `--no-cache` for package manager installs
- `.dockerignore` generated to exclude unnecessary files
