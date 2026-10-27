#!/usr/bin/env python3
"""One-time, user-run Colab setup for the existing Sheets publishing engine.

Uses keyless federation. Never creates a service-account key or another Sheet.
Only exact registered files receive a service-account permission. Credentials
stay in memory; provider response bodies must never appear in notebook output.
"""
from __future__ import annotations

import copy
import re
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

REPOSITORY = "FabinGurung/JP_Communication-Command-Centre-and-Resource-Hub"
BRANCH = "feature/daily-ops-current-work"
WORKFLOW = "daily-ops-branch-preview.yml"
CONFIG_PATH = "ops/control/sheets-actions-publishing.v1.json"
REGISTRY_PATH = "ops/control/branch-lane-registry.json"
SITE_ROOT = "https://fabingurung.github.io/JP_Communication-Command-Centre-and-Resource-Hub/"
POOL_ID = "jp-pages-github"
PROVIDER_ID = "github"
ACCOUNT_ID = "jp-pages-publisher"
ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{10,200}")


class ConnectionError(RuntimeError):
    """Safe operational messages only; never include response text or tokens."""


def file_id(value):
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise ConnectionError("REGISTERED_FILE_ID_INVALID")
    return value


def access_plan(cfg):
    """One entry per live object, irrespective of how many tabs consume it."""
    if cfg.get("repository") != REPOSITORY:
        raise ConnectionError("REPOSITORY_MISMATCH")
    plan = {}

    def add(fid, role, purpose):
        fid = file_id(fid)
        entry = plan.setdefault(fid, {"file_id": fid, "role": role, "purposes": []})
        if role != entry["role"]:
            raise ConnectionError("SOURCE_AND_OUTPUT_ID_COLLISION")
        if purpose not in entry["purposes"]:
            entry["purposes"].append(purpose)

    for name, spec in cfg["sources"].items():
        if spec.get("read_mode") != "EMPTY_TEMPLATE_NOT_CONNECTED":
            add(spec["workbook_id"], "reader", name)
    resource = cfg.get("resources_source")
    if resource:
        add(resource["workbook_id"], "reader", resource["tab"])
    for name, spec in cfg.get("notification_sources", {}).items():
        add(spec["workbook_id"], "reader", name)
    for spec in cfg.get("field_sources", []):
        add(spec["workbook_id"], "reader", spec["tab"])
    for original in cfg.get("notification_policy", {}).get("admitted_sources", {}).values():
        url = urlparse(original["drive_source_url"])
        match = re.fullmatch(r"/file/d/([A-Za-z0-9_-]+)/view", url.path)
        if url.scheme != "https" or url.netloc != "drive.google.com" or not match:
            raise ConnectionError("ORIGINAL_DRIVE_URL_INVALID")
        add(match.group(1), "reader", "Admitted original message; integrity verification")
    add(cfg["publishing_workbook_id"], "writer", "Derived publishing workbook only")
    add(cfg["previous_versions_file_id"], "writer", "Existing append-only publishing restore log")
    if cfg["previous_versions_folder_id"] in plan:
        raise ConnectionError("FOLDER_SHARING_FORBIDDEN")
    return list(plan.values())


def federation_spec(project_number, repo):
    rid, oid = str(repo.get("id", "")), str(repo.get("owner", {}).get("id", ""))
    if repo.get("full_name") != REPOSITORY or not rid.isdigit() or not oid.isdigit():
        raise ConnectionError("GITHUB_IMMUTABLE_ID_MISSING")
    if not str(project_number).isdigit():
        raise ConnectionError("GOOGLE_PROJECT_NUMBER_INVALID")
    pool = f"projects/{project_number}/locations/global/workloadIdentityPools/{POOL_ID}"
    return {
        "pool": pool,
        "provider": pool + "/providers/" + PROVIDER_ID,
        "member": "principalSet://iam.googleapis.com/" + pool + "/attribute.repository_id/" + rid,
        "body": {
            "displayName": "JP Pages GitHub",
            "attributeMapping": {
                "google.subject": "assertion.sub",
                "attribute.repository_id": "assertion.repository_id",
                "attribute.repository_owner_id": "assertion.repository_owner_id",
            },
            "attributeCondition": (
                f"assertion.repository_id == '{rid}' && "
                f"assertion.repository_owner_id == '{oid}' && "
                f"assertion.ref == 'refs/heads/{BRANCH}'"
            ),
            "oidc": {"issuerUri": "https://token.actions.githubusercontent.com"},
        },
    }


