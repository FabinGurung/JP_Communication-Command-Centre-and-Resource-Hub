-- JP Ecosystem Daily Ops canonical relational contract
-- Schema contract version: 0.2.0
-- CANONICAL ROLE:
--   1) This .sql TEXT FILE is the primary relationship/schema authority for Daily Ops.
--   2) It is PostgreSQL-compatible DDL for deterministic AI/human inspection; no live PostgreSQL server is required or implied.
--   3) projects.csv is the canonical PROJECT-MASTER current-value layer (identity, lifecycle, location, public project attributes).
--   4) ops/data/current-works.json is the canonical DAILY-OPS current-state value layer.
--   5) ops/data/project-resources.json is the canonical STRUCTURED LINK REGISTRY from projects to permission-gated Drive resources.
--      The actual files/folders remain canonical source/evidence in Google Drive.
--   6) ops/events/daily-ops-events.jsonl is the canonical append-only EVENT/HISTORY layer.
--   7) map-config.json is the controlled-value / presentation configuration authority for the public map.
--   8) Google Sheets, GitHub Pages and Slack are downstream projections / interaction surfaces only.
--   9) If a projection conflicts with these canonical files, reconcile the projection; do not silently promote it to truth.

CREATE TABLE IF NOT EXISTS ops_projects (
  project_id text PRIMARY KEY,
  map_project_id text NOT NULL UNIQUE,
  company_project_code text NOT NULL,
  legacy_project_code text NOT NULL UNIQUE,
  project_slug text NOT NULL UNIQUE,
  display_name text NOT NULL,
  contractor text NOT NULL,
  lifecycle_status text,
  -- Project lifecycle/classification (for example Construction, Maintenance, Completed).
  -- This is distinct from Daily Ops readiness/execution status.
  CHECK (lifecycle_status IS NULL OR length(trim(lifecycle_status)) > 0)
);

CREATE TABLE IF NOT EXISTS ops_daily_state (
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  ops_date date NOT NULL,
  overall_readiness text NOT NULL CHECK (
    overall_readiness IN ('READY','READY_WITH_CONDITION','HOLD','NOT_READY','UNSET')
  ),
  ready_count integer NOT NULL DEFAULT 0 CHECK (ready_count >= 0),
  total_count integer NOT NULL DEFAULT 0 CHECK (total_count >= 0),
  conflict_state text NOT NULL DEFAULT 'UNSET' CHECK (
    conflict_state IN ('NONE','UNSET','UNRESOLVED')
  ),
  source_cutoff timestamptz,
  last_reconciled_at timestamptz,
  PRIMARY KEY (project_id, ops_date),
  CHECK (ready_count <= total_count)
);

