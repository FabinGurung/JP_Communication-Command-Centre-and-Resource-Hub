"""Small, read-only Sheets API client for an Actions-issued OAuth token."""
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def records(rows, key, *required):
    if not rows:
        raise ValueError(f"Missing table: {key}")
    headers = [re.sub(r"[^a-z0-9]+", "_", str(x).lower()).strip("_") for x in rows[0]]
    if len(headers) != len(set(headers)) or not {key, *required}.issubset(headers):
        raise ValueError(f"Invalid table headers: {key}")
    seen = set()
    for source in rows[1:]:
        values = [str(x if x is not None else "").strip() for x in source]
        if not any(values):
            continue
        if len(values) > len(headers):
            raise ValueError(f"Unexpected columns: {key}")
        row = dict(zip(headers, values + [""] * (len(headers) - len(values))))
        if not row[key] or row[key] in seen:
            raise ValueError(f"Blank or duplicate key: {key}")
        seen.add(row[key])
        yield row


def read_all(sources, token):
    grouped = defaultdict(list)
    for key, (book, tab) in sources.items():
        grouped[book].append((key, tab))
    tables = {}
    for book, entries in grouped.items():
        query = urlencode({"ranges": ["'" + tab.replace("'", "''") + "'" for _, tab in entries],
                           "valueRenderOption": "UNFORMATTED_VALUE"}, doseq=True)
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{book}/values:batchGet?{query}"
        try:
            with urlopen(Request(url, headers={"Authorization": f"Bearer {token}"}), timeout=35) as response:
                ranges = json.load(response)["valueRanges"]
        except (HTTPError, URLError, TimeoutError) as error:
            code = getattr(error, "code", type(error).__name__)
            raise RuntimeError(f"Sheets read failed ({code}) for {', '.join(key for key, _ in entries)}") from None
        if len(ranges) != len(entries):
            raise RuntimeError("Incomplete Sheets response")
        for (key, _), data in zip(entries, ranges, strict=True):
            tables[key] = data.get("values", [])
    return tables


def load_tables(sources, fixture):
    if fixture:
        if os.getenv("GITHUB_EVENT_NAME") in {"push", "schedule", "workflow_dispatch"}:
            raise RuntimeError("Fixture mode cannot run in a publishing event")
        return json.loads(fixture.read_text(encoding="utf-8")), "Fixture preview"
    token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("A read-only Google Actions connection is required")
    tables = read_all(sources, token)
    if read_all(sources, token) != tables:
        raise RuntimeError("Source Sheets changed during publication; retry")
    npt = timezone(timedelta(hours=5, minutes=45))
    return tables, datetime.now(npt).isoformat(timespec="minutes")
