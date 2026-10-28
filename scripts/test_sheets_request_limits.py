#!/usr/bin/env python3
"""Exercise quota timing with a virtual clock; no real waits or Google calls."""
import contextlib
import io
import json
import unittest
from unittest.mock import Mock, patch
from sync_sheets_to_pages import Google, SheetsRequestLimiter, SyncError, safe_quota_details


class Clock:
    def __init__(self):
        self.now = 0.0
        self.waits = []

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.waits.append(seconds)
        self.now += seconds


class RequestLimitTests(unittest.TestCase):
    def client(self):
        clock = Clock()
        client = Google.__new__(Google)
        client.session = Mock()
        client.limiter = SheetsRequestLimiter(clock=clock.time, sleep=clock.sleep)
        client.sleep = clock.sleep
        return client, clock

    def response(self, status=200, retry_after="0"):
        response = Mock(status_code=status, ok=status == 200, headers={"Retry-After": retry_after})
        response.json.return_value = {"error": {"message": "PRIVATE_CELL_CONTENT", "details": [{"metadata": {
            "service": "sheets.googleapis.com", "quota_limit": "ReadRequestsPerMinutePerUser",
            "quota_limit_value": "60", "private_field": "PRIVATE_CELL_CONTENT"}}]}}
        return response

    def test_every_sliding_minute_stays_below_service_account_quota(self):
        clock = Clock()
        limiter = SheetsRequestLimiter(clock=clock.time, sleep=clock.sleep)
        sent = []
        for _ in range(150):
            limiter.wait()
            sent.append(clock.time())
        for begin in sent:
            self.assertLessEqual(sum(begin <= t < begin + 60 for t in sent), 49)
        self.assertEqual(sent[0], 0)

    def test_actual_google_transport_paces_repeated_sheet_reads(self):
        client, clock = self.client()
        client.session.request.return_value = self.response()
        for _ in range(61):
            client.request("GET", "https://sheets.googleapis.com/v4/spreadsheets/test")
        self.assertEqual(clock.time(), 75)

    def test_drive_requests_do_not_consume_sheet_throttle_slots(self):
        client, clock = self.client()
        client.session.request.return_value = self.response()
        for _ in range(10):
            client.request("GET", "https://www.googleapis.com/drive/v3/files/test")
        self.assertEqual(clock.waits, [])

    def test_quota_retry_honors_retry_after_and_never_logs_body(self):
        client, clock = self.client()
        client.session.request.side_effect = [self.response(429, "60"), self.response()]
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch("sync_sheets_to_pages.random.random", return_value=0):
            client.request("GET", "https://sheets.googleapis.com/v4/spreadsheets/test")
        self.assertGreaterEqual(clock.time(), 60)
        self.assertIn("ReadRequestsPerMinutePerUser", output.getvalue())
        self.assertNotIn("PRIVATE_CELL_CONTENT", output.getvalue())

    def test_permanent_quota_failure_has_bounded_retries_and_safe_error(self):
        client, clock = self.client()
        client.session.request.return_value = self.response(429)
        with contextlib.redirect_stdout(io.StringIO()), patch("sync_sheets_to_pages.random.random", return_value=0):
            with self.assertRaisesRegex(SyncError, "GOOGLE_HTTP_429"):
                client.request("GET", "https://sheets.googleapis.com/v4/spreadsheets/test")
        self.assertEqual(client.session.request.call_count, 8)
        self.assertLess(clock.time(), 240)

    def archive_client(self, **metadata):
        client = Google.__new__(Google)
        client.snapshot_history_id = "PINNED_ARCHIVE"
        client.call = Mock(return_value={"id": "PINNED_ARCHIVE", "mimeType": "application/x-ndjson", **metadata})
        response = Mock(content=(json.dumps({"type": "header", "format": "JP_PUBLISHING_RESTORE_HISTORY_V1",
                                             "publishing_workbook_id": "MASTER"}) + "\n").encode(),
                        headers={"ETag": '"original"'})
        client.request = Mock(return_value=response)
        return client

    def test_file_scoped_archive_accepts_hidden_parent_without_broadening_access(self):
        client = self.archive_client()
        raw, etag = client.archive_state("MASTER", "DEDICATED_FOLDER")
        self.assertEqual(etag, '"original"')
        self.assertIn(b"MASTER", raw)
        self.assertTrue(all(c.args[0] == "GET" for c in client.call.call_args_list + client.request.call_args_list))

    def test_visible_wrong_parent_or_wrong_file_id_is_rejected(self):
        for metadata in [{"parents": ["WRONG_FOLDER"]}, {"id": "DIFFERENT_FILE"}]:
            client = self.archive_client(**metadata)
            with self.assertRaisesRegex(SyncError, "DESTINATION_INVALID"):
                client.archive_state("MASTER", "DEDICATED_FOLDER")
            client.request.assert_not_called()

    def test_missing_conditional_token_or_wrong_master_stops_archive_preflight(self):
        client = self.archive_client()
        client.request.return_value.headers = {}
        with self.assertRaisesRegex(SyncError, "CONDITIONAL_WRITE_TOKEN_MISSING"):
            client.archive_state("MASTER", "DEDICATED_FOLDER")
        client = self.archive_client()
        with self.assertRaisesRegex(SyncError, "HEADER_INVALID"):
            client.archive_state("DIFFERENT_MASTER", "DEDICATED_FOLDER")


if __name__ == "__main__":
    unittest.main()
