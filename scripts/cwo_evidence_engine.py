#!/usr/bin/env python3
"""A9-CWO offline P0 verifier / private P2 staging normalizer.

No network, uploads or provider ingestion. Private inputs/outputs must stay outside
the public repository. Does not admit engineering facts or publish private media.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HEX = re.compile(r"^[a-f0-9]{64}$")
ID = re.compile(r"^EV-[a-f0-9]{64}$")


class IntegrityError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def secure_external_path(path: Path, *, write: bool = False) -> Path:
    path = path.expanduser().resolve()
    if path == REPO or REPO in path.parents:
        raise IntegrityError("Private records inside public repository forbidden")
    if write:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.parent.chmod(0o700)
    return path


def parse_jsonl(path: Path):
    for n, raw in enumerate(path.read_bytes().splitlines(), 1):
        if raw.strip():
            try:
                yield n, raw, json.loads(raw)
            except (ValueError, UnicodeDecodeError) as e:
                raise IntegrityError(f"Invalid JSONL: {path.name}:{n}") from e


def verify_index(manifest_path: Path, receipt_path: Path, partition_dir: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    run_id = manifest["run_id"]
    if run_id != receipt["run_id"] or manifest["source_receipt_status"] != receipt["status"]:
        raise IntegrityError("Manifest/receipt identity or status conflict")
    if manifest["source_scope"]["parent_channel_ids"] != receipt["target_parent_channels"]:
        raise IntegrityError("Discord parent scope mismatch")
    if len(set(manifest["source_scope"]["parent_channel_ids"])) != 2:
        raise IntegrityError("Unexpected source scope: more or fewer than 2 parents")
    if manifest["source_scope"]["archived_threads_covered"] is not False:
        raise IntegrityError("Archived thread coverage may not be inferred")
    unique = set()
    counts = []
    for part in manifest["partitions"]:
        matches = list(partition_dir.glob(f'*{part["date_npt"]}*{run_id}*.jsonl'))
        if len(matches) != 1:
            raise IntegrityError(f"Missing or ambiguous local partition {part['date_npt']}")
        blob = matches[0].read_bytes()
        if digest(blob) != part["sha256"]:
            raise IntegrityError(f"SHA256 mismatch for {part['date_npt']}")
        rows = list(parse_jsonl(matches[0]))
        if len(rows) != part["rows"]:
            raise IntegrityError(f"Row count mismatch for {part['date_npt']}")
        for _, _, row in rows:
            if row["run_id"] != run_id or row["source_receipt_id"] != manifest["source_receipt_drive_id"]:
                raise IntegrityError("Row points to different run or receipt")
            if row["parent_channel_id"] not in manifest["source_scope"]["parent_channel_ids"]:
                raise IntegrityError("Out-of-scope source channel")
            if row["admission_status"] != "NOT_RECONCILED":
                raise IntegrityError("Index row unexpectedly claims admission")
            key = (row["provider"], row["channel_id"], row["message_id"])
            if key in unique:
                raise IntegrityError("Duplicate provider/channel/message in source index")
            unique.add(key)
        counts.append({"date_npt":part["date_npt"],"rows":len(rows),"sha256_verified":True})
    if len(unique) != manifest["rows_indexed"] or len(unique) != receipt["messages_new_or_changed"]:
        raise IntegrityError("Message total mismatch")
    actual = Counter(a.get("status") for s in receipt["sources"] for a in s["attachments_evidence"])
    if sum(actual.values()) != sum(s["attachments"] for s in receipt["sources"]):
        raise IntegrityError("Attachment total mismatch")
    if actual["FAILED"] != receipt["attachment_failures"]:
        raise IntegrityError("Failed attachment count mismatch")
    for s in receipt["sources"]:
        if s["parent_channel_id"] not in manifest["source_scope"]["parent_channel_ids"]:
            raise IntegrityError("Out-of-scope receipt source")
    return {"source_run_id":run_id, "index_rows_verified":len(unique),
            "partitions_verified":len(counts),"source_scopes":len(receipt["sources"]),
            "attachment_status_counts":dict(actual),"source_receipt_status":receipt["status"],
            "source_receipt_sha256":digest(receipt_path.read_bytes()),
            "manifest_sha256":digest(manifest_path.read_bytes()),
            "partition_counts":counts,
            "construction_admission":"NONE_INDEX_NOT_CONSTRUCTION_TRUTH"}


def normalize_private(manifest_path: Path, receipt_path: Path, index_dir: Path,
                      raw_id_to_path: Path, output_path: Path, existing_path: Path | None = None) -> dict:
    """Raw map is a private JSON dict of Drive raw-file IDs to local trusted paths.

    No project inference; every new record is quarantined. Copies are local private
    staging only. Never write raw provider messages or CDN URLs to public GitHub.
    """
    output_path = secure_external_path(output_path, write=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    verified = verify_index(manifest_path, receipt_path, index_dir)
    raw_map = json.loads(raw_id_to_path.read_text(encoding="utf-8"))
    history = {}
    if existing_path:
        for _, _, older in parse_jsonl(secure_external_path(existing_path)):
            key = (older["provider"], older["provider_channel_id"], older["provider_message_id"])
            if key not in history or history[key]["version"] < older["version"]:
                history[key] = older
    source_cache = {}
    staged = []
    reused = 0
    for part in manifest["partitions"]:
        partition = next(index_dir.glob(f'*{part["date_npt"]}*{manifest["run_id"]}*.jsonl'))
        for _, _, item in parse_jsonl(partition):
            raw_id = item["raw_drive_id"]
            if raw_id not in raw_map:
                raise IntegrityError("Missing private raw file mapping")
            if raw_id not in source_cache:
                path = secure_external_path(Path(raw_map[raw_id]))
                source_cache[raw_id] = list(parse_jsonl(path))
            raw_lines = source_cache[raw_id]
            pos = item["raw_line_1_based"]
            if not isinstance(pos, int) or pos < 1 or pos > len(raw_lines):
                raise IntegrityError("Raw pointer out of bounds")
            _, raw_bytes, raw_message = raw_lines[pos-1]
            channel = item["channel_id"]
            message = item["message_id"]
            if str(raw_message.get("id")) != message or str(raw_message.get("channel_id")) != channel:
                raise IntegrityError("Source ID mismatch between pointer and raw message")
            source_sha = digest(raw_bytes)
            provider = item["provider"]
            key = (provider,channel,message)
            record_id = "EV-" + digest(f"{provider}|{channel}|{message}|{source_sha}".encode())
            prior = history.get(key)
            if prior and prior["record_id"] == record_id:
                reused += 1
                continue
            version = prior["version"]+1 if prior else 1
            rec = {
                "record_id":record_id,"provider":provider,"provider_message_id":message,
                "provider_channel_id":channel,"captured_at_utc":receipt["collection_finished_at"],
                "project_id":None,"company_id":None,
                "source_run_id":manifest["run_id"],"source_receipt_id":item["source_receipt_id"],
                "source_content_sha256":source_sha,"evidence_kind":"MESSAGE",
                "caption_or_text":raw_message.get("content") or "",
                "observation_date":None,"claim_state":"FIELD_REPORTED",
                "verification_state":"SOURCE_METADATA_ONLY",
                "attachment_ids":[str(a["id"]) for a in raw_message.get("attachments",[])],
                "access_classification":"PRIVATE_RESTRICTED",
                "source_uri_ref":f"private-drive-pointer:{raw_id}:{pos}",
                "version":version,"supersedes_id":prior["record_id"] if prior else None,
                "admission_status":"QUARANTINED_UNMAPPED","admission_receipt_id":None
            }
            staged.append(rec)
            history[key] = rec
    if output_path.exists():
        raise IntegrityError("Refusing to overwrite private normalized output; use a new versioned path")
    with output_path.open("x",encoding="utf-8") as out:
        for row in staged:
            out.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
    output_path.chmod(0o600)
    return {"status":"PRIVATE_STAGING_ONLY","new_records":len(staged),
            "replayed_unchanged":reused,"admitted":0,"source_verified":verified["index_rows_verified"],
            "output_sha256":digest(output_path.read_bytes())}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command",choices=["verify-index","normalize-private"])
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--receipt",type=Path,required=True)
    p.add_argument("--index-dir",type=Path,required=True)
    p.add_argument("--raw-map",type=Path)
    p.add_argument("--private-output",type=Path)
    p.add_argument("--existing-private-registry",type=Path)
    a = p.parse_args()
    if a.command == "verify-index":
        result = verify_index(a.manifest,a.receipt,a.index_dir)
    else:
        if not a.raw_map or not a.private_output:
            p.error("normalize-private requires --raw-map and --private-output")
        result = normalize_private(a.manifest,a.receipt,a.index_dir,a.raw_map,
                                   a.private_output,a.existing_private_registry)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
