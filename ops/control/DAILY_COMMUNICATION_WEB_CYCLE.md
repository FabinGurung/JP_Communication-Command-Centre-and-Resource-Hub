# A9-CWO · Communication & Web Operations (v1.0)

**Supersedes the user-facing name A9-SWO**; the existing `daily-slack-web-cycle.json` remains the Slack adapter. The daily cycle is now multi-source: Slack + the two specified Discord channels + future explicitly registered providers. This is a workflow alias, not a new Slack/Discord bot.

## The pinned rule
Open [Storage and daily procedure](../../controls/storage.html), backed by [storage-routing-rules.json](storage-routing-rules.json). Storage is chosen by purpose: raw messages, original images and file bytes go to the existing A9 source archive on Drive; normalized confirmed site facts, event history and control schemas belong to the owning versioned GitHub model; Pages and discussion messages are derived outputs. The Main Library is only migrated after FK/edge/cursor verification, not by copying one Sheet.

## Discord exact scope

- Guild: `682670494658330644`
- Parent channel 1: https://discord.com/channels/682670494658330644/1463826087841890417
- Parent channel 2: https://discord.com/channels/682670494658330644/1492168056858738809
- Active child threads belonging to these two parents are in scope. Archived threads and embed-only images are **not yet covered** in v1.
- Run [this Colab notebook](../discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb) using an authorized Discord Bot token + Google Drive authorization before the daily reconciliation. A first run is a 7-day bounded capture; subsequent runs use verified per-source cursor and a two-day overlap.
- The notebook must save immutable raw JSONL, actual attachment bytes with SHA-256/provider checksum verification, normalized candidate JSONL, per-source cursor state and a `handoff_current.json` receipt under the already governed Discord A9 root. It does **not** send messages, claim work DONE or scan the whole server.

## A9-CWO after Colab

1. Read the latest provider-authenticated Discord `handoff_current.json`; reject stale/missing, failed, or incomplete provider receipts as `PASS`. Explicitly report `NOT_RUN` or `PARTIAL` instead.
2. Read Slack using the existing per-channel and thread source checkpoints; scan both company discussions and governed project channels. Distinguish messages/attachments/field status.
3. Normalize all source messages to keyed evidence: `provider + guild/workspace + channel_id + message_id/ts + attachment_id`; join to project/company master only by verified IDs, not similarity of names.
4. Admit corroborated or correctly qualified domain facts to GitHub JSON/CSV, append event JSONL, validate schema and relationship invariants; expose unresolved source/project candidates separately.
5. Derive the website and then send approved per-project and company-level Slack summaries; record exact outbound message receipts. Discord outbound posting is not included unless separately approved.
6. Reconcile Drive source readback, Git commit, Pages deployment, Slack delivery, sheets status, capture gaps, and `Incomplete / Remaining`.

This configuration and notebook are staged. **The bot has not been run in this task**, and no current Discord capture should be inferred.
