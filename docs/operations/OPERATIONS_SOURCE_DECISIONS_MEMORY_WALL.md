# Operations Source & Decision Memory Wall

**Updated 14 November 2026 (Asia/Kathmandu).** This is the Operations source/decision protocol. It does not duplicate an editable project, progress or workforce database. See the [machine ledger](../../ops/control/operations-source-decision-ledger.v1.json).

## 1. Canonical provider route — current SHEETS_V2 authority
Original files are located under [02 Website Sheets and Registers](https://drive.google.com/drive/folders/1QHxD74egNFeQAmvDJzvKmDxEQUOH3Kq6) → [01 Website Source Sheets — Edit Here](https://drive.google.com/drive/folders/1u4Rg1J3KSZRPnkjlAHOVxpWoq2skRICn).

| Fact class | Original Google Sheet (edit there) | Tab | What may be published |
| --- | --- | --- | --- |
| Public site identity, listed lifecycle status, approved coordinates | [Projects and Locations](https://docs.google.com/spreadsheets/d/1JqzjBNBCT_AAIBkuGsIR5VBOJ3_HyifdPDc7K_jF5Bo/edit) | `projects` | Row `Is Public` and quality/retired-alias checks |
| Field-level visibility and individual location/status approvals | [Website Display Choices](https://docs.google.com/spreadsheets/d/1tDpsphzARq-rk1MExU4DXC8mG_clh-0TXJwRr2qljXU/edit) | `project_publication_settings` | `Show Status`, `Show Coordinates` and related controls |
| Reported public work items | [Project Work](https://docs.google.com/spreadsheets/d/17YPRpaXIdHloH5-lzsjUpNvXLbsDfrIrlsn2jZ-7KKc/edit) | `project_work_items` | Only explicitly public reports; unverified counts do not certify progress |
| Source digests and message identifiers | [Message Sources](https://docs.google.com/spreadsheets/d/1aWHzjEK0doiUcBbqhySiA6DWCp8d-aq2I08McslilAQ/edit) | `message_sources` | Reviewed/approved pointers only |
| Reviewed instructions/notifications | [Notification Instructions](https://docs.google.com/spreadsheets/d/1ZPtTos8t9Cym_qnpiUhiyuTxndSc6sGzzv390ahAw4I/edit) | `site_notifications` | Reviewed public notices, not evidence of finished work |
| Public organization labels | [Companies and Organizations — v1.2](https://docs.google.com/spreadsheets/d/1cwubE_4nB2SAEdLu6ry80G0HeNjbBdu4X3DA6jrcQ1E/edit) | `organizations` | Only `Is Public=TRUE`, `Active=TRUE` and `VALID` organization names |
| Source registry readback | [Website Publishing and Source Directory — LIVE](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit) | `00_SOURCE_DIRECTORY` | Verify the six owning source sheet IDs; **do not publish joined tables** |

The [Website Publishing and Source Directory](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit) is a **derived navigation/joined view**. Its joined progress and readiness tables contain more source data, but are **not automatically authorized for public release**. Do not assume an old source note about Actions status represents the current deployment: check the current [Operations publisher](https://github.com/FabinGurung/jp-site-operations/actions/workflows/operations-sheets-pages.yml).

The original Google Sheets retain authority. `scripts/publish_operations.py` contains the exact ID+tab allowlist. The publisher reads those seven Sheets twice and requires an unchanged read before projecting only admitted fields to `operations.json`. PR fixtures are synthetic and cannot replace Google source reads in production.

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

## 8. Map-first site workspace and seven authenticated Sheets — 13 November 2026

**Source tree:** [02 Website Sheets and Registers](https://drive.google.com/drive/folders/1QHxD74egNFeQAmvDJzvKmDxEQUOH3Kq6) → [01 Website Source Sheets — Edit Here](https://drive.google.com/drive/folders/1u4Rg1J3KSZRPnkjlAHOVxpWoq2skRICn) → six owning workbooks (projects, publication settings, Project Work, message sources, notification instructions, organization names). The separate [02 Website Publishing folder](https://drive.google.com/drive/folders/1DRECcxUaz68mS_WPWbvReKxujmZ2O58t) contains [Website Publishing and Source Directory — LIVE](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit), whose `00_SOURCE_DIRECTORY` tab is read-only pointer validation, not an editable master fact source. This makes **seven Google workbooks read in total**; six supply approved original facts, one supplies source-directory references.

**Removed Git dependencies in running projection:** `organizations.csv` and `ops/data/project-identity-index.v0.1.json` remain in versioned Git **history and existing files**, but the new publisher does not read them at build time. The live `projects` tab supplies current project IDs; `organizations` supplies only public/active/valid labels. The directory checker confirms the exact six owning sheet IDs and fails safely on stale or missing mappings. No confidential joined tabs from the publishing workbook become public, despite expanded public source links.

**Field usability decision:** Main map becomes the top panel; the Notification Center appears below it only after choosing a site (or explicitly opening Notifications from navigation). Desktop west site navigator stays in view while scrolling within its own height; phone directory is collapsed by default. Map markers are 48px touch targets. Clicking a pin reveals its source-reviewed notices without changing the map bounds. Back to all sites, tapping empty map, or Escape dismisses details; map panning and zooming deliberately **do not** close the pane to prevent accidental dismissal. Large developer/publication summaries move into Sources & History; materials, manpower and complete task backlog stay clearly unconnected until reviewed source inputs are available.

**Standards referenced for design:** [Google Android touch target guidance](https://support.google.com/accessibility/android/answer/7101858?hl=en-GB), [Mapbox map tap vs empty-map deselection](https://docs.mapbox.com/android/maps/examples/android-view/add-interaction-to-custom-featuresets/), [Material bottom-sheet dismiss patterns](https://m1.material.io/components/bottom-sheets.html), and [NN/g Mobile Usability](https://www.nngroup.com/reports/mobile-website-and-application-usability/).

**Release process:** scoped map-first branch → synthetic phone/desktop browser QA → unchanged original Sheets double-read → GitHub Pages exact-file and public-projection verification → release note and matching tag. No source records or Drive permissions rewritten.

## 9. 14 November 2026 — iPhone navigation recovery and four-lane Extraction

User-provided iPhone screenshots showed unreachably small/clipped top navigation and raw provenance status values extending beyond screen width. **Decision**: phone uses a short sticky header with a single accessible Menu; desktop has only Map, Notifications and Extraction as the three main routes. Preserve `progress.html` and `sources.html` as accessible reference pages rather than deleting historical navigation or creating competing Google Sheet masters. On phones, 16px input/select controls prevent iOS Safari focus auto-zoom, and technical dates/status use readable language and safe wrapping. Maps and selected-site notifications remain the daily field experience.

**Four lanes:** (1) conversation intake (Slack/Discord/Telegram, source IDs), (2) original evidence and source hashes, (3) normalized/approved site instructions and work, (4) publisher projection and QA. Run 01 is a bounded recovery of the seven already registered original Sheets, **not** a new automated source ingestion. Its published `extraction-status.json` is a read-only summary of the same WIF double-read as `operations.json`; source rows and private chat text are never included. The source details and live-audit records are in [Run 01 log](EXTRACTION_WORKFLOW_RUN01.md). Sites, notification counts and dates must be source-derived.

**Versioning:** keep `v2.9.0` and archived Progress/Sources routes as rollback/reference; no original Sheet edits were made on this batch, so there is no need to mint misleading PRE/POST copies. For future new verified facts, version the same live Sheet IDs with an explicit PRE backup, row-level import, POST backup, and in-place `01_VERSION_HISTORY` before publishing. This prevents the Google Drive source-directory pointers from drifting.

**Open holds:** no direct Slack, Discord or Telegram collector in the current Pages publisher; registered message SHA-256 has not been independently recomputed from original bytes; all three public work reports remain `UNVERIFIED`; published October facts are not newly certified by a November website build.

## 10. Site updates instead of a four-lane UI — 14 November 2026

**User correction:** The Run 51 "four-in-one" reference applies to the **underlying extraction and publication method**, **not** to four visible website workstreams. Field users need to see (1) Map, (2) source-reviewed Notifications, and (3) meaningful Site updates. The old seven-link phone overlay and exposed `Conversation intake / Evidence inventory / Normalize / Publish` page were misleading. Decision: keep `/extraction.html` URL as an updated **Site updates** view for backward compatibility; remove that internal template from the public UI. Keep `/progress.html`, `/sources.html`, owner guide and memory wall as supporting historical/audit links in the footer and expandable sources panel.

**Engine stays source-backed:** A7-governed source occurrence ID → original evidence/version → human approval → normalized original Google Sheet → source-restricted double-read → `operations.json`, `extraction-status.json` and new `site-updates.json`. The last file contains **public-safe per-project interpretations** computed by GitHub Actions: reviewed notification counts and Work/Materials/Supervision categories, historical report counts and verification state, most recent source message/report date, and explicit uncertainty. The browser renders these summaries and the already approved notice text; it never privately fetches Slack, Discord or WhatsApp. A successful publish is not a new field instruction.

**Actual source audit:** [Notification Instructions / `site_notifications`](https://docs.google.com/spreadsheets/d/1ZPtTos8t9Cym_qnpiUhiyuTxndSc6sGzzv390ahAw4I/edit) holds 22 reviewed instructions (4 Work, 9 Materials, 9 Supervision), all linked to [one recorded Slack message](https://docs.google.com/spreadsheets/d/1aWHzjEK0doiUcBbqhySiA6DWCp8d-aq2I08McslilAQ/edit), source date 2026-10-26, for `PRJ-000020`. It is a reviewed instruction set, **not 22 source messages**, not automatically current, and not a proven unresolved backlog. [Project Work](https://docs.google.com/spreadsheets/d/17YPRpaXIdHloH5-lzsjUpNvXLbsDfrIrlsn2jZ-7KKc/edit) has 3 public historical reports dated 2026-10-09 without verified completion. No original Sheets edited. Future Slack/Discord/WhatsApp collectors require reviewed provider/channel connections, private originals, dedup/edits/tombstones and per-row publication grants.

**Actions simplification:** The live workflow keeps test, browser QA (only when code changes/PR, not scheduled), projection, and deploy. The eight historical, version-specific release jobs are removed from the active YAML; prior GitHub tags, releases, Actions and Drive originals remain intact. One new release verifier checks exact served Pages files, derived summary parity, source privacy and legacy Library/Astam redirects. New `v3.1.0` release only if a successful deploy matches its own commit. This is **not** a modification to A7 or sibling repositories.

**Acceptance:** test 320/390px and desktop selection/no-overlay navigation; 7-Sheet authentic readback; derived counts match `operations.json`; hidden status and private project never leak; verify served site and exact release SHA. See [v3.1.0](../releases/v3.1.0.md).

## 11. Reviewed closures and archived work, not map deletion — 14 Nov 2026

**User decision:** Completed, cancelled, no-longer-required or superseded items should be kept in a dedicated, source-backed history page—not persist as noisy operational notification/task lists, and not cause a site to disappear from the Project Map. A new secondary route [Closed & Archived Work](https://fabingurung.github.io/jp-site-operations/closed-work.html) is linked from [Site updates](https://fabingurung.github.io/jp-site-operations/extraction.html), not the three-tab top menu. The `closed-work.json` public projection is derived from reviewed original source decisions.

**Original source check:** The [Notification Instructions](https://docs.google.com/spreadsheets/d/1ZPtTos8t9Cym_qnpiUhiyuTxndSc6sGzzv390ahAw4I/edit) `Detail State` is NOT a completion field; its current values describe planning/quantity/clarification gaps. All 22 notices remain reviewed but not confirmed resolved. The [Project Work register](https://docs.google.com/spreadsheets/d/17YPRpaXIdHloH5-lzsjUpNvXLbsDfrIrlsn2jZ-7KKc/edit) has only three IN_PROGRESS unverified public reports. **Current approved archive = 0**; no live source was edited in this code-only release.

**Closure input contract:** On the SAME original `site_notifications` and `project_work_items` tabs, add (after A7 source-governed PRE snapshot): `Closure Decision`, `Closure Approved`, `Closure Date`, `Closure Reviewer`, `Closure Reason`, `Closure Evidence`, `Superseded By`. Source editors provide reviewer/date/reason for every approved closure, evidence for Completed, replacement ID for Superseded; work Completed also requires `Verification Status=VERIFIED`. Only `Closure Approved=TRUE` moves a public item into `closed-work.json`; a pending decision remains active. Never expose reviewer, free-text reason or private evidence in Pages.

**History:** Do not physically delete original Sheet rows or conflate project `Completed` with an engineer-verified work item. Reopened/changed closure decisions require an append-only change event and original-IDs PRE/POST copies, with history log in the source's governed Drive. A public static website is read-only; source changes happen in the owning Sheet, not by an unauthenticated button. GitHub release `v3.2.0` is code/UI/schema-acceptance milestone, not a fabricated field-completion release.

See [governed release decision](../releases/v3.2.0.md). The active source publisher still uses the exact seven linked original Google Sheets above.
