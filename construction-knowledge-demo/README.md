# Construction Knowledge Kernel — demo

This folder is an additive prototype for the JP construction-activity knowledge system.

## What it demonstrates
- existing reusable `work_id` stays authoritative;
- ARC is a resource/readiness layer, not a replacement for QA/QC;
- WMS, ITP, codal/spec references, BOQ, drawings and evidence attach to the same work identity;
- project `activity_id` is a separate occurrence of reusable work;
- IFC / IfcOpenShell / bSDD / IDS / BCF / Primavera mappings can be added without making GitHub the operational truth.

## Safety / governance
All content here is sanitized demonstration data. It does **not** create site execution facts, technical approvals, codal numerical requirements, or soak-pit design values.

Current mapped example:
- `WRK-000023` — Cementitious Waterproofing
- existing QA template reference: `CK-BLD-WP-001`

Research-gated example:
- Soak Pit — canonical `work_id` intentionally unresolved.

Open `index.html` through GitHub Pages to use the demo.
