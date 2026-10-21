# JP AEC Operations Hub

Public [GitHub Pages website](https://fabingurung.github.io/JP_Communication-Command-Centre-and-Resource-Hub/) · [Project map](https://fabingurung.github.io/JP_Communication-Command-Centre-and-Resource-Hub/map.html)

**AI/operators: begin with [AGENTS.md](AGENTS.md), then read only the task's owning source.** Do not load historical snapshots, unrelated control files, whole Drive or every script.

## What is live

- **Website:** botanical responsive operations hub, project map, Daily Ops, site/project pages, resources, workspace and multi-depth guide. Current stable release **v2.2.0**, previous frozen **v2.1.0**.
- **Map data:** 14 editable tables / 162 baseline records in the [private native Google Sheets master](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit); public reviewed JSON in `ops/data/map-sheets-public.v1/`. Browser runtime does **not** load CSV or authenticate to private Sheets. **Sheet changes are not auto-synchronized**: validate, review publication, regenerate JSON, commit and verify Pages deploy. Root CSV files remain frozen rollback.
- **Daily Ops:** `ops/data/current-works.json` owns current state; `ops/events/daily-ops-events.jsonl` owns append-only history; `ops/data/project-resources.json` owns governed Drive resource links. SQL PK/FK declaration: `ops/schema/daily-ops-postgres.sql`.
- **Discord collection:** on hold; no scheduled collection or unapproved public source ingestion.

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

## Rollback and historic evidence

The migration baseline is commit `8a8474979a233259f27fd2c18ffc61ba78a4a8b8`. Immediately before repository cleanup: `7a322a5988f4bd788d7c28aa2c06c946960b95c2`. **175 obsolete in-repository `99_VERSION_ARCHIVE` snapshots** and the outdated `MIGRATION_CHECKLIST.md` were removed from the current tree; their complete bytes and paths remain recoverable from that pre-cleanup Git commit (`git show 7a322a59:<original-path>`). The **16 notebook archive files** required by the Discord version ledger and SHA validation remain tracked, as do all original CSV rollback datasets. No Git history, immutable release tag, private Drive file or canonical data was deleted.

Historical detail stays in `CHANGELOG.md`, `docs/releases/`, and the commit history rather than this everyday readme.
