import json
import tempfile
import unittest
from pathlib import Path

from godot_save_guard.fixtures import validate_fixtures


class FixtureTests(unittest.TestCase):
    def test_validates_json_files_under_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "v1").mkdir()
            (root / "v1" / "save.json").write_text(json.dumps({"credits": 10}), encoding="utf-8")
            schema = {"type": "object", "required": ["version"], "properties": {"version": {"type": "integer"}}}

            results = validate_fixtures(root, schema)

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].path.name, "save.json")
            self.assertIn("missing_version_field", {finding.rule_id for finding in results[0].findings})


if __name__ == "__main__":
    unittest.main()
