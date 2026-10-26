# Single-subject Sheets and human navigation — 26 October 2026

The four shared mixed workbooks contained duplicate subject tables. Fourteen separate source owners now hold the core map subjects, with readable headings, native tables, manifests and in-workbook history. Their initial publishing assembly passed source/master readback before duplicate legacy tabs were retired. Source IDs were preserved; complete PRE workbooks remain in dedicated central archive folders.

Projects retain their ward and coordinates in the same project row. The company location files now point to company-filtered views of that shared source, rather than maintaining competing coordinate copies. People contains people only; roles and assignments were copied to a dedicated source after parity verification.

Project Resources has a dedicated 46-row source and a publishing replica. A document slot is separate from file format: architectural, structural, combined architectural/structural, analysis model, 3D model, estimates/calculations, supporting files and source folders. PDF, DXF, DWG, E2K, EDB and SKP are supported. The public catalog keeps its existing reviewed IDs and URLs. No new resource or engineering approval is implied.

Operational changes reuse existing owners. Company Project Site Issues is under Daily Checklist. Manpower Team Attendance covers contractors generally. Both company inventories use a general materials movement table; 13 Fishtail and 3 Rohini entered consumption cells were retained with original dates and source-cell provenance. Opening stock and current balance are not inferred. Paras Pariyar and Shiv Narayan Chaudhary have separate attendance and expense workbooks. Existing company contact sources still feed their combined contact view. Existing daily-progress hubs are reused; Discord/Slack extraction remains deferred.

Developer Workspace retains active testing and backlog links. Durable architecture, control, repository and version references moved to Memory Poster Board, which now has a complete contents list and return links. Historical collector posters remain preserved and explicitly inactive.

The private publishing workbook's `00_SOURCE_DIRECTORY` links the 31 relevant subjects/views. It is the human directory; code-only contracts remain in GitHub.

## Actual publishing status

- The 14 core tables and Project Resources were initially assembled with the connected Sheets API, and read back successfully.
- GitHub Actions now understands readable headings and copies Project Resources into the same validated JSON bundle used by the map and Desk Resources.
- No Google identity is configured for Actions yet. Deployments use the reviewed snapshot and display an explicit workflow warning. The initial API assembly must not be described as an automatic Actions refresh.
- Configure workload identity provider plus service-account repository variables, or the existing dedicated credentials secret, then run the workflow with `require_live_sheets=true`. Share source Sheets read-only with that dedicated identity, and the publishing workbook and its existing history file with the required write access. Never copy connector OAuth into GitHub.
- Colab V8 has not been executed. It refreshes the inventory and improves archive/history handling; it does not establish Actions authentication or publish Pages. Earlier versions do not need to be run first.

## Limits

The map and Desk Resource publishing inputs have concrete native owners and joined replicas. Other historical public page projections remain reviewed snapshots while their full Sheet-to-page migration is reconciled. This release does not claim every historical website fact has already been migrated. Intake Staging is excluded. No collector was restarted, no sharing permissions were changed and no original engineering file was renamed or moved.

## Verification

Native source, publishing-copy, record-count and control readbacks; offline publishing integration tests; public-projection privacy checks; browser checks for Field filtering, Desk Resources, Workspace and all Memory contents anchors. Native Sheets browser presentation could not be inspected because this browser requires Google sign-in; connector formatting/table metadata and values were verified instead.
