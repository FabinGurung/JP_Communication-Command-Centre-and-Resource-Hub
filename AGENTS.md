# Global agent/router rule (public-safe)

Central authoritative cross-provider bootstrap:
https://github.com/FabinGurung/jp-a7-system-registry/blob/main/A9_GIT_DRIVE_BOOTSTRAP.json

Read that one short machine entrypoint before new cross-repository Git/Google Drive work. Then resolve this repository's A7_MODULE.json if present and read only the relevant local owner control and current state. A7 defines semantic routing; this repository owns its code and fact classes. A Git branch is a complete repository snapshot, not a person's folder.

Never treat this public repository as the private A9 Main Library. Keep research originals, private evidence, native Docs/Sheets and compiled PDF/PPTX in their declared provider (usually Google Drive); store code, tests, schemas and version history in Git. Git PRE/POST is commit history; use additional Drive snapshots only for provider-native change safety or local control requirements.

A9 historical private governance remains binding until explicitly reconciled and safely migrated. Do not invent completion, copy private data or tokens into public GitHub, or silently bypass project-specific rules.

This file is an agent instruction pointer; it does not change ChatGPT's account-wide/system instructions or guarantee a particular client auto-loads it.

## A7 catalogue-only / Operations lane guard

**NO A7 MUTATIONS AS A SIDE EFFECT.** A7 is read-only for Operations: an index of module identity, owner, website, release/status/history links and cross-module FK pointers; not a central data or template writer. Never create/update A7 code, policies, domain schemas, AAD/CAD templates, registry records or website content without a **separately explicit A7-scoped user request**. An outdated A7 link is a local pending discrepancy, not an automatic patch. Historical Git tables such as `projects.csv` and `ops/data/current-works.json` retain their historical authority only within their declared legacy lanes. **The public Sheets V2 Operations map and project-status display are derived from the seven registered Google workbooks (six original fact owners plus read-only publishing source directory) enumerated in `scripts/publish_operations.py`, not from these legacy Git tables.** CAD/AAD templates remain owned by the respective CAD repository.

The registered `feature/daily-ops-current-work` lane requires independent validation and governed promotion. Do not open a broad PR or modify A7 as a side effect of Operations reconciliation.

## Operations Source and Decision Memory Wall — compulsory for future changes (12 Nov 2026)

- Read [`docs/operations/OPERATIONS_SOURCE_DECISIONS_MEMORY_WALL.md`](docs/operations/OPERATIONS_SOURCE_DECISIONS_MEMORY_WALL.md) and the current [machine decision/source ledger](ops/control/operations-source-decision-ledger.v1.json) before changing public Operations display, map/status behavior, code-based derivations or source joins.
- **Fetch current facts from the actual owning Google Drive/Google Sheets file**, using the exact IDs/tabs in `scripts/publish_operations.py`, before deriving operational values. See Drive folders `02 Website Sheets and Registers` and `01 Website Source Sheets — Edit Here`. The publishing directory workbook is an aggregated navigation/view, not an editable fact authority.
- Always record a bounded, dated entry in the source-decision memory wall identifying: decision/request, source book and tab and permitted fields, publisher or code path, PR/commit, tests and release/readback, and limitations/corrections. Update links and source state, do not make duplicate Google Sheets or archives just for code changes.
- Distinguish **source facts** (Sheets/Drive) from **code, tests, UX decisions** (Git) and **generated public snapshots** (Actions). Never claim UI code was “fetched from Sheets”; only its factual inputs are. Do not infer completion, progress percentages or site urgency from absence of reports.
- `Projects and Locations` `Status` is source-owned project-level classification. Apply `Website Display Choices` `Show Status` and public row admission before it can be filtered or published. `Completed` in this column is a listed status, not a signed engineering completion certificate. Under `SHEETS_V2`, never use `Project Work` report counts to decide that an entire project has finished.
- Use a registered PR-only lane. Make changes in the owner system, check privacy flags, run synthetic and live QA, then verify `main` and actual Pages readback. Never edit A7, scheduling or the Resource Library from an Operations-only authorization.

## 13 Nov 2026 — map-first and seven-source controls

- Map-first home. On-demand notifications below map; never recreate a scroll-heavy four-panel dashboard by default. Large source/coverage and readiness disclaimers belong in Sources & History and Daily Progress.
- Pin click selects site without dropping neighbor pins, changing camera or promoting reported work to completed tasks. Explicit clear button, Back control, empty map tap and Escape dismiss; pan/zoom do not dismiss unexpectedly.
- Original Google Sheets: Companies and Organizations (only active, public, valid names) replaces local Git CSV for live labels; Projects and Locations replaces historical Git JSON as the current project identity authority. Website Publishing and Source Directory / 00_SOURCE_DIRECTORY is read solely to assert six original workbook pointers, NEVER to publish its private joined tabs. The original five fact Sheets remain governed.
- See current docs/operations/OPERATIONS_SOURCE_DECISIONS_MEMORY_WALL.md and scripts/publish_operations.py for all seven exact workbook IDs and tab names.

## 14 November 2026 — mobile navigation and extraction governance

- Primary field routes are Project Map and Notifications; the new four-lane Extraction page is for human source reconciliation and publication review. Previous Progress and Sources HTML routes remain accessible reference views, not independently authoritative datasets.
- Render the phone navigation as a compact Menu with 48px touch options. Avoid unreadable technical enums, horizontally overflowing source data, and iOS Safari input zoom (16px minimum).
- First-batch extraction only reads original seven Google Sheets via read-only WIF. Do not claim a live Slack/Discord/Telegram collector or publish unreviewed chat evidence. `extraction-status.json` contains source counts, source dates and limitations; no raw message content.
- The user-provided Run 51 example inspires bounded batch/source occurrence/evidence/checkpoint separation. See `docs/operations/EXTRACTION_WORKFLOW_RUN01.md` and the existing A7 branch lane registry.

## 14 Nov v3.1 — Visible extraction is user-centered, not a methods diagram

The Run 51 extraction **process** belongs in tests, source/evidence/version registers, publisher and QA receipts, not as four visual dashboard lanes. Primary public UI: Map, Notifications, Site updates (same legacy extraction.html route). Present only derived meaning grounded in approved original Google Sheets, identify the specific source record date and review/verification state, and never infer a task is overdue or complete from a chat instruction. Preserve other routes as quiet archives; do not delete releases. The existing read-only seven-Sheet publisher must generate site-updates.json with public project-level category distributions, report verification counts, source dates and no private data. Direct chat collectors are not implied.

## 14 Nov v3.2 — source-approved closure routing

The user wants completed, cancelled, not required and superseded items OUT of current task/noise views but NOT deleted. Use separate `closed-work.html` and generated `closed-work.json`, linked from Site updates only, not added as a primary map/notification tab. Preserve project pins. Do not infer closure from Notification Detail State, overdue dates, project Completed, Project Work prose or numerical progress. Only optional approved `Closure Decision/Approved/Date/Reviewer/Reason/Evidence/Superseded By` fields in owning original Sheets can promote a reviewed, public item out of active projections; missing approval means still active; incomplete approved closure fails closed. Never publish reviewer, reason or private evidence. No original Google Sheet change was authorized in this code-only milestone; source editors must follow A7 same-ID PRE/POST and append-only audit before enabling real closures.
