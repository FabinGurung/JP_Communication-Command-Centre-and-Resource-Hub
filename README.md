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

## Google Sheets map data authority (2026-10-21)

The map's 14 former CSV reference tables are now maintained in one [native Google Sheets workbook](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit). The browser loads 14 reviewed public JSON projections from `ops/data/map-sheets-public.v1/`, **not runtime CSV files**. These public projections require an explicit refresh and validation after Sheet edits; the private workbook is not anonymously fetched by Pages. Legacy CSV versions remain unchanged as rollback. See `docs/operations/MAP_GOOGLE_SHEETS_SOURCE_AND_PUBLICATION_v1.md`.

## Current interface development arc

The botanical workspace theme ships as **v2.2.0** after release-commit validation, sharing tokens, navigation and responsive rules across all 20 active pages. See the [design-system specification](docs/design/botanical-workspace-v1.md) for SVG ownership, mobile/print rules and repeatable visual QA. Immutable **v2.1.0** remains the previous-release rollback baseline.

## Current stable version

**v2.2.0 — JP AEC Operations Hub · Botanical UI & Mobile Harmonization**

The v2.2.0 release freezes the tested botanical theme across 20 active routes, the shared navigation/mobile behavior, five local botanical SVG assets and the documented browser QA. Project engineer approvals are shown in Progress only. The Discord collector remains on hold. See the [v2.2.0 release notes](docs/releases/v2.2.0.md).

**Previous stable release:** **v2.1.0 — JP AEC Operations Hub · Governed Platform Baseline**

The v2.1.0 milestone freezes the tested platform, branch/CI governance and project-scope isolation. Project drawing/engineer approvals appear in **Progress** and do not block software releases. The Discord collector is explicitly on hold. Future Drive, Sheets and Control Tower automation are separate platform features, not current release failures. See [v2.1.0 release notes](docs/releases/v2.1.0.md) and [platform-only roadmap](ops/control/c-web11-post-alias-roadmap.v1.0.json).

The original v2.0.0 release expanded the former data-driven project-map baseline into the Operations Hub: Project Map, Daily Ops, Site Operations, per-project pages, Workspace, Guide, Drive-resource linking and specialist-module routing.

Project and Daily Ops truth are maintained as canonical machine-readable files, separate from the application:

- `ops/schema/daily-ops-postgres.sql` — canonical relational/relationship authority (text DDL; no live database required)
- [Google Sheets map master](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit) — canonical editable values for the 14 map reference datasets; `projects.csv` is frozen rollback evidence
- `ops/data/current-works.json` — canonical Daily Ops current state
- `ops/data/project-resources.json` — canonical structured project → permission-gated Google Drive resource links; Drive owns the actual files
- `ops/events/daily-ops-events.jsonl` — canonical append-only Daily Ops event/history stream
- `map-config.json` — controlled map statuses and presentation configuration
- HTML / GitHub Pages / published JSON / Slack — downstream projections or interaction surfaces, never competing truth stores; the dedicated native map workbook is the exception for the 14 migrated map datasets

See [`ops/CANONICAL_DATA_AUTHORITY.md`](ops/CANONICAL_DATA_AUTHORITY.md) for source-of-truth rules, [`ops/PLATFORM_MODULES.md`](ops/PLATFORM_MODULES.md) for JP AEC Platform module naming, [`CHANGELOG.md`](CHANGELOG.md) for version history, and [`docs/releases/v2.2.0.md`](docs/releases/v2.2.0.md) for the current release notes.

## Start here: field users and website developers

- [`site-operations.html`](site-operations.html) — personal daily checklist for the site engineer (browser-local, not shared or authoritative progress).
- [`site-operations/history.html`](site-operations/history.html) — source-attributed public-safe progress projection (partial archive, not engineer acceptance).
- [`resources/`](resources/) — original Drive drawing/model links and authenticated source filenames; check revision and permission before use.
- [`workspace/`](workspace/) — **developer-only** source-code, architecture, Git history, control tower and deployment directory; not a site or owner project dashboard.
- [`guide/`](guide/) — canonical multi-depth operating guide: 1-page quick start, 3-page walkthrough, 7-page routine and 15-page reference. `how-to.html` is retained only as a compatibility redirect.

The design follows the same principle as the Pilates owner/member tooling: the human should not need to understand the repository tree just to operate the system.

### Important database clarification

The repository contains a PostgreSQL-compatible schema at `ops/schema/daily-ops-postgres.sql`, but the current GitHub Pages application does **not** require a live PostgreSQL or Neon connection. The SQL file is presently a deterministic relationship/constraint contract. Current live values remain in CSV/JSON/JSONL and source/evidence files remain in Google Drive.

A hosted PostgreSQL service such as Neon becomes useful later if the system requires secure authenticated write-back, many simultaneous users, server-side querying, transactions, row-level permissions or a real API/backend.


## Live architecture

```text
Private native Google Sheets map master (14 tables)
   └── explicit source review + PK/FK / publication validation
       └── ops/data/map-sheets-public.v1/*.json (14 reviewed public snapshots)
           └── map-config.json → assets/js/app.js → map.html
               └── map markers, filters, project details and GeoJSON download

Independent Daily Ops authority: ops/data/current-works.json
```

GitHub Pages never fetches private Sheets or original CSV files from the map browser. Sheet changes require a reviewed JSON refresh and successful Actions publication; refresh is not automatic.

## Where to edit

Edit the owning canonical source, never the rendered HTML or reviewed JSON directly. **For the 14 migrated map datasets only, edit the native Google Sheets master**; Google Sheets is not merely a downstream display in that scope.

