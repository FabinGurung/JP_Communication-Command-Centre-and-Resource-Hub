#!/usr/bin/env python3
from __future__ import annotations
import json, re, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
required=[
    ROOT/"ops/control/control-system.json",
    ROOT/"ops/control/branch-lane-registry.json",
    ROOT/"ops/control/branch-lane-registry.schema.json",
    ROOT/"ops/control/BRANCH_LANE_CONTROL.md",
]
missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
if missing:
    raise SystemExit(f"Missing compulsory branch/lane control files: {missing}")

registry=json.loads((ROOT/"ops/control/branch-lane-registry.json").read_text(encoding="utf-8"))
control=json.loads((ROOT/"ops/control/control-system.json").read_text(encoding="utf-8"))

if registry.get("schema_version")!="1.0.0" or registry.get("registry_id")!="OPS-BRANCH-LANE-REGISTRY-001":
    raise SystemExit("Unexpected branch registry identity/version.")
if registry.get("required_before_mutation") is not True:
    raise SystemExit("Branch registry must be compulsory before mutation.")
if control.get("status")!="ACTIVE_COMPULSORY":
    raise SystemExit("Operations control system is not ACTIVE_COMPULSORY.")

active=registry.get("active_branches",[])
archives=registry.get("archive_branches",[])
aliases=registry.get("legacy_aliases",[])

ids=[x.get("branch_id") for x in active+archives]
if any(not x for x in ids) or len(ids)!=len(set(ids)):
    raise SystemExit("branch_id values must be nonblank and unique.")

active_refs={x["branch_name"] for x in active}
archive_refs={x["branch_name"] for x in archives}
alias_refs={x["alias_ref"] for x in aliases}
if active_refs != {"main","feature/daily-ops-current-work"}:
    raise SystemExit(f"Unexpected active branches: {sorted(active_refs)}")
if active_refs & archive_refs or active_refs & alias_refs or archive_refs & alias_refs:
    raise SystemExit("Active/archive/legacy alias sets must be disjoint.")

sha_re=re.compile(r"^[0-9a-f]{40}$")
archive_by_ref={x["branch_name"]:x for x in archives}
for item in archives:
    if not item["branch_name"].startswith("archive/"):
        raise SystemExit(f"Archive outside archive namespace: {item['branch_name']}")
    if item.get("status")!="ARCHIVED_FROZEN" or item.get("allowed_for_work") is not False:
        raise SystemExit(f"Archive is not frozen/non-working: {item['branch_name']}")
    if not sha_re.match(item.get("frozen_sha","")):
        raise SystemExit(f"Archive has invalid frozen_sha: {item['branch_name']}")

for item in aliases:
    target=item.get("resolves_to_archive_ref")
    if item.get("status")!="LEGACY_ALIAS_PENDING_PROVIDER_DELETE" or item.get("do_not_use") is not True:
        raise SystemExit(f"Legacy alias not fail-closed: {item.get('alias_ref')}")
    if target not in archive_by_ref:
        raise SystemExit(f"Legacy alias target is not a registered archive: {item.get('alias_ref')} -> {target}")
    if item.get("expected_sha") != archive_by_ref[target].get("frozen_sha"):
        raise SystemExit(f"Legacy alias/archive SHA mismatch: {item.get('alias_ref')}")

remote_text=subprocess.check_output(["git","ls-remote","--heads","origin"],cwd=ROOT,text=True)
remote={}
for line in remote_text.splitlines():
    if not line.strip(): continue
    sha,ref=line.split(None,1)
    prefix="refs/heads/"
    if ref.startswith(prefix):
        remote[ref[len(prefix):]]=sha

registered=active_refs|archive_refs|alias_refs
unregistered=set(remote)-registered
missing_remote=registered-set(remote)
if unregistered:
    raise SystemExit(f"Unregistered provider branch refs: {sorted(unregistered)}")
if missing_remote:
    raise SystemExit(f"Registry expects branch refs missing at provider: {sorted(missing_remote)}")

for item in archives:
    actual=remote[item["branch_name"]]
    if actual!=item["frozen_sha"]:
        raise SystemExit(f"Frozen archive moved: {item['branch_name']} {actual} != {item['frozen_sha']}")
for item in aliases:
    actual=remote[item["alias_ref"]]
    if actual!=item["expected_sha"]:
        raise SystemExit(f"Legacy alias SHA drift: {item['alias_ref']}")

counts=registry.get("counts",{})
if counts.get("provider_branch_refs") != len(remote):
    raise SystemExit(f"Provider branch count drift: registry={counts.get('provider_branch_refs')} live={len(remote)}")
if counts.get("active_logical_branches") != len(active):
    raise SystemExit("Active branch count mismatch.")
if counts.get("canonical_archive_refs") != len(archives):
    raise SystemExit("Archive count mismatch.")
if counts.get("legacy_alias_refs_pending_delete") != len(aliases):
    raise SystemExit("Legacy alias count mismatch.")

print(f"PASS branch/lane registry: provider={len(remote)} active={len(active)} archives={len(archives)} legacy_aliases={len(aliases)}")
