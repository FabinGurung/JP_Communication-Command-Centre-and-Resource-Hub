# A9-CWO — Full Discord History, Drive Archive First (v0.1)

**Effective:** 2026-10-09 NPT. **Code authority:** notebook `20261009-013`, same permanent GitHub-backed Colab URL. **Provider execution:** NOT RUN. Historic C02 receipt remains PARTIAL; this document is not source-capture evidence.

## Intent and scope

**A rolling 168-hour replay is NOT a historical archive.** Collect *all Discord messages retrievable by the authorized bot*, from the oldest available record for **all accessible message-bearing guild channels** and all discoverable active/archived threads, regardless of message age. C06 uses live authorized guild channel/thread discovery; it is intentionally a distinct lane from the configured two-parent C02 daily collector.

The source is Discord guild `682670494658330644`. Bot permission/API limits, deleted messages, old edit versions, inaccessible private threads, DM histories, expired attachments and unsupported types cannot be silently represented as captured. They must produce explicit coverage gaps/limitations, not fabricated source records. Do not use self-bots or a user token.

## Immutable-first pipeline

1. **C01 AUTH** — Colab Google Drive OAuth and authorized Discord bot token in Colab Secrets, never committed to GitHub, public Pages or Slack.
2. **C06 COMPLETE HISTORY** — Live preflight prints all visible message channels, parent and active/archived thread IDs/names and permission/API gaps. Operator must type `FULL_HISTORY`. Fetch reverse-chronological pages until provider history is exhausted; each 100-message page is saved **immediately to private Google Drive** as a gzip-compressed UTF-8 **lossless raw Discord JSONL** blob with immutable SHA-256 readback, followed by an immutable per-page receipt. Separate historic cursors record only readback-verified progress. Run up to 8 pages per invocation and **repeat** until every source is exhausted. C06 tries up to 20 original attachments per invocation; unrecovered and deferred attachments remain explicit debt.
3. **C07 NATIVE MEDIA RECOVERY** — Re-fetch current message metadata by stable Discord message ID to refresh attachment URLs. Attempt up to 25 unresolved originals, compare the actual byte count and hashes, save original bytes separately with immutable recovery receipts. Original-size mismatch, CDN derivative or missing message never counts as an original. Repeat as needed. Frozen C06 page receipts are never rewritten.
4. **C08 PRIVATE SQLITE** — After *all history messages* and thread discovery have verifiable coverage, SHA-check each compressed and decompressed JSONL page and build a private indexed SQLite snapshot for fast `channel_id`/`message_id`, UTC timestamp, parent/project and author lookups; includes original raw message JSON. Save the SQLite binary and build manifest back to private Drive with exact-byte SHA verification. This is a **rebuildable query cache**, not an alternate source of truth. Existing SQL tables retain every captured message version by composite key and preserve reactions/attachment status.
5. **C09 DATA PUBLICATION GATE** — Require latest full-history receipt `PASS`, full channel/thread coverage, zero original-media debt, verified private query snapshot from that same source receipt and successful Drive readback. Print `BLOCKED` with reasons if anything is missing. C09 is read-only and **does not** update the website or send Slack.
6. **Reconcile private evidence** — Map to real company/project identities using owning A9 registries, annotate event-time versus message-created-time, reconcile duplicate/conflicting observations, and verify statuses (an image upload does **not** establish `DONE`).
7. **Approved outputs only** — After C09 and fact/public-safety checks, commit appropriately public-safe GitHub `JSON/JSONL/CSV` projections, test and deploy website; only then send authorized FBL/REB/project Slack updates under the current Slack send controls and read back their MessageLog receipts. Raw private transcripts, binary files, contact details and secrets **never** enter the public repo.

## Private Drive hierarchy

```text
12_DISCORD_SYSTEM_AND_ARCHIVES / [verified existing Drive root]
└── FULL_HISTORY_ARCHIVE_V1
    ├── MESSAGE_PAGES_GZIP_JSONL/  (immutable source bytes, lossless)
    ├── ATTACHMENT_BYTES/          (verified original bytes only)
    ├── PAGE_RECEIPTS/             (immutable per-page evidence)
    ├── RUN_RECEIPTS/              (history coverage progress)
    ├── RECOVERY_RECEIPTS/         (immutable original-media recovery evidence)
    ├── QUERY_SNAPSHOTS/           (rebuildable private SQLite + build manifests)
    └── historical_state_current.json (mutable readback-verified resume pointer)
```

Existing `A9_CWO_DAILY_TWO_CHANNELS` remains separately intact. Neither channel data nor A9 archive folders are deleted, renamed, duplicated unnecessarily or passed off as recovered originals.

## Machine formats / performance

| Layer | Format | Purpose |
| --- | --- | --- |
| Exact provider message evidence | `.jsonl.gz` | Lossless stream of Discord JSON objects; compresses repeated keys efficiently; byte-for-byte verifiable |
| Original images/files | Raw binary + SHA-256 | Exact fidelity, no JPEG/PNG re-encoding |
| Page/run/recovery receipts | `.json` | Readback hashes, cursor checkpoints, failure proof and provenance |
| Query acceleration | `.sqlite3` | Compact B-tree indexes on source ID, message ID, dates and author; normalized message/attachment relationships |
| Public website | Approved `.json` / `.jsonl` / `.csv` | Minimal safe projections only, **never the private raw archive** |
| Slack | Governed message receipts | Source-evidenced facts sent through authorized channels after release gate |

**JSONL is the canonical high-fidelity event archive. SQLite is the efficient query/reconstruction layer.** CSV alone would lose nested attachments/embeds/reactions; SQL-only storage would unnecessarily couple source capture to a mutable database.

## What is NOT yet complete

This is a **code and gate implementation**, not a provider-run result. No C06/C07/C08/C09 live outputs are verified as of this revision. The older C02 evidence consists of 26 two-parent/active-thread sources, 174 new/changed messages and 749 failed native media checks; it is not a complete historical run. C02 still scans only its registered two parents; guild-wide recurring delta capture must be extended separately. Any such gap remains explicit and blocks a full-complete claim.

Do not run publication or outgoing Slack updates based merely on this specification or static CI. The correct trigger is a verified authoritative Drive receipt plus downstream permissions.


**Integrity hardening (revision 013):** A previously stored Drive attachment is never classified as an original merely because its size equals Discord's declared original size. A fresh authorized provider download must satisfy declared size and SHA-256 parity with complete Drive readback; mismatches remain open debt. This is code policy, not proof that the live provider run has occurred.
