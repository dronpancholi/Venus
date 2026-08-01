# Docker Compose Development Specification
**Document ID:** VENUS-STD-077
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Purpose
This document provides a standard Docker Compose configuration file for local development, enabling developers to spin up the core service stack along with required data layers.

## 2. Docker Compose File Template (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  # Application Container API
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: builder # Runs hot-reloading development stage if configured
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=development
      - PORT=8080
      - DATABASE_URL=postgresql://postgres:postgres_secure@db:5432/venus_dev
      - REDIS_URL=redis://cache:6379/0
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy

  # Database Service Layer
  db:
    image: postgres:15-alpine
    container_name: venus-postgres-dev
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres_secure
      - POSTGRES_DB=venus_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d venus_dev"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Caching layer Service
  cache:
    image: redis:7-alpine
    container_name: venus-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3

  # Mail mock handler
  mailhog:
    image: mailhog/mailhog
    container_name: venus-mailhog-dev
    ports:
      - "8025:8025" # UI Dashboard port
      - "1025:1025" # SMTP server port

volumes:
  postgres_data:
  redis_data:
```

## 3. Operational Command Guide
*   **Startup Service:** `docker compose up -d`
*   **Teardown Service (destroy volumes):** `docker compose down -v`
*   **Access Database Console:** `docker exec -it venus-postgres-dev psql -U postgres -d venus_dev`
*   **View Real-Time Logs:** `docker compose logs -f api`

## 4. Cross-References
- [Dockerfile Blueprint](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/DOCKERFILE_BLUEPRINT.md)
