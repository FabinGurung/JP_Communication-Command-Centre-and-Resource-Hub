-- A9-CWO full-history derived PRIVATE SQLite v1
-- Canonical truth remains immutable, SHA-verified Discord JSONL in Google Drive.
-- This schema is a reconstructible indexing projection, not a raw-replacement store.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sources (
  channel_id TEXT PRIMARY KEY,
  parent_channel_id TEXT,
  kind TEXT NOT NULL,
  name TEXT,
  channel_type INTEGER
);
CREATE TABLE IF NOT EXISTS capture_pages (
  receipt_id TEXT PRIMARY KEY,
  channel_id TEXT NOT NULL REFERENCES sources(channel_id),
  raw_drive_id TEXT NOT NULL,
  raw_gzip_sha256 TEXT NOT NULL,
  raw_jsonl_sha256 TEXT NOT NULL,
  message_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
  channel_id TEXT NOT NULL REFERENCES sources(channel_id),
  message_id TEXT NOT NULL,
  version_sha256 TEXT NOT NULL,
  parent_channel_id TEXT,
  author_id TEXT,
  created_at_utc TEXT,
  edited_at_utc TEXT,
  content TEXT,
  raw_json TEXT NOT NULL,
  PRIMARY KEY (channel_id, message_id, version_sha256)
);
CREATE TABLE IF NOT EXISTS attachments (
  attachment_id TEXT NOT NULL,
  message_id TEXT NOT NULL,
  channel_id TEXT NOT NULL,
  filename TEXT,
  declared_bytes INTEGER,
  content_type TEXT,
  media_status TEXT NOT NULL,
  original_drive_id TEXT,
  PRIMARY KEY (attachment_id, channel_id, message_id)
);
CREATE TABLE IF NOT EXISTS reactions (
  channel_id TEXT NOT NULL,
  message_id TEXT NOT NULL,
  version_sha256 TEXT NOT NULL,
  reaction_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sources_parent ON sources(parent_channel_id);
CREATE INDEX IF NOT EXISTS idx_messages_channel_date ON messages(channel_id, created_at_utc);
CREATE INDEX IF NOT EXISTS idx_messages_author_date ON messages(author_id, created_at_utc);
CREATE INDEX IF NOT EXISTS idx_messages_message_id ON messages(message_id);
CREATE INDEX IF NOT EXISTS idx_attachments_message ON attachments(message_id);
-- Query pattern: SELECT * FROM messages WHERE channel_id=? AND created_at_utc BETWEEN ? AND ? ORDER BY created_at_utc;
-- Query pattern: SELECT * FROM messages WHERE message_id=? ORDER BY edited_at_utc DESC;
-- NEVER treat media_status=FAILED/DEFERRED as a verified original.
