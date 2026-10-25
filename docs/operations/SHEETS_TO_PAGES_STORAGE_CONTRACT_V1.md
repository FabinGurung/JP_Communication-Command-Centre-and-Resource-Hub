# Sheets to Pages, run by GitHub Actions

User direction of 25 October 2026: Actions owns the entire publishing run.

**Individual source Sheets → Actions assembles one publishing Sheet for this repository → Actions reads it back and validates public JSON → Pages deploys.**

People edit the source Sheets. The publishing workbook is an automatic copy. Colab handles Drive inventory and missing Sheet change histories; it is not required for publishing.

## Implementation

The existing Operations Hub production workflow on feature/daily-ops-current-work now contains the Google refresh step. scripts/sync_sheets_to_pages.py uses ops/control/sheets-actions-publishing.v1.json and the live publishing router.

1. Read and validate all 14 individual sources. Initial cutover of the ten staged copies requires exact equality with their previously active tabs. Stale copies stop the run.
2. Check headers, IDs, references, coordinates and concurrent changes. Source cells are never written.
3. Archive prior publishing values, router, manifest and history in the existing user-owned previous-versions file. Records are append-only, numbered and hash chained. Conditional upload and exact readback are required. Actions creates no new My Drive files; service accounts cannot own those files. The existing native V000002 PRE copy preserves the original import formulas.
4. Rebuild the publishing data tabs and router/history in one atomic Sheets batch. Versions advance on changed input, not an unchanged execution.
5. Read back the assembled workbook and recheck sources. Generate the public payload from this readback.
6. Validate public IDs, columns, references and visibility. Transfer exactly that public payload to the deploy job. Do not regenerate an older snapshot over it.

A configured Google connection that fails blocks deployment. Without a Google connection, code pushes can still publish the reviewed snapshot, explicitly labelled in the Actions warning, summary and live_google_sheets_fetch=false payload. A manual run with require_live_sheets=true fails if Google is unconfigured. Snapshot success is not Google-refresh success.

## One-time Google setup remains open

The connected ChatGPT Drive account is not an Actions identity. No chat access token is copied or installed in GitHub.

Preferred: configure repository variables JP_GOOGLE_WORKLOAD_IDENTITY_PROVIDER and JP_GOOGLE_SERVICE_ACCOUNT, with Google federation restricted to this repository and the registered Pages branch. Enable the Sheets and Drive APIs in that Google Cloud project. Alternatively, install a dedicated service-account key JSON in repository secret JP_GOOGLE_CREDENTIALS. Never put credentials in Sheets, source files, issues or chat.

Give that identity reader access to the 14 source workbooks and writer access to only the publishing workbook and its existing previous-versions file. No source write access or public sharing is needed. Temporary gha-creds files are ignored by Git and excluded from the explicit Pages artifact.

Then run the existing workflow on the Pages branch with require_live_sheets=true. Acceptance requires real fetch, archive/master readback, 14 distinct active source IDs, a live_google_sheets_fetch=true bundle and a successful Pages deployment. Offline tests alone do not establish that connection.

Current triggers: branch pushes and manual runs. A Sheet edit alone does not trigger GitHub. An effective hourly schedule requires a governed workflow on the default branch; no schedule is claimed on this feature branch. Other repositories require their own source assignments, publishing workbook and verified Google access. This implementation covers the Operations map.

## Public data boundary

The private publishing workbook receives the complete source tables. The public bundle uses only already-admitted IDs and explicit refresh_fields. Public names, status, coordinates and catalogue labels can refresh. Visibility revocation removes or masks records.

New records, People details, free-text evidence, money, measured construction progress and previously redacted cells retain their publication-review requirements. Reviewed static fields remain labelled in a live bundle. No private source values or PRE records are written to repository files, runner logs or Actions artifacts. Only the approved public bundle is uploaded.

## Readable Drive navigation

The 01_JP main paths are Colab Notebooks, Useful References, Shared Registers, Fishtail Builders, Rohini Engineering and Builders, Office and Site Records, and Archive Gallery. Shared Registers separates Working Sheets, Website Publishing, Not Connected Yet and System Records. Previous Sheet Versions are centralized in Archive Gallery.

The 15 core workbooks now use names such as People, Projects and Locations, Materials and Site Material Stock, retaining their data-version suffixes and original live IDs. Unconnected copies remain separated until cutover. Technical inventories and older PRE/POST records belong in System Records or the archive. No folder was deleted. JP and AEC remain separate.

Each core workbook retains its manifest/history and verified PRE copy, with a V000002 navigation-control entry; its source data release is unchanged. Colab refreshes affected Drive folders and continues missing histories for other active Sheets. Explicit archive IDs prevent readable renames from accidentally reactivating historical Sheets. Wider consumer mapping remains unfinished.

## Whole-site Sheet ownership

The later user direction extends the one-source-Sheet requirement to every displayed fact, editorial content and Excel export. `COMMUNICATION_WEB_SHEET_OWNERSHIP_V1.md` records the full hierarchy and current gaps. The map implementation does not cover every page. Native source workbooks must be identified before additional adapters or copies are created. Historical copies are grouped centrally by source, outside active working folders.
