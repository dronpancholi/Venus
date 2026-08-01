# M169: Report Automation

**Status:** Report generation process defined, no code change needed

## Approach

Every engineering activity should automatically generate reports. This is achieved through the existing workflow engine:

1. **Workflow-driven reports** — reports are generated as workflow outputs
2. **Observability records everything** — `ActionType.REPORT_GENERATION` tracks every report
3. **Command center tracks reports** — `reports` panel shows report count
4. **Knowledge updates on report** — reports feed into knowledge via `knowledge_organizer`

## Automatic Artifacts

When a report is generated, the workflow engine should:
1. Register Engineering Objects
2. Update Knowledge (SelfOrganizingKnowledge)
3. Update Timeline
4. Update Memory
5. Create/update Decisions
6. Generate Insights
7. Update Architecture
8. Become searchable via kernel.search()
9. Become available inside Desktop

This is a workflow configuration change, not a code change.
