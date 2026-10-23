# A9 / JP — Multi-chat project contribution contract v0.1
**Effective:** 2026-10-23 | **Mode:** SOURCE-FIRST / FAIL-CLOSED / NO CROSS-CHAT HANDOFF REQUIRED

## Principle
Any authorized project or domain chat may work directly in connected GitHub + Google Drive. Individual ChatGPT threads are operators, NOT separate authorities. A7 resolves identity/ownership; Drive stores the source and canonical operational facts; dedicated repo paths store versioned code, derived approved assets and release manifests; Actions validate/generate; Pages renders the final public-safe projection.

## Stage 1: single hub repository, project-isolated contributions
Do NOT create a new repository for every chat. Keep one JP Operations Hub/Pages website and specialist module repositories as warranted by shared engine ownership. Use short-lived branches matching **`contrib/PRJ-000029/basanti-drawings-01`**, based on a current authorized parent. Place only public-safe, reviewable non-executable metadata, Markdown, UTF-8 text or JSON under **`contributions/PRJ-000029/basanti-drawings-01/`** with a `manifest.json`. The branch is an ephemeral PR lane, not a new production branch, and does not overwrite `feature/daily-ops-current-work`.

The contributor chat itself: resolves its `project_id` and private source owner → reads the current GitHub branch registry → creates a scoped branch → writes its OWN path only → runs/observes Actions → opens a PR into the current development publication lane → checks the required validation and review conditions → merges only if authorized → reads back Actions/Pages. It does **not** ask the A9 owning chat to copy a handoff. Multiple projects can submit concurrently because they edit different paths and merge through GitHub PRs.

All raw PDFs, models, bills, personnel records, project-source photographs, Excel/ETABS/DXF binaries and nonpublic geometry/coordinates remain in Drive. Public GitHub PRs and Actions logs must never carry private provider credentials or unpublished source payloads. CI scope checks supplement, NOT replace, actual provider evidence/privacy authorization. The GitHub Pages generator must consume only merged, reviewed allowlisted public metadata.

## CONTRIBUTION v0.1 manifest — intentionally narrow
Every submission has `contributions/<project_id>/<submission_id>/manifest.json`, with these keys:
`schema_version` `project_id` `submission_id` `title` `workstream` `publication_state` `privacy_review` `engineering_status`.
Allowed `publication_state`: `PUBLIC_CANDIDATE`, `APPROVED_PUBLIC`; the former is never a public-site release. Public-ready requires `privacy_review=PUBLIC_SAFE_ATTESTED`. The PR must contain changes to ONE project submission directory only. A submitted Boolean/label of approval is NOT independent legal, engineering or privacy proof; an authorized project/source owner must inspect evidence before merging.

## Directory strategy and reuse
```
Google Drive / JP__ENTERPRISE__PRIVATE   (canonical metadata & originals)
       └── project folders / drawings, estimates, original files
GitHub / JP_Communication-Command-Centre-and-Resource-Hub
       ├── contributions/PRJ-000029/<submission>/manifest.json   (approved public metadata only)
       ├── scripts/ + .github/workflows/                          (system-owned validators/generators)
       └── Pages: derived site, single deployment lane
Peer repositories: Structural, CAD, Cost/Estimating, Scheduling (for reusable executable engines)
```
If a project asks to change a global page, release validator or workflow, it must create a **separate scoped systems PR** with explicit path-owner review, NOT sneak that edit into a project content PR. Shared module code belongs to its peer repository; the hub may link published artifacts rather than absorb the source engine. Prefer reusable `workflow_call` Actions (SHA pinned) and versioned schema inputs when specialization grows.

## Avoiding 20–30 collisions
1. Same-branch direct pushes by different chats: PROHIBITED for project contributions.
2. Unregistered long-lived project branches: PROHIBITED; ephemeral `contrib/` class is explicitly typed in branch registry.
3. A project PR touching another project's directory or shared `.github/`, `scripts/`, `ops/data/`, `map.html`, `resources/index.html`: FAIL.
4. Merge only after green independent project scope check and any required general release tests. No force pushes, history rewrites, deletion of source evidence or bypassing HOLD flags.
5. Serialize final Pages deploys using one publish workflow and concurrency group; do not run multiple websites as competing production authorities.
6. Existing 45 registered historical/active branch refs remain preserved; temporary contrib branches are tracked by namespace and PR audit, not promoted to a permanent library branch. Prune temporary branches after merge when provider tools/UI permit.

A GitHub Actions workflow named `Project chat scope and privacy QA` checks PR path isolation, manifest schemas, basic private-URL/secret patterns and file types (UTF-8 JSON/MD/TXT only). No SVG, binary, JS, or rich HTML is directly accepted in v0.1; reviewed CAD/estimation web modules need a separate higher-trust module PR. When a gated PR reaches the existing Pages branch, `build_project_contribution_directory.py` generates `contributions/index.html` in the release artifact from merged `APPROVED_PUBLIC` manifests only. These are **mechanical guardrails**, NOT replacements for provider privacy/engineering approval or GitHub branch rulesets.

## Current limits (do not misrepresent)
- `main` and `feature/daily-ops-current-work` already diverge; do not broad merge them.
- Existing `Operations Hub production` workflow deploys only from validated pushes to the development branch; project PRs don't deploy themselves.
- New independent project PR scope QA provides an INITIAL contribution entry. Project preview generation, automatic cross-module ingestion, GitHub ruleset/required-check enforcement and protected main/auto-merge need their own governed rollout. Current connector token does not have GitHub repository admin permission, so branch protection cannot be asserted as configured.
- The private JP Sheets 10-category `IMPORTRANGE` allow-access gates and Chaudhary P1 privacy hardening are separate outstanding tasks.
- Keep Basanti published PDF resource card distinct from private canon. Current `PRJ-000029` is canonical; `PRJ-000030` is retired alias; public resource catalog admission remains Issue #8.

## Operator read-first
`AGENTS.md` → `ops/control/branch-lane-registry.json` → `ops/control/multi-chat-contribution-policy.v0.1.json` → private project owner's manifest → only required repo files → independent provider readback.
