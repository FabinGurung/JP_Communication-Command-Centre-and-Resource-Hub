# A9-CWO · Discord daily seven-day replay and machine-index runbook

**State:** Source revision `20261009-013` published, with an explicit live roster/time-window preflight, operator `COLLECT` gate, and same-runtime C05 guard. Authenticated revision-009 provider execution and a fresh C05 receipt are not yet verified. This document and the GitHub notebook are not evidence of an executed 008 run.

[**Stable working Google Colab notebook**](https://colab.research.google.com/github/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/blob/main/ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb) · [Notebook revision ledger](notebook-versions.json) · [Archive controls](../control/storage-routing-rules.json).

## 1. What the collector truly scans

- Discord guild `682670494658330644`, parent channels `1463826087841890417` (Fishtail pictures) and `1492168056858738809` (Rohini pictures) and **currently active child threads** belonging to those parents only. It does not scan the rest of the guild; archived child threads and external embed-only images are outside v008 coverage.
- On every C02 invocation, the baseline lower bound is **the previous seven rolling 24-hour days** relative to the single frozen C02 start instant. If the prior source's verified high-water message predates that window, extend further backward by at least one day to catch missed intervals. Message pagination hard cap remains 100 pages per source; exceeding it fails the source without cursor advancement.
- Raw Discord messages are versioned on message ID + content/edit/attachment/embedding digest. Replayed unchanged messages are **not** new messages; candidates are only new or changed versions.
- Files with Discord-declared original-size mismatches are **not** certified original bytes. If any attachments fail, that source is PARTIAL and its verified watermark does not advance. The single C04 provider derivative saved 9 Oct is useful evidence, **not** a recovered original.

## 2. Daily operator sequence

1. Open the stable GitHub-backed Colab link; check notebook header shows **20261009-013**. Avoid GitHub's "save a copy in Drive" button when working on the canonical GitHub source.
2. Run **C01 SETUP**. Complete Drive OAuth and supply bot token **only** in authorized Colab Secrets. Expect **C01 06/06 PASS**; never paste credentials in source, GitHub, logs, Slack or chat.
3. Run **C02 PREFLIGHT + COLLECTOR**. C02 first reads the existing private state and live Discord parent/active-thread metadata without writing archive records. It prints the exact names, parent memberships, IDs/links, planned seven-day UTC/NPT cutoffs for every source, and whether older verified cursors extend the window. Verify this roster and the per-source time bounds BEFORE proceeding. Type **`COLLECT`** at the prompt to start message/attachment archiving, or anything else to finish PREVIEW ONLY without writes. When collecting, wait for **FINAL RECEIPT** with exact PASS/PARTIAL; do not treat a heartbeat or preflight printout as a saved source receipt.
4. **After a confirmed new C02 receipt only**, run **C05 DAILY INDEX** in the same runtime. It reads the **new** C02 frozen receipt (old 2-day receipts are rejected), hashes both private raw/candidate JSONL files, then saves one readback-verified JSONL day partition per **message creation date in Nepal**. Finally it saves the immutable run manifest. Expect **C05 06/06 PASS** with Drive file IDs.
5. Record C02/C05 run IDs, count, source receipt, index manifest, original-media PARTIAL statuses, archived-thread coverage gap and any provider errors in the A9-CWO operational handoff. Register Local/Main PRE/POST/ACK using authorized authority. No false full-complete claim.
6. Only then reconcile private candidate messages into the owning project/event model by project ID and source, review conflicts, and publish **approved public-safe facts** to the website. Google Sheets are optional downstream projections, not the primary Discord archive.

**C03/C04** are separately bounded media-integrity diagnostics/pilots. They are *not* mandatory daily collection, do not advance C02 state, and do not certify originals.

## 3. Where the bytes belong

```text
PRIVATE Google Drive · existing Discord A9 source root (DO NOT CREATE A NEW AUTHORITY)
└── A9_CWO_DAILY_TWO_CHANNELS/
    ├── RAW_JSONL/
    │   └── {channel_id}__{run_id}.jsonl           # exact provider message objects, private
    ├── CANDIDATES_JSONL/
    │   └── {channel_id}__{run_id}.jsonl           # extraction candidates, NOT verified facts
    ├── ATTACHMENT_BYTES/                           # verified original bytes only
    │   └── {channel_id}/...
    ├── DERIVATIVE_BYTES/                           # labelled provider representations, not originals
    ├── DAILY_INDEX_JSONL/
    │   └── YYYY-MM-DD/
    │       └── A9_CWO_DISCORD_DAY_INDEX__YYYY-MM-DD__{run_id}.jsonl
    ├── RUN_RECEIPTS/
    │   ├── A9_CWO_DISCORD_RECEIPT__{run_id}.json
    │   ├── A9_CWO_DISCORD_DAILY_INDEX_MANIFEST__{run_id}.json
    │   └── prior immutable C04 receipts...
    ├── state_current.json                         # existing provider-verified cursor; C05 never edits
    └── handoff_current.json                       # existing C02 handoff; C05 never edits

PUBLIC GitHub · controls and public-safe derived projection only
└── ops/discord/
    ├── ...COLLECTOR_v1.0.ipynb                      # stable GitHub-backed working path
    ├── notebook-versions.json
    ├── schemas/
    │   ├── daily-message-index-v1.schema.json
    │   └── daily-run-index-manifest-v1.schema.json
    └── 99_VERSION_ARCHIVE/...
```

### Index row (synthetic illustration — NOT a fetched message)

```json
{
  "schema": "a9-cwo-discord-day-index-v1",
  "provider": "DISCORD",
  "run_id": "20261009T120000Z",
  "guild_id": "123456789012345678",
  "parent_channel_id": "111111111111111111",
  "channel_id": "222222222222222222",
  "message_id": "333333333333333333",
  "message_created_at_utc": "2026-10-09T09:12:00+00:00",
  "date_npt": "2026-10-09",
  "event_version_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "source_message_url": "https://discord.com/channels/123456789012345678/222222222222222222/333333333333333333",
  "raw_drive_id": "synthetic_raw_drive_file",
  "raw_line_1_based": 1,
  "candidate_drive_id": "synthetic_candidate_drive_file",
  "candidate_line_1_based": 1,
  "source_receipt_id": "synthetic_receipt_file",
  "attachment_count": 2,
  "evidence_class": "MESSAGE_METADATA_POINTER_ONLY",
  "admission_status": "NOT_RECONCILED",
  "attachments_original_certification": "SOURCE_PARTIAL"
}
```

The original text lives **once** in the private RAW/CANDIDATE archive; the day-index row is a fast locator, not the truth of the construction activity. Keep `provider/guild/channel/message/version digest` as the cross-run event identity, and never make `run_id` alone a dedup key.

## 4. Day-specific construction report is a SEPARATE admission step

A source message created on a day is not necessarily about work executed on that day. For any claimed `work_date_npt`, require a dated site engineer statement or a well-supported project record. Separate `source_timestamp`, `reported_work_date`, `activity_trade`, `location`, `planned/ongoing/done/hold`, `source_id`, `engineer_approval` and `project_fk`. Do not auto-promote a photo into DONE, and do not call a future plan approved because a message mentions it.

Retain governance boundaries: stock ≠ consumption; ordered ≠ delivered; plan ≠ done; unknown ≠ zero; private raw text/attachments do not belong in this public repository.

## 5. Pending coverage and engineering gates

- **Unresolved:** 749 original-attachment byte mismatches in the previous PARTIAL collection. C04 preserved one private **provider derivative**, not original recovery.
- **Uncovered:** truly archived Discord child threads, embed-only images, deleted-message audit, comprehensive private Slack archive, and any unregistered future provider.
- **Not yet deployed:** Colab runtime execution of r008/C05; automated scheduled Colab execution; private JSONL → project-approved fact admission; optional Parquet / DuckDB / compressed warehouse generation.
- **Future efficiency:** isolate failed-original-media recovery from normal daily message metadata scans, so unresolved 749 images do not require unnecessary repeated downloads. Preserve source-side failure statuses and do not advance original-media completeness.

## 6. Transparency/read-only preflight contract (r009)

- **Before any archive writes**: print an ordered live roster of each parent and active child thread, parent ID/name, channel ID/name, direct Discord link, source type, previous verified cursor, exact effective cutoff in NPT and UTC, and frozen C02 run-start instant. The display is generated from the same `run_plan` consumed by confirmed C02 and preserved in its private immutable receipt.
- **Confirm or stop**: only exact operator input `COLLECT` runs the message/attachment/archive phase. Any other input produces PREVIEW ONLY, no new C02 receipt, no Drive archive mutation, and no cursor advance. C05 must not be treated as executed in this case.
- **Time semantics**: seven days means minimum **168 rolling hours**, not midnight-aligned dates. A stale verified cursor extends the window earlier by the one-day overlap; a missing verified cursor means only the rolling seven-day bootstrap is guaranteed. Earlier never-observed messages are not automatically recovered. Messages posted during a lengthy run can appear after the preview timestamp, so the receipt also records actual per-source API fetch start/finish timestamps.
- **Coverage**: the number and names of active child threads can change from one daily run to the next. Threads whose names contain `Archive_` may still be active; truly Discord-archived threads are outside r009. No unrestricted guild harvest.
- **Known risk**: the separate 749 original-byte mismatches remain PARTIAL and may trigger repeated recovery attempts; the transparency change does not certify, suppress, or resolve them.
- **Governance**: the stable Colab URL is unchanged. The exact r008 notebook is stored as immutable PRE revision 008 under `99_VERSION_ARCHIVE/20261009/`; the controlled working revision is `20261009-009`. C03 and C04 remain optional.

## 7. Revision `20261009-010`: reject stale receipts after preview-only

Every new C02 attempt clears its previously confirmed run marker. Only after the operator types `COLLECT` and the collector saves and reads back the exact frozen C02 receipt/handoff does it set `C02_CONFIRMED_RUN_ID` and `C02_CONFIRMED_RECEIPT_ID` in the active Colab runtime. C05 rejects attempts without both markers, or whenever the Drive handoff and frozen receipt IDs do not exactly match the current run markers. This prevents a PREVIEW ONLY execution from quietly reusing an older 7-day receipt. Existing JSONL idempotence and original-media PARTIAL classifications are preserved. The version-009 notebook is immutable at `99_VERSION_ARCHIVE/20261009/009__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_C05_PREVIEW_ONLY_GUARD.ipynb`.

## 8. Full historical capture and strict publication sequence (20261009-012)

Before treating the 7-day C02 scan as ongoing maintenance, perform the historical **full authorized guild scope**, not just the two picture parents. Run **C01 → C06**. C06 requires `FULL_HISTORY` confirmation and commits small, independent resumable batches of complete original Discord message JSON objects as gzip JSONL to Drive with SHA-256/readback, archived-thread discovery, source coverage and attachment debt. Re-run until all pages are exhausted and full source coverage is verified. Then run **C07 REPAIR_MEDIA** repeatedly for the failed/deferred original-byte attachments; only exact provider original-byte capture is certified. Then run **C08 BUILD_SQLITE** to reconstruct the private indexed query cache from each frozen raw Drive page, with SHA and relational checks. Finish **C09**: if source history, native media, discovery and current query readback are not all verified, it prints BLOCKED and website/Slack publication stays disallowed. Even after DATA PASS, separately reconcile owners/project IDs, evidence and safety, deploy only approved GitHub facts and send only authorized Slack updates; record Slack MessageLog receipts. Full design and folder tree: [FULL_HISTORY_ARCHIVE_FIRST_CONTRACT.md](../discord/FULL_HISTORY_ARCHIVE_FIRST_CONTRACT.md). **As of this code revision authenticated C06–C09 are not run; previous C02 media debt remains open.** The existing two-parent seven-day C02/C05 maintenance lane is not substituted for complete history.


**Integrity hardening r013 (9 October 2026):** A pre-existing Drive attachment is never labelled ORIGINAL_REUSED based on file-size equality alone. The authorized Discord source must be re-fetched and its declared size plus SHA-256 matched to a complete private Drive readback. Any mismatch remains unresolved media debt and blocks the publication gate. The exact r012 PRE notebook is archived at `99_VERSION_ARCHIVE/20261009/012__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_ORIGINAL_REUSE_SHA_GUARD.ipynb`. No real authenticated C06-C09 execution is claimed.
