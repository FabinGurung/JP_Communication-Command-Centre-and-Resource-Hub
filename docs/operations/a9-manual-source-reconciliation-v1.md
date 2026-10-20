# A9 manual source reconciliation — user-triggered only

**Mode:** user-initiated bounded source read, reconciliation and explicit publication approval. **No schedule, background polling or Discord collector run.** No source records overwritten, no duplicates.

## Governed workflow

1. Request selected Slack message/channel links, or an already-authorized Discord export, a date range and exact project IDs. Do not scan whole history automatically.
2. Read the source and private ingestion ledger; deduplicate by provider message ID, timestamp, revision and content checksum.
3. Preserve original messages and media in their restricted provider or controlled Google Drive, not public GitHub. Never upload private contact records, raw financial/attendance data, image originals or SQLite binaries to public Pages.
4. Normalize project, material, person and source foreign keys where verifiable. Classify PLAN, INSTRUCTION, REPORTED, OBSERVED, VERIFIED, APPROVED, BLOCKED and UNKNOWN distinctly. No fabricated completion or engineering approval.
5. Only explicit, user-authored Slack checklist instructions may be formatted and proposed for `ops/data/a9-published-checklist-public.v1.0.json` with project ID, date and provenance. This public feed is **empty until separate publication review**. Browser-local checklist stays independent.
6. Source-attributed Progress starts with the existing immutable 37-record `ops/data/progress-report-public.v0.2.jsonl`. `ops/data/a9-reviewed-progress-public.v1.0.json` records reviewed new public-safe deltas, initially **0**, not another copy of the historical 37. Use existing governed admission gates before real Progress publication.
7. The ten Sheets stay authoritative in Google Drive. The public Field Resources index is category-only with zero source rows or identifiers. Individual attendance, expenses, contact numbers, bill media and source URLs remain access-controlled.
8. DRY_RUN before any source admission; request explicit authorization to publish each safe projection, run PK/FK, privacy, freshness and browser QA, and promote via feature branch to main after passing CI. Read back website and source references.
9. Do not change the botanical theme, v2.2.0 tag, engineering source files, or other repositories. Keep Discord collection ON HOLD.

## Prompt to use manually

> A9 manual reconciliation. Selected provider sources: [Slack messages/channel or authorized existing Discord export]. Period: [Nepal date range]. Project IDs: [specific IDs]. Mode: DRY_RUN. Read current source and existing private ledger. Identify net-new messages by provider ID/hash, separate explicit user-written checklist instructions from reported site evidence, and stage only normalized, privacy-safe fields with canonical project FK. Preserve originals in their owning provider; never duplicate. Show proposed checklist and Progress changes, privacy exclusions, source links and validation counts. Wait for explicit publication permission. No scheduler, no Discord collector, no Slack outbound messages.
