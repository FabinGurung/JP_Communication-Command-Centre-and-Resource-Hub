# Existing starred Sheets and publishing integration

The source audit covered all 18 starred workbooks and their 310 original tabs.
Existing live IDs were retained. Each starred source now has an enumerated control
version, native PRE/POST copies in its own history folder, a manifest and history
receipt, and a readable starting tab. Three overlapping or empty non-starred
workbooks were also versioned while their active routes were retired.

The fuller starred Paras and Shiv originals remain the attendance/visit owners.
Twenty-seven explicitly checked Shiv visits were retained from the simplified
copy. Paras's five expense identities were reconciled without creating extra
expenses, preserving both sets of notes; one date/project remains flagged for
review. The overlapping originals are archived with their IDs and access intact.
Empty stock and Shiv expense templates are excluded from active fetching.

The existing supplier workbook's broken private IMPORTDATA was replaced with
300 authenticated context records from its original private export. Its 312
human review entries remain a review queue. This is a verified snapshot, not a
background import or reviewed invoice transcription. Other Intake Staging content
was not scanned or reorganized. Personal applications and research bookmarks stay
outside JP operational feeds.

## Joined publishing tables

`scripts/field_sheet_sources.py` interprets 16 existing input tabs across 12
populated operational workbooks. Eight derived tables were added to the same
repository publishing workbook and passed exact native source/master readback:

| Joined subject | Records | Publication |
| --- | ---: | --- |
| Company contacts | 26 | Existing admitted identities and approved fields only |
| Material movements | 16 | Private joined copy |
| Site progress | 140 | Private joined copy |
| Site readiness | 44 | Private joined copy |
| Attendance and site visits | 130 | Private joined copy |
| Expenses | 10 | Private joined copy |
| Vendor payment summaries | 27 | Private joined copy |
| Supplier/measurement review queue | 1,468 | Private joined copy |

Legacy progress-event IDs are reused for distinct reports. The adapter preserves
the old ID as evidence, gives each imported record a traceable source key, flags
reused IDs, and retains exact-repeat provenance without overwriting other reports.
Unchecked attendance boxes and formula-filled calendar rows are not absences.
Unused expense IDs are not transactions. Unparsed measurement quantities stay
blank. The vendor table is a summary, not a transaction ledger.

The publishing workbook now contains 25 data tables: 14 core contract slots,
three resource/notification tables and eight operational tables. The empty stock
slot remains empty without fetching its inactive template. There are 28 distinct
active input workbooks: 13 populated core owners, Project Resources, two
notification/provenance owners and 12 operational workbooks.

## Actions and public contacts

Actions rechecks source layouts and concurrent changes, snapshots the previous
publishing state, writes the joined copy, verifies its readback, and generates one
validated public bundle. It never writes source cells. Native joined table ranges
grow with the imported data. Only the public bundle reaches the Pages artifact.

The contact page now reads `contacts` from that same bundle. Stable Contact IDs
were added to the original company Sheets without changing their six existing
data columns. Names are pinned to admitted IDs; reassignment stops publication.
Phone, role, project and verification edits for admitted identities can refresh.
New contact IDs, private Notes, attendance, finance and raw evidence do not enter
the public bundle. The older standalone contact snapshot remains historical.

Automatic Google refresh is **not yet verified**. Initial assembly used the
connected Sheets API. Configure the dedicated Google identity, grant read access
to the 28 registered workbooks and admitted original-message files, and grant
write access only to the publishing workbook and its existing restore-history
file. Then run the Pages workflow with `require_live_sheets=true` and verify
`live_google_sheets_fetch=true` plus successful Pages deployment. Snapshot deploys
and offline tests do not satisfy that gate.

## Navigation and remaining work

The same publishing ID now opens with Start Here, a source directory, the complete
starred list and a release checklist. The same Drive HTML guide is updated in
place, retaining its earlier inventory IDs. Drive stores HTML but does not execute
its scripts in preview; the native Sheets guide is the direct mobile entry.

Two fuller source owners moved into the central working category. Four active
owners remain in their original shared folders to preserve inherited readers;
the directory links them. Source archives have readable names and dedicated
folders. Small HTML pointers link the actual folders to their live owners and
history, without duplicating facts or creating working workbooks.

Ordinary folder renames and moves do not require a full inventory scan because
Actions uses explicit Sheet IDs. New sources require an explicit configuration
entry and review. Whole-site editorial/Excel ownership migration, continuous
message intake, a new V8 receipt, and the required live Actions fetch remain
separate release gates. No milestone tag is created by this preparation pass.
