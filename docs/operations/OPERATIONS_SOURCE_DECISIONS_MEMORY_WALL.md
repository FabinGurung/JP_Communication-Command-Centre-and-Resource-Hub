# Operations Source & Decision Memory Wall

**Updated 12 November 2026 (Asia/Kathmandu).** This is the Operations source/decision protocol. It does not duplicate an editable project, progress or workforce database. See the [machine ledger](../../ops/control/operations-source-decision-ledger.v1.json).

## 1. Canonical provider route — current SHEETS_V2 authority
Original files are located under [02 Website Sheets and Registers](https://drive.google.com/drive/folders/1QHxD74egNFeQAmvDJzvKmDxEQUOH3Kq6) → [01 Website Source Sheets — Edit Here](https://drive.google.com/drive/folders/1u4Rg1J3KSZRPnkjlAHOVxpWoq2skRICn).

| Fact class | Original Google Sheet (edit there) | Tab | What may be published |
| --- | --- | --- | --- |
| Public site identity, listed lifecycle status, approved coordinates | [Projects and Locations](https://docs.google.com/spreadsheets/d/1JqzjBNBCT_AAIBkuGsIR5VBOJ3_HyifdPDc7K_jF5Bo/edit) | `projects` | Row `Is Public` and quality/retired-alias checks |
| Field-level visibility and individual location/status approvals | [Website Display Choices](https://docs.google.com/spreadsheets/d/1tDpsphzARq-rk1MExU4DXC8mG_clh-0TXJwRr2qljXU/edit) | `project_publication_settings` | `Show Status`, `Show Coordinates` and related controls |
| Reported public work items | [Project Work](https://docs.google.com/spreadsheets/d/17YPRpaXIdHloH5-lzsjUpNvXLbsDfrIrlsn2jZ-7KKc/edit) | `project_work_items` | Only explicitly public reports; unverified counts do not certify progress |
| Source digests and message identifiers | [Message Sources](https://docs.google.com/spreadsheets/d/1aWHzjEK0doiUcBbqhySiA6DWCp8d-aq2I08McslilAQ/edit) | `message_sources` | Reviewed/approved pointers only |
| Reviewed instructions/notifications | [Notification Instructions](https://docs.google.com/spreadsheets/d/1ZPtTos8t9Cym_qnpiUhiyuTxndSc6sGzzv390ahAw4I/edit) | `site_notifications` | Reviewed public notices, not evidence of finished work |

The [Website Publishing and Source Directory](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit) is a **derived navigation/joined view**. Its joined progress and readiness tables contain more source data, but are **not automatically authorized for public release**. Do not assume an old source note about Actions status represents the current deployment: check the current [Operations publisher](https://github.com/FabinGurung/jp-site-operations/actions/workflows/operations-sheets-pages.yml).

The original Google Sheets retain authority. `scripts/publish_operations.py` contains the exact ID+tab allowlist. The publisher reads those five Sheets twice and requires an unchanged read before projecting only admitted fields to `operations.json`. PR fixtures are synthetic and cannot replace Google source reads in production.

## 2. Status-filter decision — 12 November 2026
Connected live source readback (the above two original Sheets, not a Git fixture) observed **29 public projects**, plus retired alias `PRJ-000030` excluded. Project status: `Construction` 7, `Completed` 19, `Approval` 1, `Maintenance` 1. The final public project `PRJ-000029` has `Show Status = FALSE` and is included as **Not stated**; publishing its underlying status is prohibited. These values are point-in-time, **not** a hardcoded UI count.

**Decision:** On narrow screens, use keyboard-accessible 44px+ touch buttons in a single horizontal-scroll row. On desktop, use a select dropdown. Both controls have the same selected status value and filter the same source-backed map/site list/report/instruction projection. Keep `All`, `Construction`, `Completed`, `Approval`, `Maintenance` and `Not stated/other`. Never drop unknown status projects or silently place them in Completed. Direct project selection resets the status filter, so a user cannot accidentally combine contradictory filters and see an empty map.

**Critical distinction:** The project status `Completed` is a **register listing** and often has no independent engineer sign-off in the Sheet. It is not an activity completion certificate or a derived estimate. Project Work currently has three publicly permitted **IN_PROGRESS** report rows (dated 9 Oct). Work completion cannot be inferred from those reports, and a full task backlog is not yet connected.

## 3. What “derived from sources” means
1. **Facts**: read from each exact Google Sheets/Drive owning object under active authority and privacy rules. Record workbook ID, tab, allowed fields, row identifiers and source date if relevant.
2. **Decisions and code**: created as versioned Git files/PRs; document user request, implementation, trade-offs and actual QA. A UI CSS file is not itself an artifact fetched from Sheets, but the status labels and values it displays must be traceable to the Sheets.
3. **Projection**: Google Workload Identity read-only double-read → reviewed `operations.json` → GitHub Pages. No second editable factual database.
4. **Source updates**: change original Sheet; rerun/review Actions and compare served Pages. Save version/revision and correction history in owning provider; never retroactively rewrite old Git snapshots to imply different historical facts.
5. **Privacy**: disallow private photos, direct worker/payroll records, financial amounts and private coordinates. Retired alias `PRJ-000030` must never return as an active public site.

## 4. Decision/history ledger
| Date | Decision and affected files | Evidence / status |
| --- | --- | --- |
| 2026-11-11 | Astam land buyer resources migrated from Operations to Library; Operations routes redirect. `scripts/publish_operations.py`, cross-site URLs. | [Operations v2.6.0](https://github.com/FabinGurung/jp-site-operations/releases/tag/v2.6.0), [Library v1.4.0](https://github.com/FabinGurung/jp-field-desk-library/releases/tag/v1.4.0) |
| 2026-11-12 | Small mobile status chips vs desktop dropdown, source-approved values, status-hidden fallback, filter sync. `publication/operations/index.html`, `app.js`, `styles.css`, test/QA files. | [PR #35: Chromium QA passed](https://github.com/FabinGurung/jp-site-operations/actions/runs/43118856852); production release verification pending |
| 2026-11-12 | Formal source decision memory wall, linked live HTML, machine ledger and local operator rules. `AGENTS.md`, this document, `ops/control/operations-source-decision-ledger.v1.json`. | [PR #35: Chromium QA passed](https://github.com/FabinGurung/jp-site-operations/actions/runs/43118856852); production release verification pending |

## 5. Future update template
For *every* new Operations decision or derived data artifact, append one dated ledger entry (without creating a new source authority) recording:
- **Request and decision** / status `PROPOSED`, `PR_QA_PENDING`, `RELEASED` or `ON_HOLD`.
- **Fact source(s)**: original owning workbook ID, tab, key field, visibility flags, snapshot/readback date and any remaining warnings.
- **Code path(s)** and derived output path(s), source vs derived roles, PR/merge SHA and release tag.
- **QA**: unit tests, mobile/desktop interactions, successful authentic Google Sheets readback and exact Pages verification; record actual failures rather than claiming complete.
- **Rollback/retention**: Git history plus original Google revisions; old client links remain redirects.

## 6. Open holds
- More detailed work-completion and remaining-task counts require a verified, issued task register from the Scheduling/Project Work owner. A project-level Completed label is not activity-level QA.
- Material/equipment/crew demand maps await approved aggregation contracts under [issue #34](https://github.com/FabinGurung/jp-site-operations/issues/34).
- Corrections, revision supersession, retractions and provider-modified-time handling remain [issue #30](https://github.com/FabinGurung/jp-site-operations/issues/30).
- No site on the mobile UI should silently disappear because its public status is withheld.

## 7. Navigation and Notification Center decision — 13 November 2026

User requested a **hybrid multi-page website** in place of one long scrolling dashboard: two related panels may coexist on the home page, while other subjects have internal, dedicated routes. This is different from external navigation to the independent Field & Desk Library.

| Navigation item | Route | What it owns |
| --- | --- | --- |
| Notification Center | `/#notifications` (home, first panel) | Reviewed instruction cards, source date, recorded due date, category and site filter |
| Project Map | `/#map` (same home page, second panel) | Approved site pins, status filters and map layers; pin selects site notification desk |
| Daily Progress | `/progress.html` | Independently routed public Project Work reports, date/site filters and seven-date trend |
| Sources & History | `/sources.html` | Independent route for Google source dates, fact authority, privacy and release history |
| Owner Guide | `/owner-help.html` | Operator instructions |
| Resource Library | Separate `jp-field-desk-library` website | Client documents, Astam feasibility, resources |

**Authoritative source input**: already approved `Projects and Locations` + `Website Display Choices` provide public project selection; `Notification Message Sources` + `Notification Instructions` provide approved cards; `Project Work` provides report cards. `scripts/publish_operations.py` continues to double-read the five owning Sheets via read-only WIF and generate one public `operations.json`. No new source master or raw message ingestion is introduced.

Notifications are **reviewed** public instructions in `Work`, `Materials`, or `Supervision` categories. The current public projection includes no source-certified active/resolved field. Therefore the UI cannot label them “outstanding,” “overdue,” “completed,” or “closed” based on date or silence. The site-level notification count is a count of *published reviewed rows*, not verified actionable tasks. Changes to their content, due dates or resolution require the owning approved source.

`#progress` and `#sources` historical bookmarks on the old home page are mapped to the new internal routes; the older `site-operations/history.html` compatibility route is also moved to `progress.html`. Astam and Field & Desk URLs remain external redirects, not duplicates.

**Versioned code paths:** `publication/operations/{index.html,app.js,styles.css,progress.html,progress.js,sources.html,sources.js}`, `scripts/{publish_operations.py,test_ops_publication.py,status_filter_browser_qa.cjs}`, release `docs/releases/v2.8.0.md`.

**QA and evidence:** guarded PR lane `feature/notification-first-routes-r5-20261113`; synthetic source-safe desktop/mobile browser QA plus exact authenticated Pages deployment parity required. Status: pending QA at decision time; commit and release receipts will be provided after publication.
