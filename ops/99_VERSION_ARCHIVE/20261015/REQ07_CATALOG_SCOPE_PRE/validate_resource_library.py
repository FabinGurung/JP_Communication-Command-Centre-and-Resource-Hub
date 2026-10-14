#!/usr/bin/env python3
"""Req07 immutable Drive-source and idempotent Resources catalog verification.

Checks the 46 admitted source pointers against four historical metadata receipts
and the 2026-10-13 authenticated Drive metadata readback. Never writes Drive.
Later resource admission requires a new authenticated readback and explicit
review; this check alone cannot certify whole-folder inventory completeness.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
CAT="ops/data/resource-catalog-normalized.v0.1.json"
SRC="ops/data/project-resources.json"
READBACK="ops/data/resource-drive-readback.v0.1.json"
BATCH=lambda i:f"ops/data/resource-original-names/metadata-batch-{i:02d}.v0.1.json"
TIER={"issued_reports":1,"source_models":2,"calculations_and_support":3,"source_folders":4}
SENSITIVE=re.compile(r"(^|[_\s.-])(citizenship|nagarita|lalpurja|personal|legal|tax|kitta|passport|bank|salary|restricted)([_\s.-]|$)",re.I)

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def require(ok,msg):
    if not ok: raise ValueError("RESOURCE_CATALOG_FAIL: "+msg)
def flatten(catalog):
    return [(site["project_id"],f) for site in catalog["sites"] for f in site["files"]]
def validate():
    source=load(SRC)
    catalog=load(CAT)
    receipt=load(READBACK)
    batches=[item for i in range(1,5) for item in load(BATCH(i))]
    entries=flatten(catalog)
    src={x["resource_id"]:(site["project_id"],x) for site in source["projects"] for x in site["resources"]}
    batch={item["id"]:item for item in batches}
    stamped={item["resource_id"]:item for item in receipt["verified_entries"]}
    require(len(entries)==len(src)==len(batch)==len(stamped)==46,"46 admitted resources must reconcile one-to-one")
    require(len({x["resource_id"] for _,x in entries})==46,"duplicate normalized resource ID")
    require(len({x["fileId"] for x in batches})==46,"duplicate historical Drive metadata file ID")
    require(len({x["source_drive_file_id"] for _,x in entries})==46,"source Drive file ID reused for two resources")
    require(len({x["id"] for x in batches})==46,"duplicated original name/metadata record")
    require(set(x["resource_id"] for _,x in entries)==set(src)==set(batch)==set(stamped),
            "missing resource name registry or Drive readback")
    require(receipt.get("matched_id_name_mime_count")==46 and receipt.get("unmatched_count")==0,
            "authenticated Drive name/ID/MIME readback does not cover all indexed resources")
    require(receipt.get("no_source_mutations") is True and receipt.get("no_new_resources_admitted") is True,
            "historical readback misrepresented as file mutation or new publication")
    require(receipt.get("status")=="ALL_46_EXISTING_POINTERS_METADATA_MATCH__FULL_RECURSIVE_INVENTORY_OPEN",
            "whole-Drive inventory cannot be claimed from 46 pointers")
    display=load("ops/control/resource-display-and-admission.v0.1.json")
    require(display["status"]=="CURRENT_46_VERIFIED__COMPLETE_DRIVE_INVENTORY_OPEN",
            "resource directory misleadingly claims full Drive completion")
    require(display["snapshot"]["recursive_inventory_complete"] is False,
            "full recursive provider inventory asserted without complete inspection")
    web=(ROOT/"resources/index.html").read_text(encoding="utf-8")
    require("resource-drive-readback.v0.1.json" in web and
            'id="priority"' in web and 'id="priority-order"' in web,
            "resource UI lacks verified origin notice or document priority filters")
    for expected in display["priority_bands"]:
        rank=expected["priority"]
        require(expected["id"] in TIER and TIER[expected["id"]]==rank,
                "governed priority identifier drift")
        require(f'.tier[data-priority="{rank}"] .file .label' in web,
                "missing ranked heading selector "+str(rank))
        require(f"font-size:{expected['heading_px']}px" in web,
                "missing ranked font token "+str(rank))
    bands=catalog["priority_bands"]
    require([(x["id"],x["rank"]) for x in bands]==list(TIER.items()),"document tiers/order drift")
    require(len(source["projects"])==len(catalog["sites"])==8,"indexed-site FK count drift")
    require({site["project_id"] for site in source["projects"]}=={s["project_id"] for s in catalog["sites"]},
            "project FK mismatch")
    for pid,resource in entries:
        rid=resource["resource_id"]
        require(rid in src and src[rid][0]==pid,"source resource FK mismatch: "+rid)
        original=src[rid][1];meta=batch[rid];live=stamped[rid]
        for column,value in (
            ("project_id",pid),("source_drive_file_id",original["drive_file_id"]),
            ("source_drive_url",original["drive_url"]),
            ("source_registry_label",original["display_name"]),
            ("original_drive_filename",meta["name"]),
            ("mime_type",meta["mime"]),
        ):
            require(resource.get(column)==value,f"source field drift {rid}.{column}")
        require(meta["fileId"]==resource["source_drive_file_id"] and meta["pid"]==pid and meta["verified"] is True,
                "unverified historical metadata or project association: "+rid)
        require(live["source_drive_file_id"]==meta["fileId"] and live["original_drive_filename"]==meta["name"] and
                live["mime_type"]==meta["mime"] and live["name_id_mime_match"] is True,
                "authenticated metadata snapshot changed: "+rid)
        require(resource.get("original_filename_verified") is True,"unverified original filename "+rid)
        require(resource["category"] in TIER and resource["sort_priority"]==TIER[resource["category"]],
                "priority band mismatch "+rid)
        require(resource["approval_status"]=="UNVERIFIED_AS_CURRENT_ISSUE",
                "resource approval status invented "+rid)
        require(resource["format"] and resource["normalized_name"] and resource["discipline"],
                "missing document type/visible name "+rid)
        suffix=Path(meta["name"]).suffix.upper().lstrip(".")
        require(resource["format"]==("FOLDER" if meta["mime"]=="application/vnd.google-apps.folder" else suffix),
                "format cannot be inferred from false MIME or filename "+rid)
        if resource["category"]=="source_folders":
            require(resource["format"]=="FOLDER","folders-only category mismatch "+rid)
        elif resource["category"]=="issued_reports":
            require(resource["format"]=="PDF","only drawings and technical-report PDFs take first priority "+rid)
            require(not re.search(r"(cost.?estimate|boq|structural_detail_calc)",meta["name"],re.I),
                    "costs/calculation PDF incorrectly placed as issue drawing "+rid)
        elif resource["category"]=="source_models":
            require(resource["format"] in {"DWG","DXF","IFC","E2K","EDB","SKP","RVT","SDB","S2K"},
                    "unsupported model format "+rid)
        elif resource["category"]=="calculations_and_support":
            require(resource["format"] in {"PDF","XLSX","XLS","CSV","ODS","DOCX"},
                    "unsupported calculation or estimate format "+rid)
        require(not SENSITIVE.search(meta["name"]), "sensitive private document slipped into public catalog: "+rid)
        u=urlparse(resource["source_drive_url"])
        require(u.scheme=="https" and u.hostname=="drive.google.com" and
                resource["source_drive_file_id"] in u.path,
                "resource not linked to exact Drive original "+rid)
    tierCounts={key:sum(1 for _,f in entries if f["category"]==key) for key in TIER}
    require(tierCounts=={"issued_reports":14,"source_models":15,"calculations_and_support":2,"source_folders":15},
            "unexpected normalization priority distribution")
    return tierCounts

if __name__=="__main__":
    counts=validate()
    print("RESOURCE_CATALOG_PASS: 46 source originals/metadata receipts verified; "
          +" / ".join(f"{key}={v}" for key,v in counts.items())
          +"; full recursive Drive inventory remains open.")
