# A9-CWO Evidence Registry: P0–P1 baseline

This folder is a **public-safe machine contract**, not a raw communications archive.

**Authority:** existing permission-gated Drive bytes, receipt and JSONL indices. GitHub holds schemas, verified aggregate inventory, policies and eventual approved public projections. No provider messages, personnel records, signed CDN URLs, attachment bytes or private raw JSONL belong in this public repository.

## Verified P0 input (20261010T005617Z)

Read `inventory/20261010T005617Z.public-summary.json`. Six source-index partition SHA-256 hashes were locally verified against downloaded Drive bytes; all 89 JSONL lines parsed and matched manifest counts. Source receipt reports 21 scopes, 459 attachment statuses, 269 size mismatches, and missing archived-thread coverage. **None of the 89 index pointers are engineering truth or admitted project work.**

## P1 contract

- `schema/evidence-record.v0.1.schema.json`: per-version, private normalized evidence (including quarantine fields).
- `schema/attachment-fidelity.v0.1.schema.json`: per-check private byte fidelity and provenance.
- `control/project-source-map.v0.1.json`: verified public project-master aliases, **no assumed provider channel bindings**.
- `control/publication-policy.v0.1.json`: publication deny-by-default.
- `sql/evidence-registry.v0.1.sql`: relational design for authenticated private storage, not a deployed database.

Stable record ID = `EV-` + SHA256(UTF-8 of `provider|provider_channel_id|provider_message_id|source_content_sha256`). `source_content_sha256` must come from the actual preserved version bytes, not a display caption or guessed message digest. Replay of identical message version gives the same ID; changed bytes create a new version whose `supersedes_id` points to the predecessor. Preserve every older version.

Private raw/candidate files and attachment failure ledgers are handled only via authenticated private storage; the token `private-store://` is a conceptual routing label, **not an actual path**. A public projection remains blocked until private originals, independent project mapping, human admission, and privacy approval pass.

## Audit

P0 immutable PRE Git commit: `5c7e1d7010fc1f961f16232beb1fa0c19e0df4a5`. The original Drive files were read only. GitHub commits are reversible immutable snapshots. See a separately appended POST readback receipt for write verification. This P1 contract does not migrate or modify canonical project-master, Daily Ops, or Drive data.
