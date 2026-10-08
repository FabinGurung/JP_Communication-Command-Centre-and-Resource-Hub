# Daily Slack + Web Ops — governed data cycle (v1.0)

**Effective:** 2026-10-08 NPT. **Status:** process contract, not proof that raw capture or automation has completed. Source-of-truth policy remains split between private A9 Drive archive and the public-safe structured Operations repository.

## Date window and replay safety
Every eligible company/project channel is scanned **from the last provider-read, per-channel high-water message timestamp through the run's recorded cutoff**. Include new replies inside existing threads, not only new top-level messages. If the cursor is missing, read a bounded older window and flag partial coverage. Re-read overlap safely by stable `workspace_id + channel_id + message_ts` and never invent timestamps. A report dated October 8 may contain Oct 7 facts and earlier unresolved carry-forward, but those must be labeled; messages created after its capture cutoff are not included.

## Machine-readable input and truth
The existing A9 Slack Recovery Archive in PRIVATE Google Drive already defines raw UTF-8 JSONL and normalized JSON, relational/PostgreSQL restoration and attachment manifests. **Reuse it**; do not create a duplicate archive. Historical archive B004 has outstanding recovery/deep-file-binary debt, and a past source-read is not proof of fully current daily capture. Preserve original English/Nepali/mixed wording in the restricted raw archive, and attach a separate normalization/classification without changing the original. Archive capture `!=` engineering/site fact acceptance.

The Operations GitHub public repository owns **only appropriately public-safe** machine projections and cross-references: `projects.csv`, `ops/data/current-works.json`, `ops/data/project-resources.json`, `ops/events/daily-ops-events.jsonl`, and SQL DDL in `ops/schema/daily-ops-postgres.sql`. Never commit private raw Slack transcripts, personal/contact details, restricted engineering evidence or private finance data. A private company project portal needs authenticated backend access later.

## Company and site coverage
Resolve current routes from the private Slack Control Registry rather than hardcoding the roster. Project-channel trackers remain project-specific. **Both REB and FBL discussion channels must be read each run** and each gets a concise, separate company-level summary when permitted by the current Slack send controls. REB currently includes Bishal Paija and at least two other private project discussions: One Bay/Ramachandra Devkota and Ashok Adhikari. The latter two are not presently represented in the 28-row public Operations master, so they are **coverage gaps** rather than nonexistent projects. Do not fabricate a public project ID, status or website page; reconcile A9 project identities first.

## Publication order
1. Read live A9 Slack routing, private archive controls/cursors, project identities and current GitHub state.
2. Capture Slack channels and relevant threads to the **existing private Drive raw archive**, if authorized provider write/readback is possible; otherwise report archive capture `PENDING` with exact gap.
3. Normalize observations to machine-readable governed candidate facts; preserve evidence links, language and conflict states.
4. Admit only supported public-safe facts into the correct GitHub canonical files; append source-grounded JSONL events for material changes.
5. Validate the working branch, publish via successful main-branch release, and verify production.
6. Publish project-channel trackers and company rollups only under the live Slack send gate; verify each receipt and register MessageLog.
7. Reconcile required Sheets as downstream projections, or mark pending. Final report explicitly lists per-channel cutoffs, archive, GitHub release, website, Slack delivery, Sheets and unresolved fact/identity gaps.

## Non-overrides
This document does not supersede the private A9 Slack Control READ FIRST, private A9 Recovery Archive READ FIRST, project Drive authority, or current authorized Slack send modes. It adds an Operations-side machine-readable cycle contract and QA expectations. The existing A9 archive owns raw Slack JSONL; A9 Project Identity owns canonical identity; GitHub owns only normalized/public-safe Operations data.

**Important:** The existing routine Daily Ops snapshot carried a global source cutoff of 2026-10-07T17:41:56+05:45; this is *not* proof that every eligible channel/thread was fully captured after that timestamp. A new governed per-channel checkpoint and provider readback are required before upgrading coverage to PASS.

## Parent operating cycle (2026-10-08)

The operational alias is now **A9-CWO — Communication & Web Operations**. This document and its machine-readable sibling remain the **Slack adapter**, not the complete daily-cycle contract. For a source-agnostic pipeline, use [`DAILY_COMMUNICATION_WEB_CYCLE.md`](DAILY_COMMUNICATION_WEB_CYCLE.md), the pinned [`storage-routing-rules.json`](storage-routing-rules.json), and the two-channel Discord Colab. No Discord run has been executed merely by activating this contract.
