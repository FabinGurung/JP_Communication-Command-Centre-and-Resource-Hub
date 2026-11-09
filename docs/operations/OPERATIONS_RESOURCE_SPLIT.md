# Communication & Web and Resource Library ownership

Communication & Web owns the Project Map, Notification Center and Progress Report. The new Operations workflow reads only Projects and Locations, Website Display Choices, Notification Center Instructions, Message Sources and Project Work. Project Work rows must be explicitly public. Raw notes, quantities, rates, source evidence and private coordinates stay out of the artifact. The Project Map uses each project's visibility and separate display controls. An approved listing may have no public pin.

The Field & Desk Resource Library owns its catalogue and client packets in the original Project Resources workbook. A resource edit requires only that repository's refresh. Operations retains stable outbound links and compatibility routes, including the prior Basanti URL with its query string. The already-live Astam feasibility URL is preserved as a separately governed compatibility snapshot. Earlier Operations files and resource views remain available in Git at the numbered PRE checkpoint.

## Cutover order

1. Publish and verify the independent Resource Library before switching the Operations artifact, so old client document links remain usable.
2. Configure a main-only Google WIF provider for Operations and set `JP_GOOGLE_MAIN_WORKLOAD_IDENTITY_PROVIDER`. Reuse the verified `JP_GOOGLE_SERVICE_ACCOUNT` if it still has Viewer access to the five source workbooks. Leave the old branch's provider variable separate.
3. Run [Operations from Google Sheets](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/actions/workflows/operations-sheets-pages.yml) on main with **publish** clear. Verify the projection job and Pages artifact. Set `JP_OPERATIONS_PAGES_MODE=SHEETS_V2` only when the new Library is live and the Operations artifact has passed review. Run again with **publish** selected. Scheduled refreshes run hourly in SHEETS_V2 mode.
4. Verify the three sections and the old resource redirects from the resulting Pages deployment. The historical branch remains available for explicit rollback. Its old deployment must stay disabled while SHEETS_V2 is active.

See the [prior live Google-authenticated run](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/actions/runs/40784101634) for the previous working-branch setup. It does not verify the new main workflow or grant the Resource Library repo access to Google.
