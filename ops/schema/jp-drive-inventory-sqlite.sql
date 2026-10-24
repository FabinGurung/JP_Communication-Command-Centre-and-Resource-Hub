-- A9/JP Drive metadata index v1.0 (SQLite-compatible contract).
-- No production records or private inventory rows belong in this public repository.
-- Google Drive owns file bytes/ACLs/IDs. Existing ops/data/project-resources.json
-- remains canonical for project-to-resource relationships.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS drive_nodes (
 drive_file_id TEXT PRIMARY KEY NOT NULL,
 parent_drive_file_id TEXT REFERENCES drive_nodes(drive_file_id),
 original_name TEXT NOT NULL,
 mime_type TEXT NOT NULL,
 provider_url TEXT,
 size_bytes INTEGER CHECK(size_bytes IS NULL OR size_bytes>=0),
 observed_utc TEXT NOT NULL,
 display_seq INTEGER UNIQUE CHECK(display_seq IS NULL OR display_seq>0),
 relative_path TEXT,
 scan_run_id TEXT NOT NULL,
 CHECK(parent_drive_file_id IS NULL OR drive_file_id<>parent_drive_file_id)
);
CREATE INDEX IF NOT EXISTS idx_jp_drive_parent ON drive_nodes(parent_drive_file_id);
CREATE TABLE IF NOT EXISTS folder_scan_evidence (
 scan_run_id TEXT NOT NULL,
 folder_drive_id TEXT NOT NULL REFERENCES drive_nodes(drive_file_id),
 scanned_utc TEXT NOT NULL,
 reported_child_count INTEGER NOT NULL CHECK(reported_child_count>=0),
 pagination_exhausted INTEGER NOT NULL CHECK(pagination_exhausted IN(0,1)),
 error_text TEXT,
 PRIMARY KEY(scan_run_id,folder_drive_id)
);
CREATE TABLE IF NOT EXISTS archive_move_audit (
 move_id TEXT PRIMARY KEY,
 drive_file_id TEXT NOT NULL REFERENCES drive_nodes(drive_file_id),
 old_parent_id TEXT NOT NULL,
 new_parent_id TEXT NOT NULL,
 approved_by TEXT,
 approved_at_utc TEXT,
 preflight_acl_fingerprint TEXT,
 prepared_at_utc TEXT,
 provider_readback_at_utc TEXT,
 status TEXT NOT NULL CHECK(status IN('PREPARED','VERIFIED','FAILED','ROLLED_BACK')),
 rollback_evidence TEXT,
 CHECK(old_parent_id<>new_parent_id)
);
CREATE VIEW IF NOT EXISTS drive_parent_child AS
 SELECT parent_drive_file_id AS parent_id, drive_file_id AS child_id
 FROM drive_nodes WHERE parent_drive_file_id IS NOT NULL;
