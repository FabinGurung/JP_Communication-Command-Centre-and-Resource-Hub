# Global agent/router rule (public-safe)

Central authoritative cross-provider bootstrap:
https://github.com/FabinGurung/jp-a7-system-registry/blob/main/A9_GIT_DRIVE_BOOTSTRAP.json

Read that one short machine entrypoint before new cross-repository Git/Google Drive work. Then resolve this repository's A7_MODULE.json if present and read only the relevant local owner control and current state. A7 defines semantic routing; this repository owns its code and fact classes. A Git branch is a complete repository snapshot, not a person's folder.

Never treat this public repository as the private A9 Main Library. Keep research originals, private evidence, native Docs/Sheets and compiled PDF/PPTX in their declared provider (usually Google Drive); store code, tests, schemas and version history in Git. Git PRE/POST is commit history; use additional Drive snapshots only for provider-native change safety or local control requirements.

A9 historical private governance remains binding until explicitly reconciled and safely migrated. Do not invent completion, copy private data or tokens into public GitHub, or silently bypass project-specific rules.

This file is an agent instruction pointer; it does not change ChatGPT's account-wide/system instructions or guarantee a particular client auto-loads it.

## A7 catalogue-only / Operations lane guard

**NO A7 MUTATIONS AS A SIDE EFFECT.** A7 is read-only for Operations: an index of module identity, owner, website, release/status/history links and cross-module FK pointers; not a central data or template writer. Never create/update A7 code, policies, domain schemas, AAD/CAD templates, registry records or website content without a **separately explicit A7-scoped user request**. An outdated A7 link is a local pending discrepancy, not an automatic patch. Historical Git tables such as `projects.csv` and `ops/data/current-works.json` retain their historical authority only within their declared legacy lanes. **The public Sheets V2 Operations map and project-status display are derived from the five live owning Google Sheets enumerated in `scripts/publish_operations.py`, not from these legacy Git tables.** CAD/AAD templates remain owned by the respective CAD repository.

The registered `feature/daily-ops-current-work` lane requires independent validation and governed promotion. Do not open a broad PR or modify A7 as a side effect of Operations reconciliation.

## Operations Source and Decision Memory Wall — compulsory for future changes (12 Nov 2026)

- Read [`docs/operations/OPERATIONS_SOURCE_DECISIONS_MEMORY_WALL.md`](docs/operations/OPERATIONS_SOURCE_DECISIONS_MEMORY_WALL.md) and the current [machine decision/source ledger](ops/control/operations-source-decision-ledger.v1.json) before changing public Operations display, map/status behavior, code-based derivations or source joins.
- **Fetch current facts from the actual owning Google Drive/Google Sheets file**, using the exact IDs/tabs in `scripts/publish_operations.py`, before deriving operational values. See Drive folders `02 Website Sheets and Registers` and `01 Website Source Sheets — Edit Here`. The publishing directory workbook is an aggregated navigation/view, not an editable fact authority.
- Always record a bounded, dated entry in the source-decision memory wall identifying: decision/request, source book and tab and permitted fields, publisher or code path, PR/commit, tests and release/readback, and limitations/corrections. Update links and source state, do not make duplicate Google Sheets or archives just for code changes.
- Distinguish **source facts** (Sheets/Drive) from **code, tests, UX decisions** (Git) and **generated public snapshots** (Actions). Never claim UI code was “fetched from Sheets”; only its factual inputs are. Do not infer completion, progress percentages or site urgency from absence of reports.
- `Projects and Locations` `Status` is source-owned project-level classification. Apply `Website Display Choices` `Show Status` and public row admission before it can be filtered or published. `Completed` in this column is a listed status, not a signed engineering completion certificate. Under `SHEETS_V2`, never use `Project Work` report counts to decide that an entire project has finished.
- Use a registered PR-only lane. Make changes in the owner system, check privacy flags, run synthetic and live QA, then verify `main` and actual Pages readback. Never edit A7, scheduling or the Resource Library from an Operations-only authorization.
