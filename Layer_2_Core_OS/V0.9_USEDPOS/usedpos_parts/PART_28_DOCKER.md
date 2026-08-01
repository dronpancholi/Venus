# Part 28: Docker

## 1. Context & Strategy
Docker under Project Venus defines the standards for application containerization. Our container strategy mandates minimized image sizes, multi-stage builds, non-root user execution, explicit image tagging, caching optimizations, and vulnerability scanning. All software must run inside secure, reproducible container environments.

---

## 2. Container Mathematical Overhead & Layer Models

### 2.1 Container Size Overhead Index
To optimize transmission bandwidth and node start times, base operating system overhead must be minimized. The Size Overhead ratio ($O$) compares the total image size ($S_{img}$) to the compiled application binary/runtime size ($S_{bin}$):

$$O = \frac{S_{img} - S_{bin}}{S_{bin}}$$

*   *Standard*: Multi-stage container builds target $O \le 1.5$ (e.g., for a $20\text{ MB}$ Go binary, the final image size should not exceed $50\text{ MB}$).

### 2.2 Security Attack Surface Reduction Calculation
Each installed package in a container image increases the probability of a CVE vulnerability. The relative exposure index ($E_{image}$) is modeled as:

$$E_{image} = \sum_{i=1}^{P} W_i$$

Where:
*   $P$: Total count of installed binary packages.
*   $W_i$: Weighted vulnerability score of package $i$ based on historic CVSS trends.
*   *Application*: Standardizing on `distroless` or `scratch` bases reduces $P$ from $\approx 400$ (standard Debian/Alpine containing package managers and shell interpreters) to near $\approx 10$, significantly reducing vulnerability density.

---

## 3. Container Configuration Standards

### 3.1 Go Multi-Stage Dockerfile Blueprint
All compilation-based systems must build inside a builder container and run on minimal bases.

```dockerfile
# syntax=docker/dockerfile:1.4
# Stage 1: Compiler base
FROM golang:1.20-alpine AS builder
WORKDIR /src
RUN apk add --no-cache git ca-certificates
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod/ \
    go mod download
COPY . .
RUN --mount=type=cache,target=/go/pkg/mod/ \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o /bin/app ./cmd/main.go

# Stage 2: Distroless runner
FROM gcr.io/distroless/static-debian11:nonroot
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /bin/app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

### 3.2 Container Image Label Schema (OCI Standard)
Every built container image must declare standardized build metadata:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DockerImageLabels",
  "type": "object",
  "properties": {
    "org.opencontainers.image.title": { "type": "string" },
    "org.opencontainers.image.version": { "type": "string" },
    "org.opencontainers.image.revision": { "type": "string" },
    "org.opencontainers.image.vendor": { "type": "string" },
    "org.opencontainers.image.licenses": { "type": "string" }
  },
  "required": [
    "org.opencontainers.image.title",
    "org.opencontainers.image.version",
    "org.opencontainers.image.revision"
  ]
}
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that no container image executes processes as the `root` user.
*   [ ] Verified multi-stage builds are implemented to avoid leaving compilers inside final images.
*   [ ] Confirmed docker layer caching mechanisms (`--mount=type=cache`) are active in pipelines.
*   [ ] Verified that image bases are pinned to explicit SHA hashes rather than mutable tags (`latest`).
*   [ ] Confirmed security scanners (e.g., `trivy`) report zero Critical/High CVEs.
