"""Synthetic, offline regression for Discord archive-first/history C06-C09."""
import ast
import gzip
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

notebook = json.loads(Path("ops/discord/A9_CWO_DISCORD_TWO_CHANNEL_DAILY_COLLECTOR_v1.0.ipynb").read_text())
cells = {item["id"]: "".join(item["source"]) for item in notebook["cells"]}
assert notebook["metadata"]["a9_cwo_revision"]["version_id"] == "20261010-001"
c06 = cells["a9-cwo-c06-full-history"]
c07 = cells["a9-cwo-c07-media-recovery"]
c08 = cells["a9-cwo-c08-sqlite-query"]
c09 = cells["a9-cwo-c09-publication-gate"]
for key in ("a9-cwo-c06-full-history","a9-cwo-c07-media-recovery","a9-cwo-c08-sqlite-query","a9-cwo-c09-publication-gate"):
    ast.parse(cells[key], filename=key)
print("PASS: C06/C07/C08/C09 parse as Python")

assert 'input("Type FULL_HISTORY' in c06
assert 'input("Type REPAIR_MEDIA' in c07
assert 'input("Type BUILD_SQLITE' in c08
assert "PASS_DATA_VERIFIED_ONLY" in c09 and "BLOCKED" in c09
assert "H_MAX_PAGES_PER_INVOCATION = 8" in c06
assert "H_MAX_MEDIA_ATTEMPTS_PER_INVOCATION = 20" in c06
assert '"MEDIA_BYTES_OVER_LIMIT"' in c06
assert "h_hash.sha256(stored).hexdigest() != digest.hexdigest()" in c06
assert '"reason":"EXISTING_DRIVE_SHA_NOT_EQUAL_FRESH_PROVIDER_SOURCE"' in c06
assert "provider_refetched" in c06
assert "H_DISCORD_EPOCH" in c06 and "h_gzip.compress(lines,compresslevel=6,mtime=0)" in c06
assert 'h_immutable(rawdir,stem+".jsonl.gz"' in c06
assert 'page=h_immutable(pagedir,' in c06
assert 'h_mutable_json(archive_root,"historical_state_current.json",state)' in c06
assert c06.index('raw=h_immutable(rawdir') < c06.index("for msg in messages:") < c06.index("page=h_immutable(pagedir,")
assert c06.index("page=h_immutable(pagedir,") < c06.index('h_mutable_json(archive_root,"historical_state_current.json",state)')
assert "threads/archived" in c06 and "threads/active" in c06
assert "guilds/%s/channels" in c06
assert 'H_HISTORY_FOLDER = "TWO_PARENT_HISTORY_ARCHIVE_V2"' in c06
assert "in_scope = {str(ch[\"id\"]): ch for ch in channels if str(ch[\"id\"]) in H_PARENT_IDS}" in c06
assert "FULL_HISTORY_ARCHIVE_V1" not in c06
assert "QUERY_SNAPSHOTS missing because C08" in c09
assert "source_history_complete" in c08
assert "PARTIAL_BACKFILL" in c08
assert "h_media(R_MEDIA" in c07 and 'R_RECOVERED[aid]' in c07
assert 'q_database=h_immutable(q_dir,' in c08 and "sqlite3" in c08
assert 'g_fail.append("ORIGINAL_MEDIA_RECOVERY_INCOMPLETE")' in c09
assert "LAST_HISTORY_RECEIPT_INCOMPLETE" in c09 and "QUERY_INDEX_BUILT_FROM_PARTIAL_HISTORY" in c09
assert "g_build.get(\"source_run_receipt_id\")!=g_runs[-1][\"id\"]" in c09
for code in (c06,c07,c08,c09):
    assert "chat.postMessage" not in code and "slack.chat_postMessage" not in code
print("PASS: full history scope, immutable raw-before-media page order, retries and fail-closed gates")

# Execute only pure encoder and source discovery functions, not the runtime collectors.
tree = ast.parse(c06)
definitions = {x.name:x for x in tree.body if isinstance(x,ast.FunctionDef)}
assert {"h_payload","h_discover","h_archived"}.issubset(definitions)
module = ast.Module(body=[definitions["h_payload"],definitions["h_discover"]],type_ignores=[])
root = {"h_json":json,"GUILD_ID":"1234","H_PARENT_IDS":("parent1","parent2")}
def archived(parent,kind):
    return ([{"id":"archive1","name":"Past job","type":11,"parent_id":"parent1"}],None) if parent=="parent1" and kind=="public" else ([],None)
def requester(url,params=None,allow_failure=False):
    if url.endswith("/channels"):
        return ([{"id":"parent1","type":0,"name":"Company pictures"},
                 {"id":"parent2","type":15,"name":"Project forum"},
                 {"id":"voice1","type":2,"name":"Voice"}],None)
    if url.endswith("/threads/active"):
        return ({"threads":[{"id":"active1","type":11,"name":"Construction","parent_id":"parent1"}]},None)
    raise AssertionError("Unexpected provider URL in synthetic test: "+url)
root.update({"h_req":requester,"h_archived":archived})
exec(compile(module,"synthetic_archive","exec"),root)
sources,gaps=root["h_discover"]()
assert {x["id"] for x in sources}=={"parent1","parent2","archive1","active1"}
assert any(x["kind"]=="ARCHIVED_THREAD" for x in sources)
assert not gaps, "out-of-scope category/voice channels must not create false scope debt"
print("PASS: two registered parents, active and archived child threads only, no out-of-scope guild content")

payload={"id":"12345","content":"कुमारी site – 🏗","embeds":[{"image":{"url":"https://example.org/a.png"}}],
         "reactions":[{"emoji":{"name":"👍"},"count":2}],"attachments":[{"id":"999","size":1234}]}
raw=root["h_payload"](payload)
compressed=gzip.compress(raw,compresslevel=6,mtime=0)
assert gzip.decompress(compressed)==raw
assert json.loads(gzip.decompress(compressed))==payload
assert hashlib.sha256(raw).hexdigest()==hashlib.sha256(gzip.decompress(compressed)).hexdigest()
print("PASS: lossless nested multilingual provider JSONL gzip and SHA-256")

# Validate publish-query schema separately, with functional inserts/search and integrity.
ddl=Path("ops/discord/schemas/full-history-sqlite-v1.sql").read_text()
conn=sqlite3.connect(":memory:")
conn.executescript(ddl)
conn.execute("INSERT INTO sources VALUES (?,?,?,?,?)",("parent1","parent1","PARENT","Company pictures",0))
conn.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?)",
             ("parent1","12345",hashlib.sha256(raw).hexdigest(),"parent1","author1",
              "2026-10-09T00:00:00Z",None,payload["content"],raw.decode()))
row=conn.execute("SELECT raw_json FROM messages WHERE channel_id=? AND message_id=?",
                 ("parent1","12345")).fetchone()
assert json.loads(row[0])==payload
assert conn.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
conn.close()
print("PASS: normalized indexed SQLite stores original raw JSON without losing embeds, attachments or Nepali")
