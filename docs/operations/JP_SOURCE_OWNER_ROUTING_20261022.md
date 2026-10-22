# JP private normalized data sources — P2 completed 2026-10-22

## Canonical architecture
Use the private JP Project Map Master v1.2 `_SOURCE_ROUTER` for current source identifiers. All 14 map data tabs are read-only direct `IMPORTRANGE` projections of exactly FOUR private owner workbooks in `JP__ENTERPRISE__PRIVATE/JP__NORMALIZED_AUTHORITIES__PRIVATE`.

| Owner | Version | Editable authoritative tables |
|---|---|---|
| People | v1.1 | `people` plus separate private `person_roles` |
| Projects & Locations | v1.2 | `projects`, `project_parties`, `project_funding`, `project_work_items`, `project_material_inventory`, `project_components`, `project_source_links`, `project_opportunities`, `project_publication_settings`; derived `project_locations` view |
| Organizations | v1.1 | `organizations`, `organization_locations` |
| Work Catalog | v1.2 | `work_catalog`, `materials_master` |

The JP master has 14 data sheets, and only `_CONTROL_READ_FIRST` and `_SOURCE_ROUTER` as additional control tabs. There are 188 records in private source tables (including 23 private people identities); the separately reviewed public map JSON has NOT been republished merely by this change.

## QA and archives
- Nine previously local tables moved to the owning tabs; no nine new workbooks. One temporary Materials workbook was not used, and was moved into the private archive instead.
- Source cell content vs master imported view: 14 of 14 matched. Primary IDs unique; 10 project/work/material/organization FK constraints verified.
- Master and Projects v1.1 checkpoint copies were made in the private JP release archive before the move. Live Drive IDs and company project file locations remain unchanged.
- The company folder `03_Fishtail_Builders` has its own `00_JP_CANONICAL_DATA_POINTER__READ_FIRST__FISHTAIL` Google Doc.
- The sister folder `04_Rohini_Engineering_and_Builders` has its own `00_JP_CANONICAL_DATA_POINTER__READ_FIRST__ROHINI` Google Doc.
- Neither pointer duplicates data, grants access to the private master, or moves documents out of company folders. JP is operational authority; AEC thesis is separate research.

## P1 People roster-only privacy hardening: pending
Chaudhary attendance v2.6 currently imports private People columns A:C directly into hidden `4_JP_PEOPLE_IMPORT`; 23 names are linked and 14 recorded man-days remain unchanged. Shared attendance editors may be able to import other People workbook ranges after the destination is granted IMPORTRANGE access. Safer design: maintain a separate roster-only publication source with only worker code, display name and active flag, populated by a scope-limited script/service identity that reads the private People master. Repoint attendance to roster-only, verify the 23 matches and attendance totals, and audit permissions. IMPORTANT: deleting a direct IMPORTRANGE formula does NOT automatically revoke its earlier source-wide connection. Per Google's documented behavior, access persists until the user who granted it is removed from the source. Since that grantor may be the People owner, do not remove them casually. Do not place confidential attributes into the previously connected People source; plan an explicit source rotation or move restricted attributes into a separate never-imported private workbook before treating the privacy boundary as secure. Merely hiding the roles tab is NOT a security boundary.

## Next roadmap
1. P1: secure People-to-attendance link via restricted roster projection.
2. P3: verify roles, unverified amounts/units, site inventory, coordinates and contractor/legal relationships from authorized evidence.
3. P5: Gemini-safe edit controls, locked schema/PK/FK, validation and audit.
4. P4: reviewed private-to-public projection and GitHub Pages deployment automation, no private personnel or finance leaks.

## AI editing rules
Edit only one named owner tab and range. Never modify imported JP master cells, change stable PK/FK IDs, sort a single column separately, infer unrecorded attendance as absent, fill unsupported project quantities, or publish confidential information. Revalidate if any table reaches the current 500-row IMPORTRANGE limit.

## Per-work operation files and A9 hierarchy (2026-10-22)
Existing shared `A9_Fabin_Gurung/01_JP` now contains the relocated folders `03_Fishtail_Builders` and `04_Rohini_Engineering_and_Builders` (same IDs and collaborator permissions). Company documents and existing pointer Docs remain in those original folder objects. A new read-first pointer in `01_JP` links to the separate owner-only JP enterprise authority. DO NOT move private JP personnel/financial masters underneath shared `01_JP`, which has broader writers.

The canonical Work Catalog now has a `work_sheet_registry` for all 29 existing `WRK-000001` through `WRK-000029` work IDs. Its registry links 29 individual v0.1 operational Google Sheets, grouped in one private JP folder. Each has `00_MANIFEST` (catalog-derived ID/name/category/default unit/status), `01_WORK_RECORDS` (project/date/location/report/verification fields and formula-derived work_id) and compulsory `02_HOW_TO` (source, safety and Gemini rules). An original reusable work template exists in the folder. The Work Catalog is the single editable authority for definitions; operational entries in these individual files are not automatically imported into the central `project_work_items` map table or public GitHub JSON. Empty work-entry tables do not indicate zero completed work. If source work descriptions are changed in the catalog, update the copied manifest attributes deliberately; new broad `IMPORTRANGE` chains were intentionally avoided.

P1 still requires actual personnel isolation: Google's source-wide `IMPORTRANGE` authorization in shared Chaudhary attendance permits other source ranges to be requested by shared editors, even though the current formula imports only IDs/names. Merely creating a roster-only file and deleting the existing import does not automatically revoke the previous grant. Keep restricted People attributes separate until a verified permission revocation/source-rotation approach is executed.
