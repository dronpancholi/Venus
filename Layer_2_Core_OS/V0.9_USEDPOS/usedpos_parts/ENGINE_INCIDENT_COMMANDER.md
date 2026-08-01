# ENGINE — Incident Commander
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
The Incident Commander Engine is the AI-augmented brain of incident response. It coordinates detection, triage, investigation, communication, and resolution across all production incidents, applying the Incident Engineering protocol (Part 36).

---

## Activation Triggers
- PagerDuty / OpsGenie alert with severity SEV-0 or SEV-1
- Manual declaration by on-call engineer
- Automated anomaly detection exceeding threshold

---

## Command Functions

### Function 1: Incident Declaration
```
On activation:
  1. Generate unique incident ID: INC-{YYYYMMDD}-{N}
  2. Classify severity based on alert metadata + blast radius
  3. Create incident Slack channel: #inc-{date}-{short-title}
  4. Page primary on-call if not already engaged
  5. Page secondary on-call for SEV-0
  6. Start incident timeline document
  7. Set up incident bridge (Zoom/Meet)
  8. Post status page update if user-facing
```

### Function 2: Real-Time Context Assembly
Automatically gather and summarize:
```
What changed recently?
  - Last 5 deployments (service, version, time, engineer)
  - Configuration changes in last 24 hours
  - Infrastructure changes in last 24 hours

What do metrics show?
  - Error rate: current vs baseline (Δ%)
  - Latency p95/p99: current vs baseline
  - Traffic volume: current vs baseline
  - Key service health: up/down/degraded

What do traces show?
  - Top 5 slowest traces in last 5 minutes
  - Top 5 most error-prone endpoints
  - Downstream dependency errors

Auto-generated summary posted to incident channel within 2 minutes of activation.
```

### Function 3: Investigation Guidance
```
Systematic investigation checklist posted to incident channel:

Phase 1 — Impact Assessment (0-5 min):
  [ ] What services are affected?
  [ ] How many users impacted? (error rate × traffic volume)
  [ ] Is data loss occurring?
  [ ] Is there a security dimension?

Phase 2 — Root Cause Hypothesis (5-15 min):
  [ ] Correlate with recent changes
  [ ] Check upstream dependencies
  [ ] Check database performance
  [ ] Check infrastructure health (CPU, memory, disk)
  [ ] Review error log samples

Phase 3 — Mitigation (parallel with investigation):
  [ ] Feature flag disable viable?
  [ ] Traffic rerouting viable?
  [ ] Rollback viable and safe?
  [ ] Scale up viable?
```

### Function 4: Stakeholder Communication
Automatically draft and send on schedule:
```
T+0:    Initial "Investigating" status (internal + status page if user-facing)
T+30:   Update #1 — "Root cause identified / still investigating"
T+60:   Update #2 — "Mitigation in progress"
T+Resolved: Resolution notification with timeline
```

Communication templates populated with:
- Affected services
- User impact description
- Current status
- Next update time
- Workarounds if available

### Function 5: Post-Incident Automation
After incident resolved:
```
  1. Generate incident timeline from channel messages + alert timestamps
  2. Pre-populate post-mortem document template
  3. Schedule post-mortem meeting within 48 hours
  4. Extract action items from incident discussion
  5. Create follow-up tickets with owners and due dates
  6. Update incident metrics database
  7. Publish internal incident report
```

---

## MTTD/MTTA/MTTR Tracking
Every incident recorded with:
- Detection time (alert timestamp)
- Acknowledge time (first engineer response)
- Mitigation time (user impact reduced)
- Resolution time (full recovery)
- Contributing factors
- Action items generated

Trends reported weekly to engineering leadership.
