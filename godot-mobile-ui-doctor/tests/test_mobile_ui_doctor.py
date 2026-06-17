from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from godot_mobile_ui_doctor.audit import audit_mobile_ui, build_readiness_matrix
from godot_mobile_ui_doctor.cli import main
from godot_mobile_ui_doctor.layout_risk import build_layout_risk_report
from godot_mobile_ui_doctor.loader import load_metadata
from godot_mobile_ui_doctor.visual_smoke import load_visual_smoke_viewports


class MobileUiDoctorTests(unittest.TestCase):
    def test_loads_metadata_and_finds_mobile_ui_risks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ui.json"
            path.write_text(json.dumps(_sample_metadata()), encoding="utf-8")

            viewports, screens, thresholds = load_metadata(path)
            report = audit_mobile_ui(viewports, screens, thresholds)

            self.assertEqual(report["tool_version"], "0.1.10")
            self.assertEqual(report["schema_version"], "1.1")
            self.assertIn("touch_target_too_small", report["metadata"]["rules"])
            rule_ids = {finding["rule_id"] for finding in report["findings"]}
            self.assertIn("touch_target_too_small", rule_ids)
            self.assertIn("safe_area_overlap", rule_ids)
            self.assertIn("text_overflow_risk", rule_ids)
            self.assertIn("touch_targets_too_close", rule_ids)
            self.assertTrue(all("rule_help" in finding for finding in report["findings"]))

    def test_text_expansion_factor_flags_localized_layout_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ui.json"
            path.write_text(json.dumps(_localized_text_metadata()), encoding="utf-8")

            viewports, screens, thresholds = load_metadata(path)
            report = audit_mobile_ui(viewports, screens, thresholds)

            finding = next(
                item
                for item in report["findings"]
                if item["rule_id"] == "text_expansion_overflow_risk"
            )
            self.assertEqual(finding["node"], "continue")
            self.assertIn("1.4x", finding["message"])

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
        self.assertIn("godot-mobile-ui-doctor 0.1.10", stdout.getvalue())

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

    def test_overlay_command_can_use_screenshot_backgrounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            screenshots = root / "screenshots"
            output_dir = root / "overlays"
            summary = root / "overlay-summary.json"
            screenshots.mkdir()
            metadata.write_text(json.dumps(_sample_metadata()), encoding="utf-8")
            Image.new("RGB", (720, 1280), (30, 40, 50)).save(
                screenshots / "main_menu__portrait_phone.png"
            )

            exit_code = main(
                [
                    "overlays",
                    str(metadata),
                    "--screenshot-dir",
                    str(screenshots),
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
            self.assertEqual(report["summary"]["screenshots"], 1)
            self.assertTrue(report["files"][0]["screenshot"].endswith("main_menu__portrait_phone.png"))

    def test_readiness_combines_ui_matrix_with_linked_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            input_report = root / "input.json"
            export_report = root / "export.json"
            output = root / "readiness.json"
            metadata.write_text(json.dumps(_sample_metadata()), encoding="utf-8")
            input_report.write_text(
                json.dumps(
                    {
                        "tool": "godot-input-map-auditor",
                        "summary": {"errors": 0, "warnings": 1},
                        "findings": [
                            {
                                "severity": "warning",
                                "rule_id": "missing_touch_binding",
                                "action": "ui_accept",
                                "message": "Touch action missing.",
                            },
                            {
                                "severity": "warning",
                                "rule_id": "missing_touch_binding",
                                "action": "ui_cancel",
                                "message": "Back action missing.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            export_report.write_text(
                json.dumps(
                    {
                        "tool": "godot-export-preset-doctor",
                        "summary": {"errors": 1, "warnings": 0},
                    }
                ),
                encoding="utf-8",
            )

            exit_code = main(
                [
                    "readiness",
                    str(metadata),
                    "--input-report",
                    str(input_report),
                    "--export-report",
                    str(export_report),
                    "--format",
                    "json",
                    "--output",
                    str(output),
                ]
            )

            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 1)
            self.assertEqual(report["kind"], "combined_mobile_readiness")
            self.assertEqual(report["summary"]["linked_reports"], 2)
            self.assertEqual(report["summary"]["linked_report_errors"], 1)
            self.assertEqual(report["summary"]["linked_report_warnings"], 1)
            self.assertEqual(report["summary"]["linked_report_findings"], 2)
            self.assertEqual({item["slot"] for item in report["linked_reports"]}, {"input", "export"})
            input_link = next(item for item in report["linked_reports"] if item["slot"] == "input")
            self.assertEqual(input_link["top_findings"][0]["rule"], "missing_touch_binding")
            self.assertEqual(input_link["top_findings"][0]["location"], "ui_accept")
            self.assertEqual(input_link["rule_summaries"][0]["rule"], "missing_touch_binding")
            self.assertEqual(input_link["rule_summaries"][0]["findings"], 2)
            self.assertEqual(input_link["rule_summaries"][0]["locations"], ["ui_accept", "ui_cancel"])

    def test_readiness_markdown_includes_top_linked_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            input_report = root / "input.json"
            metadata.write_text(json.dumps(_sample_metadata()), encoding="utf-8")
            input_report.write_text(
                json.dumps(
                    {
                        "tool": "godot-input-map-auditor",
                        "findings": [
                            {
                                "severity": "warning",
                                "rule_id": "missing_touch_binding",
                                "action": "ui_accept",
                                "message": "Touch action missing.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "readiness",
                        str(metadata),
                        "--input-report",
                        str(input_report),
                        "--format",
                        "markdown",
                        "--fail-on",
                        "none",
                    ]
                )

            self.assertEqual(exit_code, 0)
            rendered = stdout.getvalue()
            self.assertIn("Linked report findings", rendered)
            self.assertIn("Common Rules", rendered)
            self.assertIn("`missing_touch_binding` x1 (warning)", rendered)
            self.assertIn("`missing_touch_binding` (ui_accept)", rendered)

    def test_readiness_markdown_can_use_visual_smoke_plan_viewports(self) -> None:
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
                exit_code = main(
                    [
                        "readiness",
                        str(metadata),
                        "--visual-smoke-plan",
                        str(plan),
                        "--visual-smoke-report",
                        str(plan),
                        "--fail-on",
                        "none",
                    ]
                )

            rendered = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("# Godot Mobile Readiness", rendered)
            self.assertIn("| main_menu | portrait_phone | review |", rendered)
            self.assertIn("| Visual smoke | pass | 0 | 0 |", rendered)

    def test_layout_risk_joins_stress_pack_by_translation_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            stress_manifest = _write_stress_pack_fixture(root)
            metadata.write_text(json.dumps(_layout_risk_metadata()), encoding="utf-8")

            viewports, screens, thresholds = load_metadata(metadata)
            report = build_layout_risk_report(viewports, screens, thresholds, stress_manifest)

            self.assertEqual(report["kind"], "mobile_ui_layout_risk")
            self.assertEqual(report["summary"]["matched_nodes"], 1)
            self.assertEqual(report["summary"]["warnings"], 1)
            finding = report["findings"][0]
            self.assertEqual(finding["rule_id"], "localized_text_overflow_risk")
            self.assertEqual(finding["node"], "continue")
            self.assertEqual(finding["translation_key"], "MENU_CONTINUE")

    def test_layout_risk_cli_writes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "ui.json"
            stress_manifest = _write_stress_pack_fixture(root)
            output = root / "layout-risk.md"
            metadata.write_text(json.dumps(_layout_risk_metadata()), encoding="utf-8")

            exit_code = main(
                [
                    "layout-risk",
                    str(metadata),
                    "--stress-pack",
                    str(stress_manifest),
                    "--output",
                    str(output),
                    "--fail-on",
                    "none",
                ]
            )

            rendered = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn("# Godot Mobile UI Layout Risk", rendered)
            self.assertIn("`MENU_CONTINUE`", rendered)


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


def _localized_text_metadata() -> dict[str, object]:
    return {
        "thresholds": {
            "min_touch_size": 44,
            "min_touch_spacing": 8,
            "text_expansion_factor": 1.4,
        },
        "viewports": [
            {
                "name": "portrait_phone",
                "width": 720,
                "height": 1280,
                "safe_area": {"left": 0, "top": 0, "right": 0, "bottom": 0},
            }
        ],
        "screens": [
            {
                "name": "pause_menu",
                "viewport": "portrait_phone",
                "nodes": [
                    {
                        "id": "continue",
                        "kind": "button",
                        "x": 24,
                        "y": 96,
                        "width": 120,
                        "height": 44,
                        "text": "Continue",
                        "font_size": 24,
                        "interactive": True,
                    }
                ],
            }
        ],
    }


def _layout_risk_metadata() -> dict[str, object]:
    return {
        "thresholds": {"max_text_width_ratio": 0.95},
        "viewports": [
            {
                "name": "portrait_phone",
                "width": 720,
                "height": 1280,
                "safe_area": {"left": 0, "top": 0, "right": 0, "bottom": 0},
            }
        ],
        "screens": [
            {
                "name": "pause_menu",
                "viewport": "portrait_phone",
                "nodes": [
                    {
                        "id": "continue",
                        "kind": "button",
                        "x": 24,
                        "y": 96,
                        "width": 96,
                        "height": 44,
                        "text": "Continue",
                        "translation_key": "MENU_CONTINUE",
                        "font_size": 22,
                        "interactive": True,
                    }
                ],
            }
        ],
    }


def _write_stress_pack_fixture(root: Path) -> Path:
    stress_dir = root / "localization-stress"
    stress_dir.mkdir()
    long_csv = stress_dir / "long.csv"
    long_csv.write_text(
        "keys,en,qps-long\nMENU_CONTINUE,Continue,Continue with the current game session now\n",
        encoding="utf-8",
    )
    manifest = stress_dir / "stress-pack-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "outputs": [
                    {
                        "variant": "long",
                        "locale": "qps-long",
                        "path": str(long_csv),
                        "strings": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return manifest


if __name__ == "__main__":
    unittest.main()
