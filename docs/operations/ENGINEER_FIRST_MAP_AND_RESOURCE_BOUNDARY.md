# Engineer-first site maps and Astam ownership

**Decision recorded:** 11 November 2026. Operations main in SHEETS_V2 mode owns site maps, reviewed instructions and public reported work; Field & Desk Library owns project resources, land buyer references and documents.

## Five map views — one shared set of approved locations
The five switches on the same Leaflet map are **Sites, Work, Materials & plant, Manpower, Instructions**. They share the current public project filter, organization filter and approved coordinates. A project card opens its underlying published counts and source qualification.

This is a **read-only operational triage interface**, not an independent site task, labour or inventory database.

| Layer | Current pin meaning | Data authority | Current coverage |
| --- | --- | --- | --- |
| Sites | Published project location; project status if visibility approved | Projects and Locations + Website Display Choices | 29 public listings; 28 approved pins at recent readback |
| Work | Count of public `Project Work` report entries, **not remaining uncompleted tasks** | Project Work workbook | Three public reports in latest source build |
| Materials & plant | `?` = demand unknown, no verified site shortage feed | Future approved Field & Desk requisition/plant register | Not connected; do not show fake zero |
| Manpower | `?` = crew demand unknown, no individual attendance or payroll | Future approved workforce demand source, resource publisher keeps private records | Not connected; do not infer labour need |
| Instructions | Reviewed notices per project; count is **not confirmed open work** | Message Sources + Notification Center Instructions | 22 reviewed notices in latest source build |

When approved and published in future, workforce/material/plant shortage signals will need stable `project_id`, request ID, `resource_kind`, approved quantity/unit if publicly allowed, urgency, verification/approval status, recorded-as-of time, and source owner. The map can then highlight confirmed shortages; it must never infer urgency from silence.

Work backlog counts will require issued `work_id`, open/done/blocked status and source-version controls from the Scheduling / Project Work owner. Do not derive remaining tasks from a generic current work report count or raw Slack text.

## Mobile field workflow
At phone widths, show the purpose and map first, then tap one of five source-qualified layers. Use the shared site search/dropdown and open a selected project for recorded context. Previous four publication counters move into a collapsed audit summary. No status is silently escalated to an emergency, and no personal payroll record is exposed.

## Astam land feasibility — transferred to Resource Library
The **canonical published home** is:
- https://fabingurung.github.io/jp-field-desk-library/feasibility/
- https://fabingurung.github.io/jp-field-desk-library/feasibility/buyer-guide/

Library v1.4.0 release was built and verified from previously public-safe Operations assets. The old Operations project page, guide, guide.json and two public derived source files were deleted from Operations **Git HEAD** after that release. Their exact historical bytes remain recoverable at immutable Operations revision `066beb324c46884ae74eed129b01d064b3ba1854` via Git history. Original private Drive authorities were neither moved nor modified.

Operations now publishes only old-route compatibility redirects at `/feasibility/` and `/feasibility/buyer-guide/`, forwarding original query parameters. Static JSON subpaths are no longer duplicated at Operations Pages; future consumers must use canonical Library resource URLs. Shared historical CSS and botanical assets may remain in Git as pre-existing general-purpose site assets but are not re-published by this Sheets-only dashboard.

## Original source and governance
The five Operations publisher Sheets remain unchanged and are read with previously approved Google WIF. The Library has its own workbook and publishing workflow. The repository's `A7_MODULE.json` and `ops/control/branch-lane-registry.json` update the canonical GitHub slug without altering stable provider object ID `1312147922`.

## Source limitations / next work
- Real equipment/material requisitions and crew demands are not yet connected.
- Confirmed open construction task/backlog/critical path not yet connected.
- Unresolved instructions cannot be distinguished from historical reviewed notices with current published columns.
- No engineer-certified progress is inferred.
- Source correction/tombstone and dated provider-freshness lifecycle remains in Operations issue #30.
