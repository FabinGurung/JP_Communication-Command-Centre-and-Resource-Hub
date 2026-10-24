# A9 / JP — Drive storage and archive policy (working proposal)

This is a proposed file-storage policy, **not a completed migration** or replacement for operational authorities.

## Responsibilities
- **Google Drive** retains original bytes, stable file/folder IDs, access control, human-friendly company/project folders and an archive gallery.
- **GitHub** owns versioned safe SQL text/schema and the existing public project resource relationships in `ops/data/project-resources.json`. Its project/Daily Ops authorities are unchanged.
- **Google Colab** resumes the Google Docs JSONL staging scan using Drive metadata only; makes paginated listings, generates a global-depth-first tree, and creates inspectable SQLite/JSONL/CSV outputs.
- **SQLite** is a generated private metadata query snapshot. SQL DDL in GitHub defines inspectable PK/FK relationships. JSONL is appropriate for checkpoint/events. Drive is not used as a relational database.

## Archive rules
1. Complete the recursive inventory and audit missing nodes, identity conflicts and pagination before bulk changes.
2. Keep company roots discoverable and preserve the authorized private enterprise folder.
3. Move only individually reviewed obsolete folders into the `99_ARCHIVE_GALLERY`; never select folders simply by prefix or name.
4. Keep original Drive IDs and filenames; no delete, trash, blind rename, ACL change or unrequested cross-repository change.
5. Record old/new parents and exact IDs before every move, validate visibility/permissions, read back the provider result and retain a rollback ledger.
6. Rerun inventory after moves; a metadata index is not an immutable file-content backup.

## Confidentiality
This repository is **public**. Do not commit raw Drive inventories, private file names/IDs/paths, personnel or financial data, source binaries, or unapproved private relationships. Inherited permissions on a shared Drive folder are not owner-only merely because the folder title includes 'PRIVATE'. Private snapshots require access-controlled storage.

## Workstream boundary
A9 / JP company-enterprise operations only. AEC academic thesis work remains separate. Existing resource relationship authority stays in `ops/data/project-resources.json` and `ops/schema/daily-ops-postgres.sql`.
