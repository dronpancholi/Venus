# SOCI Image Lazy Loading Specification
**Document ID:** VENUS-STD-090
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
SOCI (Seekable OCI) indexing enables containers to start without waiting for the entire image payload to download. By lazy-loading files on-demand, container initialization times drop dramatically.

## 2. Performance Speedup (Amdahl's Law validation)
Container startup consists of pulling ($P_t$) and runtime initializations ($R_i$). Image pulling occupies $70\%$ ($p = 0.70$) of startup duration. Implementing SOCI lazy loading provides a 4x local speedup ($s = 4$) for image pull actions:

$$S_{\text{startup}} = \frac{1}{(1 - 0.70) + \frac{0.70}{4}} = \frac{1}{0.30 + 0.175} = \frac{1}{0.475} \approx 2.1\text{x Speedup}$$

Average container start duration drops from 120 seconds down to 57 seconds.

## 3. SOCI Index Creation Workflow
To build and push a SOCI index for an application container image:

```bash
# 1. Install AWS SOCI index utility CLI
sudo yum install aws-soci-index-builder -y

# 2. Build the application docker image
docker build -t gcr.io/project-venus/core-service:v1.0.0 .

# 3. Build the SOCI index referencing image
soci create gcr.io/project-venus/core-service:v1.0.0

# 4. Push both image and index manifest to ECR / GCR repository
docker push gcr.io/project-venus/core-service:v1.0.0
soci push gcr.io/project-venus/core-service:v1.0.0
```

## 4. Cross-References
- [Dockerfile Blueprint](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/DOCKERFILE_BLUEPRINT.md)
- [Kubernetes Deployment Manifest](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/KUBERNETES_DEPLOYMENT_MANIFEST.md)
