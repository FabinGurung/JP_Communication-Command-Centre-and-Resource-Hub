#!/usr/bin/env python3
"""Synthetic negative tests: unlisted, candidate, path traversal and symlinks."""
import json,subprocess,sys,tempfile
from pathlib import Path
SCRIPT=Path(__file__).resolve().with_name("build_public_pages_site.py")
ROUTES=["index.html","map.html","site-operations.html","resources/index.html","workspace/index.html","guide/index.html",".nojekyll"]
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,encoding="utf-8")
def check(src,out,policy):
    return subprocess.run([sys.executable,str(SCRIPT),"--source",str(src),"--output",str(out),"--allowlist",str(policy)],capture_output=True,text=True)
def manifest(sub,state,safety):
    return dict(schema_version="0.1.0",project_id="PRJ-000029",submission_id=sub,title="Synthetic public-safe acceptance fixture",workstream="other",publication_state=state,privacy_review=safety,engineering_status="NOT_ASSERTED")
def test():
    with tempfile.TemporaryDirectory() as tmp:
        b=Path(tmp);src=b/"src";out=b/"out";pol=b/"policy.json"
        for p in ROUTES:write(src/p,"<html>safe</html>" if p.endswith(".html") else "")
        write(src/"contributions/index.html","<html>index</html>")
        yes="contributions/PRJ-000029/public-test-01/manifest.json"
        no="contributions/PRJ-000029/candidate-test-01/manifest.json"
        write(src/yes,json.dumps(manifest("public-test-01","APPROVED_PUBLIC","PUBLIC_SAFE_ATTESTED")))
        write(src/no,json.dumps(manifest("candidate-test-01","PUBLIC_CANDIDATE","PENDING")))
        write(src/"AGENTS.md","internal");write(src/"ops/data/private-people.json",'{"secret":"fixture"}')
        cfg=dict(schema_version="1.0.0",policy_id="OPS_PAGES_EXPLICIT_PUBLIC_FILES_V1",files=ROUTES)
        write(pol,json.dumps(cfg))
        r=check(src,out,pol);assert r.returncode==0,r.stderr+r.stdout
        actual={p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
        want=set(ROUTES+[yes,"contributions/index.html","publication-manifest.json"])
        assert actual==want,(actual,want)
        assert not (out/no).exists() and not (out/"AGENTS.md").exists()
        cfg["files"]=ROUTES+["../AGENTS.md"];write(pol,json.dumps(cfg))
        r=check(src,b/"bad-traversal",pol);assert r.returncode!=0 and "PAGES_ARTIFACT_FAIL" in r.stderr
        cfg["files"]=ROUTES;write(pol,json.dumps(cfg))
        (src/"map.html").unlink();(src/"map.html").symlink_to(src/"AGENTS.md")
        r=check(src,b/"bad-symlink",pol);assert r.returncode!=0 and "symlink" in r.stderr,r.stderr
    print("PAGES_ARTIFACT_NEGATIVE_TEST_PASS: unlisted files; candidate exclusion; traversal; symlink")
if __name__=="__main__":test()
