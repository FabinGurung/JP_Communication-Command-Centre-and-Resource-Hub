# Communication & Web and Resource Library ownership

Communication & Web owns the Project Map, Notification Center and Progress Report. The new Operations workflow reads only Projects and Locations, Website Display Choices, Notification Center Instructions, Message Sources and Project Work. Project Work rows must be explicitly public. Raw notes, quantities, rates, source evidence and private coordinates stay out of the artifact. The Project Map uses each project's visibility and separate display controls. An approved listing may have no public pin.

The Field & Desk Resource Library owns its catalogue and client packets in the original Project Resources workbook. A resource edit requires only that repository's refresh. The current Operations Pages site routes `/resources/` and `/resources/project-documents.html` to the current Library Pages site, preserving query strings such as `project=PRJ-000029`. Use the current repository slugs in bookmarks and shared Pages links. The already-live Astam feasibility URL is preserved as a separately governed compatibility snapshot. Earlier Operations files and resource views remain available in Git at the numbered PRE checkpoint.

## Live operation

The production Pages workflow builds from `main` in `SHEETS_V2` mode. Its five source workbooks and their exact tab names are listed in `scripts/publish_operations.py`. The file `operations.json` is generated during the build. The Git operational files and edit-routing rules used by the older lane remain available for rollback and historical work.

The former Workspace and Quick Start URLs lead to the current operator help page. The Astam landing page and buyer guide are explicitly included in the publication allowlist. The historical workspace sources remain in Git.

## Cutover order

1. Publish and verify the independent Resource Library before switching the Operations artifact, so old client document links remain usable.
2. Configure a main-only Google WIF provider for Operations and set `JP_GOOGLE_MAIN_WORKLOAD_IDENTITY_PROVIDER`. Reuse the verified `JP_GOOGLE_SERVICE_ACCOUNT` if it still has Viewer access to the five source workbooks. Leave the old branch's provider variable separate.
3. Run [Operations from Google Sheets](https://github.com/FabinGurung/jp-site-operations/actions/workflows/operations-sheets-pages.yml) on main with **publish** clear. Verify the projection job and Pages artifact. Set `JP_OPERATIONS_PAGES_MODE=SHEETS_V2` only when the new Library is live and the Operations artifact has passed review. Run again with **publish** selected. Scheduled refreshes run hourly in SHEETS_V2 mode.
4. Verify the three sections and the old resource redirects from the resulting Pages deployment. The historical branch remains available for explicit rollback. Its old deployment must stay disabled while SHEETS_V2 is active.

See the [prior live Google-authenticated run](https://github.com/FabinGurung/jp-site-operations/actions/runs/40784101634) for the previous working-branch setup. It does not verify the new main workflow or grant the Resource Library repo access to Google.
