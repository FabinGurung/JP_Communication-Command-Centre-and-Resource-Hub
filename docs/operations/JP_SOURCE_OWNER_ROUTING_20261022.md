# JP enterprise source ownership — four-workbook partition (2026-10-22)

## Purpose and privacy
The JP enterprise map private Google Sheet remains the **read-only consolidation point**. Four private owner spreadsheets contain the editable facts for (1) People, (2) Projects & Locations, (3) Organizations and office locations, and (4) Work Catalog. Open the existing private master and read `_SOURCE_ROUTER` to obtain the actual owner IDs and tab names; do not publish restricted owner file IDs in the public repository. AEC is separate research and not an owner of any of these operational facts.

## How the formulas work
Master `people`, `projects`, `organizations`, `organization_locations` and `work_catalog` each have a single `ARRAYFORMULA(IFERROR(IMPORTRANGE(...), __ROLLBACK_<category>_20261022!<baseline_range>))` at A1. Historical values were duplicated as date-stamped **hidden native Google Sheets tabs** before edits. All source-table readbacks passed with previous values intact; these fallback copies are **rollback only**, not writable owners. The master tabs also have warning-only protections discouraging edits.

Google Sheets **requires a one-time Allow access operation for each external owner workbook**. At the time of this run, `_AUTHORIZE_IMPORTS` displays `#REF! Please use a desktop web browser to connect this sheet`. The formula fallbacks work; dynamic source updates will **not** appear until the user grants the four source connections in the Google Sheets UI. No connector action can truthfully represent these as already approved. The fifth import (organization locations) shares the organizations source and typically uses that same source permission.

## Initial authority baselines
| Owner | Source tab(s) | Initial data | Important rule |
| --- | --- | --- | --- |
| People | `people`, `person_roles` | 23 team members and 23 role rows | Person IDs `PERSON-CHT-W01…W23`, public flag FALSE; actual trade/role deliberately blank or unverified |
| Projects & Locations | `projects`, `project_locations` | 28 projects; 28 calculated locations | Change project coordinates only in `projects`; `project_locations` uses native same-book ARRAYFORMULA |
| Organizations | `organizations`, `organization_locations` | 9 organizations; 1 recorded office location | Stable `organization_id` and `organization_location_id` |
| Work Catalog | `work_catalog` | 29 work definitions | Stable `work_id`; project-specific completion is a separate source |

The team roster came from the already-existing `1_MANIFEST_INDEX!A19:C41` in the Chaudhary attendance workbook. That attendance workbook now has an additional `4_PERSON_ID_MAPPING` tab linking W01–W23 to the People owner's new stable person IDs. **No existing manifest names, attendance daily statuses, cross-tab heading formulas or calculations were modified.** The attendance workbook is shared with other editors; unrestricted `IMPORTRANGE` from the private People owner would create a personnel access boundary problem. Do **not** authorize that shared import. A controlled roster-only bridge is needed for full worker-name synchronization.

## Published website boundary
GitHub Pages currently consumes reviewed 14-table JSON snapshots in `ops/data/map-sheets-public.v1`; it does not fetch Google Sheets at runtime. This move **does not change the GitHub public dataset**. The published `people.json` remains empty; no private names or roles are made public. All new owner data must pass FK and privacy review before any manual safe projection.

## What to do when operating
1. Edit only the relevant private owner workbook, not the read-only JP master mirror.
2. On desktop, open the private JP master `_AUTHORIZE_IMPORTS` and approve the four required Google `IMPORTRANGE` source connections (People is permitted in the private master; **not** shared attendance).
3. Read back the master imported tabs and check stable PK/FK IDs and privacy flags.
4. For the public website, separately validate and publish only reviewed safe JSON. Do not infer automatic updates from a Google Sheet edit.
