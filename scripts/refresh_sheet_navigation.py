#!/usr/bin/env python3
"""Refresh a private Drive navigator from verified source/version receipts.

Inputs and output are private files outside this public checkout. The script
updates known IDs only; it performs no recursive Drive scan or provider writes.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sheet_url(ident):
    return "https://docs.google.com/spreadsheets/d/" + ident + "/edit"


def folder_url(ident):
    return "https://drive.google.com/drive/folders/" + ident


def refresh(data, versions, navigation, shell, output):
    output = Path(output).resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("PRIVATE_NAVIGATION_MUST_STAY_OUTSIDE_PUBLIC_CHECKOUT")
    entries = {e["id"]: e for e in data["entries"]}
    previous = set(entries)
    sources = versions["starred"] + versions.get("extras", [])
    for p in sources:
        parent = p.get("archiveParent") or ("1DPPAvv0CdnkKKtkY6PjYZep1DyA-lH-H" if p["role"] != "OTHER_NAMESPACE" else p.get("parent"))
        if p["archive"] not in entries and parent in entries:
            entries[p["archive"]] = dict(id=p["archive"], name="Version History — " + p["baseTitle"], parent=parent, kind="folder", url=folder_url(p["archive"]), historical=True, description="Dedicated numbered PRE and POST versions of this original Sheet.")
        if p["archive"] in entries:
            entries[p["archive"]]["name"] = "Version History — " + p["baseTitle"]
        if p.get("parent") in entries:
            entries[p["id"]] = dict(id=p["id"], name=p["baseTitle"] + " — " + p["newVersion"], parent=p["parent"], kind="sheet", url=sheet_url(p["id"]), historical=p["role"] == "SUPERSEDED", description=p.get("purpose", p["role"]))
        if p["archive"] in entries:
            for phase, key in (("PRE", "pre"), ("POST", "postId")):
                ident = p[key]
                entries[ident] = dict(id=ident, name=p["newVersion"] + "__" + phase + "__20261027__" + p["baseTitle"], parent=p["archive"], kind="sheet", url=sheet_url(ident), historical=True, description="Native full-workbook version; restore into the original live ID.")
    unused = entries.get("1l58c18s2M6by5ntB_bIVqgsk7-YnzskA")
    if unused:
        unused["name"] = "03 References and Unused Templates"
    data["entries"] = list(entries.values())
    data["sheets"] = [dict(id=r[1].split("/d/")[1].split("/")[0], name=r[0], url=r[1], description=r[4] + ". " + r[3] + ". Source tabs: " + r[2]) for r in navigation["directory"][1:]]
    data["master"]["name"] = "Website Publishing and Source Directory — LIVE — V000006"
    data["master"]["description"] = "25 publishing data tables; connected-API assembly verified. Live Actions Google fetch awaits its dedicated identity."
    data["updated"] = "27 October 2026 (Nepal time)"
    data["inventoryNotice"] = "The 18 starred workbooks (310 original tabs) were inspected in full. Known source IDs, versions and editing locations were refreshed; all earlier inventory entries remain. This is not a new recursive inventory. Other 98_INTAKE_STAGING content remains excluded; only the explicitly starred supplier workbook was repaired."
    w = data["websiteDirectory"]
    w["verifiedAt"] = data["updated"]
    w["nativeGuideUrl"] = sheet_url("17y3ki0SLSG_Hmz8AipfWhhffnKastcjHvRqIdepJMu4") + "#gid=990001"
    w["stars"] = [dict(id=p["id"], name=p["baseTitle"] + " — " + p["newVersion"], url=sheet_url(p["id"]), description=p.get("purpose", p["role"]) + " History: " + folder_url(p["archive"])) for p in versions["starred"]]
    w["checklist"] = [dict(title=r[0], status=r[1] if r[1] in {"Complete", "Partial", "Pending", "Excluded"} else "Partial", detail=r[2]) for r in navigation["checklist"][1:]]
    assert previous <= set(entries)
    assert len(w["stars"]) == 18
    for entry in data["entries"]:
        assert entry["parent"] is None or entry["parent"] in entries
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    marker = '<script id="navigator-data" type="application/json">null</script>'
    if shell.count(marker) != 1:
        raise ValueError("NAVIGATOR_SHELL_MARKER_INVALID")
    output.write_text(shell.replace(marker, '<script id="navigator-data" type="application/json">' + payload + '</script>'))
    return data


def pointer(title, sources, master_url, html_url):
    """Small folder-specific link index; never a duplicate data workbook."""
    esc = html.escape
    cards = "".join('<article><h2>' + esc(p["baseTitle"]) + '</h2><p>' + esc(p.get("purpose", p["role"])) + '</p><p><a href="' + esc(sheet_url(p["id"])) + '">Open original Sheet</a> · <a href="' + esc(folder_url(p["archive"])) + '">Numbered version history</a></p><small>' + esc(p["newVersion"] + " · " + p["role"].replace("_", " ").lower()) + '</small></article>' for p in sources)
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(title) + '</title><style>body{font:17px/1.6 system-ui,sans-serif;color:#20382d;background:#f6f8f2;max-width:900px;margin:auto;padding:24px}a{color:#215f49}article{background:white;border:1px solid #d5ddce;border-radius:14px;margin:18px 0;padding:18px}h1{font-size:32px}h2{font-size:21px}small{color:#536554}.lead{padding:18px;background:#e9f0e2;border-radius:14px}</style><main><h1>' + esc(title) + '</h1><p class="lead"><a href="' + esc(master_url) + '"><strong>Open the readable Google Sheets guide →</strong></a></p><p>The original source IDs are retained. Edit facts in their owning Google Sheet. This HTML is a navigation pointer, not another data copy. Existing access-protected owners may remain in their original shared folders; use these links.</p>' + cards + '<p><a href="' + esc(html_url) + '">Full HTML navigator in Google Drive</a></p><p>Drive previews do not execute HTML scripts. On a phone, use the Google Sheets guide above. HTML preserves text, links and figures; its source code is maintained in GitHub.</p><p>Versioned on 27 October 2026. Numbered native PRE/POST copies live in each source’s dedicated history folder. GitHub Actions reads explicitly registered Sheet IDs, so folder renames do not require a full inventory scan.</p></main></html>'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for flag in ("data", "versions", "navigation", "shell", "output"):
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args()
    result = refresh(json.loads(Path(args.data).read_text()), json.loads(Path(args.versions).read_text()), json.loads(Path(args.navigation).read_text()), Path(args.shell).read_text(), args.output)
    print("PRIVATE_NAVIGATION_REFRESHED: existing IDs preserved; 18 starred sources")
