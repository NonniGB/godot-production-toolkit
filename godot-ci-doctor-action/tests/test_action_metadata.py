from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ActionMetadataTests(unittest.TestCase):
    def test_action_yml_is_composite_and_exposes_expected_inputs(self) -> None:
        text = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("using: composite", text)
        for expected_input in ("project:", "config:", "checks:", "reports-dir:", "fail-on:", "output-formats:"):
            self.assertIn(expected_input, text)
        for expected_output in ("summary-json:", "summary-markdown:", "summary-html:"):
            self.assertIn(expected_output, text)

    def test_action_installs_python_and_runs_project_doctor(self) -> None:
        text = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("actions/setup-python@v5", text)
        self.assertIn("python -m pip install", text)
        self.assertIn('python -m pip install "${tool_packages[@]}"', text)
        self.assertIn('default: "godot-production-doctor ', text)
        self.assertNotIn('default: "godot-project-doctor ', text)
        self.assertIn("godot-project-doctor run", text)
        self.assertIn("--format json", text)
        self.assertIn("--format markdown", text)
        self.assertIn("--format html", text)

    def test_shell_steps_quote_user_facing_inputs(self) -> None:
        text = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("PROJECT_PATH: ${{ inputs.project }}", text)
        self.assertIn("CONFIG_PATH: ${{ inputs.config }}", text)
        self.assertIn("CHECKS: ${{ inputs.checks }}", text)
        self.assertIn("REPORTS_DIR: ${{ inputs.reports-dir }}", text)
        self.assertIn("FAIL_ON: ${{ inputs.fail-on }}", text)
        self.assertIn("TOOL_PACKAGES: ${{ inputs.tool-packages }}", text)
        self.assertIn('--project "$PROJECT_PATH"', text)
        self.assertIn('--checks "$CHECKS"', text)
        self.assertIn('--reports-dir "$REPORTS_DIR"', text)
        self.assertIn('--fail-on "$FAIL_ON"', text)
        self.assertNotIn('python -m pip install ${{ inputs.tool-packages }}', text)
        self.assertNotIn('summarize "${{ inputs.reports-dir }}"', text)

    def test_public_documentation_includes_local_reproduction_and_sarif_notes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Usage", readme)
        self.assertIn("## Local Reproduction", readme)
        self.assertIn("## Artifacts", readme)
        self.assertIn("SARIF", readme)
        self.assertIn("godot-project-doctor run", readme)
        self.assertIn("shell-style package list", readme)


if __name__ == "__main__":
    unittest.main()
