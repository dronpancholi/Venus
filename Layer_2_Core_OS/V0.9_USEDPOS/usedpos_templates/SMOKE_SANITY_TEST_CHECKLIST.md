# Smoke and Sanity Testing Checklist
**Document ID:** VENUS-STD-072
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
Smoke tests are executed immediately after any environment deployment to ensure the platform components are online, routing traffic, and capable of performing basic operational processes.

## 2. Automated Smoke Verification Script (Bash + cURL)
The following script is bundled in CI/CD pipelines to verify health checks:

```bash
#!/usr/bin/env bash
set -eo pipefail

TARGET_ENV_HOST=${1:-"https://staging.venus.internal"}
echo "Executing Smoke Sanity Checks on: ${TARGET_ENV_HOST}"

declare -a ENDPOINTS=(
  "/healthz"
  "/metrics"
  "/v1/info"
)

for endpoint in "${ENDPOINTS[@]}"; do
  url="${TARGET_ENV_HOST}${endpoint}"
  echo -n "Checking: ${url} ... "
  
  response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${url}")
  
  if [ "${response_code}" -eq 200 ]; then
    echo "OK (200)"
  else
    echo "FAILED (${response_code})"
    exit 1
  fi
done

echo "All baseline smoke tests passed successfully."
```

## 3. Manual Inspection Checklist

| Step | Action Item | Expected Behavior | Verify Method |
| :--- | :--- | :--- | :--- |
| **1** | Navigate to UI homepage | CSS loads, no JS console errors. | Browser developer tools console. |
| **2** | Submit Test Login | Token is returned, redirected to dashboard. | Mock user credential entry. |
| **3** | Fetch API health status | Response JSON shows database `UP` status. | `GET /healthz` check dependencies field. |
| **4** | Check Log Stream | No error stacks or PANIC lines in logger. | View cloud console logs (Splunk/Datadog). |

## 4. Cross-References
- [QA Automation Suite Runbook](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/QA_AUTOMATION_SUITE_RUNBOOK.md)
- [Release Readiness Checklist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/RELEASE_READINESS_CHECKLIST.md)
