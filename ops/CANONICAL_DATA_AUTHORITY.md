# Canonical Data Authority

This repository is the canonical machine-data home for the JP Ecosystem Project Map and Daily Ops system.

The goal is simple: **edit a fact once at its owning canonical layer, then derive every presentation/projection from it.**

## 1. Canonical layers

| Layer | Canonical file | Owns |
| --- | --- | --- |
| Relational / relationship authority | `ops/schema/daily-ops-postgres.sql` | PK/FK relationships, normalized table structure, constraints and lifecycle/readiness separation. This is text DDL; no live PostgreSQL server is required. |
| Project-master current values | `projects.csv` | Project identity, company/legacy codes, lifecycle/status, coordinates and public project attributes. |
| Daily Ops current values | `ops/data/current-works.json` | Today's work, readiness, materials, blockers, progress, evidence references and projection state. |
| Project resource links | `ops/data/project-resources.json` | Normalized project → Google Drive folder/file relationships. Drive remains authority for the actual file bytes and access permissions. |
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

edit **`projects.csv` only**.

For Daily Ops current state, edit/admit into **`ops/data/current-works.json`** and append the corresponding event to **`ops/events/daily-ops-events.jsonl`**.

For engineering-file access, preserve the actual PDF/DWG/ETABS/CAD/source file in **Google Drive** and edit only its normalized project relationship/link in **`ops/data/project-resources.json`**. Never copy the engineering file into the public repository merely to make the website render it.

Do not edit HTML to change factual data. Do not edit a downstream Google Sheet merely to make a project-master fact appear correct.

## 4. Input surfaces are different from truth

Slack, Forms, or designated Google Sheets input cells may originate observations or requests.

Flow:

```text
field input / provider evidence
        ↓
validation + admission
        ↓
canonical GitHub machine data
  ├─ projects.csv
  ├─ current-works.json
  ├─ project-resources.json
  ├─ daily-ops-events.jsonl
  └─ SQL relationship contract
        ↓
downstream projections
  ├─ Project Map / GitHub Pages
  ├─ Site Operations
  ├─ Google Sheets
  └─ concise Slack follow-ups
```

An input becomes operational truth only after admission to the canonical machine layer.

## 5. Google Drive rule

Google Drive/Sheets is a **projection and/or controlled input surface**, not the project-master authority.

Project lifecycle must not be separately maintained in Drive.

Current state:

- GitHub Pages deployment is automatic from the governed GitHub branch through GitHub Actions.
- Google Sheets projection is governed and downstream, but a fully automatic GitHub → Google Sheets projection adapter is **not yet implemented for every projection**.
- Until that adapter is implemented, A9/ChatGPT must project canonical changes into any Sheet that still requires a materialized copy, with PRE/readback/POST and no reverse promotion from Sheet to canonical truth.

## 6. Conflict rule

If GitHub canonical data and a downstream projection disagree:

1. verify the canonical owning file and evidence;
2. correct the canonical file if needed;
3. regenerate/reconcile the projection;
4. never treat the projection as authority merely because it is easier to edit.

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
