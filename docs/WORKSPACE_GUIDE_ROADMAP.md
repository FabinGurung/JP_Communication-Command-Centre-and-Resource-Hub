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

**Status:** COMPLETE — core framework implemented and provider-verified on `feature/daily-ops-current-work`. Final Phase-2 source head is included in A9 Root-11 seq48 closeout. Phase 3 remains the separate illustrated-tutorial phase.

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
- CI checks for all four depth shells, print support and route wiring;
- exact deployed GitHub Pages artifact readback confirming the complete `/guide/` hierarchy is present.

Phase-2 boundary note: the public external-browser fetch path is not available from the current execution environment, so closure relies on GitHub provider deployment SUCCESS, exact deployment-artifact readback, route/content validation in CI, and source-level print CSS/JS checks. Final illustrated visual QA belongs to Phase 3.

## Phase 3 — Illustrated operational tutorials

**Status:** COMPLETE — 15 deterministic public-safe SVG tutorial visuals are implemented, wired into the 1/3/7/15-page guides, registered in `guide/image-manifest.json`, validated in CI and rendered from the exact deployed Pages artifact on desktop and mobile with zero broken guide images or page errors.

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

Current implementation uses version-controlled SVG workflow diagrams rather than screenshots for concepts that would otherwise become stale. The visual set covers Workspace routing, Project Map identity, Site Operations, project detail, Slack→canonical reconciliation, stock-vs-consumption, readiness gates, Drive resources, Sheets projection, GitHub Actions, storage/Neon decisions, A9 governance, specialist-module routing, Pages production ownership and architecture-change thresholds.

Rendered QA evidence: deployed-artifact test rendered the 1-page guide at 1/1 visuals, 7-page guide at 7/7 visuals, 15-page guide at 15/15 visuals, and the 7-page mobile layout at 7/7 visuals; all reported zero broken images and zero page-script errors.

## Phase 4 — Deeper live integration and system-health workspace

**Status:** COMPLETE — Phase-4 PRE branch `snapshot/pre-workspace-phase4-20261006` was created before mutation. The Workspace now provides live project/status integration, system-health/connection roles, guided edit routing, normalized specialist-module ownership and stale-link enforcement while preserving `workspace/links.json` as the independent fallback/navigation directory. Final rendered desktop/mobile QA passed on the exact deployed Pages artifact.

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

Phase-4 completion evidence:
- dynamic project cards resolve Daily Ops `project_id` through `map_project_id` into `projects.csv`;
- live summary shows Daily Ops project count, NEEDS_INPUT count, HOLD/BLOCKED count and latest Daily Ops date;
- each generated card keeps project-master lifecycle/status separate from operational readiness/execution state;
- static `workspace/links.json` project cards remain unchanged as fallback navigation;
- `workspace/modules.json` defines seven canonical module owners and current repository identities;
- `workspace/edit-routing.json` defines thirteen “what do I edit?” decision routes;
- System Health exposes file-first source availability plus Drive/Sheets/Slack/SQL/Pages/PostgreSQL roles without pretending to have private provider authentication;
- stale historical repository slugs are rejected by CI outside the explicit migration note, and three JSON Schema `$id` URLs were migrated to the current Operations Hub repository/Pages URLs;
- final CI verified 28 project-master rows, 8 Daily Ops projects, 25 project-resource links, 34 JSONL events, 31 static Workspace resources, 8 live Workspace projects, 7 modules, 13 edit routes and 15 guide SVGs;
- exact deployed-artifact render QA passed on 1440 px desktop and 390 px mobile with zero script errors, 8/8 live project cards, 8/8 fallback project cards, 7/7 module cards, 13/13 edit routes, CURRENT file-first health state and no mobile horizontal overflow.

## Phase 5 — Release, governance, mobile/print QA and A9 closeout

**Status:** COMPLETE at the product/release layer — v2.0.0 is production-governed with `main` as the sole GitHub Pages deployment owner. The external Root-11 A9 registration is the final governance seal for this same release operation.

Completion evidence:
- `VERSION` = `2.0.0`, with versioned notes at `docs/releases/v2.0.0.md`;
- feature lane Phase-5 validation PASS: 12 HTML pages, 66 internal references, accessibility basics, Guide print contract, release metadata and single Pages owner;
- feature-lane deploy job is intentionally skipped;
- pre-Phase-5 and pre-main-promotion rollback branches retained;
- `main` promotion was a clean fast-forward: no divergent Main commits were overwritten;
- production run `37449481389` validated and deployed successfully from `main`;
- production Pages artifact `11404905730` digest `sha256:953c55a0ab6ac3e7a8eb01afc25066103a70a8ced3d005461952ee5e194428ef`;
- critical production Workspace/Guide/UI files and all 15 Guide SVGs are byte-identical to the Phase-4 artifact that already passed desktop + 390 px mobile rendered QA with zero script errors and no horizontal overflow;
- exact production Guide data, visuals and print CSS produced a 16-page A4 reference-guide PDF (cover + 15 guide pages); PDF render-back inspection passed at the cover, representative middle page and final page with no clipping/overlap;
- stale historical repository names remain blocked by CI outside the explicit migration note.

Acceptance: production-ready Workspace + Guide system with reproducible governance and no unresolved production source/deployment ambiguity.

## Product boundary

The Workspace/Guide are public-safe orientation and training surfaces. They must never contain secrets, GitHub tokens, database credentials, unrestricted private documents or claims that a static GitHub Pages page is a secure write-back admin backend.

A future authenticated admin application may use PostgreSQL/Neon, but the current static Operations Hub does not require a live database.
