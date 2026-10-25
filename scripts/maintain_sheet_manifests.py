"""Colab helper: add missing control tabs to active Sheets, preserving source data.

Call with authenticated Sheets/Drive services and the private inventory. No private
inventory or results belong in this public repository. Archive descendants are
reported but never edited. This does not infer a consuming repository.
"""
from datetime import datetime, timezone
import re

SHEET_MIME = "application/vnd.google-apps.spreadsheet"
FOLDER_MIME = "application/vnd.google-apps.folder"

def owner_archive_folder(drive, root, item, execute):
    """One stable source-workbook folder; friendly name changes do not split history."""
    fid = item.get("drive_file_id", item.get("id"))
    suffix = " — " + fid[-8:]
    files, token = [], None
    while True:
        args = dict(q=f"'{root}' in parents and mimeType = '{FOLDER_MIME}' and trashed = false",
                    fields="nextPageToken,files(id,name,parents,appProperties)",
                    pageSize=1000, supportsAllDrives=True, includeItemsFromAllDrives=True)
        if token:
            args["pageToken"] = token
        response = execute(drive.files().list(**args))
        files.extend(response.get("files", []))
        token = response.get("nextPageToken")
        if not token:
            break
    found = [x for x in files if x.get("appProperties", {}).get("jp_source_file_id") == fid
             or (x.get("name", "").endswith(suffix)
                 and x.get("appProperties", {}).get("jp_source_file_id", fid) == fid)]
    if len(found) > 1:
        raise RuntimeError("Ambiguous workbook archive folder")
    title = re.sub(r"[_\s]+", " ", item["name"]).strip()[:110]
    folder = found[0] if found else execute(drive.files().create(
        body={"name": title + suffix, "mimeType": FOLDER_MIME, "parents": [root],
              "appProperties": {"jp_source_file_id": fid}},
        fields="id,name,parents", supportsAllDrives=True))
    proof = execute(drive.files().get(fileId=folder["id"], fields="id,parents,mimeType",
                                     supportsAllDrives=True))
    if proof.get("mimeType") != FOLDER_MIME or root not in proof.get("parents", []):
        raise RuntimeError("Workbook archive folder verification failed")
    return folder["id"]

def is_archived(item, by_id, archive_root, archive_roots=()):
    cursor = item
    seen = set()
    while cursor:
        key = cursor.get("drive_file_id", cursor.get("id"))
        if key in seen:
            raise ValueError("Inventory parent cycle")
        seen.add(key)
        if key in {archive_root, *archive_roots}:
            return True
        raw_name = cursor.get("name", "").upper()
        name = re.sub(r"[_\s]+", " ", raw_name)
        if any(word in name for word in ("ARCHIVE", "SUPERSEDED", "RECYCLE BIN", "BACKUP", "SNAPSHOT", "VERSION HISTORY", "PREVIOUS VERSIONS", "PREVIOUS RECORDS")) or re.match(r"^(?:PRE\d*|POST\d*|FINAL_POST\d*)_", raw_name):
            return True
        parent = cursor.get("parent_drive_id", cursor.get("parent_id"))
        cursor = by_id.get(parent)
    return False