CREATE TABLE IF NOT EXISTS ops_source_refs (
  source_ref text PRIMARY KEY,
  provider text NOT NULL,
  provider_object_type text,
  provider_object_id text,
  provider_url text,
  observed_at timestamptz,
  content_sha256 text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS ops_work_items (
  work_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  ops_date date NOT NULL,
  activity text NOT NULL,
  location text,
  execution_status text NOT NULL CHECK (
    execution_status IN ('PLAN','NOT_STARTED','ONGOING','PARTIAL','DONE','BLOCKED','NEEDS_INPUT','NOTE')
  ),
  overall_readiness text NOT NULL CHECK (
    overall_readiness IN ('READY','READY_WITH_CONDITION','HOLD','NOT_READY','UNSET')
  ),
  blocker text,
  responsible text,
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  conflict_state text NOT NULL DEFAULT 'UNSET' CHECK (
    conflict_state IN ('NONE','UNSET','UNRESOLVED')
  ),
  last_reconciled_at timestamptz
);

CREATE TABLE IF NOT EXISTS ops_readiness_gates (
  work_id text NOT NULL REFERENCES ops_work_items(work_id),
  gate_name text NOT NULL CHECK (
    gate_name IN ('materials','manpower','ppe','work_briefing','tools','preconditions')
  ),
  gate_status text NOT NULL CHECK (
    gate_status IN ('READY','CONDITION','HOLD','NOT_READY','UNKNOWN','NOT_APPLICABLE')
  ),
  note text,
  responsibility text,
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  observed_at timestamptz,
  conflict_state text NOT NULL DEFAULT 'UNSET' CHECK (
    conflict_state IN ('NONE','UNSET','UNRESOLVED')
  ),
  PRIMARY KEY (work_id, gate_name)
);

CREATE TABLE IF NOT EXISTS ops_materials (
  material_event_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  ops_date date NOT NULL,
  material_name text NOT NULL,
  material_state text NOT NULL,
  quantity numeric,
  unit text,
  note text,
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  observed_at timestamptz,
  conflict_state text NOT NULL DEFAULT 'UNSET' CHECK (
    conflict_state IN ('NONE','UNSET','UNRESOLVED')
  )
);

CREATE TABLE IF NOT EXISTS ops_progress (
  progress_event_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  ops_date date NOT NULL,
  status text NOT NULL,
  note text,
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  observed_at timestamptz,
  conflict_state text NOT NULL DEFAULT 'UNSET' CHECK (
    conflict_state IN ('NONE','UNSET','UNRESOLVED')
  )
);

CREATE TABLE IF NOT EXISTS ops_blockers (
  blocker_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  ops_date date NOT NULL,
  status text NOT NULL,
  blocker text NOT NULL,
  responsible text,
  target_resolution_at timestamptz,
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  observed_at timestamptz,
  conflict_state text NOT NULL DEFAULT 'UNSET' CHECK (
    conflict_state IN ('NONE','UNSET','UNRESOLVED')
  )
);

CREATE TABLE IF NOT EXISTS ops_lookahead (
  lookahead_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  target_date date,
  sequence_order integer,
  activity text NOT NULL,
  condition text,
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  conflict_state text NOT NULL DEFAULT 'UNSET' CHECK (
    conflict_state IN ('NONE','UNSET','UNRESOLVED')
  )
);

CREATE TABLE IF NOT EXISTS ops_evidence_refs (
  evidence_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  provider text NOT NULL,
  provider_object_id text,
  evidence_type text NOT NULL,
  evidence_url text,
  observed_at timestamptz,
  note text,
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS ops_projection_status (
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  projection_target text NOT NULL CHECK (
    projection_target IN ('GOOGLE_SHEETS','WEBSITE','SLACK')
  ),
  projection_state text NOT NULL CHECK (
    projection_state IN ('NOT_CONFIGURED','PENDING','CURRENT','STALE','ERROR')
  ),
  source_schema_version text NOT NULL,
  projected_at timestamptz,
  note text,
  PRIMARY KEY (project_id, projection_target)
);

CREATE TABLE IF NOT EXISTS ops_events (
  event_id text PRIMARY KEY,
  occurred_at timestamptz NOT NULL,
  event_type text NOT NULL,
  project_id text REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  payload jsonb NOT NULL,
  conflict_state text CHECK (
    conflict_state IS NULL OR conflict_state IN ('NONE','UNSET','UNRESOLVED')
  ),
  mutates_operational_truth boolean NOT NULL DEFAULT true
);


-- Project-to-Drive resource relationship authority.
-- Google Drive owns the actual source/evidence file bytes and permissions.
-- GitHub owns only the normalized current relationship/link metadata.
CREATE TABLE IF NOT EXISTS ops_project_resource_sets (
  project_id text PRIMARY KEY REFERENCES ops_projects(project_id),
  root_resolution text NOT NULL CHECK (root_resolution IN ('VERIFIED','UNRESOLVED')),
  verified_at timestamptz
);

CREATE TABLE IF NOT EXISTS ops_project_resources (
  resource_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  resource_type text NOT NULL,
  display_name text NOT NULL,
  drive_file_id text NOT NULL,
  drive_url text NOT NULL,
  mime_type text NOT NULL,
  preview_mode text NOT NULL CHECK (
    preview_mode IN ('DRIVE_FOLDER','DRIVE_PDF_PREVIEW','DRIVE_FILE_OPEN')
  ),
  access_mode text NOT NULL CHECK (access_mode = 'DRIVE_PERMISSION_GATED'),
  is_current boolean NOT NULL DEFAULT true,
  verified_at timestamptz NOT NULL,
  UNIQUE (project_id, drive_file_id, resource_type)
);

CREATE INDEX IF NOT EXISTS idx_ops_project_resources_project
  ON ops_project_resources(project_id, is_current);
