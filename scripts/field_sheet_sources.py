#!/usr/bin/env python3
"""Read existing operational Sheets into private, human-readable joined tables.

No source writes, workbook creation, private disk output or public admission happen
here. Formula-filled templates are not records; unchecked boxes are not absences.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timedelta


class FieldSourceError(ValueError):
    """Only safe error codes may reach workflow logs."""


HEADERS = {
    "company_contacts": ["Contact ID", "Company", "Name", "Phone", "Role", "Projects", "Verification", "Source Sheet", "Source Tab", "Source Row"],
    "material_movements": ["Movement ID", "Company", "Date", "Project ID", "Site", "Material", "Movement", "Quantity", "Unit", "Remarks", "Source Sheet", "Source Tab", "Source Row"],
    "site_progress": ["Progress ID", "Company", "Date", "Project ID", "Site", "Status", "Work and Location", "Quantity or Note", "Original Event ID", "Review State", "Source Sheet", "Source Tab", "Source Row"],
    "site_readiness": ["Readiness ID", "Company", "Date", "Project ID", "Site", "Work ID", "Activity", "Location", "Materials", "Manpower", "PPE", "PPE Responsibility", "Work Briefing", "Tools", "Preconditions", "Overall Readiness", "Execution Status", "Blocker", "Responsible", "Source Sheet", "Source Tab", "Source Row"],
    "site_attendance": ["Attendance ID", "Company", "Person", "Date", "Record Type", "Reported Status", "Project or Site", "Note", "Source Sheet", "Source Tab", "Source Row"],
    "site_expenses": ["Expense ID", "Company", "Person", "Date", "Item", "Project or Site", "Amount NPR", "Hardware", "Bill Photo", "Remarks", "Review State", "Source Sheet", "Source Tab", "Source Row"],
    "vendor_payments": ["Payment Summary ID", "Company", "Vendor or Purpose", "Amount NPR", "QR NPR", "Discount NPR", "Source Sheet", "Source Tab", "Source Row"],
    "source_review_queue": ["Record ID", "Kind", "Project or Thread", "Human Description", "Quantity", "Unit", "Rate", "Amount", "Review State", "Original Message ID", "Evidence Link", "Source Sheet", "Source Tab", "Source Row"],
}
ERRORS = {"#REF!", "#N/A", "#VALUE!", "#ERROR!", "#DIV/0!", "#NAME?", "#NUM!"}


def text(v):
    return str(v).strip()


def date(value):
    value = text(value)
    if not value:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T.*)?", value):
        return value[:10]
    if re.fullmatch(r"\d{5}(?:\.0+)?", value):
        return (datetime(1899, 12, 30) + timedelta(days=float(value))).date().isoformat()
    for pattern in ("%d-%b-%Y", "%d-%b-%y", "%d %b %Y", "%m/%d/%Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    # An unknown or NA source date remains unknown, rather than today's date.
    return value


def header(v):
    return re.sub(r"[^a-z0-9]+", "_", text(v).lower()).strip("_")


def source_url(spec):
    return "https://docs.google.com/spreadsheets/d/" + spec["workbook_id"] + "/edit"


def row_id(spec, number, suffix=""):
    raw = "|".join([spec["workbook_id"], spec["tab"], str(number), suffix])
    return "SRC-" + hashlib.sha256(raw.encode()).hexdigest()[:20].upper()


def transform(spec, rows):
    kind = spec["adapter"]
    table = spec["table"]
    if table not in HEADERS or not rows:
        raise FieldSourceError("FIELD_SOURCE_HEADER_MISSING")
    company, person = spec.get("company", ""), spec.get("person", "")
    origin = source_url(spec)
    offset = 1 if kind == "vendor_summary" else 0
    if len(rows) <= offset:
        raise FieldSourceError("FIELD_SOURCE_HEADER_MISSING")
    actual = [header(v) for v in rows[offset]]
    expected = spec["expected_header"]
    if actual[:len(expected)] != expected:
        raise FieldSourceError("FIELD_SOURCE_LAYOUT_CHANGED")
    result = []

    def add(values, number):
        values = [text(v) for v in values]
        if any(v in ERRORS for v in values):
            raise FieldSourceError("FIELD_SOURCE_CELL_ERROR")
        record = values + [origin, spec["tab"], str(number)]
        if len(record) != len(HEADERS[table]):
            raise FieldSourceError("FIELD_ADAPTER_WIDTH_INVALID")
        result.append(record)

    for number, raw in enumerate(rows[offset + 1:], offset + 2):
        r = [text(v) for v in raw] + [""] * max(0, 30 - len(raw))
        if kind == "contacts":
            if not r[0]:
                continue
            if not re.fullmatch(r"(?:FBL|REB)-CON-\d{6}", r[6]):
                raise FieldSourceError("CONTACT_STABLE_ID_MISSING")
            add([r[6], company, *r[:5]], number)  # Notes in F are deliberately excluded.
        elif kind == "materials":
            if not r[0] or not any(r[1:9]):
                continue
            add([r[0], company, date(r[1]), *r[2:9]], number)
        elif kind == "progress":
            if not r[0] or not r[1] or not any(r[2:5]):
                continue
            add([row_id(spec, number), company, date(r[0]), r[6], r[1], r[2], r[3], r[4], r[5], "Reported source record"], number)
        elif kind == "readiness":
            if not r[0] or not r[1] or not any(r[2:5]):
                continue
            add([row_id(spec, number), company, date(r[0]), r[19], r[1], *r[2:16]], number)
        elif kind == "attendance_split":
            if r[0] and r[1]:
                add([row_id(spec, number, "STATUS"), company, person, date(r[0]), "Daily status", r[1], "", ""], number)
            if r[3] and r[4]:
                add([row_id(spec, number, "VISIT"), company, person, date(r[3]), "Site visit", "Recorded visit", r[4], r[5]], number)
        elif kind == "attendance_checkbox":
            for index, value in enumerate(raw[1:], 1):
                if text(value).upper() in {"TRUE"} and r[0]:
                    add([row_id(spec, number, str(index)), company, person, date(r[0]), "Checked site attendance", "Checked", rows[0][index], "Unchecked cells do not imply absence."], number)
        elif kind == "expenses_rich":
            if not r[4] or not (r[1] or r[2]) or r[13].upper() == "UNUSED":
                continue
            add([r[0] or row_id(spec, number), company, person, date(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[13]], number)
        elif kind == "expenses_simple":
            if not r[2] or not (r[0] or r[1] or r[3]):
                continue
            add([row_id(spec, number), company, person, date(r[0]), "See original remarks", r[1], r[2], "", "", r[3], "Reported; original evidence retained in source"], number)
        elif kind == "vendor_summary":
            if not re.fullmatch(r"\d+(?:\.0+)?", r[0]) or not r[1]:
                continue
            add([row_id(spec, number), company, r[1], *r[2:5]], number)
        elif kind == "supplier_review":
            if not any(r[i] for i in (1, 16, 17, 18, 19, 20)):
                continue
            add([row_id(spec, number), "Supplier evidence", r[8], r[1], "", "", "", r[5], r[7] or "Not reviewed", r[19], r[17]], number)
        elif kind == "measurement_review":
            if not r[0]:
                continue
            add([r[0], "Measurement evidence", r[1] or r[2], r[6], r[7], r[8], r[9], r[10], r[19], r[14], r[17]], number)
        else:
            raise FieldSourceError("UNREVIEWED_FIELD_ADAPTER")
    return result


def collect(api, specs, project_companies=None):
    joined = {name: [values[:]] for name, values in HEADERS.items()}
    snapshots = []
    seen_inputs = set()
    for spec in specs:
        key = (spec["workbook_id"], spec["tab"])
        if key in seen_inputs:
            raise FieldSourceError("DUPLICATE_FIELD_SOURCE")
        seen_inputs.add(key)
        rows = api.read(*key)
        snapshots.append((spec["workbook_id"], spec["tab"], copy.deepcopy(rows)))
        joined[spec["table"]].extend(transform(spec, rows))
    # Legacy progress IDs are reused in several rows. They are evidence, not a
    # reliable primary key. Keep distinct reports, collapse only exact matching
    # facts with the same old ID, and retain every original source pointer.
    progress, event_facts = {}, {}
    for r in joined["site_progress"][1:]:
        if project_companies and r[3] in project_companies:
            r[1] = project_companies[r[3]]
        key = tuple(r[1:9])
        if not r[8]:
            key += (r[0],)
        if key in progress:
            existing = progress[key]
            for index in (10, 11, 12):
                existing[index] += "\n" + r[index]
            existing[9] = "Exact repeated report; all original source pointers retained"
        else:
            progress[key] = r
        if r[8]:
            event_facts.setdefault(r[8], set()).add(key)
    for r in progress.values():
        if r[8] and len(event_facts[r[8]]) > 1:
            r[9] += "; old event ID is reused for different reports, kept separate"
    joined["site_progress"] = [HEADERS["site_progress"][:], *progress.values()]
    for name, rows in joined.items():
        ids = [r[0] for r in rows[1:]]
        if len(ids) != len(set(ids)) or any(not v for v in ids):
            raise FieldSourceError("DUPLICATE_FIELD_RECORD")
    return joined, snapshots


def verify_sources(api, snapshots):
    for fid, tab, values in snapshots:
        if api.read(fid, tab) != values:
            raise FieldSourceError("FIELD_SOURCE_CHANGED_DURING_READ")


def public_contacts(rows, baseline, mode):
    if not rows or rows[0] != HEADERS["company_contacts"]:
        raise FieldSourceError("JOINED_CONTACT_HEADER_INVALID")
    live = {r[0]: r for r in rows[1:]}
    output = copy.deepcopy(baseline)
    output["refresh_mode"] = mode
    output["published_records"] = 0
    for directory in output["directories"]:
        retained = []
        for before in directory["records"]:
            r = live.get(before["contact_id"])
            if r is None:
                continue
            # Reusing an admitted ID for somebody else requires explicit review.
            if r[2] != before["name"] or r[1] != directory["company"]:
                raise FieldSourceError("CONTACT_IDENTITY_CHANGE_REQUIRES_REVIEW")
            phone = re.sub(r"[\s().-]", "", r[3])
            if re.fullmatch(r"\d{10}", phone):
                phone = "+977" + phone
            if not re.fullmatch(r"\+977\d{10}", phone):
                raise FieldSourceError("PUBLIC_CONTACT_PHONE_INVALID")
            retained.append(dict(before, phone=phone, role=r[4], projects=r[5], verification=r[6], source_row=int(r[9])))
        directory["records"] = retained
        directory["source_record_count"] = len(retained)
        output["published_records"] += len(retained)
    validate_contacts(output, baseline)
    return output


def validate_contacts(payload, baseline):
    admitted = {r["contact_id"]: (r, d) for d in baseline["directories"] for r in d["records"]}
    if set(payload) != set(baseline) or payload.get("withheld_fields") != ["Notes"]:
        raise FieldSourceError("PUBLIC_CONTACT_CONTRACT_INVALID")
    if payload.get("projection_id") != baseline["projection_id"] or payload.get("source_count") != 2 or len(payload.get("directories", [])) != 2:
        raise FieldSourceError("PUBLIC_CONTACT_CONTRACT_INVALID")
    if payload.get("refresh_mode") not in {"REVIEWED_SHEET_SNAPSHOT", "ACTIONS_JOINED_SHEET_READBACK"}:
        raise FieldSourceError("PUBLIC_CONTACT_MODE_INVALID")
    seen = set()
    for d in payload["directories"]:
        if set(d) != set(baseline["directories"][0]) or d["source_record_count"] != len(d["records"]):
            raise FieldSourceError("PUBLIC_CONTACT_COUNT_INVALID")
        for r in d["records"]:
            pair = admitted.get(r.get("contact_id"))
            if not pair or r["contact_id"] in seen:
                raise FieldSourceError("UNADMITTED_PUBLIC_CONTACT")
            before, owner = pair
            if (set(r) != set(before) or r["name"] != before["name"] or d["source_key"] != owner["source_key"]
                    or d["company"] != owner["company"] or d["source_tab"] != owner["source_tab"]
                    or not re.fullmatch(r"\+977\d{10}", r["phone"]) or not isinstance(r["source_row"], int)):
                raise FieldSourceError("PUBLIC_CONTACT_ROW_INVALID")
            seen.add(r["contact_id"])
    if payload["published_records"] != len(seen):
        raise FieldSourceError("PUBLIC_CONTACT_COUNT_INVALID")
