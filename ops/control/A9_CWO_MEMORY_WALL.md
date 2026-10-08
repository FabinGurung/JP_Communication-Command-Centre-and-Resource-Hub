# A9-CWO Memory Wall — permanent rule (2026-10-09 NPT)

**Kind:** Quick-reference poster / job aid / visual runbook (can be printed or displayed like a classroom flashcard). Live page [Control Towers Memory Wall](../../controls/memory-wall.html).

## Immutable working source rule

> I’ve implemented your date-based enumeration rule for the A9-CWO Discord notebook.
>
> The original Colab working link remains unchanged. Every future notebook modification—even a spelling correction or comment change—must receive a new numbered revision.

## Verified revision lineage

| Revision | Date (Nepal) | Description |
| --- | --- | --- |
| 20261008-001 | Oct 8 | Original notebook — archived |
| 20261009-001 | Oct 9 | Google Drive API correction — archived |
| 20261009-002 | Oct 9 | Versioning and archival controls — archived PRE before next mutation |
| 20261009-003 | Oct 9 | Live heartbeat and collector progress diagnostics — current |

These early revisions were preserved from their exact historical GitHub source contents; numbering reflects source revision creation date, **not** when a retroactive archive copy was made. Future versions continue the date ordinal, including minor edits.

## Permanent working notebook

[Open original Colab link](https://colab.research.google.com/github/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/blob/main/ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb)

[Machine-readable revision history](../discord/notebook-versions.json)

[Numbered archive](../discord/99_VERSION_ARCHIVE/README.md)

[Pinned A9-CWO Memory Wall](../../controls/memory-wall.html)

**Compulsory sequence: PRE snapshot → verify archive → edit original → increment date-based revision → POST verification → register and publish.**

The stable Colab link references a GitHub path. It is not a Google Drive-native notebook ID, and no Drive-native same-ID update is claimed.

## Collector scope, output and incomplete state

The bot scans only Discord guild `682670494658330644`, channel IDs `1463826087841890417` and `1492168056858738809` (and their active child threads). Original messages, files and images should be archived in Drive as byte-preserving artifacts; normalized JSON/JSONL candidates feed the separate A9-CWO reconciliation and website. A Colab runtime screenshot with a running Stop control and warnings alone does **not** prove scan success. Require per-channel counts, final receipt status and provider readback. No Discord collection run was performed while releasing this GitHub code.

The A9-CWO source-code release must pass GitHub validations and Pages deployment; runtime user-authorized bot execution remains a separate step.
