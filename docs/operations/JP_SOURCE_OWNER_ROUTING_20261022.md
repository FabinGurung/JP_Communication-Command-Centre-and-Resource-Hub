# JP Google Sheets release and source routing — 2026-10-22

## Live architecture
- **Four owner workbooks** hold editable source facts: People, Projects & Locations, Organizations, Work Catalog. They are each `v1.1__LIVE` on their unchanged Google Drive file IDs. Use the private JP master's `_SOURCE_ROUTER` for the current source links.
- **JP Project Map Master `v1.1__LIVE`** keeps 14 map data schemas. Its five `people`, `projects`, `organizations`, `organization_locations`, and `work_catalog` tabs are direct `IMPORTRANGE` mirrors; these import connections work. The other nine map tables still live in the JP master and have not been assigned new owner workbooks.
- **Chaudhary Team Attendance `v2.6__LIVE`** keeps `1_MANIFEST_INDEX` and the two project attendance tabs visible; hidden `4_JP_PEOPLE_IMPORT` pulls only person ID/code/display name from the People owner. The roster names `B19:B41` use worker-code lookup, now resolving without a fallback. Recorded attendance: 14 man-days, 153 project dates, 23 roster identities, two site tabs.
- Google Sheets import updates are not instantaneous and never auto-publish the private content to the public GitHub Pages JSON snapshots.

## Completed release and recovery
On 2026-10-22, six complete previous-version native Google Sheets files were copied into [owner-only JP Sheets release archive](https://drive.google.com/drive/folders/1W7ebW5Yn9TFNaEXGoUIK5QHpL-bN62Fw) **before** live cleanup. The archived JP master five imports and archived attendance People import were frozen to their then-visible historical cell values. Existing live file IDs, sharing, and document links were not changed by the v1.1/v2.6 rename.

Removed from live: five hidden `__ROLLBACK_*` tabs and redundant `_AUTHORIZE_IMPORTS` in JP master; `4_PERSON_ID_MAPPING` and `_ROSTER_NAMES_ROLLBACK_20261022` in attendance. After checks, the hidden operational People import tab was renamed `4_JP_PEOPLE_IMPORT`. Kept: `_CONTROL_READ_FIRST`, `_SOURCE_ROUTER`, owner `_READ_FIRST`, and all fourteen needed relational schemas. Do not delete a currently blank tab just because there are zero rows: the map schema loads fourteen projections.

## Outstanding work / roadmap
1. **Data-integrity and permissions hardening:** audit shared attendance editors' access to private People source before adding payroll, banking, identity, phone or sensitive fields. Google `IMPORTRANGE` permission is source-workbook-wide for any destination editor, not range-limited. If adding restricted fields, introduce a purpose-built roster-only projection instead of keeping them in the imported People source.
2. **Owner normalization — next stage:** partition remaining relational tables (project parties, funding, per-project work items, materials, inventory, components, source links, opportunities, publication settings) in controlled batches only, preserving current primary/foreign IDs and source evidence.
3. **Public publication pipeline:** add a provider-backed controlled refresh with PK/FK, source freshness, access flags and privacy review before GitHub JSON deployment; avoid directly exposing private Sheets on Pages.
4. **Data quality:** verify worker roles and assignments, missing BOQ units and project work quantities, and project/organization coordinates with owner evidence. Never infer engineering approval from field reports.
5. **Maintenance:** validate the 23 worker names, attendance counts, owner imports and five master mirrors after edits; review and tag a stable Sheets release when materially changed.

## Gemini editing guardrails
- Only edit the **named owner tab** and requested cell range. Never edit the JP master import spill ranges, or the attendance import helper.
- Never delete or rename schema tabs, IDs or join columns, or sort one column without sorting whole records.
- Never fill blank attendance as `ABSENT`; blank means **UNRECORDED**. No bulk human approval or fabricated quantities.
- `projects` holds editable project coordinates; `project_locations` is derived. `work_catalog` defines names only, not completed quantities. `people` holds identity names; `person_roles` stores verified role assertions separately.
- Review Gemini's proposed edits and affected range before applying. Use native Sheets version history and the external archive for rollback. Avoid putting private IDs/names in unreviewed public GitHub files.
- Adding more than 500 source rows may exceed the configured `IMPORTRANGE` capture ranges: extend ranges and revalidate intentionally.
