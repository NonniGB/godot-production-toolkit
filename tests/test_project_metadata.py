import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProjectMetadataTests(unittest.TestCase):
    def test_project_metadata_has_public_orientation_fields(self) -> None:
        metadata = json.loads((ROOT / "project-metadata.json").read_text(encoding="utf-8"))

        for key in (
            "project_name",
            "one_line_summary",
            "repository",
            "tool_count",
            "tools",
            "automation_interfaces",
            "ci_and_maintenance",
            "governance",
            "verification_commands",
            "current_limitations",
            "release_priorities",
        ):
            self.assertIn(key, metadata)

        self.assertEqual(metadata["tool_count"], 12)
        self.assertEqual(len(metadata["tools"]), 12)
        self.assertGreaterEqual(len(metadata["verification_commands"]), 4)

    def test_project_overview_is_root_visible_and_neutral(self) -> None:
        text = (ROOT / "PROJECT_OVERVIEW.md").read_text(encoding="utf-8")

        for phrase in (
            "# Project Overview",
            "What Ships",
            "Design Principles",
            "Main Entry Points",
            "Maintenance Model",
            "Current Limitations",
            "godot-project-doctor",
            "godot-ci-doctor-action",
        ):
            self.assertIn(phrase, text)

    def test_project_health_and_publication_docs_exist_with_required_sections(self) -> None:
        required_sections = {
            "docs/PROJECT_HEALTH.md": (
                "# Project Health",
                "Tool Coverage",
                "Maintenance Checks",
                "Known Limitations",
                "Privacy And Fixture Policy",
            ),
            "docs/PUBLICATION_GUIDE.md": (
                "# Publication Guide",
                "GitHub release",
                "PyPI release",
                "Godot community outreach",
                "Feedback loop",
            ),
            "docs/MAINTAINER_AUTOMATION.md": (
                "# Maintainer Automation",
                "Issue triage",
                "Release cadence",
                "Automation maintenance",
                "Validation commands",
            ),
        }

        for rel_path, sections in required_sections.items():
            text = (ROOT / rel_path).read_text(encoding="utf-8")
            for section in sections:
                self.assertIn(section, text)
