# Tool Sandboxing Policy (Project Venus V0.8)

## 1. Sandbox Architecture
This policy defines standard isolation mechanisms and container constraints for tools executed under the Venus Enterprise Agent runtime. The objective is to secure the host environment against remote code execution (RCE) and local privilege escalation.

```mermaid
graph LR
    subgraph Host OS (VPC)
        subgraph gVisor Sandbox Boundary
            A[Exec Daemon] --> B[Tool Process]
        end
    end
    B -->|Blocked System Call| C{Filter check}
    C -->|Allowed| D[Host Kernel]
    C -->|Blocked / Logged| E[Security Alarm]
```

---

## 2. Sandboxing Isolation Levels

### 2.1 Level A: High-Security WebAssembly (Wasm) Isolation
*   *Implementation:* Wasmtime / Wasmer Runtime.
*   *Application:* Mathematical calculations, data formatting, simple parsers.
*   *Properties:* Zero access to host filesystem, network, or process IDs. Shared memory bounds are explicitly pre-allocated:

$$\text{Memory Bounds} \le 128 \text{ MB}$$

### 2.2 Level B: gVisor / Firecracker Container Isolation
*   *Implementation:* Docker / Containerd with `runsc` (gVisor) runtime handler.
*   *Application:* Code execution engines (Python interpreter, Node runtime), SQLite database lookups.
*   *Properties:* Intercepts all system calls via a user-space proxy kernel ("Sentry"), separating container execution from the host kernel.

---

## 3. Resource Bounds and Hard Limits

| Resource Parameter | Sandboxed Containers (gVisor) | WebAssembly RunTime (Wasm) | Enforcement Action |
| :--- | :--- | :--- | :--- |
| **Max CPU Limit** | $0.5$ vCPU (shares) | $0.1$ vCPU equivalent | Hard throttle / scale-down |
| **Max Memory Allocation**| $256\text{ MB}$ | $128\text{ MB}$ | Out-Of-Memory (OOM) Kill |
| **Ephemeral Disk Space** | $50\text{ MB}$ (read-only base) | $0\text{ MB}$ (in-memory only) | Disk IO error |
| **Execution Timeout** | $5000\text{ ms}$ | $1000\text{ ms}$ | Process Terminate (SIGKILL) |
| **Network Egress** | Disabled (unless whitelisted) | Completely Disabled | Socket rejection |

---

## 4. System Calls Whitelist (gVisor/Linux)
Only the following system calls are allowed for running execution engines:
*   `read`, `write` (file descriptor handling limited to standard streams `/dev/stdout` and `/dev/stderr`).
*   `futex`, `exit_group` (process control and standard garbage collection handling).
*   `clock_gettime` (system clock query).
*   *Blocked System Calls:* `execve`, `fork`, `clone`, `socket`, `bind`, `listen`.

---

## 5. Verification Checks
To verify that a sandbox remains intact:
1.  **Readiness Probe:** Prior to task execution, a lightweight verification container runs a test script to query the host kernel. If it detects direct host access, it triggers a system shutdown.
2.  **Auditd Monitor:** System-level auditing tools check file system write permissions. Write activities to any directory except `/tmp` generate a security event.

---

## 6. Cross-References
*   The schema validation rules are governed by [TOOL_SCHEMA_DEFINITION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/TOOL_SCHEMA_DEFINITION.md).
*   Authorization tokens mapping execution levels are detailed in [MCP_SECURITY_POLICY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/MCP_SECURITY_POLICY.md).
*   Recovery routing for blocked execution timeouts is governed by [TOOL_FALLBACK_CIRCUIT_BREAKER.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/TOOL_FALLBACK_CIRCUIT_BREAKER.md).
