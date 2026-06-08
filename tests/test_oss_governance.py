import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class OssGovernanceTests(unittest.TestCase):
    def test_root_governance_files_exist_with_required_sections(self) -> None:
        required_sections = {
            "LICENSE": ("MIT License",),
            "CONTRIBUTING.md": ("# Contributing", "Local validation", "Pull requests", "Release changes"),
            "SECURITY.md": ("# Security Policy", "Supported scope", "Reporting a vulnerability", "Secret handling"),
            "SUPPORT.md": ("# Support", "Before opening an issue", "Where to ask", "What to include"),
            "CODE_OF_CONDUCT.md": ("# Code of Conduct", "Expected behavior", "Unacceptable behavior", "Enforcement"),
            "CHANGELOG.md": ("# Changelog", "0.1.0", "Godot Production Toolkit"),
            "docs/RELEASE_CHECKLIST.md": ("# Release Checklist", "Pre-release verification", "Tagging", "Post-release evidence"),
            "docs/ADOPTION_TRACKER.md": ("# Adoption Tracker", "Evidence to collect", "Public usage", "Maintainer activity"),
            "docs/REVIEWER_SCORECARD.md": ("# Reviewer Scorecard", "Automated review", "Open-source maintenance", "Known gap"),
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
        self.assertIn("package-ecosystem: \"pip\"", dependabot)
        self.assertIn("directory: \"/godot-project-doctor\"", dependabot)
        self.assertIn("directory: \"/godot-asset-pipeline-doctor\"", dependabot)
        self.assertIn("directory: \"/godot-mobile-perf-doctor\"", dependabot)

    def test_evidence_json_links_governance_and_scorecard(self) -> None:
        evidence = json.loads((ROOT / "oss-review-evidence.json").read_text(encoding="utf-8"))

        self.assertIn("governance", evidence)
        self.assertIn("reviewer_scorecard", evidence)
        self.assertEqual(evidence["reviewer_scorecard"], "docs/REVIEWER_SCORECARD.md")
        self.assertIn("CODE_OF_CONDUCT.md", evidence["governance"])
        self.assertIn("SUPPORT.md", evidence["governance"])
        self.assertIn("docs/ADOPTION_TRACKER.md", evidence["governance"])


if __name__ == "__main__":
    unittest.main()
