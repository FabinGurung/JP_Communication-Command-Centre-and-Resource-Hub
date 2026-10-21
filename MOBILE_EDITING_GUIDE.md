# Edit the map from a phone

1. Open the [native Google Sheets map master](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit) with your authorized Google account.
2. Edit the correct worksheet (for project name, status, coordinates and public project details use **projects**). Keep the existing project IDs and column headers unchanged.
3. For any new or corrected project, request the **reviewed map Sheet refresh**. A Sheet edit alone does **not** change GitHub Pages.
4. The publisher validates PK/FK links, data fields and public-visibility rules, updates the approved JSON projection on `feature/daily-ops-current-work`, and confirms GitHub Actions validation and Pages deployment.
5. Open the [live project map](https://fabingurung.github.io/JP_Communication-Command-Centre-and-Resource-Hub/map.html) and check markers, popups, search and mobile layout.

**Never edit root CSV files for active map data.** They are frozen historical rollback. Never publish private details or place Google access tokens into public GitHub. Map presentation settings belong to `map-config.json`; engineering source documents remain in permission-gated Drive.
