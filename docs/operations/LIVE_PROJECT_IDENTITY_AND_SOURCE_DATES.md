# Live project identities and source dates — 10 November 2026

## Ownership decision
The current public Project Maps and Progress website is published from the five already-authorized Google Sheets through the read-only Google Cloud Workload Identity workflow. The original `Projects and Locations` Sheet and its companion `Website Display Choices` Sheet decide which projects and information may be publicly listed. Their original IDs, native revision history and permissions remain unchanged.

The versioned `ops/data/project-identity-index.v0.1.json` is **not** a current live-source mirror. It is a historically consistent 28-project derivative of the older `projects.csv` file, which must remain available for legacy source-to-foreign-key reconciliation and rollback. Do not overwrite that file with new live Sheet rows or disable its historical tests to conceal divergence.

## Reconciled facts
The live source Sheet reviewed on 10 November 2026 contains 30 project identity rows: 29 currently public project listings and one retired, nonpublic alias. A 29th public project, `PRJ-000029`, is absent from the historical Git index and is admitted by the current live publication settings. Its source quality is `WARNING`. It is **not** legally verified or certified by its presence in the public map.

The retired alias is excluded from the website and the public operations.json. Its original private Source Reference and row contents must never be copied to this public GitHub repository, a static website, or user-visible logs. Keep its original identity linkage within the restricted source system.

The publication process now compares only **publicly admitted** project IDs with the historical Git index and records added public IDs, counts and source scope in the generated `operations.json.identity` metadata. The Git historical snapshot remains unchanged. This is a reconciliation bridge, not a second editable master database.

## Source freshness is not publication freshness
The authorized workflow uses Sheets API `spreadsheets.readonly` and performs two consistent-read checks. It does **not** presently receive Google Drive file revision or `modifiedTime` metadata.

The public `operations.json.provenance.source_dates` therefore reports separate latest dated **public rows**, never fabricated provider modification timestamps:

| Category | Governed date field | Meaning |
| --- | --- | --- |
| Projects | `Projects and Locations / Last Updated` | Latest dated public project row; **not** Google Drive modified time |
| Reviewed instructions | `Message Sources / Date NPT` | Latest dated original message represented by a published approved instruction; not a full Slack capture cutoff |
| Work | `Project Work / Last Updated` | Latest published reported-work row; not a signed completion date |

`source_readback_at_npt` is when the **publishing job** read the five workbooks. `provider_modified_at_status=NOT_AVAILABLE_WITH_CURRENT_SHEETS_READONLY_SCOPE` is deliberate, not an error hidden by a recent build timestamp.

Do not infer that reported work `VERIFIED` means engineer-issued certification, billable measurement, payment approval, or a completed construction milestone. Those decisions remain with the original authorized record and reviewer.

## Safeguards
- Distinct public display choices remain required even when the master marks a row public.
- `RETIRED_ALIAS_ONLY` is excluded regardless of display choices.
- Every public source-project identity is a valid stable `PRJ-######`.
- Public quality warnings are displayed, but no private row details or source references are copied.
- Original legacy URLs, Astam public buyer guide, and outbound Field & Desk Library links are preserved.
- Do not broaden the Google OAuth scope, create new tokens, resume Discord or claim Slack full-history ingestion as part of this publication.

## Remaining
Live source-specific provider `modifiedTime` requires an explicit authorized metadata integration, with proven public-safe disclosure. Discord remains on hold. Slack private channel cursors, revision/tombstone pipeline, and standalone browser acceptance are separately tracked by [issue #30](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/issues/30).
