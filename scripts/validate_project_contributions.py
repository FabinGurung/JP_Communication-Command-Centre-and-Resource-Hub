#!/usr/bin/env python3
"""Fail-closed PR scope guard for independent ChatGPT project-thread submissions.

Runs without private Google Drive credentials. This checks path isolation and
obvious content hazards only; it CANNOT authenticate private source approval.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANCH = re.compile(r"^contrib/(PRJ-[0-9]{6})/([a-z0-9][a-z0-9-]{2,48})$")
PATH = re.compile(r"^contributions/(PRJ-[0-9]{6})/([a-z0-9][a-z0-9-]{2,48})/([A-Za-z0-9_.-]+)$")
EXTENSIONS = {".json", ".md", ".txt"}
FIELDS = {"schema_version", "project_id", "submission_id", "title", "workstream",
          "publication_state", "privacy_review", "engineering_status"}
FORBIDDEN = [
    re.compile(r"docs\.google\.com/(?:document|spreadsheets)", re.I),
    re.compile(r"drive\.google\.com/(?:file|folders)/", re.I),
    re.compile(r"maps\.app\.goo\.gl", re.I),
    re.compile(r"(?i)(?:api_key|private_key|client_secret|access_token|refresh_token)"),
    re.compile(r"(?i)(?:salary|bank_account|national_id|citizenship_number|passport_number)"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
]
def die(message: str) -> None:
    raise SystemExit("PROJECT_CONTRIBUTION_FAIL: " + message)
def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def main() -> None:
    branch = os.getenv("GITHUB_HEAD_REF", "")
    target = os.getenv("GITHUB_BASE_REF", "")
    match = BRANCH.fullmatch(branch)
    if not match or target not in {"main", "feature/daily-ops-current-work"}:
        die(f"PR source branch or target is outside registered project lane: {branch} -> {target}")
    project_id, submission_id = match.groups()
    base = git("merge-base", "HEAD", f"origin/{target}")
    changes = [p for p in git("diff", "--name-only", "--no-renames", base, "HEAD").splitlines() if p]
    if not changes:
        die("Empty project content PR")
    if len(changes) > 40:
        die("Too many files in one project submission")
    for path in changes:
        m = PATH.fullmatch(path)
        if not m or (m.group(1), m.group(2)) != (project_id, submission_id):
            die(f"Change outside the exact project submission path: {path}")
        file = ROOT / path
        if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to(ROOT):
            die(f"Missing, symlinked or unsafe file: {path}")
        if file.suffix.lower() not in EXTENSIONS or file.stat().st_size > 200_000:
            die(f"Disallowed public-file type or size: {path}")
        try:
            content = file.read_text(encoding="utf-8")
        except UnicodeError:
            die(f"Non-UTF8 submission: {path}")
        for regex in FORBIDDEN:
            if regex.search(content):
                die(f"Private source URL, PII or secret-looking field: {path}")
    manifest_file = ROOT / "contributions" / project_id / submission_id / "manifest.json"
    if not manifest_file.exists():
        die("Required manifest.json absent")
    payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not FIELDS.issubset(payload):
        die("Missing required manifest fields")
    if set(payload) - FIELDS:
        die(f"Unreviewed manifest keys: {sorted(set(payload) - FIELDS)}")
    if payload.get("schema_version") != "0.1.0" or payload.get("project_id") != project_id or payload.get("submission_id") != submission_id:
        die("Manifest identity does not match its project branch and folder")
    if not isinstance(payload.get("title"), str) or not 3 <= len(payload["title"]) <= 100:
        die("Manifest title length invalid")
    if payload.get("workstream") not in {"drawing", "estimate", "schedule", "engineering", "progress", "resource", "communication", "other"}:
        die("Unknown module workstream")
    if payload.get("publication_state") not in {"PUBLIC_CANDIDATE", "APPROVED_PUBLIC"}:
        die("Unsupported publication state")
    if payload.get("privacy_review") not in {"PENDING", "PUBLIC_SAFE_ATTESTED"}:
        die("Unrecognized privacy status")
    if payload.get("engineering_status") not in {"NOT_ASSERTED", "ENGINEERING_HOLD", "UNVERIFIED"}:
        die("Engineering approval cannot be asserted in project content manifest")
    if payload["publication_state"] == "APPROVED_PUBLIC" and payload["privacy_review"] != "PUBLIC_SAFE_ATTESTED":
        die("Cannot publish without public-safety attestation")
    print(f"PROJECT_CONTRIBUTION_SCOPE_PASS: {project_id}/{submission_id}, {len(changes)} scoped, text-only file(s); private-provider QA remains external.")

if __name__ == "__main__":
    main()
