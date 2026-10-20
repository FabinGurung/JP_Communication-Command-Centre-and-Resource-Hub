#!/usr/bin/env python3
"""A9 public-safe additions: no private Sheets rows, no duplicate provider ingestion."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path): return (ROOT/path).read_text(encoding="utf-8")
def data(path): return json.loads(read(path))
def test():
    routes=data("ops/control/a9-page-section-registry.v1.0.json")
    arc=data("ops/control/botanical-workspace-arc.v1.0.json")
    catalog=data("ops/data/a9-field-source-catalog-public.v1.0.json")
    checklist=data("ops/data/a9-published-checklist-public.v1.0.json")
    progress=data("ops/data/a9-reviewed-progress-public.v1.0.json")
    pending=data("ops/data/pending-works.json")
    cycle=data("ops/control/daily-communication-web-cycle.json")
    projects={x["project_id"] for x in data("ops/data/current-works.json")["projects"]}
    assert routes["schema_version"]=="1.0.0"
    listed=routes["pages"]
    assert len(arc["active_pages"])==20 and len(listed)==21
    assert routes["memory_poster_level"]=="L1"
    assert "MEMORY" in routes["primary_destinations"] and len(routes["primary_destinations"])==7
    assert next(x for x in listed if x["page_id"]=="A9-PAGE-CONTROL_MEMORY")["page_role"]=="PRIMARY"
    assert "A9-MEM-01" in {s["section_id"] for s in routes["sections"]}
    assert len([s for s in routes["sections"] if s["section_id"].startswith("A9-FLD-")])==10
    paths={x["path"] for x in listed}
    assert paths==set(arc["active_pages"])|{"resources/field/index.html"}
    assert len({x["page_id"] for x in listed})==len(paths)
    assert all((ROOT/x).is_file() for x in paths)
    assert all((ROOT/x["path"]).exists() and x["status"]=="ACTIVE" for x in listed)
    for section in routes["sections"]:
        assert section["path"] in paths,section
        assert section["section_id"].startswith("A9-"),section
    assert len({s["section_id"] for s in routes["sections"]})==len(routes["sections"])
    assert all(x["level"] in {"L0","L1","L2","L3","L4","L5"} for x in routes["levels"])
    assert catalog["kind"]=="PUBLIC_SAFE_SOURCE_CATEGORY_INDEX"
    assert catalog["sheets_count"]==len(catalog["sources"])==10
    assert catalog["published_rows"]==0 and catalog["public_source_file_ids_included"] is False
    assert len({s["source_key"] for s in catalog["sources"]})==10
    assert all(s["private_sheet_url_included"] is False and s["projection_state"].startswith("AWAITING_") for s in catalog["sources"])
    assert checklist["kind"]=="MANUALLY_PUBLISHED_DAILY_CHECKLIST"
    assert checklist["count"]==len(checklist["rows"])==0 and checklist["automatic_polling"] is False
    assert progress["kind"]=="MANUALLY_REVIEWED_PROGRESS_PUBLICATION_QUEUE"
    assert progress["published_new_record_count"]==len(progress["records"])==0
    assert progress["historical_records_preserved"]==37 and progress["automatic_polling"] is False
    assert progress["render_mode"]=="VERBATIM_FIRST_NO_AUTO_DERIVATION"
    assert progress["derived_data_requires_explicit_new_user_prompt"] is True
    plan=data("ops/control/a9-field-visualization-plan.v1.0.json")
    assert plan["individual_sheet_count"]==10 and len(plan["dashboards"])==10
    assert plan["record_level_data_included"] is False and plan["private_source_urls_included"] is False
    assert plan["worksheet_policy"]["hide_tab_count_this_change"]==0
    source_links=data("ops/data/a9-field-source-links-public.v1.0.json")
    assert source_links["registry_id"]=="A9_FIELD_SOURCE_LINKS_PUBLIC_20261021"
    assert source_links["source_count"]==len(source_links["google_sheet_urls"])==10
    assert source_links["source_records_copied"]==0 and source_links["sharing_permissions_changed"] is False
    assert source_links["urls_publicly_visible"] is True
    link_keys={x["source_key"] for x in source_links["google_sheet_urls"]}
    assert link_keys=={x["source_key"] for x in catalog["sources"]}
    assert len({x["url"] for x in source_links["google_sheet_urls"]})==10
    assert all(x["url"].startswith("https://docs.google.com/spreadsheets/d/") and x["url"].endswith("/edit") and x["dashboard_id"]=="A9-FIELD-"+x["source_key"][-2:] for x in source_links["google_sheet_urls"])
    assert "a9-field-source-links-public.v1.0.json" in read("assets/js/a9-field-resources.js")
    assert 'a.target="_blank"' in read("assets/js/a9-field-resources.js")
    assert 'a.rel="noopener noreferrer"' in read("assets/js/a9-field-resources.js")
    assert len([l for l in read("ops/data/progress-report-public.v0.2.jsonl").splitlines() if l.strip()])==37
    originals=data("ops/data/resource-catalog-normalized.v0.1.json")
    assert sum(len(site["files"]) for site in originals["sites"])==46
    assert len(projects)>=8
    assert next(x for x in pending["items"] if x["pending_id"]=="OPS-PEND-000004")["status"]=="ON_HOLD_USER_REQUEST_20261019"
    assert next(x for x in cycle["source_providers"] if x["provider"]=="DISCORD")["execution_hold"]["run_discord_apis"] is False
    page_data={
        "resources/index.html":["href=\"field/\"","id=\"desk-resources\""],
        "resources/field/index.html":["field-sources","a9-field-resources.js","a9-ui-extensions.css"],
        "site-operations.html":["id=\"a9-published-instructions\"","a9-published-checklist.js","JPAEC:diy-checklist:v1:"],
        "site-operations/history.html":["id=\"a9-manual-progress\"","a9-manual-progress.js","progress-report-public.v0.2.jsonl"],
        "workspace/index.html":["id=\"memory-poster-board\"","controls/memory-wall.html","A9_SITE_TREE_AND_EDIT_LEVELS.v1.md"]
    }
    for path,markers in page_data.items():
        html=read(path)
        for marker in markers:
            assert marker in html,(path,marker)
    assert "github.com" not in read("ops/data/a9-field-source-catalog-public.v1.0.json")
    forbidden=(
      "1Cyuj0uti-IN7ddDNVdAd1kM0NNpATdTnNabfcY7P1cw",
      "15szptLz7q3-Rote1SnNuIqdcrxrm0z2m0k7yx9j51c4",
      "10l4F1ZShkPKt7L8HBT1BJ3K0rjkJ6GktXRZdI4k35Bg",
      "1j_866LE1heYTozkUheH3kU55TV8ZXuLzTwTCZzZNbqw",
      "1FuFvccGvDwlszfzGL7_TP4qChBptA8Pil7eq6O5qlPw",
      "1YshLrDAJDg3CO8F1jmIr2Eucy0-TKwiviVNF5tiAfT0"
    )
    new_files=["resources/field/index.html","assets/js/a9-field-resources.js",
        "ops/data/a9-field-source-catalog-public.v1.0.json",
        "ops/data/a9-published-checklist-public.v1.0.json",
        "ops/data/a9-reviewed-progress-public.v1.0.json"]
    public_text=" ".join(read(path) for path in new_files)
    assert all(id not in public_text for id in forbidden)
    assert not any(".sqlite" in x for x in new_files)
    for p in ("assets/js/a9-field-resources.js","assets/js/a9-published-checklist.js","assets/js/a9-manual-progress.js"):
        source=read(p)
        assert "fetch(" in source and "textContent" in source
        assert "setInterval" not in source and "setTimeout" not in source and "innerHTML" not in source
    assert "No schedule" in read("docs/operations/a9-manual-source-reconciliation-v1.md")
    assert "VERBATIM_FIRST_NO_AUTO_DERIVATION" in read("assets/js/a9-manual-progress.js")
    assert "website-level-tree" in read("controls/memory-wall.html")
    assert "🧠 Memory Poster" in read("assets/js/site-shell.js")
    print("A9_MANUAL_SURFACES_PASS: 21 active routes, 10 metadata-only Sheets, 0 unpublished checklist/progress rows, 37 legacy events, 46 preserved resources, collector on hold.")
if __name__=="__main__":
    test()
