# Construction Knowledge Kernel v0.1 — prototype architecture

## Intent
Build a Nepal-localized construction execution knowledge layer on top of the existing JP governed work/project model, while aligning reusable concepts with open standards.

## Identity model
```
work_id           reusable work type / catalogue identity
activity_id       project occurrence of work
wbs_id            project scope hierarchy
checklist_template_id reusable control template
checklist_execution_id real execution only
evidence_id       real captured evidence only
```

## Knowledge envelope
```
WORK TYPE
├── ARC / Resource Readiness
├── WMS / Method Statement
├── Technical Specification
├── Codal / Authority References
├── ITP / QAQC
├── Safety / JSA
├── BOQ / Cost
├── Drawings / Details
└── Evidence / Lessons Learned
```

## Open-standard direction
- IFC 4.3: work/task/schedule/resource/cost interoperability
- IfcOpenShell / Ifc4D: open calculation/manipulation + P6/MS Project exchange
- bSDD: classifications/properties/dictionaries
- IDS: machine-readable information requirements/validation
- BCF / OpenCDE: issue and document interoperability

## Authority rule
GitHub is for code, schemas, mappings, tests, documentation and sanitized/reference data. It is not the canonical live site/project database.

## Prototype guardrails
1. Never fabricate `work_id`, `activity_id`, execution IDs or evidence IDs.
2. Never promote a source-chat/local practice into a standard detail without verification.
3. Numerical/codal requirements require source + edition + clause/table/figure + applicability.
4. Reusable work knowledge and project execution facts remain separate.
5. Existing specialist authorities are referenced rather than duplicated.
