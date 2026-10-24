# Sheets to Pages and human-readable Drive storage

User direction of 24 October 2026 supersedes the old GitHub-CSV-first map workflow.

## Ownership and publishing

1. Humans and authorized agents edit the individual source workbook for a feature.
2. One publishing Google workbook per consuming repository assembles those sources.
   Its data tabs are derived by imports or a validated API synchronizer; they are not
   a second place to hand-edit the same facts. Multiple tabs in that one workbook are fine.
3. Read the assembled workbook, validate PK/FK, formulas, source coverage and publication
   eligibility, then produce one JSON payload for the website.
4. GitHub Actions validates/builds; GitHub Pages serves that JSON and the interface.
5. GitHub owns code, SQL relationship definitions, source contracts and approved release
   artifacts. Drive holds original files and human-readable company/project storage.

The master is a replica of the source workbooks. The generated JSON is a replica of
the publishable master values. Neither is an independently edited authority.
Every active Sheet needs an explicit consumer mapping or an explicit UNUSED/REVIEW
disposition. Archived versions have historical use and do not need live website wiring.
Consumer coverage does not mean displaying every private column on a public page.

## Current verified implementation

The Operations map has 14 category workbooks, four currently connected owner files,
and ten staged category cutovers. Private `_SOURCE_ROUTER` identifies active and
target sources; staged copies must not silently become owners. The master uses
`IMPORTRANGE`. The public map previously requested 14 reviewed JSON tables.

The new build generates `ops/data/map-data.v1.json` from those reviewed projections;
the map requests this single payload. Actions regenerates it before assembling the
Pages artifact. This changes packaging, not the approved records.

**Private source refresh remains operator-driven.** Actions currently has no configured
Google identity/source-read job. Do not claim that a Sheet edit automatically reaches
Pages. Completing that part requires a configured Google identity authorized to read
the sources and update the publishing replica, plus source admission/coverage checks.
Do not replace this with a public anonymous export of private workbooks.

Other repositories and non-map Daily Ops sources require their own verified consumer
contracts and Sheet replicas; this map build does not migrate them implicitly.

## Version controls for every active workbook

- `00_MANIFEST`: stable workbook ID, purpose, owning source tabs/features, schema/data
  release, control version, consumer repository, publishing-master ID, JSON destination,
  connection status, and version-history reference.
- `01_VERSION_HISTORY`: append version, time, affected feature/tab, exact change, PRE
  snapshot ID, validation, rollback and data release. Initialize the control sequence
  at `V000001`; advance for verified material edits, not ordinary executions.
- Snapshot the current state into the dedicated version archive before material edits.
  Update the original live ID. Never rewrite historical entries or equate native Drive
  revision numbers with the governed release sequence.
- Keep legacy source tabs until their new owners are connected and readback passes.
- `scripts/maintain_sheet_manifests.py` is the authenticated Colab helper for adding
  missing controls. It reports unmapped consumers rather than inventing wiring. Its
  presence is not evidence that all private workbooks have been processed.

## Drive navigation cleanup

The obsolete navigation guide, superseded v0.1 roadmap and old project-map workspace
are archived with their original IDs. The old project-map publishing manifest describes
a completed historical branch promotion; it is not today's source-ingestion engine.
The command-center design is retained under Useful System References because its
architecture/routing designs may be reused. It is labelled reference-only, not running.
The user's additional enterprise writers are their own backup accounts; their presence
is not a restructuring blocker. No access changes are required by this contract.
