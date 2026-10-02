-- JP Ecosystem Daily Ops relational contract
-- PostgreSQL-oriented schema. JSON/JSONL remain machine-first exchange/state layers.
-- Google Sheets and web pages are downstream projections.

CREATE TABLE IF NOT EXISTS ops_projects (
  project_id text PRIMARY KEY,
  project_slug text NOT NULL UNIQUE,
  display_name text NOT NULL,
  contractor text NOT NULL
);

CREATE TABLE IF NOT EXISTS ops_daily_state (
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  ops_date date NOT NULL,
  overall_readiness text NOT NULL CHECK (
    overall_readiness IN ('READY','READY_WITH_CONDITION','HOLD','NOT_READY','UNSET')
  ),
  ready_count integer NOT NULL DEFAULT 0 CHECK (ready_count >= 0),
  total_count integer NOT NULL DEFAULT 0 CHECK (total_count >= 0),
  last_reconciled_at timestamptz,
  PRIMARY KEY (project_id, ops_date)
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
  responsible text
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
  note text
);

CREATE TABLE IF NOT EXISTS ops_progress (
  progress_event_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  ops_date date NOT NULL,
  status text NOT NULL,
  note text
);

CREATE TABLE IF NOT EXISTS ops_blockers (
  blocker_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  ops_date date NOT NULL,
  status text NOT NULL,
  blocker text NOT NULL,
  responsible text,
  target_resolution_at timestamptz
);

CREATE TABLE IF NOT EXISTS ops_lookahead (
  lookahead_id text PRIMARY KEY,
  project_id text NOT NULL REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  target_date date,
  sequence_order integer,
  activity text NOT NULL,
  condition text
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
  note text
);

CREATE TABLE IF NOT EXISTS ops_events (
  event_id text PRIMARY KEY,
  occurred_at timestamptz NOT NULL,
  event_type text NOT NULL,
  project_id text REFERENCES ops_projects(project_id),
  work_id text REFERENCES ops_work_items(work_id),
  source_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
  payload jsonb NOT NULL,
  mutates_operational_truth boolean NOT NULL DEFAULT true
);
