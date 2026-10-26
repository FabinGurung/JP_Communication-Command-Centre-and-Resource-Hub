#!/usr/bin/env python3
"""Source preservation, three-category projection and privacy failure modes."""
import copy
import hashlib
import unittest
from notification_projection import NotificationError, compile_notifications, validate_public


class NotificationTests(unittest.TestCase):
    def setUp(self):
        # More than 3,000 words: no provider text is embedded in this repository.
        self.original = "planner " * 3000 + "Add curing water today. Arrange bricks. Check the joints."
        self.sha = hashlib.sha256(self.original.encode()).hexdigest()
        self.policy = {"source_sheet_url": "https://docs.google.com/spreadsheets/d/synthetic/edit",
                       "admitted_sources": {"SYN-1": {"sha256": self.sha, "version": "V000001"}}}
        self.sources = [["Source ID", "Project ID", "Site Reference", "Project", "Company", "Date", "Origin", "Source Message", "Saved Original", "Source SHA256", "Source Version"],
                        ["SYN-1", "PRJ-000020", "P020", "Synthetic Site", "Company", "2026-10-26", "Slack", "https://jp09.slack.com/archives/C123/p1792979252137289", "https://drive.google.com/file/d/synthetic/view", self.sha, "V000001"]]
        self.headers = ["Notification ID", "Notice ID", "Source ID", "Project ID", "Site Reference", "Project", "Company", "Category", "Instruction", "Source Message", "Saved Original", "Source SHA256", "Source Version", "Source Quote", "Display Order", "Review State", "Publish"]
        self.rows = [self.headers]
        for i, (category, text) in enumerate(zip(("Work", "Materials", "Supervision"), ("Add curing water today.", "Arrange bricks.", "Check the joints.")), 1):
            self.rows.append([f"N-{i}", "synthetic-notice", "SYN-1", "PRJ-000020", "P020", "Synthetic Site", "Company", category, text, self.sources[1][7], self.sources[1][8], self.sha, "V000001", text, str(i), "Reviewed", "TRUE"])

    def run_projection(self):
        return compile_notifications(self.sources, self.rows, self.policy, {"SYN-1": self.original}, {"PRJ-000020"})

    def test_long_original_three_categories_and_no_raw_text(self):
        result = self.run_projection()
        self.assertEqual(result["count"], 3)
        self.assertEqual({r["category"] for r in result["items"]}, {"Work", "Materials", "Supervision"})
        self.assertNotIn("source_quote", result["items"][0])
        self.assertNotIn(self.original, str(result))
        self.assertFalse(result["automatic_provider_polling"])

    def test_duplicate_id_rejected(self):
        self.rows[2][0] = self.rows[1][0]
        with self.assertRaisesRegex(NotificationError, "DUPLICATE"):
            self.run_projection()

    def test_unknown_project_rejected(self):
        self.rows[1][3] = "PRJ-999999"
        with self.assertRaisesRegex(NotificationError, "JOIN_MISMATCH"):
            self.run_projection()

    def test_modified_original_stops_publication(self):
        self.original += " changed"
        with self.assertRaisesRegex(NotificationError, "HASH_MISMATCH"):
            self.run_projection()

    def test_untraceable_quote_rejected(self):
        self.rows[1][13] = "An invented quantity"
        with self.assertRaisesRegex(NotificationError, "QUOTE_NOT_IN_ORIGINAL"):
            self.run_projection()

    def test_draft_and_withdrawn_rows_not_published(self):
        self.rows[1][-2] = "Draft"
        self.rows[2][-2] = "Withdrawn"
        self.assertEqual(self.run_projection()["count"], 1)

    def test_new_source_version_requires_admission(self):
        self.rows[1][12] = "V000002"
        with self.assertRaisesRegex(NotificationError, "VERSION_MISMATCH"):
            self.run_projection()

    def test_unknown_public_fields_rejected(self):
        result = self.run_projection()
        result["items"][0]["original_text"] = "must remain private"
        with self.assertRaisesRegex(NotificationError, "PUBLIC_ITEM_INVALID"):
            validate_public(result, self.policy)

    def test_source_urls_cannot_execute_code(self):
        self.sources[1][7] = self.rows[1][9] = "javascript:alert(1)"
        with self.assertRaisesRegex(NotificationError, "ORIGIN_URL_INVALID"):
            self.run_projection()


if __name__ == "__main__":
    unittest.main()
