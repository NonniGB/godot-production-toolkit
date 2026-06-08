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
        self.assertIn("godot-project-doctor run", text)
        self.assertIn("--format json", text)
        self.assertIn("--format markdown", text)
        self.assertIn("--format html", text)

    def test_public_documentation_includes_local_reproduction_and_sarif_notes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Usage", readme)
        self.assertIn("## Local Reproduction", readme)
        self.assertIn("## Artifacts", readme)
        self.assertIn("SARIF", readme)
        self.assertIn("godot-project-doctor run", readme)


if __name__ == "__main__":
    unittest.main()
