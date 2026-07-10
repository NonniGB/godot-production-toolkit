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

        self.assertIn("actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065", text)
        self.assertIn("python -m pip install", text)
        self.assertIn('python -m pip install "${tool_packages[@]}"', text)
        self.assertIn("godot-release-dashboard build", text)
        self.assertIn("--format json", text)
        self.assertIn('"${extra_args[@]}"', text)
        self.assertIn("actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02", text)

    def test_shell_steps_quote_user_facing_inputs(self) -> None:
        text = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("REPORTS_DIR: ${{ inputs.reports-dir }}", text)
        self.assertIn("DASHBOARD_TITLE: ${{ inputs.dashboard-title }}", text)
        self.assertIn("DASHBOARD_DESCRIPTION: ${{ inputs.dashboard-description }}", text)
        self.assertIn("PROJECT_NAME: ${{ inputs.project }}", text)
        self.assertIn("PREVIOUS_REPORTS_DIR: ${{ inputs.previous-reports-dir }}", text)
        self.assertIn("EXTRA_ARGS: ${{ inputs.extra-args }}", text)
        self.assertIn('build "$REPORTS_DIR"', text)
        self.assertIn('--title "$DASHBOARD_TITLE"', text)
        self.assertIn('previous_arg=(--previous-reports-dir "$PREVIOUS_REPORTS_DIR")', text)
        self.assertIn('description_arg=(--description "$DASHBOARD_DESCRIPTION")', text)
        self.assertIn('project_arg=(--project "$PROJECT_NAME")', text)
        self.assertNotIn('build "${{ inputs.reports-dir }}"', text)
        self.assertNotIn('          ${{ inputs.extra-args }}', text)

    def test_readme_shows_minimal_usage_and_local_reproduction(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Usage", readme)
        self.assertIn("## Local Reproduction", readme)
        self.assertIn("reports/release-dashboard", readme)
        self.assertIn("godot-release-dashboard build", readme)
        self.assertIn("shell-style package install list", readme)
        self.assertIn("optional shell-style arguments", readme)


if __name__ == "__main__":
    unittest.main()