def add_identity_binding(policy, member):
    """Retain unrelated bindings, conditions, policy version and etag."""
    policy = copy.deepcopy(policy)
    role = "roles/iam.workloadIdentityUser"
    binding = next((b for b in policy.get("bindings", [])
                    if b.get("role") == role and not b.get("condition")), None)
    if binding is None:
        binding = {"role": role, "members": []}
        policy.setdefault("bindings", []).append(binding)
    if member not in binding["members"]:
        binding["members"].append(member)
    return policy


class API:
    def __init__(self, session, root):
        self.session, self.root = session, root.rstrip("/")

    def response(self, method, path, *, accepted=(200,), **kwargs):
        if not path.startswith("/") or path.startswith("//"):
            raise ConnectionError("API_PATH_INVALID")
        try:
            response = self.session.request(method, self.root + path, timeout=60, **kwargs)
        except Exception:
            raise ConnectionError("API_TRANSPORT_FAILED; rerun this cell to resume") from None
        if response.status_code not in accepted:
            raise ConnectionError(f"SETUP_HTTP_{response.status_code} at {path.split('?')[0]}")
        return response

    def call(self, method, path, **kwargs):
        response = self.response(method, path, **kwargs)
        return response.json() if response.content else {}


def github_api(token):
    import requests
    session = requests.Session()
    session.headers.update({"Authorization": "Bearer " + token,
                            "Accept": "application/vnd.github+json",
                            "X-GitHub-Api-Version": "2022-11-28"})
    return API(session, "https://api.github.com")


def load_registered_config(gh):
    import base64
    import json
    prefix = "/repos/" + REPOSITORY
    repo = gh.call("GET", prefix)
    ref = gh.call("GET", prefix + "/git/ref/heads/" + BRANCH)
    sha = ref["object"]["sha"]

    def read(path):
        data = gh.call("GET", prefix + "/contents/" + path, params={"ref": sha})
        return json.loads(base64.b64decode(data["content"]))

    cfg, registry = read(CONFIG_PATH), read(REGISTRY_PATH)
    lanes = registry.get("active_branches", [])
    if not any(r.get("branch_name") == BRANCH and r.get("allowed_for_work") is True for r in lanes):
        raise ConnectionError("PUBLISHING_BRANCH_NOT_AUTHORIZED")
    access_plan(cfg)  # Validate the complete set before sharing anything.
    return cfg, repo, sha


def permissions(api, fid):
    rows, page = [], None
    while True:
        params = {"fields": "nextPageToken,permissions(id,type,role,emailAddress,deleted)",
                  "supportsAllDrives": "true", "pageSize": 100}
        if page:
            params["pageToken"] = page
        result = api.call("GET", "/drive/v3/files/" + fid + "/permissions", params=params)
        rows.extend(p for p in result.get("permissions", []) if not p.get("deleted"))
        page = result.get("nextPageToken")
        if not page:
            return rows


def sufficient_permission(rows, email, role):
    permitted = {"reader", "writer", "owner", "organizer", "fileOrganizer"}
    if role == "writer":
        permitted.remove("reader")
    return any(p.get("type") == "user" and p.get("emailAddress", "").lower() == email.lower()
               and p.get("role") in permitted for p in rows)


