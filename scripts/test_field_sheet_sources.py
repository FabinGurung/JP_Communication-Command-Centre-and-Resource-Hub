#!/usr/bin/env python3
"""Operational import edge cases using synthetic, non-private records."""
import copy
import json
import unittest
from pathlib import Path
from field_sheet_sources import FieldSourceError, HEADERS, collect, transform

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "ops/control/sheets-actions-publishing.v1.json").read_text())


class ImportTests(unittest.TestCase):
    def spec(self, adapter):
        return copy.deepcopy(next(s for s in CONFIG["field_sources"] if s["adapter"] == adapter))

    def test_unchecked_and_formula_filled_calendar_are_not_absences(self):
        s = self.spec("attendance_checkbox")
        rows = [s["expected_header"], ["2026-10-01", "FALSE"], ["2026-10-02", "TRUE"], ["2026-10-03", ""]]
        actual = transform(s, rows)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0][3:7], ["2026-10-02", "Checked site attendance", "Checked", s["expected_header"][1]])

    def test_statuses_and_atomic_visits_survive_independently(self):
        s = self.spec("attendance_split")
        rows = [s["expected_header"], ["2026-10-01", "SITE CLOSED", "", "2026-10-02", "Site A", "Original note"], ["2026-10-03"]]
        actual = transform(s, rows)
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0][5], "SITE CLOSED")
        self.assertEqual(actual[1][3:8], ["2026-10-02", "Site visit", "Recorded visit", "Site A", "Original note"])

    def test_seeded_expense_ids_are_not_real_expenses(self):
        s = self.spec("expenses_rich")
        unused = ["EXP-000001"] + [""] * 12 + ["UNUSED"]
        real = ["EXP-000002", "NA", "Reported expense", "", "150", "", "", "Date not recorded"]
        actual = transform(s, [s["expected_header"], unused, real])
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0][3], "NA")
        self.assertEqual(actual[0][6], "150")

    def test_exact_repeated_progress_retains_both_source_pointers(self):
        a = self.spec("progress")
        b = copy.deepcopy(a)
        b["workbook_id"] = "SECOND_SOURCE"
        row = ["2026-10-01", "Site A", "Reported", "Work A", "2 units", "REUSED-ID", "PRJ-000007", ""]
        data = {(a["workbook_id"], a["tab"]): [a["expected_header"], row],
                (b["workbook_id"], b["tab"]): [b["expected_header"], row, row[:3] + ["Different work"] + row[4:]]}
        class API:
            def read(self, fid, tab):
                return data[fid, tab]
        joined, _ = collect(API(), [a, b], {"PRJ-000007": a["company"]})
        rows = joined["site_progress"]
        self.assertEqual(len(rows), 3)
        self.assertIn("SECOND_SOURCE", rows[1][10])
        self.assertIn("reused for different reports", rows[2][9])
        self.assertNotEqual(rows[1][0], rows[2][0])

    def test_unparsed_measurements_stay_blank(self):
        s = self.spec("measurement_review")
        row = ["REC-1", "PRJ-000007", "Site", "", "", "", "Original evidence", "", "", "", "", ""] + [""] * 7 + ["ARCHIVED_SOURCE_NOT_SEMANTIC_QTO_PARSED"]
        actual = transform(s, [s["expected_header"], row])
        self.assertEqual(actual[0][4:8], ["", "", "", ""])
        self.assertEqual(actual[0][8], "ARCHIVED_SOURCE_NOT_SEMANTIC_QTO_PARSED")


if __name__ == "__main__":
    unittest.main()
