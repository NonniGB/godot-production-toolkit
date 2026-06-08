import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AiReviewPackageTests(unittest.TestCase):
    def test_machine_readable_evidence_file_has_reviewer_fields(self) -> None:
        evidence = json.loads((ROOT / "oss-review-evidence.json").read_text(encoding="utf-8"))

        for key in (
            "project_name",
            "one_line_summary",
            "open_source_programme_fit",
            "tool_count",
            "tools",
            "agentic_interfaces",
            "ci_and_maintenance",
            "verification_commands",
            "current_limitations",
            "adoption_gap",
        ):
            self.assertIn(key, evidence)
        self.assertEqual(evidence["tool_count"], 12)
        self.assertEqual(len(evidence["tools"]), 12)
        self.assertIn("organic public usage", evidence["adoption_gap"].lower())
        self.assertGreaterEqual(len(evidence["verification_commands"]), 4)

    def test_ai_review_package_is_root_visible_and_explicit(self) -> None:
        text = (ROOT / "AI_REVIEW_PACKAGE.md").read_text(encoding="utf-8")

        for phrase in (
            "# AI Review Package",
            "Why this exists",
            "What an automated reviewer should check",
            "Evidence at a glance",
            "Current limitation",
            "organic public usage",
            "godot-project-doctor",
            "godot-ci-doctor-action",
        ):
            self.assertIn(phrase, text)

    def test_readiness_and_publication_docs_exist_with_required_sections(self) -> None:
        required_sections = {
            "docs/CODEX_FOR_OSS_READINESS.md": (
                "# Codex For Open Source Readiness",
                "Technical readiness",
                "Maintenance evidence",
                "Adoption gap",
                "Application draft",
            ),
            "docs/PUBLICATION_GUIDE.md": (
                "# Publication Guide",
                "GitHub release",
                "PyPI release",
                "Godot community outreach",
                "Evidence to collect",
            ),
            "docs/MAINTAINER_AUTOMATION.md": (
                "# Maintainer Automation",
                "Issue triage",
                "Release cadence",
                "Agentic maintenance",
                "Validation commands",
            ),
        }

        for rel_path, sections in required_sections.items():
            text = (ROOT / rel_path).read_text(encoding="utf-8")
            for section in sections:
                self.assertIn(section, text)
