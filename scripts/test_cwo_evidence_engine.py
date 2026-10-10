"""Privacy and stable identity sanity tests for A9-CWO offline engine."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cwo_evidence_engine import IntegrityError, digest, secure_external_path


class EvidenceTests(unittest.TestCase):
    def test_sha256_known_vector(self):
        self.assertEqual(digest(b"abc"),hashlib.sha256(b"abc").hexdigest())
        self.assertEqual(len(digest(b"abc")),64)

    def test_private_write_protected(self):
        with self.assertRaises(IntegrityError):
            secure_external_path(Path(__file__).resolve().parents[1] / "ops/evidence/raw.jsonl",write=True)

    def test_private_new_path(self):
        with tempfile.TemporaryDirectory() as temp:
            result = secure_external_path(Path(temp)/"private"/"output.jsonl",write=True)
            self.assertTrue(result.parent.exists())
            self.assertFalse(Path(__file__).resolve().parents[1] in result.parents)


if __name__ == "__main__":
    unittest.main()
