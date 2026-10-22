# JP private worksheet-to-workbook architecture — corrected on 22 October 2026

## Precisely what is meant by a category workbook
There is exactly one **Google workbook per one of the 14 JP master data worksheets**; **not** one workbook per WRK catalog row. The source owner workbooks are private within JP__ENTERPRISE__PRIVATE/JP__NORMALIZED_AUTHORITIES__PRIVATE.

Existing live workbook IDs reused:
- people → JP People workbook (includes pre-existing person_roles, a related subtable)
- organizations → JP Organizations workbook
- projects → JP Projects & Locations workbook (keeps an existing calculated project_locations view)
- work_catalog → JP Work Catalog workbook

Newly created category workbooks (10):
- project_parties
- project_funding
- project_work_items
- materials_master
- project_material_inventory
- project_components
- project_source_links
- project_opportunities
- organization_locations
- project_publication_settings

**Every workbook** now has the compulsory `00_MANIFEST` and `02_HOW_TO` tabs alongside its data. Original cell values in the 10 new categories exactly matched the previous owner tabs on verified readback. Keys and names were preserved. Every new file lives under the same private JP authorities folder. No false claims of newly verified quantities or project approvals.

## Migration staging and Google approval limitation
Four pre-existing workbook connections still power the private JP master, so all 14 map data tabs resolve correctly. Its `_SOURCE_ROUTER` retains the current source workbook ID and adds a target workbook ID, URL, and cutover status. Its new `00_CUTOVER_APPROVALS` contains ten independent `IMPORTRANGE` test formulas that currently return Google `#REF!` requiring a **desktop Allow access**. The connected Drive/Sheets action cannot grant it. Until the user authorizes each new source, keep legacy category data tabs in their old owner books and do not overwrite the JP master import formulas. During the staging interval, the new files should not receive independent operational edits, to avoid divergence.

After permission approval: verify source parity and all PK/FK references, change exactly the ten JP master A1 imports to the new sources, read back, change the router status to ACTIVE, and remove/retire old copied tabs only after archival and verified cutover. One file per category becomes authoritative **after** that cutover, not merely from physical creation.

## Incorrect per-work files
The previous 29 WRK-code operational files and template were an incorrect interpretation and have been **removed from the live JP data directory**. Their entire folder is stored in the owner-only version archive as `99_WRONG_29_WORK_ITEM_SHEETS__RECYCLE_BIN_PENDING__ARCHIVED_20261022`. The live Work Catalog's mistaken `work_sheet_registry` tab was removed after archiving the full workbook. There is currently no supported Google Drive connector action to move a file to Trash (only irreversible permanent deletion). No irreversible deletion was performed. A user can move the archived folder to Trash in the Drive UI if desired.

## Google Drive folder boundaries
The original company folders `03_Fishtail_Builders` and `04_Rohini_Engineering_and_Builders` now sit under the shared A9/`01_JP` folder with unchanged folder IDs and permissions. Private source workbooks remain separately owner-only under JP__ENTERPRISE__PRIVATE and are discoverable by links from the shared read-first pointer. Neither AEC thesis nor public GitHub JSON is an alternate company data authority.

## P1 People security: deferred
Chaudhary v2.6 attendance already imports worker IDs/codes/names from People Master and the names resolve. However Google Sheets' import permission is source-wide, not restricted to just A:C; a shared destination editor may request private related ranges. A true roster-only boundary requires isolating/syncing a minimal roster through separately permissioned source and addressing the earlier grant, which may require Google UI/permission actions and source rotation. Because the user asked to leave P1 if manual setup is required, no new P1 permissions or files were changed. Do not add sensitive personnel fields to broadly importable sources.

## Remaining
1. Ten Google import approvals (in JP master `00_CUTOVER_APPROVALS`) and safe 14-owner cutover.
2. Later P1 source-wide personnel access hardening.
3. Data quality / key constraints / Gemini-safe editing and controlled GitHub JSON refresh.
