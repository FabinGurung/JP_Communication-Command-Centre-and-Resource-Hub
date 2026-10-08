# JP AEC Operations Hub

The live project-experience layer of the **JP AEC Platform**, hosted with GitHub Pages. The existing repository slug is retained for URL stability.

## Mandatory Operations control read order

Branch/lane governance is now a compulsory repository-local control, not an optional convention.

Before ChatGPT, automation or a human starts a repository mutation:

1. Read `ops/control/control-system.json`.
2. Read `ops/control/branch-lane-registry.json` and resolve the intended lane.
3. Work only on a branch with `allowed_for_work=true`.
4. Read `ops/CANONICAL_DATA_AUTHORITY.md` and the lane-specific canonical files.
5. Require validation before promotion to `main`.

The registry maps the **Main Library** to `main`, the **Local Library** to `feature/daily-ops-current-work`, and the **Lane Library** to the branch registry itself. Archive refs under `archive/*` are frozen. Historical non-archive aliases are marked **DO_NOT_USE** and resolve to their archive equivalents.

## Current stable version

**v2.0.0 — JP AEC Operations Hub**

v2.0.0 is the governed production release that expands the former data-driven project-map baseline into the Operations Hub: Project Map, Daily Ops, Site Operations, per-project pages, Workspace, Guide, Drive-resource linking and specialist-module routing.

Project and Daily Ops truth are maintained as canonical machine-readable files, separate from the application:

- `ops/schema/daily-ops-postgres.sql` — canonical relational/relationship authority (text DDL; no live database required)
- `projects.csv` — canonical project-master current values: IDs, lifecycle, coordinates, public project attributes
- `ops/data/current-works.json` — canonical Daily Ops current state
- `ops/data/project-resources.json` — canonical structured project → permission-gated Google Drive resource links; Drive owns the actual files
- `ops/events/daily-ops-events.jsonl` — canonical append-only Daily Ops event/history stream
- `map-config.json` — controlled map statuses and presentation configuration
- HTML / GitHub Pages / Google Sheets / Slack — downstream projections or interaction surfaces, never competing truth stores

See [`ops/CANONICAL_DATA_AUTHORITY.md`](ops/CANONICAL_DATA_AUTHORITY.md) for source-of-truth rules, [`ops/PLATFORM_MODULES.md`](ops/PLATFORM_MODULES.md) for JP AEC Platform module naming, [`CHANGELOG.md`](CHANGELOG.md) for version history, and [`docs/releases/v2.0.0.md`](docs/releases/v2.0.0.md) for the current release notes.

## Start here if you are the owner or manager

- [`workspace/`](workspace/) — searchable owner/manager directory: projects, Daily Ops, data sources, Sheets, specialist modules, governance and storage/database status.
- [`guide/`](guide/) — canonical multi-depth operating guide: 1-page quick start, 3-page walkthrough, 7-page routine and 15-page reference. `how-to.html` is retained only as a compatibility redirect.

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

The working lane `feature/daily-ops-current-work` remains available for governed validation, but production GitHub Pages deployment is owned by `main` only. Feature-lane runs validate and skip deployment; production changes reach Pages only after an explicit fast-forward release to `main`.

## Files

- `index.html` — Operations Hub landing page
- `workspace/` — canonical Paila-style owner/manager resource directory (`index.html`, `links.json`, `workspace.css`, `workspace.js`)
- `workspace.html` — backward-compatible redirect to `/workspace/`
- `guide/` — canonical Phase-2 1/3/7/15-page guide framework with shared CSS/JS, print support and image manifest
- `how-to.html` — backward-compatible redirect to `/guide/`
- `docs/WORKSPACE_GUIDE_ROADMAP.md` — five-phase Workspace + Guide parity plan
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

## Phase 3 illustrated guide layer

The canonical `/guide/` hierarchy now includes 15 public-safe, version-controlled SVG workflow diagrams. The diagrams are mapped across the 1-page, 3-page, 7-page and 15-page guide depths through `guide/guide.js`, inventoried in `guide/image-manifest.json`, validated as accessible SVG XML in CI, and designed to explain workflows without publishing private project data.


## Phase 4 live Workspace layer

The canonical `/workspace/` is now a live read-only orientation console rather than only a static resource directory. It joins `projects.csv` with `ops/data/current-works.json` for current project/status cards, while preserving `workspace/links.json` as the independent fallback/navigation registry.

Phase 4 also adds:

- `workspace/modules.json` — normalized specialist-module ownership and current repository identities;
- `workspace/edit-routing.json` — owner-facing “what do I edit?” routing;
- System Health roles for canonical files, Drive, Sheets, Slack, SQL, GitHub Actions/Pages and PostgreSQL/Neon;
- CI enforcement for module identity, edit-routing integrity, live/fallback project coverage and stale historical repository slugs;
- rendered desktop/mobile QA with no horizontal overflow at 390 px.

## Daily Slack + Web cycle contract

See [`ops/control/daily-slack-web-cycle.json`](ops/control/daily-slack-web-cycle.json) and [the governed procedure](ops/control/DAILY_SLACK_WEB_CYCLE.md). The existing PRIVATE A9 Slack Recovery Archive owns raw multilingual JSONL; this public repository holds public-safe normalized JSON/JSONL/CSV/SQL contracts only. The cycle must read both REB/FBL company rollups as well as governed project channels and must show per-channel cutoffs and receipt status. Missing Rohini project-master mappings are coverage gaps, not evidence that those projects do not exist.
