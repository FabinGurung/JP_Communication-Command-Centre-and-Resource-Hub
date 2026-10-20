# JP AEC website — complete live skeleton and editing levels

**Registry ID:** `A9_PUBLIC_WEBSITE_PAGE_SECTION_TREE_20261020`  
**Arc:** Manual Communication, Field Resources, Memory Poster Board (post v2.2.0)  
**Frozen release:** `v2.2.0` (unchanged)  
**Governed working branch:** `feature/daily-ops-current-work` → validated fast-forward → `main`

This documents **21 active public HTML page routes**, plus three compatibility URLs. This is a website tree, not a folder of private Google Drive data. Historical archived HTML, archived CSS/JS, frozen branches, generated screenshots and release artifacts are intentionally not active pages.

## Page hierarchy with stable IDs

```text
L0 JP AEC Operations Hub  [ROOT /]
|
+-- L1 HOME                 A9-PAGE-HOME              /index.html
|    +-- L3 Overview, hero, destination navigation, project snapshot
|
+-- L1 MAP                  A9-PAGE-MAP               /map.html
|    +-- L3 A9-MAP-01        Public location map, markers, cluster/filter controls
|
+-- L1 DAILY CHECKLIST      A9-PAGE-CHECKLIST         /site-operations.html
|    +-- L3 A9-CHK-01        Slack-authored, manually published site instructions (empty until reviewed)
|    +-- L3 A9-CHK-02        Personal browser-local checklist (unchanged)
|
+-- L1 PROGRESS             A9-PAGE-PROGRESS          /site-operations/history.html
|    +-- L3 A9-PRG-01        Verbatim source-message feed (derived review only on explicit user prompt)
|    +-- L3 A9-PRG-02        Existing 37-source historical report (preserved)
|    +-- L3 A9-PRG-03        Project-specific drawing / revision status
|
+-- L1 RESOURCES            A9-PAGE-RESOURCES_DESK    /resources/
|    +-- L2 DESK            A9-RES-01    Project drawings, estimates, calculations (46 existing references)
|    +-- L2 FIELD           A9-RES-02    /resources/field/
|         +-- L3 Contacts         3 private original Sheets (no public phone rows)
|         +-- L3 Issues           Sharada site issue and potential backcharge (not approved debt)
|         +-- L3 Attendance       Hari site/team status, private person/date detail
|         +-- L3 Materials        PPC / OPC / movement / stock / site progress
|         +-- L3 Visits           Two private personnel visit/expense books
|         +-- L3 Locations        Fishtail and Rohini site coordinate Sheets (join by project_id)
|
+-- L1 DEVELOPER WORKSPACE  A9-PAGE-DEV_WORKSPACE      /workspace/
|    +-- L3 A9-DEV-01        Platform status and CI/development controls
|    +-- L3 A9-DEV-02        Embedded Memory Poster Board (historical / Discord hold warning)
|    +-- L2 BACKLOG         A9-PAGE-DEV_BACKLOG        /workspace/backlog/
|    +-- L2 CONTROL TOWER   A9-PAGE-CONTROL_TOWER     /controls/
|         +-- Memory Poster also has an independent L1 destination
|         +-- A9-PAGE-CONTROL_STORAGE   /controls/storage.html
|         +-- A9-PAGE-CONTROL_ARCHIVE   /controls/archive-formats.html
|    +-- L2 PENDING          A9-PAGE-PENDING           /pending/
|
+-- L1 MEMORY POSTER        A9-PAGE-CONTROL_MEMORY    /controls/memory-wall.html
|    +-- L3 A9-MEM-01        L0–L5 colorful hierarchy poster
|
+-- L1 HOW-TO               A9-PAGE-HOWTO             /guide/
|    +-- L2 3-page guide    A9-PAGE-HOWTO_3           /guide/3-pages/
|    +-- L2 7-page guide    A9-PAGE-HOWTO_7           /guide/7-pages/
|    +-- L2 15-page guide   A9-PAGE-HOWTO_15          /guide/15-pages/
|
+-- L2 SITE OPERATIONS      [under Checklist / Progress tools, NOT extra primary tab]
     +-- A9-PAGE-OPS_COORDINATION   /site-operations/coordination.html
     +-- A9-PAGE-OPS_QUESTIONS      /site-operations/questions.html
     +-- A9-PAGE-OPS_SCHEDULE       /site-operations/schedule.html
     +-- A9-PAGE-OPS_PROJECT        /site-operations/project.html?project=P001

L2 LEGACY COMPATIBILITY URLs (retain, do not put back into primary menu):
    /current-works.html     /how-to.html     /workspace.html

ARCHIVED CONTENT (frozen / never uninstall by deleting):
    ops/99_VERSION_ARCHIVE/
    site-operations/99_VERSION_ARCHIVE/
    assets/css/99_VERSION_ARCHIVE/
    assets/js/99_VERSION_ARCHIVE/
```

## Levels: install, uninstall and prompt precisely