def share_registered_files(api, plan, email, *, apply=False):
    """Preflight every file first. No folder, public, group or email notification."""
    pending, names = [], {}
    for item in plan:
        fid = item["file_id"]
        meta = api.call("GET", "/drive/v3/files/" + fid, params={
            "fields": "id,name,mimeType,capabilities(canShare)", "supportsAllDrives": "true"})
        if meta.get("mimeType") == "application/vnd.google-apps.folder":
            raise ConnectionError("REGISTERED_FOLDER_SHARING_FORBIDDEN")
        names[fid] = meta.get("name", fid)
        existing = permissions(api, fid)
        if sufficient_permission(existing, email, item["role"]):
            continue
        if not meta.get("capabilities", {}).get("canShare"):
            raise ConnectionError("CANNOT_SHARE_REGISTERED_FILE " + fid)
        same_user = [p for p in existing if p.get("type") == "user"
                     and p.get("emailAddress", "").lower() == email.lower()]
        pending.append((item, same_user))
    if apply:
        for item, existing in pending:
            path = "/drive/v3/files/" + item["file_id"] + "/permissions"
            if existing:
                api.call("PATCH", path + "/" + existing[0]["id"],
                         params={"supportsAllDrives": "true"}, json={"role": item["role"]})
            else:
                api.call("POST", path, accepted=(200, 201),
                         params={"sendNotificationEmail": "false", "supportsAllDrives": "true"},
                         json={"type": "user", "role": item["role"], "emailAddress": email})
            if not sufficient_permission(permissions(api, item["file_id"]), email, item["role"]):
                raise ConnectionError("FILE_PERMISSION_READBACK_FAILED " + item["file_id"])
    return {"files": len(plan), "new_or_changed_permissions": len(pending), "names": names}


def wait_operation(api, operation, emit=print):
    deadline = time.monotonic() + 180
    while not operation.get("done"):
        if time.monotonic() > deadline:
            raise ConnectionError("GOOGLE_OPERATION_PENDING; rerun to resume")
        emit("Waiting for Google to finish the identity configuration…")
        time.sleep(5)
        operation = api.call("GET", "/v1/" + operation["name"])
    if operation.get("error"):
        raise ConnectionError("GOOGLE_OPERATION_FAILED_" + str(operation["error"].get("code", "UNKNOWN")))
    return operation.get("response", {})


