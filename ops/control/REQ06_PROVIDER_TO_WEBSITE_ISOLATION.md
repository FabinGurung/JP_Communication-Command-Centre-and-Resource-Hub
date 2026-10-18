# Request 06 — Discord/Slack Evidence and Website Data Separation

**Status:** WEBSITE_PIPELINE_GATES_VERIFIED; NEW_PRIVATE_PROVIDER_INGESTION_NOT_RUN  
**Canonical sources:** live Google Drive originals; GitHub is version control for approved public-safe website projections and code.  
**Website:** public read-only GitHub Pages; not a private archive or a source of engineer acceptance.

## 1. Simple operational separation

```text
DISCORD originals ─┐
                   ├─→ EXISTING AUTHORIZED GOOGLE DRIVE ORIGINAL ARCHIVES
SLACK originals ───┘                     │
                    provider-specific, append-only capture receipts
                                         ↓
A9_CWO_DAILY_TWO_CHANNELS / machine staging and quality checks
  RAW_JSONL / ATTACHMENT_BYTES / DERIVATIVE_BYTES / DAILY_INDEX_JSONL
  RUN_RECEIPTS / CANDIDATES_JSONL / PROVIDER_SOURCE_POINTERS
  PROJECT_ASSOCIATION_STAGE / QUARANTINE_UNMAPPED
  PROGRESS_REPORT_MACHINE_STAGE
                                         ↓
                Verify provider identity, SHA-256, project FK,
                source coverage and attachment fidelity
                                         ↓
                  Human source/privacy admission review
                                         ↓
                      PUBLISH APPROVED SUMMARY ONLY
                                         ↓
                     GitHub progress JSONL (read-only)
                                         ↓
                         Progress Report page

CHECKLIST: Engineer → browser-local notes. Not read from Progress Report.
RESOURCES:  Drive source file refs → versioned resource index. Not from Progress Report.
DEVELOPER:  Repo code/rules/CI/software tasks. Not a project data registry.
```

## 2. Storage authority and stable identity

Existing Drive workstream root: [A9_CWO_DAILY_TWO_CHANNELS](https://drive.google.com/drive/folders/1mtTZUPlBHd7bDV715qSWACRS2i5MalT9). Reuse the ten verified category folder IDs in `communication-extract-staging.v0.1.json`; metadata was read back on **2026-10-13 NPT** in `req06-drive-folder-readback.v0.1.json`. Discord and Slack provider originals stay in their existing separate Drive archives. The workstream's staging root does not imply either provider has been fully harvested. Do not move, overwrite or duplicate existing originals.

Private normalized records follow the existing [evidence-record JSON Schema](../evidence/schema/evidence-record.v0.1.schema.json), [attachment-fidelity schema](../evidence/schema/attachment-fidelity.v0.1.schema.json), [append-only SQL contract](../evidence/sql/evidence-registry.v0.1.sql) and [project association map](../evidence/control/project-source-map.v0.1.json). Preserve:

- Message source PK: `provider + provider_channel_id + provider_message_id`; each revised content SHA-256 becomes a version with forward/backward lineage.
- Evidence PK: stable `record_id`; run FK, receipt FK, source hash, observation time, evidence type and claim state.
- Project/company FK: only join to verified canonical project and company authority. Ambiguous source mappings go to `QUARANTINE_UNMAPPED`.
- Attachment record: source ID, declared length, actual bytes, original/archive SHA-256, fidelity classification. A derivative is never asserted to be an original.
- Capture receipt: source scopes, collection cursor, row counts, media failures and PRE/POST readback evidence. Deduplicate by provider PK and verified hash.

**Never commit raw Discord/Slack rows, private source bytes, operational credentials or original attachment material into the public GitHub Pages repository.**

## 3. Who can change what?

| Lane | May change | Must not change |
| --- | --- | --- |
| Provider collector | Authorized private Drive source archive and receipt | Public Progress Report, checklist, resources |
| Private evidence normalization | Private JSONL, hashes, quarantine and project source review | Website pages or approved engineering facts |
| Progress publisher | After documented review, one public-safe report projection | Checklist, drawings/resource catalog, project master |
| Site engineer checklist | Their own browser-local project/date reminders | Progress JSONL, Drive source, resource index |
| Resource librarian | Versioned pointer library after authorized Drive metadata check | Progress report, checklist, provider original bytes |
| Website developer | Presentation, governance, schemas, CI | Invented work progress, quantities or acceptance |

`scripts/validate_publication_lanes.py` is the CI gate: it inspects the **full Git push range** (or PR merge-base), blocks independent data domains changed together, rejects raw binary/private provider source paths, verifies Drive folder route IDs, checks every public progress FK/type and freezes historical rows.

`ops/control/progress-publication-gate.v0.1.json` controls prospective publication. The existing 37 records are a **legacy partial public seed**, not newly certified engineering truth. New rows are denied unless a review entry contains a source receipt/hash, project identity, privacy and media gate, human-review declaration and conservative engineering claim limit. CI verifies the declared metadata and cannot independently authenticate the reviewer; actual review still requires an authorized person and provider readback.

## 4. Release procedure

1. Read live source ownership and current Drive metadata. Keep original provider coverage and source-run receipts authoritative.
2. Normalize privately; quarantine ambiguous project aliases, mismatched attachments and conflicting versions. Never infer completed work.
3. Record an actual source-review receipt and permit only a sanitized, source-attributed projection.
4. Make a **single-owner Git change**. No parallel writes to checklist or resource original names.
5. Run `python scripts/test_cwo_evidence_engine.py`, `python scripts/test_publication_lanes.py`, `python scripts/validate_publication_lanes.py`, existing source validators and browser QA.
6. Verify the exact Pages source commit/deployment, Git readback, original Drive receipt and PRE/POST rollback trail.
7. Only then surface the approved summary under Progress Report or a future project subpage. Do not automatically populate a daily checklist.

## 5. 2026-10-13 checkpoint boundaries

Verified Drive: all ten existing staging category folder IDs and parent links; previous six-file Progress Report machine stage exists. The pointer, project-association, quarantine, and direct RAW_JSONL/RUN_RECEIPTS staging folders were observed empty, so **no new ingestion is certified** by this run. The previous 269 media mismatches have **not** been freshly reaudited. No new public progress rows, work status changes or engineer claims were created.

**Next independent provider run:** authenticated original inventory, receipt/cursor comparison, permitted idempotent private candidate staging and media-fidelity QA. No provider run should be marked complete solely because a folder or a public website page exists.
