# Communication and Web: human-editable source ownership

User direction, 25 October 2026: every displayed business fact and every Excel
output must have an identifiable Google Sheet owner. Humans edit that source.
GitHub owns code, validation, rendering and generated outputs. Multiple pages
reuse one source; do not make another editable workbook for the same facts.

This is a migration contract. The entire website is not yet Sheet-driven.
The 14-category publishing implementation covers the map, still requires its
Google identity and its first verified live fetch, and does not automatically
connect all the other website panels. JSON/CSV remain generated output formats;
they must not become independent places to edit the facts.

## Current website hierarchy and missing owners

```text
Communication and Web
├── Home
│   └── Navigation, introductions and destination descriptions
│       └── Website Content Sheet: owner still needed
├── Project Map
│   ├── Projects, company, locations and public display choices
│   ├── People and company relationships
│   ├── Work catalogue, funding and assigned work
│   ├── Materials and site stock
│   └── Project sections, file links and potential projects
│       └── 14 existing category workbooks; four current source owners,
│           ten prepared category copies awaiting verified cutover
├── Daily Checklist
│   ├── Published instructions: Published Site Instructions Sheet needed
│   └── Personal notes: currently browser-local; shared Sheet intake needed
├── Progress Report
│   ├── Reviewed messages and source evidence
│   ├── Historical reported progress
│   └── Drawing/document issue states
│       └── Editable Sheet owners and publication adapters still needed
├── Resources
│   ├── Desk: drawings, reports, models, estimates and original folders
│   │   └── Reconcile the existing Project File Links category before
│   │       creating another resource register; publication adapter needed
│   └── Field
│       ├── Rohini and Fishtail contacts: two existing contact workbooks
│       ├── Shared contact master: existing contact workbook
│       ├── Sharada issues: existing issue/backcharge register
│       ├── Chaudhary attendance: existing team attendance workbook
│       ├── Materials: existing Fishtail materials/inventory workbook
│       ├── Paras: existing attendance/expenses workbook
│       ├── Shiv: existing site-visits/expenses workbook
│       └── Company locations: two existing location workbooks
│           These source cards are not ten live public data mirrors.
├── Site Coordination
│   ├── Project context and current work
│   ├── Open issues and engineer questions
│   └── Three-day schedule
│       └── Coordination owner Sheet needed; resolve schedule ownership
│           with Scheduling rather than creating a second activity owner
├── Developer Workspace
│   ├── Repository and software links
│   ├── Software backlog and older pending-work view
│   ├── Integration/readiness status and release receipts
│   └── Control, storage and archive instructions
│       └── Website Operations/Content Sheet owners still needed
├── Memory Poster Board
│   └── Poster text and operating rules: Website Content owner needed
├── How-To
│   └── 1-, 3-, 7- and 15-page guides: Website Content owner needed
├── Files and Sheets
│   └── Browser-local navigator: currently Drive inventory-derived;
│       human-editable Drive directory Sheet still needed
├── Project submissions directory
│   └── Generated approved-submission directory; source/admission Sheet
│       ownership still needed before treating it as Sheet-driven
└── Older compatibility URLs
    └── current-works.html, how-to.html and workspace.html
        Reuse the same domain owners; do not create duplicate sources
```

The two company contact directories and two company location workbooks overlap
with shared enterprise subjects. Existing files must be inspected for formulas,
row ownership and parity before choosing or changing their editing authority.
A prepared split copy or a published JSON snapshot does not establish a live
connection. Do not duplicate entries across those files during reconciliation.

## Human-visible provenance

Every published panel and Excel export should identify its source Sheet name,
link, relevant tab, source version/read date and publication status. Raw drawings,
photos, messages and models remain in their original Drive files; their editable
labels, associations, issue states and display decisions belong in the owning
Sheet. Generated figures retain their source record references.

The current browser-local checklist is not a shared Google Sheet. Preserve
existing local notes before implementing authenticated submission/readback.
Do not place Google credentials in public client-side code.

## Archive placement

All PRE, POST, superseded and rollback copies belong under `01_JP / 99 Archive
Gallery`, grouped by company/person/project and source workbook. Keep the live
file in its working folder. Move existing historical files and folders by ID;
do not duplicate or delete them. Preserve each original parent and destination
in the private restore log. The live Sheet version-history tab may link to its
central archive; it must not create another working copy.

The control helper now locates one workbook archive folder by stable source ID,
reusing it after a source-title change. Existing friendly archive folders use a
stable source-ID suffix. Newly created folders also carry jp_source_file_id.
Historical VERSION_HISTORY and FINAL_POST records remain archive-classified.

`98_INTAKE_STAGING` is excluded while the owner edits it. These rules do not
promote data into other repositories or change source sharing/publication scope.

## Existing editable workbook links

Four current shared source owners and ten prepared category copies:

