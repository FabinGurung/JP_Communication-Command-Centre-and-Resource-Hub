# JP AEC Operations Hub

The live project-experience layer of the **JP AEC Platform**, hosted with GitHub Pages. The existing repository slug is retained for URL stability.

## Current stable version

**v1.1.0 — Data-driven Stable Map**

This is the first stable data-driven version of the JP Ecosystem Project Map.

Project and Daily Ops truth are maintained as canonical machine-readable files, separate from the application:

- `ops/schema/daily-ops-postgres.sql` — canonical relational/relationship authority (text DDL; no live database required)
- `projects.csv` — canonical project-master current values: IDs, lifecycle, coordinates, public project attributes
- `ops/data/current-works.json` — canonical Daily Ops current state
- `ops/data/project-resources.json` — canonical structured project → permission-gated Google Drive resource links; Drive owns the actual files
- `ops/events/daily-ops-events.jsonl` — canonical append-only Daily Ops event/history stream
- `map-config.json` — controlled map statuses and presentation configuration
- HTML / GitHub Pages / Google Sheets / Slack — downstream projections or interaction surfaces, never competing truth stores

See [`ops/CANONICAL_DATA_AUTHORITY.md`](ops/CANONICAL_DATA_AUTHORITY.md) for source-of-truth rules, [`ops/PLATFORM_MODULES.md`](ops/PLATFORM_MODULES.md) for JP AEC Platform module naming, and [`CHANGELOG.md`](CHANGELOG.md) for version history.

## Start here if you are the owner or manager

- [`workspace.html`](workspace.html) — owner-facing control desk: what the system contains, where each fact belongs, storage/database choices and operational shortcuts.
- [`how-to.html`](how-to.html) — plain-language step-by-step guide for project edits, Daily Ops, Drive resources, Sheets/Slack projections, GitHub Actions, recovery and future database migration.

The design follows the same principle as the Pilates owner/member tooling: the human should not need to understand the repository tree just to operate the system.

### Important database clarification

The repository contains a PostgreSQL-compatible schema at `ops/schema/daily-ops-postgres.sql`, but the current GitHub Pages application does **not** require a live PostgreSQL or Neon connection. The SQL file is presently a deterministic relationship/constraint contract. Current live values remain in CSV/JSON/JSONL and source/evidence files remain in Google Drive.

A hosted PostgreSQL service such as Neon becomes useful later if the system requires secure authenticated write-back, many simultaneous users, server-side querying, transactions, row-level permissions or a real API/backend.


## Live architecture

```text
index.html
├── loads map-config.json
├── loads projects.csv
├── creates filters, project list, markers and popups
└── downloads filtered data as GeoJSON
```

The live website no longer stores project records inside `index.html`.

## Where to edit

Edit the canonical file that owns the fact. Do **not** manually maintain the same fact in HTML or Google Sheets.

| Fact | Canonical edit location |
| --- | --- |
| Project identity, lifecycle/status, coordinates, public project attributes | `projects.csv` |
| Daily work, readiness, blockers, materials, current operational state | `ops/data/current-works.json` |
| Project engineering resource links | `ops/data/project-resources.json` |
| Append-only operational/governance history | `ops/events/daily-ops-events.jsonl` |
| Relationships, PK/FK structure and data contract | `ops/schema/daily-ops-postgres.sql` |
| Allowed map statuses / visual configuration | `map-config.json` |

GitHub Pages reads these canonical files and is a downstream presentation layer. Google Sheets is also a downstream projection; it is not where project-master truth should be edited.

During the current Daily Ops development lane, changes are made on `feature/daily-ops-current-work`, validated by GitHub Actions, and deployed by the branch-preview workflow. `main` remains untouched until an explicit governed promotion.

## Files

- `index.html` — Operations Hub landing page
- `workspace.html` — owner/manager workspace and storage architecture explainer
- `how-to.html` — plain-language operating guide
- `map.html` — map interface and logic
- `projects.csv` — live public project dataset
- `map-config.json` — title, map settings and status colours
- `.github/workflows/validate-projects.yml` — automatic validation
- `MOBILE_EDITING_GUIDE.md` — iPhone editing instructions
- `.nojekyll` — tells GitHub Pages to serve files directly

## Coordinate rules

- CSV columns: `latitude` and `longitude`
- Leaflet uses `[latitude, longitude]`
- GeoJSON uses `[longitude, latitude]`

Never swap the order.

## Dates

Use `YYYY-MM-DD`, for example `2026-07-23`.

## Status values

The status must exactly match a key in `map-config.json`:

- Construction
- Maintenance
- Completed
- Approval
- Planned
- On Hold
- Cancelled

## Public/private rule

GitHub Pages and this repository are public. Only public information belongs in `projects.csv`.

`is_public=FALSE` hides a record from the map, but does not secure it because the CSV remains public. Remove genuinely sensitive information from the public repository.

## Safe change workflow

1. Edit the owning canonical data file, not the rendered page or a downstream Sheet.
2. Validate the project identity / PK-FK relationship against the SQL contract.
3. Commit on the governed working branch.
4. Require GitHub Actions validation to pass.
5. Let Pages update from the canonical files.
6. Project into Google Sheets only as a downstream view when that projection is configured.
7. Promote to `main` only through an explicit governed release.

GitHub Pages deployment initialized.
