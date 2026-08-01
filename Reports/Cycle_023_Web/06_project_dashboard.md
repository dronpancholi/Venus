# Project Dashboard

## Home Page (`/`)
- Platform branding with Genesis logo
- 4 stat cards: Status, Services, Messages, Sessions
- Quick Actions grid (6 actions with shortcuts)
- Recent Activity section showing imported project watchers
- Active Tasks section

## Dashboard (`/desktop`, `/app`, `/dashboard`)
- 6 stat cards: Status, Services, Executions, Messages, Sessions, Storage
- Projects list with change/scan counts
- AI Activity section with agent/conversation status
- System Metrics display

## Project View (`/project/:name`)
- Back navigation to previous page
- 4 stat cards: Status, Scans, Changes, Last Scan
- Recent Events section (last 10 events)
- Active Tasks section

## Knowledge (`/knowledge`)
- Search input for knowledge catalog
- Knowledge Catalog list (imported projects)
- Knowledge Events feed
- Search Results display

## Timeline (`/timeline`)
- 3 stat cards: Events, Audit Entries, Uptime
- Combined Activity Log (events + audit entries, reverse chronological)
- Timeline dot visualization with color-coded categories

## Data Refresh
- Health: 5s polling
- Events: 10s polling
- Other: 10s stale time with background refetch
