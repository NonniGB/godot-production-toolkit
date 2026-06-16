from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_pack_mod_doctor.cli import main


class PackModDoctorTests(unittest.TestCase):
    def test_check_reports_manifest_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "pack.json"
            manifest.write_text(
                json.dumps(
                    {
                        "id": "demo_pack",
                        "version": "1.0.0",
                        "files": [
                            {"path": "res://items/sword.tres", "overrides": True},
                            {"path": "res://items/sword.tres"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["check", str(manifest), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["tool_version"], "0.1.0")
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("duplicate_file_path", rules)
            self.assertIn("override_not_allowed", rules)

    def test_check_base_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "pack.json"
            base = root / "base.json"
            manifest.write_text(
                json.dumps({"id": "demo", "version": "1", "files": [{"path": "res://a.tres", "references": ["missing"]}]}),
                encoding="utf-8",
            )
            base.write_text(json.dumps({"content": [{"id": "present"}]}), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["check", str(manifest), "--base", str(base), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["findings"][0]["rule_id"], "unknown_base_reference")


if __name__ == "__main__":
    unittest.main()
