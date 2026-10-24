# JP Operations Hub

Public [GitHub Pages website](https://fabingurung.github.io/JP_Communication-Command-Centre-and-Resource-Hub/) · [Project map](https://fabingurung.github.io/JP_Communication-Command-Centre-and-Resource-Hub/map.html)

**AI/operators: begin with [AGENTS.md](AGENTS.md), then read only the task's owning source.** Do not load historical snapshots, unrelated control files, whole Drive or every script.

**Scope:** JP is the operational company/enterprise system; **AEC is a separate research/thesis hypothesis**. JP operational project facts must not be reclassified as thesis evidence. The unchanged GitHub repository slug is a legacy stable URL, not the product name.

**Project threads can contribute directly without manual inter-chat handoffs:** follow [Multi-chat scoped GitHub contribution protocol](docs/operations/MULTI_CHAT_PROJECT_CONTRIBUTIONS_V0.1.md). Independent PRs from project branches are path-validated and tested before merge to the existing Pages lane; raw/PII/finance/source drawings stay in Google Drive. This is an initial no-auto-merge gate, not unrestricted production write access.

**Basanti identity correction:** `PRJ-000029 / REB-002` is canonical; `PRJ-000030 / REB-003` is a retired mistaken duplicate alias. Both Ramachandra and Radha are historical incorrect project labels. Current private coordinates are stored in Drive; public resource catalog admission [Issue #8](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/issues/8) remains open.

## What is live

- **Website:** botanical responsive operations hub, project map, Daily Ops, site/project pages, resources, workspace and multi-depth guide. Current stable release **v2.2.0**, previous frozen **v2.1.0**.
- **Map data:** 14 table schemas / 162 initial-migration records, with 3 subsequently reviewed work rows in the [private native Google Sheets master](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit); public reviewed JSON in `ops/data/map-sheets-public.v1/`. Browser runtime does **not** load CSV or authenticate to private Sheets. **Sheet changes are not auto-synchronized**: validate, review publication, regenerate JSON, commit and verify Pages deploy. Root CSV files remain frozen rollback.
- **Daily Ops:** `ops/data/current-works.json` owns current state; `ops/events/daily-ops-events.jsonl` owns append-only history; `ops/data/project-resources.json` owns governed Drive resource links. SQL PK/FK declaration: `ops/schema/daily-ops-postgres.sql`.
- **Discord collection:** on hold; no scheduled collection or unapproved public source ingestion.

**Basanti canonical identity update (2026-10-23):** Private Drive project sources now contain `PRJ-000030 / REB-003`, with original PDF linked under private `PSL-000005` and non-public publication controls. Public GitHub resource-catalog admission remains under [Issue #8](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/issues/8); no changes to existing 46 public resources or frozen 28-row CSV. [Live source trace](docs/operations/A9_BASANTI_FOREIGN_CHAT_TRACE_20261022.md).

**Corrected category partition (22 October 2026):** Every one of the private JP master’s **14 data categories now has its own Google workbook**. The four existing live People/Projects/Organizations/Work Catalog IDs remain; the ten other categories are copied to new private Google Sheets with mandatory `00_MANIFEST` and `02_HOW_TO` tabs. **The ten new source imports require a one-time desktop `Allow access` before cutover**, so master data intentionally continues to read from the four existing authorized sources; there is no broken map. The active and staged IDs are maintained in private `_SOURCE_ROUTER` and `00_CUTOVER_APPROVALS`. Do not edit split copies until live cutover. The mistaken 29 WRK-specific files were removed from the active directory and archived as `RECYCLE_BIN_PENDING`; the live Work Catalog registry was removed. Drive actions cannot soft-trash files. P1’s personnel access isolation remains deferred pending user permission action. See [corrected ownership map](docs/operations/JP_SOURCE_OWNER_ROUTING_20261022.md).

## Read only what you need

| Task | Open |
| --- | --- |
| AI execution / branch scope | [AGENTS.md](AGENTS.md), then `ops/control/branch-lane-registry.json` **only before Git mutations** |
| Sheet → map publication | `docs/operations/MAP_GOOGLE_SHEETS_SOURCE_AND_PUBLICATION_v1.md`, `ops/control/map-sheets-source.v1.0.json` |
| Map UI | `map.html`, `assets/js/app.js`, `map-config.json` |
| Daily Ops | `ops/data/current-works.json`, relevant schema / event |
| Resource or module routing | `workspace/edit-routing.json` |
| Full authority conflict | `ops/CANONICAL_DATA_AUTHORITY.md` |
| GitHub Pages | `ops/control/pages-publication-lane.v0.1.json` and `.github/workflows/daily-ops-branch-preview.yml` |

## Development and publication

Registered development/Pages branch: **`feature/daily-ops-current-work`**; canonical production source branch: **`main`**. Validated development pushes deploy to the existing Pages URL via [GitHub Actions](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/actions); `main` is not fast-forwarded for every test. Never claim a deploy based on a commit alone. Run relevant checks, including `python scripts/test_map_sheets_migration.py` for map changes; confirm Actions validation, deploy and visual QA. Do not change frozen tags.

## Drive ownership\n\nThe private Sheet resides under [JP__ENTERPRISE__PRIVATE](https://drive.google.com/drive/folders/1QHxD74egNFeQAmvDJzvKmDxEQUOH3Kq6) → [JP__PROJECT_MAP__SHEETS_SOURCE](https://drive.google.com/drive/folders/1DRECcxUaz68mS_WPWbvReKxujmZ2O58t). Existing shared `A9_Fabin_Gurung/01_JP` is a separate linked directory and is **not** the workbook parent because its inherited sharing would broaden access.\n\n## Rollback and historic evidence

The migration baseline is commit `8a8474979a233259f27fd2c18ffc61ba78a4a8b8`. Immediately before repository cleanup: `7a322a5988f4bd788d7c28aa2c06c946960b95c2`. **175 obsolete in-repository `99_VERSION_ARCHIVE` snapshots** and the outdated `MIGRATION_CHECKLIST.md` were removed from the current tree; their complete bytes and paths remain recoverable from that pre-cleanup Git commit (`git show 7a322a59:<original-path>`). The **16 notebook archive files** required by the Discord version ledger and SHA validation remain tracked, as do all original CSV rollback datasets. No Git history, immutable release tag, private Drive file or canonical data was deleted.

Historical detail stays in `CHANGELOG.md`, `docs/releases/`, and the commit history rather than this everyday readme.

## 24 October 2026 — source Sheets, generated master and single JSON

Humans edit individual source workbooks. The publishing Google workbook aggregates them; it is not a second fact-entry surface. The map loads `ops/data/map-data.v1.json`, generated and checked by Actions from the 14 reviewed projections. Live private Google authentication/source-refresh is still unconfigured; a Sheet edit alone does not trigger fresh public data. [Current storage and version contract](docs/operations/SHEETS_TO_PAGES_STORAGE_CONTRACT_V1.md).

Enterprise storage is inside `01_JP`; additional writers are the owner’s backup accounts. The old project-map Drive workspace is archived.
