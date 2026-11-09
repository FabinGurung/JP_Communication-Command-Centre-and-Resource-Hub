"""Validate curated Sheet rows and produce the public Notification Center feed.

Semantic cleanup happens after a user-authorized source read, not in a browser
or an unattended regex summarizer. Original text/quotes never enter this output.
"""
import hashlib
import re
from datetime import date
from urllib.parse import urlsplit


class NotificationError(RuntimeError):
    pass


def records(rows, key):
    if not rows:
        raise NotificationError("NOTIFICATION_HEADER_MISSING")
    headers = [re.sub(r"[^a-z0-9]+", "_", str(x).lower()).strip("_") for x in rows[0]]
    if key not in headers or len(headers) != len(set(headers)):
        raise NotificationError("NOTIFICATION_HEADER_INVALID")
    out = []
    for values in rows[1:]:
        if not any(str(x).strip() for x in values):
            continue
        if len(values) > len(headers):
            raise NotificationError("NOTIFICATION_ROW_TOO_WIDE")
        row = dict(zip(headers, [str(x).strip() for x in values] + [""] * (len(headers) - len(values))))
        out.append(row)
    keys = [r[key] for r in out]
    if not all(keys) or len(keys) != len(set(keys)):
        raise NotificationError("NOTIFICATION_DUPLICATE_OR_MISSING_ID")
    return out


def original_file_id(url):
    u = urlsplit(url)
    match = re.fullmatch(r"/file/d/([\w-]+)/view", u.path)
    if u.scheme != "https" or u.netloc != "drive.google.com" or not match:
        raise NotificationError("NOTIFICATION_ORIGINAL_URL_INVALID")
    return match[1]


def check_origin(provider, url):
    u = urlsplit(url)
    if provider == "Chat" and not url:
        return  # A chat without a share link still has its archived original.
    allowed = (provider == "Slack" and u.netloc.endswith(".slack.com") and re.fullmatch(r"/archives/[A-Z0-9]+/p[0-9]+", u.path)
               or provider == "Discord" and u.netloc == "discord.com" and u.path.startswith("/channels/")
               or provider == "Chat" and u.netloc == "chatgpt.com" and u.path.startswith("/c/"))
    if u.scheme != "https" or not allowed:
        raise NotificationError("NOTIFICATION_ORIGIN_URL_INVALID")


