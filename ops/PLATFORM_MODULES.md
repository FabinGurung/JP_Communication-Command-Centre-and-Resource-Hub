# JP AEC Platform — Module Ownership

## Umbrella

**JP AEC Platform**

A family of connected AEC/construction systems. The Operations Hub is the live project-experience layer; specialist repositories own deeper planning, cost, structural, drawing, research and study capabilities.

The machine-readable authority for current Workspace module identity is `workspace/modules.json`.

## Current canonical repositories

| Role | Display name | Canonical repository | Pages |
| --- | --- | --- | --- |
| Live field + web experience | **JP AEC Operations Hub** | `FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub` | `https://fabingurung.github.io/JP_Communication-Command-Centre-and-Resource-Hub/` |
| Scheduling / work / resources | **JP Scheduling Work and Resources Management** | `FabinGurung/JP_Scheduling_Work_and_Resources_Management` | `https://fabingurung.github.io/JP_Scheduling_Work_and_Resources_Management/` |
| Cost / estimation | **JP Cost Estimation** | `FabinGurung/JP_Cost_Estimation` | `https://fabingurung.github.io/JP_Cost_Estimation/` |
| Structural analysis | **JP Structural Analysis** | `FabinGurung/JP_Structural_Analysis` | `https://fabingurung.github.io/JP_Structural_Analysis/` |
| CAD / drawings | **JP Computer-Aided Drawings** | `FabinGurung/JP_Computer-Aided-Drawings` | `https://fabingurung.github.io/JP_Computer-Aided-Drawings/` |
| Research | **JP Research and Development** | `FabinGurung/JP_Research-and-Development` | `https://fabingurung.github.io/JP_Research-and-Development/` |
| Study / learning | **JP Study Hub** | `FabinGurung/JP_Study_Hub` | `https://fabingurung.github.io/JP_Study_Hub/` |

## Ownership rule

The Operations Hub owns project identity and current field operations. It does not absorb specialist-engine logic.

- scheduling, sequencing, calendars, resource planning and Primavera/open-source planning interoperability → **JP Scheduling Work and Resources Management**
- BOQ, rate analysis and cost calculations → **JP Cost Estimation**
- structural models, OpenSees/open-source analysis, verification and structural analysis reports → **JP Structural Analysis**
- drawing production/publication → **JP Computer-Aided Drawings**
- AEC/Structural and Hydropower research dissemination → **JP Research and Development**
- academic study/learning workflows → **JP Study Hub**

## Operations Hub role

The **JP AEC Operations Hub** remains the main human-facing point for real project experience:

- Slack Daily Ops input and concise field interaction
- Project Map
- Site Operations dashboard
- per-project operations pages
- Drive-backed Project Files / Engineering Documents
- Workspace and Guide
- evidence/readiness surfaced from canonical machine data

Specialist repositories may link back into the Operations Hub, but must not become competing authorities for Daily Ops truth.

## Naming / migration rule

Current repository names above are canonical for new links. Historical slugs may still redirect on GitHub, but must not be introduced into new Workspace/module documentation.

The following historical names are stale and must not be used as current ownership targets:

- `jp-ecosystem-project-map-v1`
- `jp-building-cost-estimator`
- `Project_Drawings`
- `Project-Controls-Kernel`

Any future repository rename requires a governed link audit and update to `workspace/modules.json`, this document and affected public navigation.
