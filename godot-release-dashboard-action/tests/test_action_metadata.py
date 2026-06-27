from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseDashboardActionMetadataTests(unittest.TestCase):
    def test_action_yml_is_composite_and_exposes_dashboard_inputs(self) -> None:
        text = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("using: composite", text)
        for expected_input in (
            "reports-dir:",
            "dashboard-dir:",
            "dashboard-title:",
            "dashboard-description:",
            "previous-reports-dir:",
            "artifact-name:",
            "python-version:",
            "tool-packages:",
        ):
            self.assertIn(expected_input, text)
        for expected_output in ("dashboard-html:", "dashboard-json:"):
            self.assertIn(expected_output, text)

    def test_action_builds_html_and_json_dashboard_artifacts(self) -> None:
        text = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("actions/setup-python@v5", text)
        self.assertIn("python -m pip install", text)
        self.assertIn("godot-release-dashboard build", text)
        self.assertIn("--format json", text)
        self.assertIn("actions/upload-artifact@v4", text)

    def test_readme_shows_minimal_usage_and_local_reproduction(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Usage", readme)
        self.assertIn("## Local Reproduction", readme)
        self.assertIn("reports/release-dashboard", readme)
        self.assertIn("godot-release-dashboard build", readme)


if __name__ == "__main__":
    unittest.main()
