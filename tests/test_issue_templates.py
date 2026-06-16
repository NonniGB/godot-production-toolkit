from pathlib import Path
import unittest

import verify_tool_manifests


ROOT = Path(__file__).resolve().parents[1]


class IssueTemplateTests(unittest.TestCase):
    def test_bug_and_feature_templates_list_every_tool(self) -> None:
        templates = [
            ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
        ]

        missing: list[str] = []
        for template in templates:
            text = template.read_text(encoding="utf-8")
            for tool in verify_tool_manifests.TOOLS:
                if f"- {tool}" not in text:
                    missing.append(f"{template.relative_to(ROOT)}: {tool}")

        self.assertEqual([], missing)

    def test_workflow_feedback_template_exists(self) -> None:
        template = ROOT / ".github" / "ISSUE_TEMPLATE" / "workflow_feedback.yml"
        text = template.read_text(encoding="utf-8")

        for phrase in (
            "Workflow feedback",
            "Android, desktop, or web export review",
            "Mobile UI, touch, or input review",
            "Scenario, telemetry, or runtime evidence review",
            "Do not include private assets",
        ):
            self.assertIn(phrase, text)

    def test_workflow_labels_are_documented(self) -> None:
        labels = (ROOT / ".github" / "labels.yml").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")

        for label in (
            "workflow: export",
            "workflow: mobile-ui",
            "workflow: localization",
            "workflow: visual-regression",
            "workflow: runtime-evidence",
            "workflow: content-data",
            "workflow: gdscript-architecture",
            "workflow: dashboard",
            "report schema",
        ):
            self.assertIn(label, labels)
            self.assertIn(label, roadmap)


if __name__ == "__main__":
    unittest.main()
