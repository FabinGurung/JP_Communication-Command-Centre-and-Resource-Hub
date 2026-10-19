#!/usr/bin/env python3
"""Verify six user-confirmed resource-to-project aliases; do not equate people."""
import csv
import json
import sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COLUMNS=("alias_id","project_id","resource_id","observed_label_key","label_role",
"association_state","authority_ref","association_date","identity_scope",
"same_legal_person_asserted","engineering_issue_state",
"archive_location_unmodified","public_disclosure_additional_authorized")
def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def sql_value(value):
    if type(value) is bool:
        return "TRUE" if value else "FALSE"
    return "'"+str(value).replace("'","''")+"'"
def sql_seed(rows):
    header=("-- Generated from ops/data/resource-project-name-aliases.v1.0.json\n"
            "-- Apply after ops/schema/daily-ops-postgres.sql. Do not edit manually.\n"
            "-- These aliases do not equate people or certify construction use.\n"
            "INSERT INTO ops_project_resource_name_aliases (\n  "+
            ",\n  ".join(COLUMNS)+"\n) VALUES\n")
    values=",\n".join("("+", ".join(sql_value(r[k]) for k in COLUMNS)+")" for r in rows)
    return header+values+"\nON CONFLICT (alias_id) DO UPDATE SET observed_label_key = EXCLUDED.observed_label_key, association_state = EXCLUDED.association_state, authority_ref = EXCLUDED.authority_ref;\n"
def verify():
    a=read("ops/data/resource-project-name-aliases.v1.0.json")
    sources=read("ops/data/project-resources.json")
    review=read("ops/data/resource-review-dispositions-public.v1.0.json")
    status=read("ops/data/source-readiness-public.v1.0.json")
    rows=a["rows"]
    assert a["count"]==len(rows)==6
    assert a["registry_id"]=="REQ07_PROJECT_SCOPED_SOURCE_NAME_ALIAS_20261019"
    assert set(a["semantics"]["allowed_projects"])=={"P001","P002"}
    assert len({r["alias_id"] for r in rows})==len({r["resource_id"] for r in rows})==6
    assert {r["resource_id"] for r in rows}=={r["resource_id"] for r in review["items"]}
    pair={p["project_id"]:p for p in a["project_pairs"]}
    assert set(pair)=={"P001","P002"}
    with (ROOT/"projects.csv").open(encoding="utf-8",newline="") as f:
        master={r["legacy_project_code"]:r for r in csv.DictReader(f) if r["legacy_project_code"] in pair}
    assert set(master)==set(pair)
    for p,m in master.items():
        q=pair[p]
        assert (q["global_project_id"],q["company_project_code"],q["source_organization"])==(m["project_id"],m["company_project_code"],m["executing_company_id"])
    src={r["resource_id"]:(p["project_id"],r) for p in sources["projects"] for r in p["resources"]}
    assert len(src)==46
    for r in rows:
        assert r["project_id"] in pair and r["resource_id"] in src
        assert src[r["resource_id"]][0]==r["project_id"],"Cross-project alias attempted"
        assert r["observed_label_key"].startswith(r["project_id"]+"_")
        assert r["association_state"]=="USER_CONFIRMED_PROJECT_RESOURCE_ASSOCIATION"
        assert r["identity_scope"]=="RESOURCE_TO_PROJECT_ONLY"
        assert r["same_legal_person_asserted"] is False
        assert r["engineering_issue_state"]=="NOT_CERTIFIED"
        assert r["archive_location_unmodified"] is True
        assert r["public_disclosure_additional_authorized"] is False
    assert sum(r["project_id"]=="P001" for r in rows)==3
    assert sum(r["project_id"]=="P002" for r in rows)==3
    assert sum(r["label_role"]=="SOURCE_TITLEBLOCK_CLIENT" for r in rows)==1
    assert status["resources"]["file_specific_review"]["project_associations_user_confirmed"]==6
    assert status["resources"]["file_specific_review"]["engineer_issued_for_construction"]==0
    assert status["communication"]["collector_operational_mode"]=="ON_HOLD_BY_USER"
    ddl=(ROOT/"ops/schema/daily-ops-postgres.sql").read_text(encoding="utf-8")
    for fragment in ("CREATE TABLE IF NOT EXISTS ops_project_resource_name_aliases","FOREIGN KEY (project_id, resource_id)",
                     "REFERENCES ops_project_resources(project_id, resource_id)","CHECK (project_id IN ('P001','P002'))",
                     "same_legal_person_asserted = false","public_disclosure_additional_authorized = false"):
        assert fragment in ddl,fragment
    assert (ROOT/"ops/schema/resource-project-name-alias-seed.v1.0.sql").read_text(encoding="utf-8")==sql_seed(rows)
    db=sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
    CREATE TABLE project(id TEXT PRIMARY KEY);
    CREATE TABLE resource(project_id TEXT NOT NULL,resource_id TEXT NOT NULL UNIQUE,
      PRIMARY KEY(project_id,resource_id),FOREIGN KEY(project_id) REFERENCES project(id));
    CREATE TABLE alias(alias_id TEXT PRIMARY KEY,project_id TEXT NOT NULL,resource_id TEXT NOT NULL,
      observed_label_key TEXT NOT NULL,
      FOREIGN KEY(project_id,resource_id) REFERENCES resource(project_id,resource_id),
      CHECK(project_id IN ('P001','P002')));
    """)
    db.executemany("INSERT INTO project VALUES(?)",[("P001",),("P002",)])
    db.executemany("INSERT INTO resource VALUES(?,?)",[(p,k) for k,(p,_) in src.items() if p in pair])
    db.executemany("INSERT INTO alias VALUES(?,?,?,?)",[(r["alias_id"],r["project_id"],r["resource_id"],r["observed_label_key"]) for r in rows])
    assert db.execute("SELECT COUNT(*) FROM alias JOIN resource USING(project_id,resource_id)").fetchone()[0]==6
    sample=next(r for r in rows if r["project_id"]=="P002")
    for wrong in ("P001","P003"):
        try:
            db.execute("INSERT INTO alias VALUES(?,?,?,?)",("FORBIDDEN"+wrong,wrong,sample["resource_id"],"BAD"))
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Cross-project/global alias was accepted: "+wrong)
    print("SCOPED_RESOURCE_ALIAS_PASS: six FK-validated aliases, two projects only, no person identity merge, no construction release.")
if __name__=="__main__":
    verify()
