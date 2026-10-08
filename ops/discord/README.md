# A9-CWO · Two-channel Discord daily collection

**Run the [Colab notebook](A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb) before A9-CWO.** The browser-friendly launcher is [Open in Colab](https://colab.research.google.com/github/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/blob/main/ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb).

Only server `682670494658330644` and channels `1463826087841890417`, `1492168056858738809` (plus currently active child threads with those parent IDs) are in scope. No whole-server message harvest.

- Setup: create/authorize a Discord application **bot** with `View Channel`, `Read Message History`, and message-content access, then store its bot secret as **`DISCORD_BOT_TOKEN`** in Colab Secrets. Never store it in Drive, GitHub or notebook outputs; do not use a personal Discord token/self-bot.
- The collector uses `discord.com/api/v10` and a signed CDN image/file download; originals are preserved in the existing A9 Discord domain root, within one scope-specific daily intake folder.
- First run: last **7 days**. Later: per-channel/thread cursor plus two-day overlap for edited/new content. Cursor advances only after raw JSONL, attachments and provider readback pass for that source.
- Outputs: immutable batch `RAW_JSONL/`, `CANDIDATES_JSONL/`, `ATTACHMENT_BYTES/`, `RUN_RECEIPTS/`; two current source pointers `state_current.json` and `handoff_current.json`.
- `handoff_current.json` gives A9-CWO source coverage and receipt IDs; until Colab actually executes successfully, this is **NOT COLLECTED**.
- v1 boundary: active threads are supported; archived threads and embed-only externally hosted images are **not** included. No claim of complete server history or media OCR. Bad permissions, missing bot message text, attachment failures, or pagination cap yield partial/failed coverage. A source's watermark does not move on incomplete attachment readback.
- A9-CWO reconciles candidates to project identities, site progress, drawings and engineering references, then publishes validated GitHub JSON/JSONL/CSV, website, and authorized outbound Slack discussion posts. The Colab never automatically claims construction facts or posts messages.

Existing A9 Discord archive and its Local/Main catalogues remain intact. This daily intake is a **bounded delta lane**, not a replacement for prior archived source batches. Repeat history is recorded by immutable Discord message IDs and digest/version, not by filename alone.

### Colab Google Drive API hotfix — 2026-10-09

**v1.0.1 compatibility fix, same notebook filename:** `drive.files().list()` uses `pageSize=100` and `pageToken=token`, not snake_case `page_size`/`page_token`. The failure was in the `children()` Drive folder lookup, before collecting Discord messages; it did **not** prove messages had been archived. The notebook setup now supplies an authorized `httplib2.Http(timeout=120)` transport instead of relying on per-request timeout behavior. Restart the notebook from the current GitHub/Colab link, run **Setup**, then **Collector**, and check the final receipt. A saved older Colab copy may still contain the faulty code.


## Compulsory date-based notebook revisions (stable working link)

The exact Colab URL above is **GitHub-backed**, not a Drive `/drive/<id>` notebook. Therefore, keep the GitHub working path above constant; there is no verified Google Drive file ID to copy/update. The source versions are enumerated by **Nepal creation date** in [`notebook-versions.json`](notebook-versions.json) and physically snapshotted under [`99_VERSION_ARCHIVE/`](99_VERSION_ARCHIVE/README.md).

**Mandatory every-edit sequence:** read live main/feature refs; identify current `YYYYMMDD-NNN` revision and previous archive; PRE copy exact working notebook bytes to an immutable numbered archive if not already snapshotted; provider readback and compare Git blob; increment the day's ordinal for every notebook change (including a minor spelling/code/comment change); update only the stable original working path; update manifest and clear status (CURRENT vs ARCHIVED); run CI; promote to main on PASS; re-read source and archive. Do not rewrite archived blobs or alter GitHub Colab URL.

**Verified lineage:** `20261008-001` is the October 8 original; `20261009-001` is the October 9 Drive API hotfix; `20261009-002` is the October 9 immutable-versioning policy annotation. The first two snapshots were recovered from their actual historical Git blobs and archived on October 9; their date prefixes indicate **source revision creation**, not when copies were made. The current notebook's technical collector logic did not change from the hotfix.

## Oct 9 · Revision 20261009-003 — progress visibility and debugging

This notebook retains the **same Colab / GitHub working URL**. The exact `20261009-002` source was first frozen at `99_VERSION_ARCHIVE/20261009/002__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_PROGRESS_DIAGNOSTICS.ipynb`. The `20261009-003` revision adds:

- Timestamped progress lines at Drive root, folder checks, cursor load/save, Discord channel and active-thread discovery, message page retrieval, image/file download and upload, raw/candidate JSONL, frozen receipt and handoff.
- A **heartbeat every 20 seconds** while long requests continue. Seeing `Still running` is not proof that data has been archived.
- Source-specific `FAILED`/partial messages and an explicit `FINAL RECEIPT` line if the run completes.
- Background heartbeat stops on success, exception, or ordinary interruption with a try/finally boundary.

**Correct response to a long-running cell:** wait for heartbeat plus per-source progress and eventually a frozen Drive handoff; if it stays at the same stage for many minutes, note the last stage and stop the cell before sharing the sanitized error/output. Do not paste Discord tokens or Google OAuth credentials into chat. A paused/stopped run may have some Drive output; resume using cursors and readback, never wipe the archive.
