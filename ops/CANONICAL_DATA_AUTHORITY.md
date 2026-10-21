# Canonical Data Authority

> **Map data source migration (2026-10-21):** The 14 map reference tables were imported, cell-by-cell verified and are now owned for human editing by the private [Google Sheets map workbook](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit). The public website renders reviewed JSON projections at `ops/data/map-sheets-public.v1/*.json` instead of fetching the 14 legacy CSV files. This publication is **not** an automatic Google Sheets sync: edited rows need an explicit review and re-projection. The root CSV files remain frozen rollback/baseline inputs, not new-edit authority. This does not change the separate Daily Ops canonical JSON, PK/FK DDL, original engineering files or event history. See `docs/operations/MAP_GOOGLE_SHEETS_SOURCE_AND_PUBLICATION_v1.md`.


This repository is the canonical machine-data home for the JP enterprise Project Map and Daily Ops system.

**Namespace separation:** JP owns the operational enterprise and real company/project workflow. AEC represents the independent thesis hypothesis, research/experiments and evidence. AEC may cite an approved JP case study but does not own or rewrite live JP operational records. Historical `JP_AEC` identifiers are compatibility aliases, not shared authority.

The goal is simple: **edit a fact once at its owning canonical layer, then derive every presentation/projection from it.**

## 1. Canonical layers

| Layer | Canonical file | Owns |
| --- | --- | --- |
| Relational / relationship authority | `ops/schema/daily-ops-postgres.sql` | PK/FK relationships, normalized table structure, constraints and lifecycle/readiness separation. This is text DDL; no live PostgreSQL server is required. |
| Project-master current values | Google Sheets map workbook → `projects` worksheet | Project identity, company/legacy codes, lifecycle/status, coordinates and public project attributes. Published projection: `ops/data/map-sheets-public.v1/projects.json`; `projects.csv` retained as legacy rollback. |
| Daily Ops current values | `ops/data/current-works.json` | Today's work, readiness, materials, blockers, progress, evidence references and projection state. |
| Project resource links | `ops/data/project-resources.json` | Normalized project → Google Drive folder/file relationships. Drive remains authority for the actual file bytes and access permissions. |
| Scoped resource-name equivalences | `ops/data/resource-project-name-aliases.v1.0.json` + `ops_project_resource_name_aliases` in `ops/schema/daily-ops-postgres.sql` | Exactly six user-confirmed `resource_id` ↔ `project_id` labels for P001/P002, not person-name equality or construction approval. |
| Append-only history | `ops/events/daily-ops-events.jsonl` | Operational and governance events. Existing events are not rewritten. |
| Controlled map configuration | `map-config.json` | Allowed public map statuses and presentation configuration. |

## 2. Downstream surfaces

These are **not** independent truth stores:

- GitHub Pages / Project Map
- Site Operations dashboard
- Per-project Site Operations pages
- Google Sheets projection tabs
- Slack messages

They must be derived from, or reconciled back to, the canonical files above.

## 3. Where humans should edit

For a project-master correction such as:

- Construction vs Maintenance vs Completed
- project identity/name
- coordinates
- company project code
- public project attributes

edit the **`projects` worksheet** of the linked Google Sheets map master. Before publishing, run source PK/FK, publication and website validation and update its reviewed JSON projection. The old `projects.csv` must not be edited as a new data source.

For Daily Ops current state, edit/admit into **`ops/data/current-works.json`** and append the corresponding event to **`ops/events/daily-ops-events.jsonl`**.

For engineering-file access, preserve the actual PDF/DWG/ETABS/CAD/source file in **Google Drive** and edit only its normalized project relationship/link in **`ops/data/project-resources.json`**. Never copy the engineering file into the public repository merely to make the website render it.

Do not edit HTML to change factual data. Do not edit a downstream Google Sheet merely to make a project-master fact appear correct.

## 4. Input surfaces, canonical facts and public projections

The 14 map reference datasets have a single private native Google Sheets master. Do not independently edit their frozen GitHub CSV rollback copies. Daily Ops, resource links and historical events remain owned by their separately governed repository machine records.

