# A9-CWO · Two-channel Discord daily collection

**Run [Colab notebook revision `20261009-013`](A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb) before A9-CWO.** The working filename/link remains unchanged. The browser-friendly launcher is [Open in Colab](https://colab.research.google.com/github/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/blob/main/ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb).

Only server `682670494658330644` and channels `1463826087841890417`, `1492168056858738809` (plus currently active child threads with those parent IDs) are in scope. No whole-server message harvest.

- Setup: create/authorize a Discord application **bot** with `View Channel`, `Read Message History`, and message-content access, then store its bot secret as **`DISCORD_BOT_TOKEN`** in Colab Secrets. Never store it in Drive, GitHub or notebook outputs; do not use a personal Discord token/self-bot.
- Before any raw-message or attachment archive writes, C02 performs a live, read-only preflight: it prints the two parent channel names and all currently active child-thread names, source IDs/links, exact per-source cutoff in Nepal and UTC, seven-day/catch-up mode, and previous verified cursor. The operator must type `COLLECT` to proceed; anything else means PREVIEW ONLY with no new receipt or cursor write.
- The collector uses `discord.com/api/v10` and signed CDN image/file downloads; verified originals are preserved in the existing A9 Discord domain root, within one scope-specific daily intake folder.
- Every C02 run: replay at least the previous **seven rolling 24-hour days** for each scoped source. If a verified source cursor predates that window, extend the scan back to the cursor with a **one-day safety overlap**. A source cursor advances only after its required raw JSONL, original-attachment integrity, and provider readback checks pass. Repeated failures to recover earlier original media remain an explicit efficiency and completeness debt; C05 indexing does not certify or repair them.
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

## 2026-10-09 PARTIAL provider run and v20261009-004 retry diagnostics

First real collector run `20261009T004444Z` completed at 06:35:34 Nepal time, scanning 26 parent/active-thread sources with 174 new/changed messages. Frozen provider receipts, message JSONL and candidate JSONL were written. The final receipt is `PARTIAL`, not `PASS`: **17 sources PASS; 9 sources PARTIAL_ATTACHMENTS; 749 attachments failed with reported byte-size mismatches; 207 attachments were marked PREVIOUSLY_ARCHIVED**. This is based on the frozen original Drive receipt `1gwH1_kGG4kSmfRv3r7DRrPOMGHN_QBrN`, with current handoff `1QUZRvXuW3Z7z4UD1BkoI_jJD2ZWkZQN4`. The exact reason actual bytes differ from Discord attachment metadata is NOT established. Do not accept image bytes as originals only because CDN returned HTTP 200.

Current notebook revision **`20261009-004`** (same working Colab link) adds `Accept-Encoding: identity` plus safe error diagnostics for `declared`, `observed`, MIME, content-length header, encoding, hostname and first 16-byte hex. No signed URL queries or secrets are printed. Failed source cursors remain unadvanced. Run the revised collector once and inspect the first 2–3 `MEDIA FAILURE DETAIL` lines and final receipt; do not claim complete until all required attachments verify. Mismatched media remains rejected, not silently stored as verified source.

## C01 / C02 permanent cell identifiers — notebook revision 20261009-005

- **C01 — SETUP** (`a9-cwo-c01-setup`): six `[A9-CWO C01 SETUP | nn/06]` stages from START to PASS. A `Connecting` or `Resuming execution` status without **C01 01/06 START** means Colab has not started Python; reconnect Colab runtime, then run C01. At **03/06 GOOGLE_AUTH_WAIT**, complete the Google authorization dialog. At **05/06 DRIVE_CLIENT_READY**, check notebook access to the Colab Secret `DISCORD_BOT_TOKEN`, never paste tokens into chat.
- **C02 — COLLECTOR** (`a9-cwo-c02-collector`): all ongoing progress lines start `[A9-CWO C02 COLLECTOR |`, including the heartbeat. Run only after **C01 06/06 PASS**, report C02's last visible line and FINAL RECEIPT (PASS or PARTIAL).

Stable working Colab URL stays the same. The revision only changes diagnostic/logging presentation and cell identifiers, not the two Discord channel scope, source verification rules, Drive IDs, or prior partial receipt. Each future change still needs a new date-based revision and exact PRE archive.

## C03 / revision 20261009-006 · read-only CDN byte-size diagnosis

Frozen second C02 run: `20261009T020256Z`, `PARTIAL`, 26 scoped sources, 174 new/changed messages, 749 attachment byte-size mismatches. Frozen receipt: Google Drive ID `1rOQO9Q7i8vZVeQAGOuZsj8OM3W4RXYA3`; handoff stable ID `1QUZRvXuW3Z7z4UD1BkoI_jJD2ZWkZQN4`. For failed samples the HTTP `Content-Length` equals bytes received, `Content-Encoding` is identity, and file signature starts with JPEG SOI/JFIF; both larger-than-metadata and smaller-than-metadata examples occur. Source of difference **remains unknown**. One recorded URL has only signed `ex/is/hm` and `backend` query keys, no resize keys. The raw source `url` was used in C02, not the `proxy_url`.

After opening the **unchanged** Colab working link, run `C01`, then (optionally) `C03 CDN PROBE` **without rerunning C02**. C03 reads the frozen receipt and selects one failed attachment automatically. It safely compares up to two URLs refreshed from Discord message metadata; printout includes declared/observed bytes, MIME, JPEG dimensions, SHA256 and HTTP response, **never signed URL/token values**. No media or cursor writes. C03 is diagnostic, not a fix nor evidence that any returned variant is the uploaded original. Preserve the last completed PARTIAL receipt and retry only after identifying the variant discrepancy.

## 2026-10-09 · revision 20261009-007 — C04 one-image derivative pilot

C03 has now been run by the user. The chosen Discord attachment declares 1,103,988 JPEG bytes at 4284×5712; source CDN returned a decodable 8,830,415-byte JPEG, proxy CDN a decodable 1,943,867-byte JPEG, same resolution but different SHA-256. Neither is certified original. The httplib2 timeout warnings did not stop the C03 diagnostic. Do not repeat C02 just to investigate these 749 failures.

Revision **20261009-007** keeps the working Colab URL unchanged and adds **C04 SINGLE DERIVATIVE PILOT** (stable ID `a9-cwo-c04-derivative-pilot`). Run C01 and C03 in the same runtime if not already running, then C04. C04 re-fetches just ONE source CDN JPEG, requires exact C03 byte-count and SHA-256 agreement and matching dimensions, then stores it exclusively as `PROVIDER_DERIVATIVE_NOT_ORIGINAL` under existing private A9 Drive run folder `DERIVATIVE_BYTES`, with immutable per-attachment sidecar in `RUN_RECEIPTS`. Both are provider-read back. Max single file 25 MiB; no token or signed URL printing. No modification to raw/original archives, `state_current.json`, `handoff_current.json`, frozen receipts or source cursors. A derivative is useful supporting evidence **but never satisfies the original-file certification debt**.

**Execution status at publication:** C04 NOT RUN; no Drive derivative or sidecar may be claimed until user runs the cell and its result is read back. The previous working notebook revision 006 was frozen exact-byte as `99_VERSION_ARCHIVE/20261009/006__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_DERIVATIVE_PILOT.ipynb` before source modification. The notebook version manifest records both versions and their actual Git blobs. The new GitHub branch must pass validation and be merged before main-backed Colab exposes C04.


## Current · 2026-10-09 NPT · revision 20261009-008

**New daily pattern is implemented in notebook source but has not been executed in Colab.** See [the full machine-first daily runbook](DAILY_7_DAY_MACHINE_ARCHIVE_RUNBOOK.md) and the [version ledger](notebook-versions.json). The same GitHub-backed working Colab URL at the top of this README remains unchanged.

- **C01** authenticates Drive and the bot. **C02** now scans at least the last seven rolling days on **every** run, extending backwards if a verified high-water cursor predates that range. The scope is STILL exactly two parents and currently active children; archived threads and embed-only images remain uncovered.
- **C05** verifies the *new* immutable C02 raw and candidate JSONL by SHA-256, then saves **pointer-only private JSONL indexes grouped by message creation date in Nepal time** and an immutable per-run JSON manifest. This is NOT an additional raw message archive, a public GitHub data dump, a daily construction-completion statement, or an automated Google Sheets projection. C05 does not advance cursors.
- Public machine contracts: [day index schema](schemas/daily-message-index-v1.schema.json) and [index manifest schema](schemas/daily-run-index-manifest-v1.schema.json). Runtime test: [synthetic offline fixture](../../scripts/test_discord_daily_index_contract.py) with [CI evidence](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/actions/runs/37922352759).
- PRE snapshot of exactly the former v007 notebook: [007 archive](99_VERSION_ARCHIVE/20261009/007__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_SEVEN_DAY_DAILY_INDEX.ipynb), Git blob `cb8a4228ab4e9c59ffbfab680aaaac37d4734e22`. Current source revision is `20261009-008` and has separate Git blob `6b954da36225d58f62207a3973418bf4d205b584`.
- **Correction to the historical 007 release note above:** C04 did subsequently run. Live Drive has verified one private 8,830,415-byte provider derivative (file `1HBLKmpQV5yCD_90_v9iHEIbiTw3VduPw`) and its immutable sidecar receipt `1ftkzIKyqUhVvCCWYAw5ka_YfKlDg2tVi`. The old 749 mismatched *original* attachments remain unresolved; C04 did not certify them or move cursors. Last full C02 provider run remains `20261009T020256Z` PARTIAL.
- Important efficiency debt: repeat capture may reattempt unresolved media on a PARTIAL source; design a separate governed failed-media recovery lane before claiming that unattended seven-day daily collection is resource-efficient. Do not discard the failure evidence or silently certify media.


### Revision `20261009-009` — transparent source-by-source preflight

Daily operator sequence: **C01 → C02 preview → type `COLLECT` → inspect source-by-source progress/final C02 receipt → C05**. The preview is based on live authorized Discord metadata (exactly two parents plus currently active child threads) and existing private Drive cursor state, so the thread roster may differ from the previous 26-source receipt. Each source's lower bound is frozen to one C02 run-start timestamp: normally the previous 168 hours, extended backward when its verified high-water is older (one-day overlap). The preview distinguishes parent channels from active threads, prints NPT window dates, and shows whether no verified cursor exists. The confirmed run receipt preserves this preflight plan and the actual per-source message-fetch timestamps. A name beginning `Archive_` is only a name: Discord's actual archived threads remain outside this version's discovery. Messages added after the preview starts may be fetched during the run; the printed start time is not an enforced upper message-ID bound. No bot secret or private raw message text is shown in the preflight.

Preview-only creates **no frozen C02 receipt**, no new raw JSONL, no index, and no state advancement. It must NOT be followed by C05 using the previous handoff. C05 is only legitimate after a new confirmed C02 run. Previous 749 original-media size mismatches remain explicitly unresolved; the preview does not make them PASS and may still cause costly retries in affected sources.

Immutable PRE: [notebook revision 008 snapshot](99_VERSION_ARCHIVE/20261009/008__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_TRANSPARENT_SEVEN_DAY_PREFLIGHT.ipynb). Current source and ledger: [working notebook](A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb) · [version registry](notebook-versions.json).


### Revision `20261009-010` — no stale receipt indexing

A C02 preview-only attempt invalidates any earlier C02 confirmation in the same notebook runtime. C05 now requires the `C02_CONFIRMED_RUN_ID` and `C02_CONFIRMED_RECEIPT_ID` set only after that exact confirmed collector run successfully read back its frozen Drive receipt/handoff. It rejects both missing confirmation and any mismatch with the latest Drive handoff. Therefore the daily index cannot be falsely marked newly generated by simply running C05 after choosing PREVIEW ONLY. This is a notebook-source and synthetic-QA improvement, **not** proof of a real Discord runtime collection. The r009 PRE snapshot is immutable under `99_VERSION_ARCHIVE/20261009/009__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_C05_PREVIEW_ONLY_GUARD.ipynb`.


## Full historical Discord archive (r012) — separate from two-channel daily C02

**Seven days is only the ongoing replay window; it is not the full archive.** The user requires all retrievable authorized guild message history and original media preserved in private Google Drive before any downstream site/Slack facts. C06 performs a live scoped full-guild text/forum/announcement/media channel and discoverable active/archived thread preflight; type `FULL_HISTORY` to capture immutable gzip JSONL pages and per-page receipts with a resumable independent cursor. Repeat C06 until every source has reached its oldest accessible message. C07 repairs failed/deferred native media and never certifies CDN derivatives as originals. C08 builds the *private SQLite index* only after historical message coverage has been verified. C09 enforces the **fail-closed archive and query readiness gate**; afterward identity reconciliation, website deploy and governed Slack send/readback remain independent mandatory gates. No C06+ provider run has been observed yet. Full authoritative procedure: [FULL_HISTORY_ARCHIVE_FIRST_CONTRACT.md](FULL_HISTORY_ARCHIVE_FIRST_CONTRACT.md). The original C02/C05 daily path is maintained unmodified for its two selected parents and must not be represented as complete historical or guild-wide incremental coverage.


**Integrity hardening r013 (9 October 2026):** A pre-existing Drive attachment is never labelled ORIGINAL_REUSED based on file-size equality alone. The authorized Discord source must be re-fetched and its declared size plus SHA-256 matched to a complete private Drive readback. Any mismatch remains unresolved media debt and blocks the publication gate. The exact r012 PRE notebook is archived at `99_VERSION_ARCHIVE/20261009/012__A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR__PRE_ORIGINAL_REUSE_SHA_GUARD.ipynb`. No real authenticated C06-C09 execution is claimed.
