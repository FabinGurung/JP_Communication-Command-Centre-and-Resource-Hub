# A9 contact-directory current dependency readback (2026-10-21)

**Scope:** verified directly against the three current native Google Sheets, the Ops Hub registered testing branch, and available public GitHub search / Drive title and manifest search. No contact workbook changed.

## Three different roles

| Source | File ID | Status | Worksheet and website path |
|---|---|---|---|
| Rohini company contact directory | `1Cyuj0uti-IN7ddDNVdAd1kM0NNpATdTnNabfcY7P1cw` | company-specific contact table | `2_PEOPLE_DIRECTORY` → Field Resources `SRC-01` |
| Fishtail company contact directory | `15szptLz7q3-Rote1SnNuIqdcrxrm0z2m0k7yx9j51c4` | company-specific contact table | `2_PEOPLE_DIRECTORY` → Field Resources `SRC-02` |
| A9 6NF master | `10l4F1ZShkPKt7L8HBT1BJ3K0rjkJ6GktXRZdI4k35Bg` | source-of-identity/PK-FK master | `PERSON`, `PERSON_NAME_FACT`, `PERSON_PHONE_FACT`, `PERSON_ORG_ROLE`, `PERSON_PROJECT_ROLE`, `SOURCE` etc. → Field Resources `SRC-03` secure source link |

## Observed connections versus unknown

- Source URLs for all 3 were already present in `ops/data/a9-field-source-links-public.v1.0.json`; `assets/js/a9-field-resources.js` only fetched the public link catalog and visualization blueprint, **not original Google Sheet values**.
- Two company `2_PEOPLE_DIRECTORY` tables were checked via Google Sheets `FORMULA` reads; no `IMPORTRANGE`/worksheet linking formulas appeared in the populated rows. They are separate tables, not proved to be live projections of A9 master.
- The master has 20 populated `PERSON` records (plus header), 19 phone facts, 24 project-role rows, and source references to historic master registry, user assertions and Slack. These facts make it useful for stable relationships even without a current website fetch.
- Private Google Drive search finds prior master-registry workbooks, control/snapshot records and company-directory histories. Historical and named references prove governance use but not continuous execution.
- An available GitHub code search for exact live IDs did not surface other repositories. This **does not prove** that there are no references in private repositories, scripts, Apps Script, authorized connected services or deployments.
- `SRC-01` and `SRC-02` now load a privacy-minimized `26`-row snapshot on the public page, not a live API connection. Rohini 7/Fishtail 19. Contact phone values and personal notes are not published.
- Do not modify the original Google Sheets or stable 6NF PK/FK from this website flow. Before master edits preserve `CDP-*` person keys and source IDs; reconcile possible new names and role assignments without auto-merging.

## Security and refresh

The original 3 Sheets remain restricted Google documents. Public Pages exposes **only** name, role, project and source-status labels for the two selected company tables. The projection is a dated manual snapshot. The user must request a refresh when Gemini updates the worksheets; no background polling or automations configured.
