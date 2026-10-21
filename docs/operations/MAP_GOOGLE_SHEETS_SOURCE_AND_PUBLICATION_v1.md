# Map — Google Sheets Master and reviewed JSON publication (2026-10-21)

**Native source workbook:** [JP Project Map 14 Tables v1.0 LIVE](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit)

**Drive folder:** https://drive.google.com/drive/folders/1DRECcxUaz68mS_WPWbvReKxujmZ2O58t (renamed `JP__PROJECT_MAP__SHEETS_SOURCE`)\n\n**Restricted JP parent:** https://drive.google.com/drive/folders/1QHxD74egNFeQAmvDJzvKmDxEQUOH3Kq6 (`JP__ENTERPRISE__PRIVATE`). Workbook title: `JP__PROJECT_MAP__14_TABLES__v1.0__LIVE`. Same original file/folder IDs and access restrictions. **JP = enterprise operational owner; AEC = separate hypothesis/thesis research**, not an alternate authority for this map.

This migration preserves all 14 original CSV datasets in the Git repository solely as rollback/history, imports their 162 populated records into one Google Sheet with 14 named worksheets and a `_CONTROL_READ_FIRST` tab, and publishes **reviewed JSON snapshot objects** for GitHub Pages.

The map now renders from `map-config.json → ops/data/map-sheets-public.v1/*.json → assets/js/app.js`. It **does not fetch CSV or authenticate to private Sheets inside a visitor's browser**. All records/cell values were compared against the CSV source at migration (14/14 tabs, 0 differences). The JSON projections represent only information already present in the public CSV repository; existing `is_public` and project-publication rules still apply in the renderer.

**Refreshing after editing Google Sheets:** A Google Sheet edit does NOT instantly modify the public website. Request an A9 *map Sheet refresh*. The operator reads the 14 current native worksheets, validates schema, PK/FK, field visibility, coordinates and project-publication controls, then regenerates only the reviewed public JSON projections and deploys via the registered Actions branch. Never paste Google OAuth tokens or service-account credentials into public source. Do not replace or copy private Drive source rows in the Git repo outside the reviewed public projection. User did not request a recurring schedule; no automation schedule was created.

**Scope separation:** `ops/data/current-works.json`, historical JSONL, resource links and source engineering approvals are **not** migrated by this work. Only the 14 CSV-backed map reference tables are switched.

**Rollback:** checkout the immutable v2.2.0 release or previous verified branch commit `8a8474979a233259f27fd2c18ffc61ba78a4a8b8`. Original 14 CSV files remain unchanged in Git. The new Sheets workbook has a stable ID; do not replace it with a copy when updating.

**Permission warning:** The 14 public JSON snapshots are readable in the public GitHub repository just as the prior CSV datasets were. Do not put private phones, identities, sensitive finance, unpublished site evidence or any other confidential data in those public projections. Google Sheets sharing stays restricted.


## 2026-10-22 — First operational work links, field-reported only

The private owner-only Google Sheet tab `project_work_items` now links three public field-reported operations to existing JP project IDs and `work_catalog` IDs: P002 slab reinforcement, P005 formwork/ply stage, and P020 shuttering. Provenance is the previously published `ops/data/progress-report-public.v0.2.jsonl` records `FLD-P002-20261009-01`, `FLD-P005-20261009-01`, and `FLD-P020-20261009-01`. These are dated **2026-10-09**; they are **not** live daily work statuses as of 2026-10-22. Public projection omits private source originals, crew details, prices, quantities, unsupported percent complete, and QA acceptance. Values `IN_PROGRESS` mean field-reported activity, not engineer-certified readiness. Do not change the separate Daily Ops authoritative projections on account of these map work links.

The frozen source CSV files remain intact. The reviewed public `project_work_items.json` intentionally diverges from the empty legacy CSV after the verified Sheet edit; never reapply original CSV parity to this published tab.
