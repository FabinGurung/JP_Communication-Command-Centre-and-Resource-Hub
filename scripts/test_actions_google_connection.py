#!/usr/bin/env python3
"""Offline tests of setup boundaries; these are not a live Google connection."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from connect_actions_google import (
    ACCOUNT_ID, API, BRANCH, ConnectionError, REPOSITORY, access_plan,
    add_identity_binding, configure_variables, dispatch_refresh, federation_spec,
    find_refresh_run, share_registered_files, verify_public_receipt,
)

ROOT = Path(__file__).resolve().parents[1]


class SetupBoundaries(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / "ops/control/sheets-actions-publishing.v1.json").read_text())

    def test_registered_plan_has_no_duplicates_inactive_sources_or_folder_grants(self):
        plan = access_plan(self.cfg)
        ids = [r["file_id"] for r in plan]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sum(r["role"] == "writer" for r in plan), 2)
        self.assertNotIn(self.cfg["previous_versions_folder_id"], ids)
        for s in self.cfg["sources"].values():
            if s.get("read_mode") == "EMPTY_TEMPLATE_NOT_CONNECTED":
                self.assertNotIn(s["workbook_id"], ids)
        # The original message is a file reader, not a broad channel/folder grant.
        self.assertTrue(any("integrity verification" in " ".join(r["purposes"]) for r in plan))

    def test_changed_configuration_cannot_make_source_a_writer(self):
        self.cfg["previous_versions_file_id"] = next(iter(self.cfg["sources"].values()))["workbook_id"]
        with self.assertRaisesRegex(ConnectionError, "COLLISION"):
            access_plan(self.cfg)

    def test_untrusted_original_host_rejected(self):
        next(iter(self.cfg["notification_policy"]["admitted_sources"].values()))["drive_source_url"] = "https://attacker.test/file/d/123456789012/view"
        with self.assertRaisesRegex(ConnectionError, "ORIGINAL_DRIVE_URL_INVALID"):
            access_plan(self.cfg)

    def test_federation_uses_immutable_repo_owner_and_exact_branch(self):
        spec = federation_spec("123456", {"id": 777, "owner": {"id": 888}, "full_name": REPOSITORY})
        condition = spec["body"]["attributeCondition"]
        self.assertIn("assertion.repository_id == '777'", condition)
        self.assertIn("assertion.repository_owner_id == '888'", condition)
        self.assertIn("assertion.ref == 'refs/heads/" + BRANCH + "'", condition)
        self.assertNotIn("assertion.repository ==", condition)

    def test_iam_merge_preserves_conditions_etag_and_is_idempotent(self):
        old = {"version": 3, "etag": "unchanged", "bindings": [{"role": "roles/viewer", "members": ["user:owner@example.test"]},
                {"role": "roles/iam.workloadIdentityUser", "members": ["existing"], "condition": {"expression": "false", "title": "retained"}}]}
        original = copy.deepcopy(old)
        result = add_identity_binding(old, "new-principal")
        self.assertEqual(old, original)
        self.assertEqual(result["etag"], old["etag"])
        self.assertEqual(result["bindings"][:2], old["bindings"])
        self.assertEqual(add_identity_binding(result, "new-principal"), result)

    def test_sharing_preflights_all_files_before_any_mutation(self):
        api = Mock()
        api.call.side_effect = [
            {"id": "first", "mimeType": "text/plain", "capabilities": {"canShare": True}}, {"permissions": []},
            {"id": "second", "mimeType": "text/plain", "capabilities": {"canShare": False}}, {"permissions": []}]
        with self.assertRaisesRegex(ConnectionError, "CANNOT_SHARE"):
            share_registered_files(api, [{"file_id": "first", "role": "reader"}, {"file_id": "second", "role": "writer"}], "sa@example.test", apply=True)
        self.assertTrue(all(c.args[0] == "GET" for c in api.call.call_args_list))

    def test_new_permission_targets_exact_account_and_sends_no_email(self):
        api = Mock()
        api.call.side_effect = [
            {"id": "first", "mimeType": "text/plain", "capabilities": {"canShare": True}}, {"permissions": []},
            {"id": "new"}, {"permissions": [{"type": "user", "emailAddress": "sa@example.test", "role": "reader"}]}]
        share_registered_files(api, [{"file_id": "first", "role": "reader"}], "sa@example.test", apply=True)
        creation = api.call.call_args_list[2]
        self.assertEqual(creation.kwargs["params"]["sendNotificationEmail"], "false")
        self.assertEqual(creation.kwargs["json"], {"type": "user", "role": "reader", "emailAddress": "sa@example.test"})

    def test_existing_writer_is_not_downgraded_or_duplicated(self):
        api = Mock()
        api.call.side_effect = [
            {"id": "first", "mimeType": "text/plain"},
            {"permissions": [{"type": "user", "emailAddress": "sa@example.test", "role": "writer"}]}]
        result = share_registered_files(api, [{"file_id": "first", "role": "reader"}], "sa@example.test", apply=True)
        self.assertEqual(result["new_or_changed_permissions"], 0)
        self.assertEqual(api.call.call_count, 2)

    def test_existing_different_connection_is_never_overwritten(self):
        gh = Mock()
        response = Mock(status_code=200)
        response.json.return_value = {"value": "other-existing-identity"}
        gh.response.return_value = response
        with self.assertRaisesRegex(ConnectionError, "DIFFERENT_EXISTING"):
            configure_variables(gh, {"provider": "new-provider", "service_account": "new-account"}, apply=True)
        gh.call.assert_not_called()

    def test_branch_move_blocks_dispatch(self):
        gh = Mock()
        gh.call.return_value = {"object": {"sha": "new"}}
        with self.assertRaisesRegex(ConnectionError, "BRANCH_MOVED"):
            dispatch_refresh(gh, "previous")
        self.assertEqual(gh.call.call_count, 1)

    def test_unrelated_successful_run_cannot_satisfy_setup(self):
        gh = Mock()
        gh.call.return_value = {"workflow_runs": [
            {"display_title": "Sheets refresh requested", "head_sha": "wrong", "head_branch": BRANCH},
            {"display_title": "Other run", "head_sha": "expected", "head_branch": BRANCH}]}
        self.assertIsNone(find_refresh_run(gh, "requested", "expected"))

    def test_public_live_flag_without_this_runs_receipt_is_not_success(self):
        for data in [
            {"live_google_sheets_fetch": True},
            {"live_google_sheets_fetch": True, "publication_receipt": {"workflow_run_id": "old", "commit_sha": "sha"}},
            {"live_google_sheets_fetch": False, "publication_receipt": {"workflow_run_id": "123", "commit_sha": "sha"}}]:
            with self.assertRaisesRegex(ConnectionError, "NOT_YET_VERIFIED"):
                verify_public_receipt(data, 123, "sha")
        self.assertEqual(verify_public_receipt({"live_google_sheets_fetch": True, "publication_receipt": {"workflow_run_id": "123", "commit_sha": "sha"}}, 123, "sha")["workflow_run_id"], "123")

    def test_provider_body_and_credentials_are_not_exposed_in_errors(self):
        session = Mock()
        session.request.return_value = Mock(status_code=403, text="PRIVATE_TOKEN_AND_DATA")
        with self.assertRaises(ConnectionError) as err:
            API(session, "https://example.test").call("GET", "/resource")
        self.assertNotIn("PRIVATE_TOKEN", str(err.exception))

    def test_notebook_contains_reviewed_helper_and_no_saved_outputs(self):
        import hashlib
        notebook = json.loads((ROOT / "ops/notebooks/JP_Actions_Google_Connection__V000001__LIVE.ipynb").read_text())
        helper = (ROOT / "scripts/connect_actions_google.py").read_text()
        self.assertEqual("".join(notebook["cells"][3]["source"]), helper)
        self.assertEqual(notebook["metadata"]["jp_release"]["helper_sha256"], hashlib.sha256(helper.encode()).hexdigest())
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                self.assertEqual(cell.get("outputs", []), [])
                self.assertIsNone(cell.get("execution_count"))
        source = "".join(notebook["cells"][7]["source"])
        self.assertIn('getpass(', source)
        self.assertIn('github_token = None', source)


if __name__ == "__main__":
    unittest.main()
