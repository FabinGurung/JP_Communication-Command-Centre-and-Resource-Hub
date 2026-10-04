# JP AEC Platform — Module Naming

## Umbrella

**JP AEC Platform**

A family of connected AEC/construction systems. The Operations Hub is the live experience layer fed by real project operations; the other modules are standardized specialist systems.

## Module names

| Role | Display name | Current repository / status |
| --- | --- | --- |
| Live field + web experience | **JP AEC Operations Hub** | `FabinGurung/jp-ecosystem-project-map-v1` — current working repo; slug retained for URL stability |
| Planning / controls | **JP AEC Project Controls** | Primavera P6 / project-controls workstream; standard module |
| Cost / estimation | **JP AEC Cost Estimation** | `FabinGurung/jp-building-cost-estimator` — standard module |
| Structural analysis | **JP AEC Structural Analysis** | OpenSees structural-analysis/report workstream; standard module |
| CAD / drawings | **JP AEC CAD & Drawings** | `FabinGurung/Project_Drawings` — standard module |
| Control kernel | **JP AEC Control Kernel** | `FabinGurung/Project-Controls-Kernel` — shared governance/control module |

## Current naming rule

Do not rename existing repository slugs casually. Public GitHub Pages URLs, Slack links and cross-repo references may depend on them.

Use the display/module names above in human-facing pages now. Perform any future repository-slug rename only as a governed migration with redirect/link audit.

## Operations Hub role

The **JP AEC Operations Hub** is the main current human-facing point for real project experience:

- Slack Daily Ops input and concise field interaction
- Project Map
- Site Operations dashboard
- per-project operations pages
- Drive-backed Project Files / Engineering Documents
- evidence and readiness surfaced from canonical machine data

Primavera P6, estimation, OpenSees and CAD remain standardized specialist modules/subpages and should link into the Operations Hub without competing for operational truth.