```text
Google Sheets map master (private, 14 tabs)
          ↓ authenticated operator readback
validated source rows, PK/FK + publication/privacy review
          ↓
ops/data/map-sheets-public.v1/*.json (reviewed public JSON, 14 tables)
          ↓
map-config.json → assets/js/app.js → GitHub Pages map

Separately:
admitted Daily Ops evidence → ops/data/current-works.json
                           → ops/events/daily-ops-events.jsonl
Drive original files → ops/data/project-resources.json (links only)
Relational constraint specification → ops/schema/daily-ops-postgres.sql
```

Field inputs, Slack, Forms and other operational Sheets remain unadmitted observations until their designated owning layer validates and admits them. Only the dedicated map-master workbook owns edits to the migrated project reference tables.

## 5. Google Drive and publication rule

- The map-master workbook `17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4` is **private** and authoritative for the 14 map tables. It is not a publicly readable API.
- The live static map fetches **reviewed JSON projections**, not the private workbook and not CSV.
- A Sheet edit does **not** automatically refresh the public JSON. An authorized operator must read back the changed cells, validate PK/FK, coordinates, schema, publication controls and restricted fields, then commit reviewed projections to the registered working branch.
- GitHub Actions validates the branch and deploys to the existing Pages URL only after validation succeeds. The actual deploy SHA must be checked.
- Existing location registers, contacts, worker records, finance and Drive engineering originals are separate; they are not automatically imported into this map workbook.
- A UI-only `is_public` filter is not security for material already committed to public JSON. Never include restricted information in any public projection.
- No OAuth credentials, service-account keys, or private source records outside approved projections belong in this public repository.

## 6. Conflict rule

If a map Sheet value and its GitHub reviewed JSON differ:

1. Read the native master, its provenance, publication settings and last successful projection commit.
2. Confirm whether the Sheet edit was approved and eligible for public disclosure.
3. Repair the **owning Sheet value**, or regenerate the vetted public JSON from approved master cells; do not revise `projects.csv` as a competing authority.
4. Preserve the previous public JSON commit as rollback, and verify Actions tests plus actual Pages deploy.
5. For **non-map** Daily Ops or resources, resolve conflict against that dataset's separate canonical JSON/JSONL contract, not against the map workbook.

## 7. Current lifecycle examples

- P004 / PRJ-000004 / FBL-003 / 16 Yamuna Pun Adai → **Maintenance**
- P005 / PRJ-000005 / FBL-004 / 30 Sabitri Giri / Dipti Giri → **Construction**

Lifecycle is distinct from Daily Ops readiness and execution status.

## 8. Repository-control authority

Operational data authority and Git branch authority are separate concerns.

The compulsory branch/lane control files are:

- `ops/control/control-system.json` — repository-local Main / Local / Lane Library contract and required read order.
- `ops/control/branch-lane-registry.json` — stable logical branch IDs, active/archive status, frozen archive SHAs and legacy-alias resolution.
- `ops/control/BRANCH_LANE_CONTROL.md` — human-readable branch/lane operating rule.

Before any repository mutation, resolve the intended branch through the registry. An unregistered branch is not an authorized working lane. Archived branches are frozen and legacy aliases must not receive new work.

## 9. Slack source archival and company rollups

The existing **private A9 Slack Recovery Archive** is the durable destination for original multilingual Slack message text in JSONL, associated normalized JSON, thread/file manifests and archive readback. The public Operations GitHub repository is the derived, properly classified machine-data/control layer, **not a raw Slack dump**. The A9 Slack Control Registry owns private company/project channel routing. Read both Rohini (REB) and Fishtail (FBL) company discussion channels, and include private project channels not yet in public projects.csv as unresolved coverage gaps, not silently skipped sites. Keep private financial/personnel/engineering data outside GitHub Pages. See `ops/control/DAILY_SLACK_WEB_CYCLE.md` for collection-window, archive, source-admission, publication and output gates.
