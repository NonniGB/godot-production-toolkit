import json
from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROOT_VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


class GovernanceTests(unittest.TestCase):
    def test_root_governance_files_exist_with_required_sections(self) -> None:
        required_sections = {
            "LICENSE": ("MIT License",),
            "CONTRIBUTING.md": ("# Contributing", "Local validation", "Pull requests", "Release changes"),
            "SECURITY.md": ("# Security Policy", "Supported scope", "Reporting a vulnerability", "Secret handling"),
            "SUPPORT.md": ("# Support", "Before opening an issue", "Where to ask", "What to include"),
            "CODE_OF_CONDUCT.md": ("# Code of Conduct", "Expected behavior", "Unacceptable behavior", "Enforcement"),
            "CHANGELOG.md": ("# Changelog", ROOT_VERSION, "Godot Production Toolkit"),
            "docs/PROJECT_HEALTH.md": ("# Project Health", "Tool Coverage", "Privacy And Fixture Policy"),
        }

        for rel_path, sections in required_sections.items():
            text = (ROOT / rel_path).read_text(encoding="utf-8")
            for section in sections:
                self.assertIn(section, text)

    def test_github_maintenance_config_exists(self) -> None:
        required_files = {
            ".github/CODEOWNERS",
            ".github/dependabot.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
        }

        missing = sorted(rel_path for rel_path in required_files if not (ROOT / rel_path).exists())
        self.assertEqual([], missing)

        dependabot = (ROOT / ".github/dependabot.yml").read_text(encoding="utf-8")
        self.assertIn('package-ecosystem: "pip"', dependabot)
        self.assertIn('directory: "/godot-project-doctor"', dependabot)
        self.assertIn('directory: "/godot-asset-pipeline-doctor"', dependabot)
        self.assertIn('directory: "/godot-mobile-perf-doctor"', dependabot)

    def test_fixture_contribution_guide_warns_about_private_inputs(self) -> None:
        guide = ROOT / "examples" / "CONTRIBUTING_FIXTURES.md"
        text = guide.read_text(encoding="utf-8")

        self.assertIn("# Contributing Fixtures And Sample Reports", text)
        self.assertIn("Private game assets", text)
        self.assertIn("Signing keys", text)
        self.assertIn("private local paths", text)
        self.assertIn("exact command used to regenerate the report", text)

        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("examples/CONTRIBUTING_FIXTURES.md", contributing)

    def test_project_metadata_links_governance_files(self) -> None:
        metadata = json.loads((ROOT / "project-metadata.json").read_text(encoding="utf-8"))

        self.assertIn("governance", metadata)
        self.assertIn("CODE_OF_CONDUCT.md", metadata["governance"])
        self.assertIn("SUPPORT.md", metadata["governance"])
        self.assertIn("docs/PROJECT_HEALTH.md", metadata["governance"])


if __name__ == "__main__":
    unittest.main()
