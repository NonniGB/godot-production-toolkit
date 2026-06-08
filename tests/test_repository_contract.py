import unittest
from pathlib import Path
import verify_agent_interfaces


ROOT = Path(__file__).resolve().parents[1]

EXISTING_TOOLS = {
    "gdscript-api-comment-coverage",
    "godot-asset-pipeline-doctor",
    "godot-export-preset-doctor",
    "godot-input-map-auditor",
    "godot-localization-qa-guard",
    "godot-mobile-perf-doctor",
    "godot-save-schema-guard",
    "godot-scene-signal-auditor",
    "godot-visual-smoke-test-kit",
    "pixel-space-asset-toolkit",
}

NEW_PROJECTS = {
    "godot-project-doctor",
    "godot-ci-doctor-action",
}

PRIVATE_TERMS = tuple(
    "".join(parts)
    for parts in (
        ("Space", "Game"),
        ("space", "game"),
        ("Space", " ", "Game"),
        ("space", " ", "game"),
        ("space", "_", "economy"),
        ("space", "-", "trading"),
    )
)


class RepositoryContractTests(unittest.TestCase):
    def test_expected_projects_exist(self) -> None:
        missing = sorted(name for name in EXISTING_TOOLS | NEW_PROJECTS if not (ROOT / name).is_dir())
        self.assertEqual([], missing)

    def test_existing_tools_keep_standalone_package_contract(self) -> None:
        required = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "pyproject.toml",
            "agent-tool.json",
            "docs/AGENTIC_USAGE.md",
        }

        missing: list[str] = []
        for tool in sorted(EXISTING_TOOLS):
            for rel_path in sorted(required):
                if not (ROOT / tool / rel_path).exists():
                    missing.append(f"{tool}/{rel_path}")

        self.assertEqual([], missing)

    def test_umbrella_cli_contract_files_exist(self) -> None:
        required = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "pyproject.toml",
            "agent-tool.json",
            "docs/AGENTIC_USAGE.md",
            "examples/godot-project-doctor.toml",
            "src/godot_project_doctor/cli.py",
            "src/godot_project_doctor/runner.py",
            "src/godot_project_doctor/reports.py",
            "tests/test_cli.py",
        }

        missing = sorted(rel_path for rel_path in required if not (ROOT / "godot-project-doctor" / rel_path).exists())
        self.assertEqual([], missing)

    def test_github_action_contract_files_exist(self) -> None:
        required = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "agent-tool.json",
            "action.yml",
            "tests/test_action_metadata.py",
        }

        missing = sorted(rel_path for rel_path in required if not (ROOT / "godot-ci-doctor-action" / rel_path).exists())
        self.assertEqual([], missing)

    def test_repository_automation_files_exist(self) -> None:
        required = {
            ".gitignore",
            "pyproject.toml",
            ".github/workflows/portfolio-ci.yml",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/pull_request_template.md",
        }

        missing = sorted(rel_path for rel_path in required if not (ROOT / rel_path).exists())
        self.assertEqual([], missing)

    def test_agent_manifest_verifier_covers_all_agent_projects(self) -> None:
        self.assertTrue((EXISTING_TOOLS | NEW_PROJECTS).issubset(set(verify_agent_interfaces.TOOLS)))

    def test_public_files_do_not_reference_private_project_names(self) -> None:
        ignored_dirs = {".git", ".pytest_cache", "__pycache__", "build", "dist", ".venv", "venv"}
        text_suffixes = {
            ".cfg",
            ".gd",
            ".html",
            ".json",
            ".md",
            ".py",
            ".toml",
            ".txt",
            ".yml",
            ".yaml",
        }

        matches: list[str] = []
        for path in ROOT.rglob("*"):
            if any(part in ignored_dirs for part in path.parts):
                continue
            if not path.is_file() or path.suffix.lower() not in text_suffixes:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in PRIVATE_TERMS:
                if term in text:
                    matches.append(f"{path.relative_to(ROOT)}: {term}")

        self.assertEqual([], matches)

    def test_public_files_do_not_use_placeholder_repository_urls(self) -> None:
        placeholders = (
            "github.com/" + "example",
            "owner/" + "godot-production-toolkit",
            "OWNER/" + "godot-production-toolkit",
            "your-" + "user",
        )
        ignored_dirs = {".git", ".pytest_cache", "__pycache__", "build", "dist", ".venv", "venv"}
        text_suffixes = {".json", ".md", ".py", ".toml", ".yml", ".yaml"}

        matches: list[str] = []
        for path in ROOT.rglob("*"):
            if any(part in ignored_dirs for part in path.parts):
                continue
            if not path.is_file() or path.suffix.lower() not in text_suffixes:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for placeholder in placeholders:
                if placeholder in text:
                    matches.append(f"{path.relative_to(ROOT)}: {placeholder}")

        self.assertEqual([], matches)


if __name__ == "__main__":
    unittest.main()
