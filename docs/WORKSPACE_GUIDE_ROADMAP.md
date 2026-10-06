# Workspace + Guide parity roadmap

Target: bring `JP_Communication-Command-Centre-and-Resource-Hub` to the same owner-facing usability pattern as `Paila-Pilates-SOP/workspace/` and `/guide/`, while preserving the JP AEC system's stronger live Daily Ops, project, Drive-resource, Slack and GitHub governance model.

## Phase 1 — Workspace foundation and resource registry

**Status:** COMPLETE — A9 Root-11 Local/Main seq47 FINAL_CLOSED_PASS

Deliverables:

- canonical `/workspace/` directory;
- `workspace/links.json` as the editable resource directory;
- search, category, status and audience filters;
- LIVE / VERIFIED / PREVIEW / INCOMPLETE / BLOCKED state labels;
- owner / manager daily routine;
- current storage/database explanation;
- direct links to Operations Hub, project pages, Sheets, GitHub sources, Actions and specialist repositories;
- backward-compatible redirect from `workspace.html`;
- navigation links from existing Operations Hub pages;
- GitHub Actions deployment verification.

Acceptance: a user who does not know the repository tree can find the correct tool/source from one page.

## Phase 2 — Guide framework parity

**Status:** ACTIVE — core framework implemented on `feature/daily-ops-current-work`; latest framework validation run `37403514647` SUCCESS. Phase-2 A9 durable closeout is intentionally not yet performed because the phase has only just commenced.

Create the canonical `/guide/` hierarchy:

- `/guide/` — one-page quick start;
- `/guide/3-pages/` — guided first visit;
- `/guide/7-pages/` — practical daily/weekly routine;
- `/guide/15-pages/` — reference manual;
- shared `guide.css`, `guide.js` and `image-manifest.json`;
- print / Save PDF support;
- links from each guide step back to the real Operations Hub screens.

Acceptance: all four guide depths navigate and print correctly even before final illustrations are added.

Current implementation already includes:

- `/guide/`;
- `/guide/3-pages/`;
- `/guide/7-pages/`;
- `/guide/15-pages/`;
- shared `guide.css` and `guide.js`;
- `image-manifest.json` placeholder for Phase 3 visuals;
- Print / Save PDF support;
- legacy `how-to.html` redirect;
- Operations Hub / Map / Site Operations / Project-page navigation integrated to `/guide/`;
- CI checks for all four depth shells, print support and route wiring.

## Phase 3 — Illustrated operational tutorials

Create public-safe visual tutorial pages for the real JP workflow:

- project map;
- site operations portfolio;
- project detail;
- Slack → validation → canonical Daily Ops;
- material stock vs consumption;
- blockers/readiness;
- Drive-backed engineering resources;
- Sheets projections;
- Workspace/resource directory;
- GitHub Actions/deployment;
- database/storage decision model;
- A9 PRE/readback/POST concept.

Acceptance: each guide page has a matching visual, concise text and an “Open the real screen” link.

## Phase 4 — Deeper live integration and system-health workspace

Upgrade Workspace from a static directory into a live orientation console:

- derive project counts/current date from canonical JSON;
- surface GitHub deployment status where safely possible;
- link active project pages dynamically;
- show data-layer roles and connection status;
- show specialist-module ownership;
- expose safe pointers to permission-gated Sheets/Drive resources;
- add “what do I edit?” guided decision paths;
- remove stale repository/module names;
- preserve public/private boundaries.

Acceptance: Workspace answers “where do I go, what is connected, and what owns this fact?” without opening raw repository files.

## Phase 5 — Release, governance, mobile/print QA and A9 closeout

- cross-browser/mobile QA;
- accessibility review;
- link checker;
- print/PDF QA for guides;
- stale-link and old-slug cleanup;
- final Pages deployment verification;
- explicit promotion decision for `main`;
- A9 PRE → mutation → provider readback → POST;
- Root-11 Local/Main registration;
- versioned release notes.

Acceptance: production-ready Workspace + Guide system with reproducible governance and no unresolved deployment/source ambiguity.

## Product boundary

The Workspace/Guide are public-safe orientation and training surfaces. They must never contain secrets, GitHub tokens, database credentials, unrestricted private documents or claims that a static GitHub Pages page is a secure write-back admin backend.

A future authenticated admin application may use PostgreSQL/Neon, but the current static Operations Hub does not require a live database.