- People — v1.1: https://docs.google.com/spreadsheets/d/1gBYUKwt3_eUy-h9FdDCv4o2-RxxT6dBqqY4yRG2Hws4/edit
- Projects and Locations — v1.2: https://docs.google.com/spreadsheets/d/1JqzjBNBCT_AAIBkuGsIR5VBOJ3_HyifdPDc7K_jF5Bo/edit
- Companies and Organizations — v1.1: https://docs.google.com/spreadsheets/d/1cwubE_4nB2SAEdLu6ry80G0HeNjbBdu4X3DA6jrcQ1E/edit
- Work Catalogue — v1.2: https://docs.google.com/spreadsheets/d/1D4T08NciyhlMxxTgTtik_SJWf-UaIytB56fNRsvuqms/edit
- Project People and Companies — v1.0: https://docs.google.com/spreadsheets/d/1SC0Iz5IKwUCx5elSVyok0Z0hV0Z5hHiMCzkWWv0Y2uU/edit
- Project Funding — v1.0: https://docs.google.com/spreadsheets/d/1pNXK4JQnYI62V8iZsI64yyVEYiRxB3UZ7Z9R6JxoZUs/edit
- Project Work — v1.0: https://docs.google.com/spreadsheets/d/17YPRpaXIdHloH5-lzsjUpNvXLbsDfrIrlsn2jZ-7KKc/edit
- Materials — v1.0: https://docs.google.com/spreadsheets/d/10D96YqZn6NbbSm6X6nsPVw4tG_IELIj957uZ2DmhJZs/edit
- Site Material Stock — v1.0: https://docs.google.com/spreadsheets/d/1J0c-usE3jUubT_hCTxxklHzyVBzxoFZaJtCsuG3toWA/edit
- Project Sections — v1.0: https://docs.google.com/spreadsheets/d/1kAtyZPQOdSzxDS83AYwIBzrj5OIsvBKE_8orH8ez07U/edit
- Project File Links — v1.0: https://docs.google.com/spreadsheets/d/1uC1IZG440Hrg78hurYlmVA_OJG5Z-04TgKcxs1_TZmU/edit
- Potential Projects — v1.0: https://docs.google.com/spreadsheets/d/1dAz0QhEj_UItB-m_BIt7jJZ_qJvjmJ8Ou9rVv2yXqWE/edit
- Office Locations — v1.0: https://docs.google.com/spreadsheets/d/12wGg0UBLbN03u3EhJN-uQV9O2s_FRVwX9V_D2rTDXC8/edit
- Website Display Choices — v1.0: https://docs.google.com/spreadsheets/d/1tDpsphzARq-rk1MExU4DXC8mG_clh-0TXJwRr2qljXU/edit

Existing field-source workbooks (links verified against Drive metadata):

- Rohini Contact Directory: https://docs.google.com/spreadsheets/d/1Cyuj0uti-IN7ddDNVdAd1kM0NNpATdTnNabfcY7P1cw/edit
- Fishtail Builders Contact Directory: https://docs.google.com/spreadsheets/d/15szptLz7q3-Rote1SnNuIqdcrxrm0z2m0k7yx9j51c4/edit
- A9 Master Contact Directory (6NF): https://docs.google.com/spreadsheets/d/10l4F1ZShkPKt7L8HBT1BJ3K0rjkJ6GktXRZdI4k35Bg/edit
- Sharada 31 Site Issues: https://docs.google.com/spreadsheets/d/1j_866LE1heYTozkUheH3kU55TV8ZXuLzTwTCZzZNbqw/edit
- Hari Chaudhary Team Attendance: https://docs.google.com/spreadsheets/d/1FuFvccGvDwlszfzGL7_TP4qChBptA8Pil7eq6O5qlPw/edit
- Fishtail Materials and Daily Progress: https://docs.google.com/spreadsheets/d/1YshLrDAJDg3CO8F1jmIr2Eucy0-TKwiviVNF5tiAfT0/edit
- Paras Pariyar Attendance and Expenses: https://docs.google.com/spreadsheets/d/1HSmklPhqSPo6-N-7tbidOzwsZleJHrHlIyR34h7GgtI/edit
- Shiv Narayan Chaudhary Site Visits and Expenses: https://docs.google.com/spreadsheets/d/11uTBk0DDF_OkpNpmgbee4zXNGhAOQK0DS-ao8Qw0-uc/edit
- Fishtail Project Site Locations: https://docs.google.com/spreadsheets/d/10uW7hxagyvcNCUVDXTmwHopJgUbbqGBOxjjYjogQd_E/edit
- Rohini Project Site Locations: https://docs.google.com/spreadsheets/d/1wC5KRv45UCmRhSesO2WcwN8fNGdC5gSjvjqlR9USsdM/edit

Archive centralization: 886 existing historical items/folder trees moved; 428 container-parent relationships read back. Stable source IDs and live-file locations retained. The private restore record and navigator hold the exact per-source folder routes. Colab V000008 has been prepared with full freshness scanning and per-workbook backup routing; V000007 remains the last successful runtime.
