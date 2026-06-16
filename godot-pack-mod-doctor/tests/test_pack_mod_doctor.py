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
            self.assertEqual(report["tool_version"], "0.1.1")
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

    def test_diff_reports_added_removed_and_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.json"
            current = root / "current.json"
            baseline.write_text(
                json.dumps(
                    {
                        "id": "demo",
                        "version": "1.0.0",
                        "files": [
                            {"path": "res://items/sword.tres", "references": ["iron"]},
                            {"path": "res://items/old.tres"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            current.write_text(
                json.dumps(
                    {
                        "id": "demo",
                        "version": "1.1.0",
                        "files": [
                            {"path": "res://items/sword.tres", "references": ["steel"]},
                            {"path": "res://items/new.tres"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["diff", str(baseline), str(current), "--format", "json"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["kind"], "pack_manifest_diff")
            self.assertEqual(report["diff"]["added"], ["res://items/new.tres"])
            self.assertEqual(report["diff"]["removed"], ["res://items/old.tres"])
            self.assertEqual(report["diff"]["changed"], ["res://items/sword.tres"])

    def test_load_order_reports_undeclared_override_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.json"
            patch = root / "patch.json"
            base.write_text(
                json.dumps({"id": "base", "version": "1", "files": [{"path": "res://items/sword.tres"}]}),
                encoding="utf-8",
            )
            patch.write_text(
                json.dumps({"id": "patch", "version": "1", "files": [{"path": "res://items/sword.tres"}]}),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["load-order", str(base), str(patch), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["kind"], "pack_load_order")
            self.assertEqual(report["findings"][0]["rule_id"], "load_order_conflict")


if __name__ == "__main__":
    unittest.main()
