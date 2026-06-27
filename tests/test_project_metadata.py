import json
from pathlib import Path
import tomllib
import unittest

import verify_tool_manifests


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
            "script_and_ci_interfaces",
            "ci_and_maintenance",
            "governance",
            "verification_commands",
            "current_limitations",
            "release_priorities",
        ):
            self.assertIn(key, metadata)

        self.assertEqual(metadata["tool_count"], len(verify_tool_manifests.TOOLS))
        self.assertEqual(len(metadata["tools"]), len(verify_tool_manifests.TOOLS))
        self.assertGreaterEqual(len(metadata["verification_commands"]), 4)

    def test_project_metadata_matches_manifest_list(self) -> None:
        metadata = json.loads((ROOT / "project-metadata.json").read_text(encoding="utf-8"))
        metadata_tools = {tool["name"] for tool in metadata["tools"]}

        self.assertEqual(set(verify_tool_manifests.TOOLS), metadata_tools)
        self.assertEqual(len(verify_tool_manifests.TOOLS), metadata["tool_count"])
        self.assertIn("python verify_release_alignment.py", metadata["verification_commands"])

        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(
            len(verify_tool_manifests.TOOLS),
            pyproject["tool"]["godot-production-toolkit"]["tool_count"],
        )

    def test_project_overview_is_root_visible_and_neutral(self) -> None:
        text = (ROOT / "PROJECT_OVERVIEW.md").read_text(encoding="utf-8")

        for phrase in (
            "# Project Overview",
            "What Ships",
            "Design Principles",
            "Main Entry Points",
            "Maintenance Model",
            "Current Limitations",
            "godot-production-doctor",
            "godot-ci-doctor-action",
        ):
            self.assertIn(phrase, text)

    def test_project_health_and_use_case_docs_exist_with_required_sections(self) -> None:
        required_sections = {
            "docs/PROJECT_HEALTH.md": (
                "# Project Health",
                "Tool Coverage",
                "Maintenance Checks",
                "Known Limitations",
                "Privacy And Fixture Policy",
            ),
            "docs/USE_CASES.md": (
                "# Use Cases",
                "Android Release Readiness",
                "Pixel-Art Asset Hygiene",
                "Input Coverage For Touch And Desktop",
                "Script And CI Workflows",
            ),
        }

        for rel_path, sections in required_sections.items():
            text = (ROOT / rel_path).read_text(encoding="utf-8")
            for section in sections:
                self.assertIn(section, text)
