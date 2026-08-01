# USPTCROS Container Image Base Hardening Standard
**Document Link:** [Container Image Base Hardening](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CONTAINER_IMAGE_BASE_HARDENING.md)  
**References:** [Container Sandbox gVisor Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CONTAINER_SANDBOX_GVISOR_SPEC.md)

## 1. Secure Container Packaging Standards
* **Distroless Base Images:** Workload containers must use Google Distroless or Alpine Minimal base packages. General Linux distributions (Ubuntu, Debian) are blocked.
* **Non-Root Execution:** Workload execution users must use explicitly defined UID 10001 or greater. UID 0 (root) execution is disabled.
* **Multi-Stage Builds:** Separate build dependencies from runtime environments.

## 2. Hardened Multi-Stage Dockerfile Pattern
```dockerfile
# Stage 1: Build compilation environment
FROM golang:1.20-alpine AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/venus-engine main.go

# Stage 2: Runtime packaging
FROM gcr.io/distroless/static-debian11:nonroot
COPY --from=builder /app/venus-engine /bin/venus-engine
USER 65532:65532
ENTRYPOINT ["/bin/venus-engine"]
```