def ensure_identity(session, project_id, repo, emit=print):
    if not re.fullmatch(r"[a-z][a-z0-9-]{4,28}[a-z0-9]", project_id):
        raise ConnectionError("ENTER_A_GOOGLE_CLOUD_PROJECT_ID_NOT_ITS_DISPLAY_NAME")
    crm = API(session, "https://cloudresourcemanager.googleapis.com")
    project = crm.call("GET", "/v1/projects/" + project_id)
    if project.get("lifecycleState") != "ACTIVE":
        raise ConnectionError("GOOGLE_CLOUD_PROJECT_NOT_ACTIVE")
    number = str(project["projectNumber"])
    service = API(session, "https://serviceusage.googleapis.com")
    enabled = service.call("POST", f"/v1/projects/{number}/services:batchEnable", json={"serviceIds": [
        "iam.googleapis.com", "iamcredentials.googleapis.com", "sts.googleapis.com",
        "drive.googleapis.com", "sheets.googleapis.com"]})
    wait_operation(service, enabled, emit)
    iam = API(session, "https://iam.googleapis.com")
    email = ACCOUNT_ID + "@" + project_id + ".iam.gserviceaccount.com"
    sa_path = "/v1/projects/" + project_id + "/serviceAccounts/" + email
    response = iam.response("GET", sa_path, accepted=(200, 404))
    if response.status_code == 404:
        iam.call("POST", "/v1/projects/" + project_id + "/serviceAccounts", accepted=(200, 201),
                 json={"accountId": ACCOUNT_ID, "serviceAccount": {"displayName": "JP Pages publishing runner"}})
    spec = federation_spec(number, repo)
    pool_path = "/v1/" + spec["pool"]
    response = iam.response("GET", pool_path, accepted=(200, 404))
    if response.status_code == 404:
        op = iam.call("POST", f"/v1/projects/{number}/locations/global/workloadIdentityPools",
                      params={"workloadIdentityPoolId": POOL_ID},
                      json={"displayName": "JP Pages GitHub", "description": "Exact registered JP publishing branch"})
        wait_operation(iam, op, emit)
    elif response.json().get("state") != "ACTIVE" or response.json().get("disabled"):
        raise ConnectionError("EXISTING_IDENTITY_POOL_DISABLED")
    provider_path = "/v1/" + spec["provider"]
    response = iam.response("GET", provider_path, accepted=(200, 404))
    if response.status_code == 404:
        op = iam.call("POST", pool_path + "/providers", params={"workloadIdentityPoolProviderId": PROVIDER_ID},
                      json=spec["body"])
        wait_operation(iam, op, emit)
    else:
        found = response.json()
        if found.get("disabled") or found.get("state") != "ACTIVE" or any(
                found.get(k) != spec["body"][k] for k in ("attributeMapping", "attributeCondition", "oidc")):
            raise ConnectionError("EXISTING_PROVIDER_DIFFERS; review before replacing any trust policy")
    policy = iam.call("GET", sa_path + ":getIamPolicy", params={"options.requestedPolicyVersion": 3})
    updated = add_identity_binding(policy, spec["member"])
    if updated != policy:
        iam.call("POST", sa_path + ":setIamPolicy", json={"policy": updated})
    verified = iam.call("GET", sa_path + ":getIamPolicy", params={"options.requestedPolicyVersion": 3})
    if add_identity_binding(verified, spec["member"]) != verified:
        raise ConnectionError("IDENTITY_POLICY_READBACK_FAILED")
    return {"provider": spec["provider"], "service_account": email, "project_number": number}


def configure_variables(gh, identity, *, apply=False):
    prefix = "/repos/" + REPOSITORY + "/actions/variables"
    expected = {"JP_GOOGLE_WORKLOAD_IDENTITY_PROVIDER": identity["provider"],
                "JP_GOOGLE_SERVICE_ACCOUNT": identity["service_account"]}
    current = {}
    for name, value in expected.items():
        response = gh.response("GET", prefix + "/" + name, accepted=(200, 404))
        current[name] = response.json().get("value") if response.status_code == 200 else None
        if current[name] and current[name] != value:
            raise ConnectionError("DIFFERENT_EXISTING_GOOGLE_IDENTITY; reuse it or review before replacing")
    if apply:
        for name, value in expected.items():
            if current[name] == value:
                continue
            if current[name] is None:
                gh.call("POST", prefix, accepted=(201,), json={"name": name, "value": value})
            else:
                gh.call("PATCH", prefix + "/" + name, accepted=(204,), json={"name": name, "value": value})
        for name, value in expected.items():
            if gh.call("GET", prefix + "/" + name).get("value") != value:
                raise ConnectionError("GITHUB_VARIABLE_READBACK_FAILED")
    return expected


def dispatch_refresh(gh, expected_sha):
    prefix = "/repos/" + REPOSITORY
    actual = gh.call("GET", prefix + "/git/ref/heads/" + BRANCH)["object"]["sha"]
    if actual != expected_sha:
        raise ConnectionError("PUBLISHING_BRANCH_MOVED; rerun to read the current approved configuration")
    request_id = "colab-" + uuid.uuid4().hex[:16]
    gh.call("POST", prefix + "/actions/workflows/" + WORKFLOW + "/dispatches", accepted=(204,),
            json={"ref": BRANCH, "inputs": {"require_live_sheets": True, "refresh_request_id": request_id}})
    return request_id


