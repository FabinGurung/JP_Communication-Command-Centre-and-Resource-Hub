# Request 07 — Resource Library, Original Names and Safe Future Intake

## Delivery checkpoint: 2026-10-13 NPT

**Existing indexed resources: 46 in 8 linked projects.** All 46 registered Drive IDs were individually retrieved through authenticated metadata lookup, and their original filenames and MIME types matched. This is a verification of the **existing index**, not a complete recursive inventory of project Drive folders.

The public website is the **Project Resources** page at \`resources/index.html\`. It contains only approved-to-list original *links*, not source file bytes. Google Drive retains access control and source authority.

## Document browsing — four strict priorities

1. **📄 Drawing Sets & Technical Reports:** architecture, structure, MEP, soil and analysis-report PDFs. No engineering issue/approval status is inferred from file names.
2. **🧱 Editable Drawings & Models:** native CAD, BIM, SketchUp and structural-analysis sources (DWG, DXF, IFC, SKP, RVT, E2K, EDB, etc.).
3. **📊 Estimates, Calculations & Supporting Files:** Excel/BOQ/estimate files, cost-estimate PDFs, structural detailing calculations and supporting records.
4. **🗂️ Original Source Folders & Archives:** links to provider-owned original folders. A source-folder link is **not** permission to publish everything inside it.

Styling, priority, formats and conservative display rules are recorded in \`ops/control/resource-display-and-admission.v0.1.json\`. The UI uses the priority recorded in the normalized catalog, renders a rank-specific font hierarchy, preserves the original Drive name on every card, and exposes an honest source coverage note.

## Authority and relationships

\`\`\`text
projects.csv (canonical project name and project_id)
   │
   └── project-resources.json (existing resource_id → Drive file ID/source URL)
            │
            ├── resource-original-names/metadata-batch-01..04.v0.1.json
            ├── resource-drive-readback.v0.1.json  ← LIVE metadata check for the existing 46
            │
            └── resource-catalog-normalized.v0.1.json
                     │
                     └── resources/index.html (public read-only; display only)
\`\`\`

**Never rename, overwrite, delete or move Drive source files** as a way to normalize their labels. Store a new human-readable *display label* alongside the original source ID/name. Every public resource retains its stable resource ID and project foreign key, as well as Drive ID, link, MIME and original registry description. Original file names containing \`final\` or \`revised\` do not establish construction approval.

The current catalog records **14 drawing/report PDF links, 15 editable model links, 2 estimate/calculation PDFs and 15 folder/archive links**. Resource source status remains **UNVERIFIED_AS_CURRENT_ISSUE** for every item.

## Future metadata intake: review before admission

\`scripts/preview_resource_intake.py\` is a private metadata intake-preview tool. Give it an authenticated provider metadata export **outside this public repository**:

\`\`\`bash
python scripts/preview_resource_intake.py \
  --input /private/drive-metadata-export.json \
  --output /private/resource-review-candidates.json
\`\`\`

It is deterministic for the same source rows: it deduplicates unchanged provider Drive IDs, identifies conflicts, suggests the priority from safe file-type evidence, and quarantines known private/ambiguous document types. It **does not** publish candidate names or record source bytes in GitHub; it refuses to save the preview in this public repository. It does **not** call Drive automatically and is **not** a replacement for an authenticated Drive incremental collector.

Before adding a new public record: verify the owning project and authorized Drive parent, source ID, name, MIME and receipt; classify privacy/revision/engineering approval; resolve duplicate Drive IDs; append the verified source registry and metadata record in the proper owning lane; rebuild the normalized catalog idempotently; run CI; archive/read back the change. Missing receipts or uncertain project association mean **no admission**.

## Authenticated recursive inventory runner — prepared, not executed

An independent metadata-only Drive collector is now available in \`scripts/collect_private_drive_resource_metadata.py\`. In a Google-authorized environment with \`google-auth\` and \`google-api-python-client\`, create a **private** JSON mapping like \`{"P001":"<verified-folder-id>","P007":"<verified-folder-id>"}\` for the roots actually authorized for collection, and run:

\`\`\`bash
python scripts/collect_private_drive_resource_metadata.py \
  --roots /private/reviewed-project-roots.json \
  --private-jsonl /private/source-inventory-20261013.jsonl \
  --receipt /private/source-inventory-20261013.receipt.json
\`\`\`

The collector paginates through child folders without downloading bytes; refuses cross-project ID collisions, duplicate output paths and public-repo outputs; writes readback-verified SHA-256 and coverage totals. It never publishes new catalog items. It **has not been executed against the complete Drive tree as part of this checkpoint**, and therefore cannot establish whole-Drive completeness yet.

## 2026-10-13 inventory boundary

Drive root and selected original-source-folder metadata were browsed for the eight indexed projects. Several contain additional nested archives, engineering sources and restricted legal/personal material not represented in the existing index. Direct-child searches and source-folder spot checks are **not a complete authorized recursive inventory**. Some returned zero items and that is not proof of folder completeness. Unexpected project-association records were not published. No sensitive original document names/IDs were copied into the public catalog.

### Resumed live Drive finding — 2026-10-13

The connector-backed folder enumeration cannot currently be accepted as an exhaustive inventory: the approved indexed drawing \`RES-P004-ARCH-DWG-001\` was found by metadata ID, with its verified parent in Yamuna's original CAD folder, but repeated folder-child searches reported **zero**. The search-based pass reported **11 files across 21 queried folders**, whereas a direct `list_folder` pass through the same 21-folder scope returned **35 file entries** (no individual folder reached the 100-entry response cap). This is a scoped cross-check, **not** a full eight-project or independently certified provider inventory. The method comparison is recorded in `ops/control/req07-p004-scoped-folder-inventory-crosscheck.v0.1.json`. Hari's branch traversal is also incomplete. The mismatch is registered in \`ops/control/req07-drive-child-search-coverage-gap.v0.1.json\` without exposing names of newly encountered private records.

The authenticated collector now independently looks up each previously published source ID and its parent, compares original name/MIME, and **fails** if a source whose parent was visited is omitted by folder enumeration. It supports multiple registered roots per project, and root IDs can be derived directly from the governed resource registry without manually re-entering them:

\`\`\`bash
python scripts/collect_private_drive_resource_metadata.py \
  --registered-roots \
  --private-jsonl /private/resource-inventory.jsonl \
  --receipt /private/resource-inventory.receipt.json
\`\`\`

Use \`--projects P004\` for an explicitly scoped validation, then expand to all registered project roots. This requires a separately authenticated Google Drive API environment with metadata-only permissions. Do not copy the private inventory into GitHub or declare Request 7 closed merely because a saved inventory file exists. The receipt remains flagged if an indexed source belongs to an unscanned/alternate parent.

### Private inventory → review candidates (validated handoff)

Once a properly authenticated direct-Drive metadata scan succeeds, convert its JSONL and matching SHA-256 receipt to a private candidate ledger:

\`\`\`bash
python scripts/preview_resource_intake.py \
  --input /private/resource-inventory.jsonl \
  --receipt /private/resource-inventory.receipt.json \
  --output /private/resource-review-candidates.json
\`\`\`

The handoff checks the recorded SHA-256, entry count, source receipt and no-publication boundary. It does not treat folder placement as independently verified project ownership: newly discovered resources remain review-required or quarantined. This handoff is implemented and tested, but the **direct API collector has not been executed on all authorized Drive roots in this run**.

### Second continuation: registered-root traversal — 2026-10-13

All nine currently registered project root folders were traversed through the authenticated Drive connector using direct folder listing. **215 folder nodes and 1,309 file entries were returned across eight project aliases.** Results are folder-list observations, **not a durable private, unique-ID inventory** and not a source approval. The safe aggregate checkpoint is \`ops/control/req07-registered-roots-metadata-traversal-20261013.v0.1.json\`.

Three folders that initially returned exactly 100 items were queried again with \`top_k=1000\`, returning **111, 101 and 178 items**. This removed the known 100-result cutoff within those three listings but does not substitute for Google Drive API page-token verification.

**Independent project-root debt:** six existing, published resources under P001 and P002 are accessible by individual ID, yet their metadata ancestry did not reach the currently registered project root within seven levels. A root returning zero direct children does not mean an entire project's source archive is empty. Keep those six pointers unchanged until original owner and alternate-root provenance are resolved.

**Publication boundary:** none of the newly encountered file IDs/names are added to the public GitHub Pages site. No original bytes were downloaded, moved or renamed. Direct Google Drive API recursion with exact project-root authority, independent by-ID parent reconciliation, a private deduplicated JSONL and SHA-256 readback is still the next execution gate; owner/privacy/approval reviews remain independent.

**Outstanding before Request 07 can claim full inventory completion:** an authenticated, recursively paginated metadata-only inventory of all authorized project roots (including alternate originals), a private candidate review ledger with PK/FK/revision/privacy decisions, readback receipts, and a reviewed incremental publication process. Future Drive-event automation requires authenticated provider execution and explicit ownership of admission decisions.

## QA and trace

- \`scripts/validate_resource_library.py\` — exact 46-entry source/metadata/Drive-readback reconciliation; no invented approval or category drift.
- \`scripts/test_resource_library.py\` — deterministic categorization, duplicate protection and private metadata candidate handling.
- \`scripts/validate_site_experience_contract.py\` — preserves checklist/progress/resource isolation.
- \`scripts/qa_field_ux_browser.py\` — site/format/priority filters, type hierarchy, accessible links, mobile layout.
- Existing original catalog and UI versions archived under \`ops/99_VERSION_ARCHIVE/20261013/REQ07_RESOURCE_DIRECTORY_PRE/\`.

**No source bytes, private provider originals or engineering claims were modified by this task.**