| Level | Defines | How to request a change |
|---|---|---|
| **L0** Website deployment | Domain, Pages, theme, branch governance | “Change L0 theme shell without changing project facts.” |
| **L1** Primary navigation | Home + Map, Checklist, Progress, Resources, Developer Workspace, Memory Poster, How-To | “Move A9-PAGE-PROGRESS from main nav to More Tools.” |
| **L2** Departments and child pages | Desk/Field, Guides, Control Towers, project views | “Uninstall the navigation link to A9-PAGE-OPS_SCHEDULE; keep its code and source.” |
| **L3** Named sections inside a page | A9-CHK-01, A9-PRG-02, A9-RES-02, etc. | “Replace the empty state in A9-CHK-01, preserving CHK-02.” |
| **L4** Specific UI components | cards, filters, forms, buttons, map marker, embedded poster | “Change the mobile selector in A9-RES-02 at L4, no other page.” |
| **L5** Data sources and schemas | projects.csv, public-reviewed JSON, private Drive/Sheets originals | “Change the L5 schema only after exact source and FK QA.” |

**Install** = add an L2 page or L3 section, register ID + route + owner + shared theme, link from an L1 department, validate sources/privacy, run browser CI and publish.  
**Uninstall** = hide/deactivate visible links and renderers; never delete original files, historical data, archived routes or database rows. Keep reversible Git history and source refs.  
**Move** = change parent L1/L2 and links; do not regenerate resource IDs or move original Drive bytes.  
**Archive** = mark inactive, retain backing file/readme and exact Git SHA, de-link from current UI; modify frozen tags never.

## Source layer boundaries

- `projects.csv` is project identity authority. Map and resource locations join using exact project ID.
- `ops/data/project-resources.json` owns existing project-to-Drive links. Desk display: `ops/data/resource-catalog-normalized.v0.1.json`.
- `ops/data/a9-field-source-catalog-public.v1.0.json` records **ten category-only source descriptors**, with no original Sheet URLs, phone values or private rows.
- `ops/data/a9-published-checklist-public.v1.0.json` holds only manually reviewed, publicly approved Slack-authored instructions. Initially **0**. The personal browser checklist is not overwritten.
- `ops/data/progress-report-public.v0.2.jsonl` contains **37 frozen public-safe historical items**. Additional-review ledger `ops/data/a9-reviewed-progress-public.v1.0.json` starts with **0**; never duplicate 37.
- Original Slack/Discord messages, private Google Sheets, employee attendance, expenses and source images are controlled in the original provider / restricted Drive. GitHub Pages is public, *not an access-control system*.
- Discord collector remains on hold; no timer/schedule created.
- `docs/operations/a9-manual-source-reconciliation-v1.md` defines the optional user-triggered ingestion procedure.

## Existing technical architecture

```text
GitHub repository and versioned main branch
+-- Root *.html and nested pages            L1/L2 physical presentation
+-- assets/css/jp-theme-tokens.css           L0 common palette
+-- assets/css/jp-botanical.css              L0 decoration
+-- assets/css/site-shell.css                L1 shared navigation
+-- assets/js/site-shell.js                  L1 navigation and context routing
+-- assets/css/a9-ui-extensions.css          L3 new panels only
+-- assets/js/a9-*.js                         L4 new read-only renderers
+-- ops/data/                                 L5 controlled public-safe projections
+-- ops/schema/                               L5 normalized PK/FK text DDL
+-- ops/control/                              L0-L5 controls and page registry
+-- ops/events/                               Append-only governance audit
+-- scripts/ + .github/workflows/             CI/Pages and release automation
+-- docs/                                     How-To, release notes, manual prompt and this tree
```

## Change log and rollback

This page registry is a **post-v2.2.0 development change**, not a new release. Do not modify frozen `v2.2.0`. The latest working branch is validated, fast-forwarded to `main` and the Git SHA verified before treating the new route as deployed.

Original botanical theme, source IDs, current-works and original 46 resource pointers remain preserved. Historical Discord/poster instructions are labelled as legacy and never used as active collection instructions.

## Revised L1 poster and ten L3 Field dashboards (20 October 2026)

- Memory Poster is now an L1 navigation destination, not only an L2 Control Tower link; L3 panel `A9-MEM-01` is the colorful visual level-tree.
- Field Resources is L2; every Sheet has its own named L3 dashboard blueprint `A9-FLD-01` to `A9-FLD-10`; L4 are calendars, charts, filters and detail drawers. See `ops/control/a9-field-visualization-plan.v1.0.json` for all display choices. L5 remains the original Sheet and normalized hidden fact tables.
- Progress `A9-PRG-01` displays reviewed, approved-public *verbatim source messages*. Interpretation and summary require a later explicit user request; the 37-entry historical projection is retained unchanged.
- Publication is separate from source branch identity: Actions may deploy from the governed testing lane to the **same** Pages URL, but un-deployed branches do not change the public website automatically.

## L3 Field dashboard Google Sheets source links (2026-10-21)

At user request, each L3 Field Resources dashboard (`SRC-01`–`SRC-10`, `A9-FLD-01`–`A9-FLD-10`) now contains an **Open secure Google Sheet ↗** reference. The exact 10 link URLs are maintained in `ops/data/a9-field-source-links-public.v1.0.json` and keyed by the existing stable source IDs. These direct URLs and Sheet IDs are visible in the public static repository and website with explicit user authorization; their contents, native permissions, phone numbers, attendance, expenses, bill media and historical data are **not** copied or altered. External links open in a new tab and require whatever permission the Google Sheets owner has granted. Public GitHub Pages does not authenticate or authorize access to original Sheets. No inline iframes or public data mirrors are created.
