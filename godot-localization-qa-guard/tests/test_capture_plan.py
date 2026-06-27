import json
import tempfile
import unittest
from pathlib import Path

from godot_l10n_guard.capture_plan import build_capture_plan, render_capture_plan
from godot_l10n_guard.cli import main


class CapturePlanTests(unittest.TestCase):
    def test_build_capture_plan_creates_locale_screen_viewport_matrix(self) -> None:
        manifest = {
            "metadata": {"schema_version": "1.0", "report_kind": "localization_stress_pack"},
            "source_language": "en",
            "outputs": [
                {"variant": "pseudo", "locale": "qps-ploc", "path": "stress/pseudo.csv", "strings": 12},
                {"variant": "long", "locale": "qps-long", "path": "stress/long.csv", "strings": 12},
            ],
        }

        plan = build_capture_plan(
            manifest,
            screens=["main_menu", "settings"],
            viewports=["portrait_phone"],
            output_dir=Path("captures"),
            include_source_locale=True,
        )

        self.assertEqual(plan["metadata"]["report_kind"], "localization_capture_plan")
        self.assertEqual(plan["summary"]["locales"], 3)
        self.assertEqual(plan["summary"]["captures"], 6)
        self.assertEqual(plan["captures"][0]["locale"], "en")
        self.assertEqual(plan["captures"][1]["locale"], "qps-ploc")
        self.assertEqual(plan["captures"][1]["stress_variant"], "pseudo")
        self.assertEqual(plan["captures"][1]["output_path"], "captures/main_menu/portrait_phone/qps-ploc.png")

    def test_render_capture_plan_markdown_lists_capture_rows(self) -> None:
        plan = {
            "summary": {"captures": 1, "locales": 1, "screens": 1, "viewports": 1},
            "captures": [
                {
                    "screen": "settings",
                    "viewport": "portrait_phone",
                    "locale": "qps-long",
                    "stress_variant": "long",
                    "output_path": "captures/settings/portrait_phone/qps-long.png",
                }
            ],
        }

        markdown = render_capture_plan(plan, "markdown")

        self.assertIn("# Localization Capture Plan", markdown)
        self.assertIn("| settings | portrait_phone | qps-long | long |", markdown)

    def test_capture_plan_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            manifest_path = project / "stress-pack-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "metadata": {"schema_version": "1.0", "report_kind": "localization_stress_pack"},
                        "source_language": "en",
                        "outputs": [
                            {
                                "variant": "pseudo",
                                "locale": "qps-ploc",
                                "path": "stress/pseudo.csv",
                                "strings": 3,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            report_path = project / "capture-plan.json"

            exit_code = main(
                [
                    "capture-plan",
                    str(project),
                    "--stress-pack",
                    str(manifest_path),
                    "--screen",
                    "main_menu",
                    "--viewport",
                    "portrait_phone",
                    "--format",
                    "json",
                    "--output",
                    str(report_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metadata"]["report_kind"], "localization_capture_plan")
            self.assertEqual(report["summary"]["captures"], 1)


if __name__ == "__main__":
    unittest.main()
