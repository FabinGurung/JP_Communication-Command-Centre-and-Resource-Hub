# Astam Village — JP Enterprise client page and source-control handover

Date: 2026-11-05 (Asia/Kathmandu)  
Owner: JP_Enterprise, not Fishtail Builders or Rohini Engineering.  
State: **STAGED / SOURCE PERMISSION AND LIVE DEPLOY NOT YET VERIFIED**.

## Canonical owner and presentation

- Google Drive owns original evidence, document versions and access permission.
- A dedicated native Google Sheet owns editable due-diligence checks, observations, approved-public fields and document links. Its permanent ID is defined only in `ops/control/astam-sheet-source.v1.json`; no source material is mirrored into this GitHub repository.
- `ops/data/land-feasibility/astam-village-public.v1.0.json` is the allowlisted reviewed public snapshot, updated during eligible GitHub Actions runs.
- `/feasibility/` is the intended public client-facing entry point; the existing home page links there. Google Drive links are presented as permission-gated categorized cards rather than as a standalone folder navigator.
- Charts count ten due-diligence checks grouped by domain and status. These are *checklist counts*, not physical measurements, financial estimates, confidence scores or licensed assessments.
- Detailed exact parcel location, owner documents, private conversations, and transaction amounts are excluded from public JSON and static HTML.

## A7 original-ID and version rules

The original native Sheet ID never changes. Its first source version is V000001, with PRE and POST whole-workbook copies under the centralized private archive. The private audit/source-register contains the exact original/PRE/POST IDs, readbacks and rollback instructions. Do not relink the website to a snapshot; restore into the same live original ID.

The platform's existing main and working branch diverged previously. This project uses only the registered `feature/daily-ops-current-work` Pages lane; no force-push or merge-to-main is authorized by this change.

## Actions pipeline

1. Run project privacy and source-contract tests.
2. Authenticate with the existing repository-scoped Google Workload Identity.
3. Read the four approved native source tabs and reject unknown identities, unsafe links, unsupported certification statuses, sensitive values or missing allowed fields.
4. Preserve last approved public snapshot when a non-required source read cannot be performed; emit an explicit warning. A required-live refresh must fail closed.
5. Upload the validated Astam JSON from the validation job; the Pages deployment job downloads that exact artifact.
6. Assemble only explicitly allowlisted public assets and deploy through the existing Pages workflow.

**A push is not a deployment receipt.** Confirm the validation job, source readback, deployment job and browser view before calling this release live.

## Outstanding blockers

- The dedicated Google Sheet needs Reader access for the *same established GitHub Actions publisher account* that can already read the older single-subject sources. The connected share operation was blocked, so this grant remains unverified.
- The global Projects master PRE duplication was blocked. No global project ID was allocated, and no existing master/party/publication rows were changed.
- A successful Actions run/deployment readback for the latest Astam commits has not been retrieved from the available connector surface.
- Site geotechnical, water, title, access, power corridor, planning and view protections remain pending independent verification.

The homepage link, static source snapshot and client dashboard code are committed to the registered branch, but production publication must be verified separately.
