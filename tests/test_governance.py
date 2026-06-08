import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GovernanceTests(unittest.TestCase):
    def test_root_governance_files_exist_with_required_sections(self) -> None:
        required_sections = {
            "LICENSE": ("MIT License",),
            "CONTRIBUTING.md": ("# Contributing", "Local validation", "Pull requests", "Release changes"),
            "SECURITY.md": ("# Security Policy", "Supported scope", "Reporting a vulnerability", "Secret handling"),
            "SUPPORT.md": ("# Support", "Before opening an issue", "Where to ask", "What to include"),
            "CODE_OF_CONDUCT.md": ("# Code of Conduct", "Expected behavior", "Unacceptable behavior", "Enforcement"),
            "CHANGELOG.md": ("# Changelog", "0.1.0", "Godot Production Toolkit"),
            "docs/RELEASE_CHECKLIST.md": ("# Release Checklist", "Pre-release verification", "Tagging", "Post-release notes"),
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

    def test_project_metadata_links_governance_files(self) -> None:
        metadata = json.loads((ROOT / "project-metadata.json").read_text(encoding="utf-8"))

        self.assertIn("governance", metadata)
        self.assertIn("CODE_OF_CONDUCT.md", metadata["governance"])
        self.assertIn("SUPPORT.md", metadata["governance"])
        self.assertIn("docs/PROJECT_HEALTH.md", metadata["governance"])


if __name__ == "__main__":
    unittest.main()
