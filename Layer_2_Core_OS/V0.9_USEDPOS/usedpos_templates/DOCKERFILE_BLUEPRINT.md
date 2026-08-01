# Dockerfile Blueprint for Node.js Applications
**Document ID:** VENUS-STD-076
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This document defines a production-ready, secure, multi-stage Dockerfile for Node.js/TypeScript applications, enforcing minimum size overhead and low attack surface.

## 2. Multi-Stage Dockerfile Template
Put this file (`Dockerfile`) in the root of the application directory:

```dockerfile
# ==========================================================
# Stage 1: Build Environment
# ==========================================================
FROM node:20.11-alpine AS builder

# Set build directory
WORKDIR /usr/src/app

# Copy dependency specifications
COPY package*.json tsconfig.json ./

# Install all dependencies (including devDependencies)
RUN npm ci

# Copy application source files
COPY src/ ./src

# Build TypeScript to production JavaScript (output to dist/)
RUN npm run build

# Remove development dependencies to keep build directory clean
RUN npm prune --production

# ==========================================================
# Stage 2: Production Runtime Environment
# ==========================================================
FROM node:20.11-alpine AS runner

# Establish production environment variable
ENV NODE_ENV=production
PORT=8080

WORKDIR /app

# Copy production node_modules from Stage 1
COPY --from=builder /usr/src/app/node_modules ./node_modules
# Copy built assets
COPY --from=builder /usr/src/app/dist ./dist
COPY --from=builder /usr/src/app/package*.json ./

# Create a non-privileged system user/group to execute application code
RUN addgroup -g 1001 -S nodejs &&     adduser -u 1001 -S nodejs -G nodejs &&     chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

# Expose target application port
EXPOSE 8080

# Configure health check interface
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3   CMD wget --no-verbose --tries=1 --spider http://localhost:8080/healthz || exit 1

# Execute runtime process
CMD ["node", "dist/index.js"]
```

## 3. Docker Build and Run Instructions
To build and execute the container image locally:

```bash
# Build the image using proper tagging
docker build -t venus/core-service:v1.0.0 .

# Run the container mapping ports and injecting ENV variables
docker run -d   -p 8888:8080   --name core-service-runtime   --env DATABASE_URL="postgresql://user:pass@host:5432/db"   venus/core-service:v1.0.0
```

## 4. Cross-References
- [Docker Compose Development Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/DOCKER_COMPOSE_DEVELOPMENT_SPEC.md)
- [Kubernetes Deployment Manifest](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/KUBERNETES_DEPLOYMENT_MANIFEST.md)
