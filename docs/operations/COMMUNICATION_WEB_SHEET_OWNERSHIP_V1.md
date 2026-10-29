# Communication and Web — current source ownership

Updated 29 October 2026. Human edits belong in the existing subject Sheets. Code,
validation, rendering and public projections belong in GitHub. JSON/CSV and Excel
are generated views, never alternative editing authorities.

## Implemented publishing engine

`ops/control/sheets-actions-publishing.v1.json` is the exact machine source list.
It registers **28 distinct populated source workbooks / 32 input tabs**, plus one
admitted original message file for integrity checking. One existing publishing
workbook holds **25 data tables**: 14 core contract slots (empty stock excluded
from source fetching), resources, message sources, notifications, and eight
private operational joins. Navigation/control tabs are not extra data owners.

[Open the existing live directory](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit#gid=990001).
[All exact source links](https://docs.google.com/spreadsheets/d/17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4/edit#gid=700125).

| Display or export | Existing owner / editing place | Current behavior |
| --- | --- | --- |
| Project Map | Thirteen populated single-subject category owners; Projects and Locations owns coordinates | Same validated bundle; admitted public IDs/fields only |
| Resource cards | Project Resources; File Links retains its distinct link relationships | Same bundle; reviewed file identities retained |
| Notification Center | Message Sources + Site Notifications | Same bundle; work/material/supervision bullets, original evidence preserved, Company filter |
| Company contact pages | Existing Fishtail and Rohini contact directories | Same bundle; stable admitted Contact IDs; private Notes excluded |
| Materials movements | Existing Fishtail and Rohini materials inventories | Joined privately; not silently published as stock balances |
| Progress and readiness inputs | Existing Fishtail and Rohini Site Operations | 140 progress + 44 readiness rows joined privately; not all are engineer-approved work |
| Attendance and expenses | Fuller original Paras, Shiv and Gupta workbooks | Existing owners reused; 27 checked visits recovered; no unchecked-as-absence inference |
| Vendor summaries | Existing Gupta payments workbook | Private vendor-summary projection, not public transaction data |
| Supplier and measurement evidence | Existing supplier review workbook + measurement source archive | 312 + 1,156 source entries joined into the private review queue; no invented quantities/rates/payments |
| Excel of a current source or publishing workbook | That same Google Sheet | Google Sheets' authenticated XLSX export; no extra editable workbook needed |
| File navigation | Existing Drive inventory + the publishing workbook's source directory | Inventory supplies locations; explicit IDs drive Actions; no recursive scan per website refresh |

The engine stages reads, validates relations and public admission, checks for
concurrent edits, preserves a restorable PRE state in the existing append-only
history file, atomically updates the publishing workbook, reads it back, checks
sources again, and builds one approved public bundle. A required-live run fails
if authentication, source validation, archive or readback fails. The previous
site remains deployed if the new run fails.

**Observed connection state:** live Google fetching and Pages deployment are verified. Runs [40704962943](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/actions/runs/40704962943) and [40784101634](https://github.com/FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub/actions/runs/40784101634) passed source/master readback, public JSON validation and deployment. The latter public receipt matches commit `1803ff387140d482720fcce4ec00a85a55ae64b8`; the live map rendered eight working projects, the Rohini filter returned one, and Notification Center displayed 22 source-linked bullets. Its second refresh reported `publishing_copy_changed=false`, confirming no redundant data rewrite. The data assembly is V000008; V000009 and V000010 record human control/navigation updates. The same 29 file readers and two output writers remain; no folder-wide grants or new source workbooks were needed.

Routine publishing needs no new Cloud project, Colab run or personal GitHub token. It runs on the registered Pages branch push or manual workflow dispatch. Editing a Sheet alone does not trigger a deployment. Hourly scheduling remains unimplemented and requires a governed default-branch dispatcher; do not silently promote the working branch to main. The historical migration and business review below remain separate from this completed connection.

## Located historical pages — no user file hunt

These paths are already in this repository. They are retained history, not
missing files to be recovered by the user. Current source registrations must not
be represented as if they automatically replaced these historical projections.

| Existing data path | Known content | Handling / correct owner boundary |
| --- | --- | --- |
| `ops/data/current-works.json` | Eight older site-context snapshots | Resolve business changes through Projects/Locations and the original company Site Operations owners; do not create another project or Scheduling authority |
| `ops/data/field-three-day-board.json` | Eight old three-day display snapshots | Carry-forward requests are not approved assignments; no dated engineer-authorized schedule is inferred |
| `ops/data/site-execution-questions.v0.1.json` | Eight site contexts, five reports, 18 open issues, 36 engineer questions | Historical coordination projection; a future editable question intake must reconcile the existing issue register and preserve evidence/IDs |
| `ops/data/project-document-review-public.v1.0.json` | Three unverified document issue/revision records | Keep unverified; use Project Resources/File Links associations, never certify drawings from a file's existence |
| `ops/data/progress-report-public.v0.2.jsonl` | 37 retained records: five field-reported observations, 18 previous routine templates, 14 pending communications | Preserve immutable history. The 32 non-observation records are explicitly not measured/completed work. No exact record-ID match to the 140 operational progress rows was found; do not auto-merge them |
| `ops/data/a9-reviewed-progress-public.v1.0.json` | Empty new reviewed-progress queue | Empty is an honest state; do not fabricate records to populate it |
| Guide, Memory Wall and software control pages | Editorial instructions and code-control content | Code/documentation control in GitHub; no operational fact ownership inferred from a navigation label |

The existing Company Project Site Issues workbook is
`1j_866LE1heYTozkUheH3kU55TV8ZXuLzTwTCZzZNbqw`. It contains two real repair/cost
follow-ups; it is not an empty replacement for the 18 historical coordination
issues. Its potential backcharges remain unconfirmed. Do not overwrite those
rows or turn them into final liabilities.

## What the review queue means

A queue entry is preserved source evidence waiting for interpretation or
confirmation. It is not proof of an approved bill, payment, measured quantity or
completed work. The existing source files are already located and registered.
Their private joined queue works independently of public map/notification
publishing. Business review can continue without blocking the Google connection
or asking the user to search for the files again.

## Excel rule

The active page/JavaScript dependency audit found no `.xls`/`.xlsx` download
sources in the current presentation routes. The map's `projects.csv` reference
is rollback compatibility, not the active edit authority. Do not invent an Excel
migration requirement from this absence. Private wage/payment Excel originals
located by the Colab inventory remain private in their recorded business folders;
they are not website feeds and must not be duplicated or imported merely because
they have an Excel extension. If a particular export is needed, generate it from
its same owning Sheet and retain provenance/version information.

## Versions and scope

Each live source retains its ID and a human Manifest + enumerated Version
History. Native PRE/POST copies stay in a dedicated source folder under the
central Archive Gallery. Restore into the same live ID. Generated publishing
refreshes use the documented existing append-only restore file because the
service account cannot own new My Drive copies. Keep notebook, Sheet, Git commit
and milestone version sequences separate.

V8 is the Drive inventory/history notebook. It is not an Actions connection
notebook and is not required for each refresh. A self-contained latest inventory
notebook replaces earlier notebook code; do not run V5 → V6 → V8 in sequence.
`98_INTAKE_STAGING` stays out of broad scans/cleanup; Discord collection stays
paused. No full-site Sheet migration, automatic scheduling or completed milestone
release may be claimed solely from the current source integrations.