def compile_notifications(source_rows, instruction_rows, policy, original_texts=None, project_ids=None, mode="REVIEWED_SHEET_SNAPSHOT"):
    sources = {r["source_id"]: r for r in records(source_rows, "source_id")}
    admitted = policy["admitted_sources"]
    public_sources, items = {}, []
    for row in records(instruction_rows, "notification_id"):
        if row.get("publish", "").upper() != "TRUE" or row.get("review_state") != "Reviewed":
            continue
        source_id = row.get("source_id")
        source = sources.get(source_id)
        grant = admitted.get(source_id)
        if source is None or grant is None:
            raise NotificationError("NOTIFICATION_SOURCE_NOT_ADMITTED")
        if any(grant.get(k, value) != value for k, value in (("source_url", source.get("source_message")), ("drive_source_url", source.get("saved_original")), ("project_id", source.get("project_id")))):
            raise NotificationError("NOTIFICATION_SOURCE_POINTER_CHANGED")
        if (row.get("source_sha256") != source.get("source_sha256") or row.get("source_sha256") != grant["sha256"]
                or row.get("source_version") != source.get("source_version") or row.get("source_version") != grant["version"]):
            raise NotificationError("NOTIFICATION_SOURCE_VERSION_MISMATCH")
        if not re.fullmatch(r"[a-f0-9]{64}", row["source_sha256"]):
            raise NotificationError("NOTIFICATION_DIGEST_INVALID")
        if any(row.get(k) != source.get(k) for k in ("project_id", "site_reference", "project", "company", "source_message", "saved_original")):
            raise NotificationError("NOTIFICATION_SOURCE_JOIN_MISMATCH")
        if project_ids is not None and row["project_id"] not in project_ids:
            raise NotificationError("NOTIFICATION_PROJECT_UNKNOWN")
        if not re.fullmatch(r"PRJ-[0-9]{6}", row["project_id"]) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,79}", row.get("notice_id", "")):
            raise NotificationError("NOTIFICATION_ID_INVALID")
        check_origin(source["origin"], row["source_message"])
        original_file_id(row["saved_original"])
        try:
            date.fromisoformat(source["date"])
            if row.get("due_date"):
                date.fromisoformat(row["due_date"])
            order = int(row["display_order"])
            if order < 1:
                raise ValueError()
        except (ValueError, KeyError):
            raise NotificationError("NOTIFICATION_DATE_OR_ORDER_INVALID") from None
        if row.get("category") not in {"Work", "Materials", "Supervision"} or not row.get("instruction") or len(row["instruction"]) > 1200:
            raise NotificationError("NOTIFICATION_INSTRUCTION_INVALID")
        if not row.get("source_quote"):
            raise NotificationError("NOTIFICATION_QUOTE_MISSING")
        if original_texts is not None:
            original = original_texts.get(source_id)
            if original is None or hashlib.sha256(original.encode("utf-8")).hexdigest() != row["source_sha256"]:
                raise NotificationError("NOTIFICATION_ORIGINAL_HASH_MISMATCH")
            if row["source_quote"] not in original:
                raise NotificationError("NOTIFICATION_QUOTE_NOT_IN_ORIGINAL")
        public_sources[source_id] = {"source_id": source_id, "provider": source["origin"], "date_npt": source["date"],
                                     "source_url": source["source_message"], "drive_source_url": source["saved_original"],
                                     "version": source["source_version"], "sha256": source["source_sha256"]}
        # Explicit allowlist: no raw original, private quotes, author email or bill evidence.
        items.append({"notification_id": row["notification_id"], "notice_id": row["notice_id"], "source_id": source_id,
                      "project_id": row["project_id"], "site_reference": row["site_reference"], "project_name": row["project"],
                      "company": row["company"], "category": row["category"], "instruction": row["instruction"],
                      "quantity": row.get("quantity", ""), "unit": row.get("unit", ""), "due_date": row.get("due_date", ""),
                      "detail_state": row.get("detail_state", ""), "display_order": order})
    output = {"schema_version": "1.0.0", "kind": "SOURCE_LINKED_SITE_NOTIFICATIONS", "mode": mode,
              "source_sheet_url": policy["source_sheet_url"], "originals_in_public_bundle": False,
              "automatic_provider_polling": False, "count": len(items), "sources": list(public_sources.values()), "items": items}
    validate_public(output, policy)
    return output


def validate_public(payload, policy):
    if (payload.get("kind") != "SOURCE_LINKED_SITE_NOTIFICATIONS" or payload.get("count") != len(payload.get("items", []))
            or payload.get("originals_in_public_bundle") is not False or payload.get("automatic_provider_polling") is not False
            or payload.get("source_sheet_url") != policy["source_sheet_url"]):
        raise NotificationError("NOTIFICATION_PUBLIC_CONTRACT_INVALID")
    expected = {"notification_id", "notice_id", "source_id", "project_id", "site_reference", "project_name", "company",
                "category", "instruction", "quantity", "unit", "due_date", "detail_state", "display_order"}
    allowed_source_fields = {"source_id", "provider", "date_npt", "source_url", "drive_source_url", "version", "sha256"}
    source_ids, seen, notices = set(), set(), {}
    for source in payload["sources"]:
        if set(source) != allowed_source_fields or source["source_id"] in source_ids:
            raise NotificationError("NOTIFICATION_PUBLIC_SOURCE_INVALID")
        grant = policy["admitted_sources"].get(source["source_id"])
        if grant is None or source["sha256"] != grant["sha256"] or source["version"] != grant["version"]:
            raise NotificationError("NOTIFICATION_PUBLIC_SOURCE_UNADMITTED")
        if any(grant.get(k, source[k]) != source[k] for k in ("source_url", "drive_source_url")):
            raise NotificationError("NOTIFICATION_PUBLIC_SOURCE_POINTER_CHANGED")
        check_origin(source["provider"], source["source_url"])
        original_file_id(source["drive_source_url"])
        source_ids.add(source["source_id"])
    for item in payload["items"]:
        if (set(item) != expected or item["source_id"] not in source_ids or item["notification_id"] in seen
                or item["category"] not in {"Work", "Materials", "Supervision"} or not item["instruction"]):
            raise NotificationError("NOTIFICATION_PUBLIC_ITEM_INVALID")
        identity = (item["source_id"], item["project_id"], item["site_reference"], item["project_name"])
        if item["notice_id"] in notices and notices[item["notice_id"]] != identity:
            raise NotificationError("NOTIFICATION_NOTICE_JOIN_INVALID")
        notices[item["notice_id"]] = identity
        seen.add(item["notification_id"])