def ensure_controls(items, sheets, drive, archive_root, snapshot_folder, execute, archive_roots=()):
    """Yield one result per workbook; reruns reuse snapshots and existing controls."""
    by_id = {x.get("drive_file_id", x.get("id")): x for x in items}
    for fid, item in sorted(by_id.items()):
        if item.get("mime_type") != SHEET_MIME:
            continue
        result = {"spreadsheet_id": fid, "name": item["name"],
                  "consumer_status": "UNMAPPED_REQUIRES_OWNER_REVIEW"}
        if is_archived(item, by_id, archive_root, archive_roots):
            yield dict(result, status="ARCHIVED_NO_LIVE_CONSUMER_REQUIRED")
            continue
        meta = execute(sheets.spreadsheets().get(spreadsheetId=fid,
                       fields="spreadsheetId,sheets.properties"))
        tabs = {t["properties"]["title"]: t["properties"] for t in meta["sheets"]}
        missing = [x for x in ("00_MANIFEST", "01_VERSION_HISTORY") if x not in tabs]
        if not missing:
            yield dict(result, status="CONTROL_TABS_PRESENT_CONTENT_REVIEW_PENDING")
            continue
        # An exact-ID key makes snapshot recovery idempotent after interruption.
        name = f"PRE_MANIFEST_V000001__{fid}"
        owner_folder = owner_archive_folder(drive, snapshot_folder, item, execute)
        found = execute(drive.files().list(
            q=f"'{owner_folder}' in parents and name = '{name}' and trashed = false",
            fields="files(id,name,parents)", pageSize=100, supportsAllDrives=True,
            includeItemsFromAllDrives=True))["files"]
        if len(found) > 1:
            raise RuntimeError("Ambiguous snapshot; reconcile before retry")
        snapshot = found[0] if found else execute(drive.files().copy(
            fileId=fid, body={"name": name, "parents": [owner_folder]},
            fields="id,name,parents", supportsAllDrives=True))
        proof = execute(drive.files().get(fileId=snapshot["id"], fields="id,parents,mimeType",
                                         supportsAllDrives=True))
        if owner_folder not in proof.get("parents", []) or proof["mimeType"] != SHEET_MIME:
            raise RuntimeError("PRE snapshot verification failed")
        ids = {t["sheetId"] for t in tabs.values()}
        requests = []
        stamp = datetime.now(timezone.utc).isoformat()
        for title in missing:
            sid = next(n for n in range(700123, 701123) if n not in ids)
            ids.add(sid)
            rows = ([['Field', 'Value', 'Guidance'],
                     ['CONTROL_VERSION', 'V000001', 'Structure/control version; preserve data release separately'],
                     ['WORKBOOK_ID', fid, 'Stable ID; update this live object in place'],
                     ['CONSUMING_REPOSITORY', 'UNMAPPED', 'Assign from verified use; never guess from filename'],
                     ['PUBLISHING_MASTER_ID', 'UNMAPPED', 'One derived publishing workbook per consumer repository'],
                     ['SOURCE_DATA_TABS', 'REVIEW_REQUIRED', 'Define one owning source for each feature'],
                     ['PRE_SNAPSHOT_ID', snapshot['id'], 'Restore content into original live ID']]
                    if title == '00_MANIFEST' else
                    [['Version', 'Changed at UTC', 'Scope', 'Change', 'PRE snapshot ID', 'Validation', 'Rollback', 'Data version'],
                     ['V000001', stamp, 'Manifest controls only', 'Added missing control tabs; source cells unchanged',
                      snapshot['id'], 'PRE verified; POST readback required', 'Restore PRE into same live ID', 'UNCHANGED']])
            width = max(map(len, rows))
            requests += [
                {"addSheet": {"properties": {"sheetId": sid, "title": title,
                    "gridProperties": {"rowCount": 100, "columnCount": 8, "frozenRowCount": 1}}}},
                {"updateCells": {"range": {"sheetId": sid, "startRowIndex": 0,
                    "endRowIndex": len(rows), "startColumnIndex": 0, "endColumnIndex": width},
                    "rows": [{"values": [{"userEnteredValue": {"stringValue": str(v)}}
                              for v in row + [''] * (width-len(row))]} for row in rows],
                    "fields": "userEnteredValue"}},
                {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0,
                    "endRowIndex": len(rows), "startColumnIndex": 0, "endColumnIndex": width},
                    "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
                    "fields": "userEnteredFormat"}},
                {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS",
                    "startIndex": 0, "endIndex": width}, "properties": {"pixelSize": 220}, "fields": "pixelSize"}}]
        execute(sheets.spreadsheets().batchUpdate(spreadsheetId=fid, body={"requests": requests}))
        post = execute(sheets.spreadsheets().get(spreadsheetId=fid, fields="spreadsheetId,sheets.properties.title"))
        if not {"00_MANIFEST", "01_VERSION_HISTORY"} <= {x["properties"]["title"] for x in post["sheets"]}:
            raise RuntimeError("Missing control after write")
        yield dict(result, status="MISSING_CONTROLS_ADDED_VERIFIED", snapshot_id=snapshot["id"])