| Fact | Canonical edit location |
| --- | --- |
| Project identity, lifecycle/status, coordinates, public project attributes | Google Sheets map master → `projects` worksheet |
| Daily work, readiness, blockers, materials, current operational state | `ops/data/current-works.json` |
| Project engineering resource links | `ops/data/project-resources.json` |
| Append-only operational/governance history | `ops/events/daily-ops-events.jsonl` |
| Relationships, PK/FK structure and data contract | `ops/schema/daily-ops-postgres.sql` |
| Allowed map statuses / visual configuration | `map-config.json` |

GitHub Pages loads only validated public JSON projections of the private map workbook and other independently governed public JSON. For map-master edits, validate and republish the projection; do not edit the frozen CSV rollback files.

The registered `feature/daily-ops-current-work` lane is authorized to validate and deploy to the existing GitHub Pages URL after the production workflow succeeds. `main` remains the canonical branch; promotion to `main` is separately governed and is not required for each test-lane deployment. See `ops/control/pages-publication-lane.v0.1.json`.

## Files

- `index.html` — Operations Hub landing page
- `workspace/` — developer-only navigation (`index.html`, `developer-links.v0.1.json`); legacy workspace data files remain preserved for provenance but are not the current developer landing-page source.
- `workspace.html` — backward-compatible redirect to `/workspace/`
- `guide/` — canonical Phase-2 1/3/7/15-page guide framework with shared CSS/JS, print support and image manifest
- `how-to.html` — backward-compatible redirect to `/guide/`
- `docs/WORKSPACE_GUIDE_ROADMAP.md` — five-phase Workspace + Guide parity plan
- `map.html` — map interface and logic
- `ops/data/map-sheets-public.v1/*.json` — 14 reviewed public map data projections; legacy `projects.csv` is retained solely for rollback
- `map-config.json` — title, map settings and status colours
- `.github/workflows/validate-projects.yml` — automatic validation
- `MOBILE_EDITING_GUIDE.md` — iPhone editing instructions
- `.nojekyll` — tells GitHub Pages to serve files directly

## Coordinate rules

- Map-master and JSON field names: `latitude` and `longitude`
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

GitHub Pages and this repository are public. Only approved public information belongs in published JSON projections. The native source workbook stays private.

`is_public=FALSE` hides a record from the map interface, **not** from any public GitHub JSON file. Enforce the publication boundary before projection; never treat a UI filter as access control. The legacy public CSV rollback files must likewise never contain confidential information.

## Safe change workflow

1. Edit the owning source: the private native Google Sheets master for the 14 map tables; the relevant governed JSON/JSONL file for independent Daily Ops records.
2. Validate source identity, values, PK/FK relationships, and publication controls; reject private data before constructing the reviewed public projection.
3. Regenerate the reviewed `ops/data/map-sheets-public.v1/*.json` files from the approved native Sheet values; never treat CSV rollback files as the new source.
4. Commit on the registered `feature/daily-ops-current-work` working lane and require GitHub Actions validation and visual QA to pass.
5. Verify Pages deployed the precise validated SHA before reporting a published change. A Sheet edit alone does **not** refresh Pages.
6. Promote to `main` only when separately governed and approved.

GitHub Pages deployment initialized.

## Phase 3 illustrated guide layer

The canonical `/guide/` hierarchy now includes 15 public-safe, version-controlled SVG workflow diagrams. The diagrams are mapped across the 1-page, 3-page, 7-page and 15-page guide depths through `guide/guide.js`, inventoried in `guide/image-manifest.json`, validated as accessible SVG XML in CI, and designed to explain workflows without publishing private project data.


## Historical Phase 4 Workspace layer (superseded by developer-only scope on 2026-10-11)

The following describes an earlier owner-facing Phase 4 implementation and is retained as a historical engineering record. **It no longer describes the current `/workspace/` landing page**, which is strictly developer-focused and reads `workspace/developer-links.v0.1.json`. Site records and resources are available through Map, Checklist, Progress Report and Project Resources.

Phase 4 also adds:

- `workspace/modules.json` — normalized specialist-module ownership and current repository identities;
- `workspace/edit-routing.json` — owner-facing “what do I edit?” routing;
- System Health roles for canonical files, Drive, Sheets, Slack, SQL, GitHub Actions/Pages and PostgreSQL/Neon;
- CI enforcement for module identity, edit-routing integrity, live/fallback project coverage and stale historical repository slugs;
- rendered desktop/mobile QA with no horizontal overflow at 390 px.

## Daily Slack + Web cycle contract

See [`ops/control/daily-slack-web-cycle.json`](ops/control/daily-slack-web-cycle.json) and [the governed procedure](ops/control/DAILY_SLACK_WEB_CYCLE.md). The existing PRIVATE A9 Slack Recovery Archive owns raw multilingual JSONL; this public repository holds public-safe normalized JSON/JSONL/CSV/SQL contracts only. The cycle must read both REB/FBL company rollups as well as governed project channels and must show per-channel cutoffs and receipt status. Missing Rohini project-master mappings are coverage gaps, not evidence that those projects do not exist.

## A9-CWO — Communication & Web Operations

**A9-CWO** supersedes the user-facing A9-SWO nickname. It represents a multi-source operating cycle (governed Slack, two-channel Discord Colab and future admitted providers), **not a new Discord/Slack bot account**. See the [pinned storage and daily pipeline](controls/storage.html), machine contract `ops/control/storage-routing-rules.json`, and [two-channel Discord Colab](ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb). An operator runs the Discord notebook before daily reconciliation and the run must report Discord `PASS/PARTIAL/NOT_RUN`. Full historical Discord server harvesting is out of scope. Storage assignment is by original evidence / normalized truth / binary file / human projection, not by channel brand.
