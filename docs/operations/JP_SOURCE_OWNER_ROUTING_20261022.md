# JP enterprise source ownership — four-workbook partition (2026-10-22)

## Purpose and privacy
The JP enterprise map private Google Sheet remains the **read-only consolidation point**. Four private owner spreadsheets contain the editable facts for (1) People, (2) Projects & Locations, (3) Organizations and office locations, and (4) Work Catalog. Open the existing private master and read `_SOURCE_ROUTER` to obtain the actual owner IDs and tab names; do not publish restricted owner file IDs in the public repository. AEC is separate research and not an owner of any of these operational facts.

## Live source routing (verified 2026-10-22)

All five linked tabs in the **private JP master** (`people`, `projects`, `organizations`, `work_catalog`, `organization_locations`) now use direct `IMPORTRANGE` formulas pointing to the four owner workbooks, **without the old-data fallback**. Source grants are working and the key IDs were re-read successfully. The earlier hidden rollback tabs are inactive recovery history, not consulted by formulas.

The **shared Chaudhary attendance workbook** now has a visible `5_JP_PEOPLE_IMPORT` tab that imports only stable People ID, worker code and display name columns. Every name in `1_MANIFEST_INDEX!B19:B41` is a worker-code-based lookup against that imported source; the daily project sheet headers continue to reference those cells unchanged. Since Google currently shows `#REF! Please use a desktop web browser to connect this sheet` at `5_JP_PEOPLE_IMPORT!A1`, the attendance's hidden historical name backup maintains the original display **until the user grants Allow access**. All 23 name entries and 14 historical recorded man-days were re-verified intact. Once granted, edited People names flow to attendance through those formulas.

**Privacy:** Destination-based Google `IMPORTRANGE` authorization is broader than one requested range. Because Chaudhary attendance is shared with editors, approving access can let them request other People workbook ranges, including future private role data. Approve deliberately; for stricter future separation, insert a dedicated roster-only projection workbook.

GitHub Pages continues using manually reviewed JSON snapshots. No direct master/attendance data or personnel names are automatically sent to public GitHub.

## Initial authority baselines
| Owner | Source tab(s) | Initial data | Important rule |
| --- | --- | --- | --- |
| People | `people`, `person_roles` | 23 team members and 23 role rows | Person IDs `PERSON-CHT-W01…W23`, public flag FALSE; actual trade/role deliberately blank or unverified |
| Projects & Locations | `projects`, `project_locations` | 28 projects; 28 calculated locations | Change project coordinates only in `projects`; `project_locations` uses native same-book ARRAYFORMULA |
| Organizations | `organizations`, `organization_locations` | 9 organizations; 1 recorded office location | Stable `organization_id` and `organization_location_id` |
| Work Catalog | `work_catalog` | 29 work definitions | Stable `work_id`; project-specific completion is a separate source |

## Published website boundary
GitHub Pages currently consumes reviewed 14-table JSON snapshots in `ops/data/map-sheets-public.v1`; it does not fetch Google Sheets at runtime. This move **does not change the GitHub public dataset**. The published `people.json` remains empty; no private names or roles are made public. All new owner data must pass FK and privacy review before any manual safe projection.

## Operating instructions

1. Edit the source owner workbook; the private JP master now imports directly.
2. Open the **Chaudhary attendance** sheet `5_JP_PEOPLE_IMPORT!A1` on desktop and choose **Allow access**. This is the only pending source connection.
3. Recheck 23 workers and 14 historic man-days; take care before adding sensitive data to an owner shared through imports.
4. Rebuild and validate public JSON explicitly when required; this is independent of cross-workbook formulas.
