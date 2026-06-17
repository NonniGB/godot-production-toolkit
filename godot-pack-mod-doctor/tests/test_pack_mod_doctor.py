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
            self.assertEqual(report["tool_version"], "0.1.4")
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("duplicate_file_path", rules)
            self.assertIn("override_not_allowed", rules)
            self.assertNotIn("pack_unsafe_file_type", rules)

    def test_check_reports_dependency_shape_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "pack.json"
            manifest.write_text(
                json.dumps(
                    {
                        "id": "demo_pack",
                        "version": "1.0.0",
                        "dependencies": [
                            {"id": "base_pack"},
                            {"id": "base_pack"},
                            {"id": "demo_pack"},
                            {"name": "missing_id"},
                            "",
                        ],
                        "files": [{"path": "res://items/sword.tres"}],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["check", str(manifest), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["dependencies"], 5)
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("pack_dependency_duplicate_id", rules)
            self.assertIn("pack_dependency_missing_id", rules)
            self.assertIn("pack_self_dependency", rules)

    def test_manifest_from_folder_generates_stable_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack_root = root / "pack"
            nested = pack_root / "addons" / "demo"
            nested.mkdir(parents=True)
            (nested / "item.tres").write_text("name = \"Item\"\n", encoding="utf-8")
            (nested / "icon.png").write_bytes(b"png")
            (pack_root / ".godot").mkdir()
            (pack_root / ".godot" / "editor_cache.bin").write_bytes(b"skip")
            output = root / "generated" / "pack-manifest.json"

            exit_code = main(
                [
                    "manifest",
                    "from-folder",
                    str(pack_root),
                    "--id",
                    "demo_pack",
                    "--version",
                    "1.2.3",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(manifest["id"], "demo_pack")
            self.assertEqual(manifest["version"], "1.2.3")
            self.assertEqual(
                [item["path"] for item in manifest["files"]],
                ["res://addons/demo/icon.png", "res://addons/demo/item.tres"],
            )
            self.assertEqual(len(manifest["files"][0]["sha256"]), 64)

            stdout = StringIO()
            with redirect_stdout(stdout):
                check_exit_code = main(["check", str(output), "--format", "json"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(check_exit_code, 0)
            self.assertEqual(report["summary"]["files"], 2)

    def test_check_flags_unsafe_paths_and_private_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "pack.json"
            manifest.write_text(
                json.dumps(
                    {
                        "id": "demo",
                        "version": "1",
                        "files": [
                            {"path": "res://addons/demo/mod.gd"},
                            {"path": "res://addons/demo/debug/run.log"},
                            {"path": "res://addons/demo/Config.cfg"},
                            {"path": "res://addons/demo/config.CFG"},
                            {"path": "../outside/file.tres"},
                            {"path": "C:/local/file.tres"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "check",
                        str(manifest),
                        "--unsafe-extension",
                        ".cfg",
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("pack_unsafe_file_type", rules)
            self.assertIn("pack_dev_or_private_file", rules)
            self.assertIn("pack_path_traversal", rules)
            self.assertIn("pack_absolute_path", rules)
            self.assertIn("pack_non_res_path", rules)
            self.assertIn("pack_duplicate_path_case_insensitive", rules)

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

    def test_check_reports_duplicate_content_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "pack.json"
            manifest.write_text(
                json.dumps(
                    {
                        "id": "demo",
                        "version": "1",
                        "files": [
                            {"path": "res://items/sword.tres", "content_id": "sword"},
                            {"path": "res://items/sword_icon.png", "content_ids": ["sword", "sword_icon"]},
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
            self.assertEqual(report["summary"]["content_ids"], 3)
            self.assertEqual(report["summary"]["risk_level"], "blocked")
            self.assertGreater(report["summary"]["risk_score"], 0)
            self.assertEqual(report["risk"]["level"], "blocked")
            self.assertIn("duplicate_content_id", {finding["rule_id"] for finding in report["findings"]})

    def test_diff_reports_added_removed_changed_and_moved_files(self) -> None:
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
                            {"path": "res://items/moved_old.tres", "content_id": "moved", "sha256": "abc", "size": 10},
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
                            {"path": "res://items/moved_new.tres", "content_id": "moved", "sha256": "abc", "size": 10},
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
            self.assertEqual(
                report["diff"]["moved"],
                [{"from": "res://items/moved_old.tres", "to": "res://items/moved_new.tres"}],
            )
            self.assertEqual(report["summary"]["moved"], 1)
            self.assertEqual(report["summary"]["risk_level"], "attention")

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

    def test_load_order_reports_dependency_problems(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.json"
            patch = root / "patch.json"
            duplicate = root / "duplicate.json"
            missing_dep = root / "missing-dep.json"
            base.write_text(
                json.dumps({"id": "base", "version": "1", "files": [{"path": "res://items/base.tres"}]}),
                encoding="utf-8",
            )
            patch.write_text(
                json.dumps(
                    {
                        "id": "patch",
                        "version": "1",
                        "dependencies": [{"id": "base"}, {"id": "optional"}],
                        "files": [{"path": "res://items/patch.tres"}],
                    }
                ),
                encoding="utf-8",
            )
            duplicate.write_text(
                json.dumps({"id": "base", "version": "2", "files": [{"path": "res://items/base2.tres"}]}),
                encoding="utf-8",
            )
            missing_dep.write_text(
                json.dumps(
                    {
                        "id": "early_patch",
                        "version": "1",
                        "dependencies": ["patch", "missing_pack", {"name": "broken"}],
                        "files": [{"path": "res://items/early.tres"}],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "load-order",
                        str(missing_dep),
                        str(base),
                        str(patch),
                        str(duplicate),
                        "--format",
                        "json",
                        "--fail-on",
                        "none",
                    ]
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["dependencies"], 5)
            self.assertEqual(report["summary"]["content_ids"], 0)
            self.assertEqual(report["summary"]["errors"], 4)
            rules = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("duplicate_pack_id", rules)
            self.assertIn("pack_dependency_missing_id", rules)
            self.assertIn("pack_dependency_missing", rules)
            self.assertIn("pack_dependency_order", rules)
            early_pack = report["packs"][0]
            self.assertEqual(early_pack["dependencies"], ["patch", "missing_pack"])

    def test_load_order_reports_content_id_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.json"
            patch = root / "patch.json"
            base.write_text(
                json.dumps(
                    {
                        "id": "base",
                        "version": "1",
                        "files": [{"path": "res://items/sword.tres", "content_id": "sword"}],
                    }
                ),
                encoding="utf-8",
            )
            patch.write_text(
                json.dumps(
                    {
                        "id": "patch",
                        "version": "1",
                        "dependencies": ["base"],
                        "files": [{"path": "res://items/sword_plus.tres", "id": "sword"}],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["load-order", str(base), str(patch), "--format", "json", "--fail-on", "none"])

            report = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["content_ids"], 2)
            self.assertEqual(report["packs"][1]["content_ids"], ["sword"])
            self.assertIn("content_id_conflict", {finding["rule_id"] for finding in report["findings"]})

    def test_load_order_text_and_markdown_include_dependency_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.json"
            patch = root / "patch.json"
            base.write_text(
                json.dumps({"id": "base", "version": "1", "files": [{"path": "res://items/base.tres"}]}),
                encoding="utf-8",
            )
            patch.write_text(
                json.dumps(
                    {
                        "id": "patch",
                        "version": "1",
                        "dependencies": [{"id": "base"}],
                        "files": [{"path": "res://items/patch.tres"}],
                    }
                ),
                encoding="utf-8",
            )

            text_stdout = StringIO()
            with redirect_stdout(text_stdout):
                text_exit = main(["load-order", str(base), str(patch), "--format", "text"])

            markdown_stdout = StringIO()
            with redirect_stdout(markdown_stdout):
                markdown_exit = main(["load-order", str(base), str(patch), "--format", "markdown"])

            self.assertEqual(text_exit, 0)
            self.assertEqual(markdown_exit, 0)
            self.assertIn("Dependencies: 1", text_stdout.getvalue())
            self.assertIn("Risk: ready (0)", text_stdout.getvalue())
            self.assertIn("| Order | Pack | Files | Dependencies |", markdown_stdout.getvalue())
            self.assertIn("| 1 | patch | 1 | base |", markdown_stdout.getvalue())
            self.assertIn("| Risk | ready (0) |", markdown_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
