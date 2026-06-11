from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from godot_mobile_ui_doctor.audit import audit_mobile_ui, build_readiness_matrix
from godot_mobile_ui_doctor.cli import main
from godot_mobile_ui_doctor.loader import load_metadata
from godot_mobile_ui_doctor.visual_smoke import load_visual_smoke_viewports


class MobileUiDoctorTests(unittest.TestCase):
    def test_loads_metadata_and_finds_mobile_ui_risks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ui.json"
            path.write_text(json.dumps(_sample_metadata()), encoding="utf-8")

            viewports, screens, thresholds = load_metadata(path)
            report = audit_mobile_ui(viewports, screens, thresholds)

            rule_ids = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("touch_target_too_small", rule_ids)
            self.assertIn("safe_area_overlap", rule_ids)
            self.assertIn("text_overflow_risk", rule_ids)
            self.assertIn("touch_targets_too_close", rule_ids)

    def test_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            output = root / "report.json"
            metadata.write_text(json.dumps(_sample_metadata()), encoding="utf-8")

            exit_code = main([str(metadata), "--format", "json", "--output", str(output)])

            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertGreater(report["summary"]["warnings"], 0)

    def test_cli_can_use_visual_smoke_plan_viewports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            plan = root / "visual-plan.json"
            output = root / "report.json"
            data = _sample_metadata()
            data.pop("viewports")
            metadata.write_text(json.dumps(data), encoding="utf-8")
            plan.write_text(json.dumps(_visual_smoke_plan()), encoding="utf-8")

            exit_code = main(
                [
                    str(metadata),
                    "--visual-smoke-plan",
                    str(plan),
                    "--format",
                    "json",
                    "--output",
                    str(output),
                ]
            )

            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["summary"]["viewports"], 1)
            self.assertGreater(report["summary"]["warnings"], 0)

    def test_matrix_can_use_visual_smoke_plan_viewports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            plan = root / "visual-plan.json"
            data = _sample_metadata()
            data.pop("viewports")
            metadata.write_text(json.dumps(data), encoding="utf-8")
            plan.write_text(json.dumps(_visual_smoke_plan()), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["matrix", str(metadata), "--visual-smoke-plan", str(plan), "--fail-on", "none"])

            self.assertEqual(exit_code, 0)
            self.assertIn("| main_menu | portrait_phone | 720x1280 | review |", stdout.getvalue())

    def test_loads_visual_smoke_plan_viewports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "visual-plan.json"
            path.write_text(json.dumps(_visual_smoke_plan()), encoding="utf-8")

            viewports = load_visual_smoke_viewports(path)

            self.assertEqual(viewports["portrait_phone"].safe_area.top, 48)

    def test_cli_can_fail_on_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            metadata = Path(tmp) / "ui.json"
            metadata.write_text(json.dumps(_sample_metadata()), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(metadata), "--fail-on", "warning"])

            self.assertEqual(exit_code, 1)

    def test_cli_prints_version(self) -> None:
        stdout = StringIO()

        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("godot-mobile-ui-doctor 0.1.3", stdout.getvalue())

    def test_builds_mobile_readiness_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ui.json"
            path.write_text(json.dumps(_sample_metadata()), encoding="utf-8")

            viewports, screens, thresholds = load_metadata(path)
            matrix = build_readiness_matrix(viewports, screens, thresholds)

            self.assertEqual(matrix["kind"], "mobile_readiness_matrix")
            self.assertEqual(matrix["summary"]["review"], 1)
            self.assertEqual(matrix["matrix"][0]["screen"], "main_menu")
            self.assertEqual(matrix["matrix"][0]["safe_area"], "review (1)")
            self.assertEqual(matrix["matrix"][0]["touch_targets"], "review (1)")

    def test_cli_outputs_markdown_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            metadata = Path(tmp) / "ui.json"
            metadata.write_text(json.dumps(_sample_metadata()), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["matrix", str(metadata), "--fail-on", "none"])

            self.assertEqual(exit_code, 0)
            rendered = stdout.getvalue()
            self.assertIn("# Godot Mobile UI Readiness Matrix", rendered)
            self.assertIn("| main_menu | portrait_phone | 720x1280 | review |", rendered)

    def test_missing_viewport_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            metadata = Path(tmp) / "ui.json"
            data = _sample_metadata()
            data["screens"][0]["viewport"] = "missing"
            metadata.write_text(json.dumps(data), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(metadata), "--format", "json"])

            self.assertEqual(exit_code, 1)

    def test_cli_renders_overlay_pngs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            output_dir = root / "overlays"
            summary = root / "overlay-summary.json"
            metadata.write_text(json.dumps(_sample_metadata()), encoding="utf-8")

            exit_code = main(
                [
                    "overlays",
                    str(metadata),
                    "--output-dir",
                    str(output_dir),
                    "--output",
                    str(summary),
                    "--format",
                    "json",
                    "--scale",
                    "0.25",
                    "--fail-on",
                    "none",
                ]
            )

            report = json.loads(summary.read_text(encoding="utf-8"))
            overlay = output_dir / "main_menu__portrait_phone.png"
            self.assertEqual(exit_code, 0)
            self.assertTrue(overlay.exists())
            self.assertGreater(overlay.stat().st_size, 500)
            self.assertEqual(report["kind"], "mobile_ui_overlay_previews")
            self.assertEqual(report["summary"]["files"], 1)

    def test_overlay_command_can_use_visual_smoke_plan_viewports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            plan = root / "visual-plan.json"
            output_dir = root / "overlays"
            data = _sample_metadata()
            data.pop("viewports")
            metadata.write_text(json.dumps(data), encoding="utf-8")
            plan.write_text(json.dumps(_visual_smoke_plan()), encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "overlays",
                        str(metadata),
                        "--visual-smoke-plan",
                        str(plan),
                        "--output-dir",
                        str(output_dir),
                        "--scale",
                        "0.2",
                        "--fail-on",
                        "none",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("Godot Mobile UI Overlay Previews", stdout.getvalue())
            self.assertTrue((output_dir / "main_menu__portrait_phone.png").exists())


def _sample_metadata() -> dict[str, object]:
    return {
        "thresholds": {"min_touch_size": 44, "min_touch_spacing": 8},
        "viewports": [
            {
                "name": "portrait_phone",
                "width": 720,
                "height": 1280,
                "safe_area": {"left": 0, "top": 48, "right": 0, "bottom": 24},
            }
        ],
        "screens": [
            {
                "name": "main_menu",
                "viewport": "portrait_phone",
                "nodes": [
                    {
                        "id": "title",
                        "kind": "label",
                        "x": 24,
                        "y": 16,
                        "width": 180,
                        "height": 24,
                        "text": "A very long localized title",
                        "font_size": 22,
                    },
                    {
                        "id": "play",
                        "kind": "button",
                        "x": 24,
                        "y": 96,
                        "width": 40,
                        "height": 40,
                        "text": "Play",
                        "interactive": True,
                    },
                    {
                        "id": "options",
                        "kind": "button",
                        "x": 66,
                        "y": 96,
                        "width": 44,
                        "height": 44,
                        "text": "Options",
                        "interactive": True,
                    },
                ],
            }
        ],
    }


def _visual_smoke_plan() -> dict[str, object]:
    return {
        "metadata": {"report_kind": "visual_smoke_capture_plan"},
        "commands": [
            {
                "name": "main_menu",
                "scene": "res://scenes/main_menu.tscn",
                "viewport": {
                    "name": "portrait_phone",
                    "width": 720,
                    "height": 1280,
                    "safe_area": {"left": 0, "top": 48, "right": 0, "bottom": 24},
                },
                "output": "visual-smoke-output/main_menu.png",
                "command": ["godot"],
                "shell": "godot",
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
