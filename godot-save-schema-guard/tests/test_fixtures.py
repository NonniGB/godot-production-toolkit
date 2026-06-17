import json
import tempfile
import unittest
from pathlib import Path

from godot_save_guard.fixtures import generate_fixture, validate_fixtures


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

    def test_generates_required_fixture_from_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "generated" / "save.json"
            schema = {
                "type": "object",
                "required": ["version", "credits", "player"],
                "properties": {
                    "version": {"type": "integer", "default": 3},
                    "credits": {"type": "number", "minimum": 100},
                    "player": {
                        "type": "object",
                        "required": ["id"],
                        "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
                    },
                    "debug": {"type": "boolean"},
                },
            }

            result = generate_fixture(schema, output, overrides=["player.id=\"pilot-1\""])

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result.findings[0].rule_id, "fixture_generated")
            self.assertEqual(data["version"], 3)
            self.assertEqual(data["credits"], 100.0)
            self.assertEqual(data["player"], {"id": "pilot-1"})
            self.assertNotIn("debug", data)

    def test_generates_optional_fields_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "save.json"
            schema = {
                "type": "object",
                "required": ["version"],
                "properties": {
                    "version": {"type": "integer"},
                    "settings": {
                        "type": "object",
                        "properties": {"touch_controls": {"type": "boolean"}},
                    },
                },
            }

            generate_fixture(schema, output, include_optional=True)

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["settings"], {"touch_controls": False})

    def test_generation_requires_overwrite_for_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "save.json"
            output.write_text("{}", encoding="utf-8")

            result = generate_fixture({"type": "object"}, output)

            self.assertEqual(result.findings[0].rule_id, "fixture_output_exists")
            self.assertEqual(output.read_text(encoding="utf-8"), "{}")

    def test_generation_reports_invalid_override_without_writing_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "save.json"

            result = generate_fixture({"type": "object"}, output, overrides=["version=not-json"])

            self.assertEqual(result.findings[0].rule_id, "fixture_override_invalid")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
