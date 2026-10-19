# Changelog

All notable changes to the JP AEC Operations Hub are recorded here.

## [v2.1.0] — 2026-10-19

### Platform milestone

- Froze tested GitHub Pages/Actions platform baseline, six primary routes, resource library, source-aware Progress, software-only Developer Workspace and stable main/feature reconciliation.
- Kept engineer/document issue approvals in project Progress, not the developer software release backlog.
- Preserved 46 permission-gated resource links, 37 frozen progress observations, and six scoped P001/P002 resource-name aliases with FK/negative-join tests.
- Kept the Discord collector explicitly paused; no new provider harvest or construction acceptance claimed.
- Added deterministic release governance/notes, immutable tag and GitHub Release automation gated on a successful production deployment.

### Deferred integrations (not release blockers)

- Authenticated repeatable Google Drive full-pagination refresh and private candidate intake.
- GitHub-to-Sheets projections, Control Tower sync, optional query architecture and role-based backend.

See [`docs/releases/v2.1.0.md`](docs/releases/v2.1.0.md).

## [v2.0.0] — 2026-10-06

### Added

- Canonical Daily Ops current-state, append-only history and project-resource registries
- Site Operations portfolio and per-project operations pages
- Permission-gated Google Drive engineering-resource linking
- Owner/manager Workspace with live project status, System Health and guided edit routing
- Normalized specialist-module ownership registry
- Canonical 1/3/7/15-page operating Guide with 15 public-safe SVG workflow illustrations
- Phase-5 release QA covering internal links, accessibility basics, print contract and Pages ownership
- Versioned release notes at `docs/releases/v2.0.0.md`

### Changed

- Repository role expanded from the v1.x project-map baseline to the JP AEC Operations Hub
- GitHub Pages production deployment ownership moved to `main` only
- The feature lane remains validation-only and cannot deploy production Pages
- Current repository/module names replace historical slugs in active documentation and schema identifiers

### Architecture

- `projects.csv` owns public project-master values
- `ops/data/current-works.json` owns Daily Ops current state
- `ops/events/daily-ops-events.jsonl` owns append-only operational history
- `ops/data/project-resources.json` owns normalized project → Drive relationships
- Google Drive owns source/evidence file bytes and access permissions
- `workspace/modules.json` owns public Workspace module identity
- `workspace/edit-routing.json` owns owner-facing edit routing
- PostgreSQL remains a schema/relationship contract; Neon is not required by this release

### Release governance

- `snapshot/pre-workspace-phase5-20261006` preserves the pre-Phase-5 working state
- `snapshot/pre-main-promotion-v2.0.0-20261006` preserves pre-promotion `main`
- Production promotion is fast-forward only; divergent `main` history is not overwritten
- Final production Pages artifact and Root-11 Local/Main closeout are provider-readback gates

## [v1.1.0] — 2026-07-26

### Added

- Data-driven architecture using `projects.csv`
- Central map configuration using `map-config.json`
- Search by project ID, project name, and contractor
- Status filtering
- Contractor filtering
- Public project list
- Status-coloured project markers
- Marker popups
- Google Maps directions
- GeoJSON download
- Responsive desktop and mobile interface
- Automatic project-data validation through GitHub Actions

### Fixed

- Corrected Leaflet CSS integrity configuration
- Fixed broken and disconnected map-tile rendering
- Added Leaflet resize handling for changing browser and mobile viewport sizes
- Improved mobile map layout

### Architecture

- `projects.csv` — public project information
- `map-config.json` — map settings, statuses, and visual configuration
- `index.html` — map application and interface
- GitHub Pages — website hosting
- `.github/workflows/validate-projects.yml` — project-data validation

### Status

Stable baseline for future development of the JP Ecosystem Project Map.