def find_refresh_run(gh, request_id, expected_sha):
    data = gh.call("GET", "/repos/" + REPOSITORY + "/actions/workflows/" + WORKFLOW + "/runs",
                   params={"event": "workflow_dispatch", "branch": BRANCH, "per_page": 50})
    matches = [r for r in data.get("workflow_runs", [])
               if r.get("display_title") == "Sheets refresh " + request_id
               and r.get("head_sha") == expected_sha and r.get("head_branch") == BRANCH]
    if len(matches) > 1:
        raise ConnectionError("AMBIGUOUS_REFRESH_RUN")
    return matches[0] if matches else None


def verify_public_receipt(bundle, run_id, sha):
    receipt = bundle.get("publication_receipt", {})
    if (bundle.get("live_google_sheets_fetch") is not True
            or receipt.get("workflow_run_id") != str(run_id) or receipt.get("commit_sha") != sha):
        raise ConnectionError("LIVE_PUBLICATION_NOT_YET_VERIFIED")
    return receipt


def wait_for_refresh(gh, request_id, sha, *, minutes=25, emit=print, public_session=None):
    import requests
    public_session = public_session or requests.Session()
    deadline, last = time.monotonic() + minutes * 60, None
    run = None
    while time.monotonic() < deadline:
        run = find_refresh_run(gh, request_id, sha)
        status = run.get("status") if run else "waiting for GitHub to queue the run"
        if status != last:
            emit("Actions: " + status)
            if run:
                emit(run["html_url"])
            last = status
        if run and run["status"] == "completed":
            if run.get("conclusion") != "success":
                raise ConnectionError("LIVE_REFRESH_" + str(run.get("conclusion", "UNKNOWN")).upper()
                                      + "; inspect " + run["html_url"])
            try:
                response = public_session.get(SITE_ROOT + "ops/data/map-data.v1.json",
                    params={"jp_run": run["id"]}, headers={"Cache-Control": "no-cache"}, timeout=30)
                if response.ok:
                    receipt = verify_public_receipt(response.json(), run["id"], sha)
                    return {"verified": True, "run_url": run["html_url"], "receipt": receipt}
            except ConnectionError:
                pass  # Pages/CDN propagation is not a successful live readback yet.
            except Exception:
                pass
        time.sleep(15)
    link = run.get("html_url", SITE_ROOT) if run else "https://github.com/" + REPOSITORY + "/actions"
    raise ConnectionError("VERIFICATION_PENDING; no success claimed. Check " + link)


def connect(session, token, project_id, *, emit=print, wait_minutes=25):
    gh = github_api(token)
    cfg, repo, sha = load_registered_config(gh)
    plan = access_plan(cfg)
    email = ACCOUNT_ID + "@" + project_id + ".iam.gserviceaccount.com"
    drive = API(session, "https://www.googleapis.com")
    # Check all sharing rights before IAM changes, then reject any conflicting
    # existing repository identity before enabling or creating Cloud resources.
    preview = share_registered_files(drive, plan, email)
    project = API(session, "https://cloudresourcemanager.googleapis.com").call("GET", "/v1/projects/" + project_id)
    spec = federation_spec(project["projectNumber"], repo)
    configure_variables(gh, {"provider": spec["provider"], "service_account": email})
    emit(f"Reusing {len(plan)} registered files; {sum(x['role'] == 'writer' for x in plan)} output writers. No Sheet creation.")
    identity = ensure_identity(session, project_id, repo, emit)
    share_registered_files(drive, plan, email, apply=True)
    configure_variables(gh, identity, apply=True)
    emit("Identity and exact file permissions verified. IAM propagation can take several minutes.")
    # Keep this wait visible and shorter than a minute; the next dispatch must
    # actually authenticate and fetch, rather than assuming propagation finished.
    emit("Waiting 45 seconds for initial identity propagation…")
    time.sleep(45)
    request_id = dispatch_refresh(gh, sha)
    result = wait_for_refresh(gh, request_id, sha, minutes=wait_minutes, emit=emit)
    emit("LIVE SHEETS → PUBLISHING SHEET → VALIDATED JSON → ACTIONS → PAGES: VERIFIED")
    return result
