# EDR-002: Atlas–OmegaLoop Feedback Loop

**Status:** Implemented
**Date:** 2025-06-28

## Problem

Atlas and OmegaLoop operated as independent execution engines with no
cross-awareness. Atlas analyzed the repository, identified architectural
problems, generated roadmaps — and wrote its findings to `_generated/atlas/`.
OmegaLoop executed the 18-Book constitution, computed metrics, generated
roadmaps — never reading Atlas outputs. The feedback loop was entirely
manual: a human architect needed to read Atlas findings and manually
translate them into OmegaLoop priorities.

## Context

Atlas produces 15 stages of analysis per run, including: subsystem profiles,
architectural boundaries, capability inventory, problem discovery (6 problems
identified), engineering designs (5 solutions), architectural simulations,
benchmarks, and a prioritized roadmap. OmegaLoop's Book XII (Self Evolution)
was generating roadmaps from iteration-phase deliverables only (duplicate
abstractions, debt, experiments, contracts). These are operational metrics,
not architectural insights.

## Evidence

- Atlas identified P1 (OmegaLoop coupling) as high-severity — something
  OmegaLoop's internal metrics would never detect
- Atlas found 2 high-severity and 3 medium-severity problems across the
  entire repository
- OmegaLoop's `_phase_13_self_evolution` had no mechanism to read external
  analysis
- Both engines share the same filesystem — file-based IPC is feasible

## Chosen Solution

Add `_read_atlas_findings()` to OmegaLoop that scans `_generated/atlas/run_*`
(sorted by mtime, newest first) and reads structured JSON outputs. Update
`_phase_13_self_evolution` to prepend Atlas findings (tagged `[ATLAS]`) to
the self-evolution roadmap.

## Migration Impact

Zero. Fallback preserves prior behavior if Atlas hasn't been run.

## Expected Lifetime

Indefinite. This is the bridge between analysis and execution autonomy.
