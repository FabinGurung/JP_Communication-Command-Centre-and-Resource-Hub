-- A9-CWO append-only PRIVATE registry design contract v0.1.0.
-- Do not execute in a public database. Does not migrate ops project data.
-- ops_projects(project_id) remains the existing canonical project FK.
CREATE TABLE IF NOT EXISTS cwo_source_receipts (
 source_receipt_id text PRIMARY KEY, source_run_id text NOT NULL,
 source_receipt_sha256 char(64) NOT NULL CHECK(source_receipt_sha256 ~ '^[a-f0-9]{64}$'),
 archive_ref text NOT NULL, scan_state text NOT NULL,
 UNIQUE(source_run_id,source_receipt_id)
);
CREATE TABLE IF NOT EXISTS cwo_source_messages (
 provider text NOT NULL, provider_channel_id text NOT NULL,
 provider_message_id text NOT NULL, first_receipt_id text NOT NULL REFERENCES cwo_source_receipts(source_receipt_id),
 PRIMARY KEY(provider,provider_channel_id,provider_message_id)
);
CREATE TABLE IF NOT EXISTS cwo_project_company_links (
 project_id text PRIMARY KEY REFERENCES ops_projects(project_id),
 company_id text NOT NULL CHECK(company_id ~ '^ORG-[0-9]{6}$'),
 verified_source_ref text NOT NULL,
 UNIQUE(project_id,company_id)
);
CREATE TABLE IF NOT EXISTS cwo_evidence_records (
 record_id text PRIMARY KEY CHECK(record_id ~ '^EV-[a-f0-9]{64}$'),
 provider text NOT NULL, provider_channel_id text NOT NULL,provider_message_id text NOT NULL,
 captured_at_utc timestamptz NOT NULL, project_id text, company_id text,
 source_run_id text NOT NULL, source_receipt_id text NOT NULL REFERENCES cwo_source_receipts(source_receipt_id),
 source_content_sha256 char(64) NOT NULL CHECK(source_content_sha256 ~ '^[a-f0-9]{64}$'),
 evidence_kind text NOT NULL, caption_or_text text NOT NULL,
 observation_date date, claim_state text NOT NULL, verification_state text NOT NULL,
 access_classification text NOT NULL DEFAULT 'PRIVATE_RESTRICTED',
 source_uri_ref text NOT NULL, version integer NOT NULL CHECK(version >= 1),
 supersedes_id text UNIQUE REFERENCES cwo_evidence_records(record_id),
 admission_status text NOT NULL DEFAULT 'PENDING_REVIEW',
 admission_receipt_id text,
 FOREIGN KEY(provider,provider_channel_id,provider_message_id)
  REFERENCES cwo_source_messages(provider,provider_channel_id,provider_message_id),
 FOREIGN KEY(project_id) REFERENCES cwo_project_company_links(project_id),
 FOREIGN KEY(project_id,company_id) REFERENCES cwo_project_company_links(project_id,company_id),
 CHECK ((project_id IS NULL AND company_id IS NULL) OR (project_id IS NOT NULL AND company_id IS NOT NULL)),
 CHECK (version > 1 OR supersedes_id IS NULL),
 CHECK (admission_status <> 'ADMITTED' OR (project_id IS NOT NULL AND admission_receipt_id IS NOT NULL)),
 UNIQUE(provider,provider_channel_id,provider_message_id,source_content_sha256),
 UNIQUE(provider,provider_channel_id,provider_message_id,version)
);
CREATE TABLE IF NOT EXISTS cwo_attachment_versions (
 fidelity_event_id text PRIMARY KEY,provider text NOT NULL,
 provider_channel_id text NOT NULL,provider_message_id text NOT NULL,
 attachment_id text NOT NULL, source_run_id text NOT NULL,
 fidelity_status text NOT NULL, checked_at_utc timestamptz NOT NULL,
 declared_bytes bigint CHECK(declared_bytes >= 0),
 observed_bytes bigint CHECK(observed_bytes >= 0),
 original_sha256 char(64),archived_sha256 char(64),archive_ref text,
 supersedes_fidelity_event_id text REFERENCES cwo_attachment_versions(fidelity_event_id),
 FOREIGN KEY(provider,provider_channel_id,provider_message_id)
 REFERENCES cwo_source_messages(provider,provider_channel_id,provider_message_id),
 CHECK (fidelity_status <> 'ORIGINAL_VERIFIED' OR
  (original_sha256 IS NOT NULL AND archived_sha256 IS NOT NULL
   AND original_sha256=archived_sha256 AND archive_ref IS NOT NULL
   AND declared_bytes IS NOT NULL AND observed_bytes IS NOT NULL
   AND declared_bytes=observed_bytes))
);
CREATE TABLE IF NOT EXISTS cwo_evidence_attachment_links(
 record_id text NOT NULL REFERENCES cwo_evidence_records(record_id),
 fidelity_event_id text NOT NULL REFERENCES cwo_attachment_versions(fidelity_event_id),
 PRIMARY KEY(record_id,fidelity_event_id)
);
CREATE TABLE IF NOT EXISTS cwo_public_projection_receipts (
 projection_id text PRIMARY KEY, generated_at_utc timestamptz NOT NULL,
 policy_revision text NOT NULL, admitted_record_ids jsonb NOT NULL,
 privacy_approved boolean NOT NULL DEFAULT false,
 public_payload_sha256 char(64) NOT NULL
);
-- Application roles must have INSERT + SELECT only; no UPDATE/DELETE to evidence tables.
-- Revisions append new records and reference supersedes_id. Never publish these tables directly.
