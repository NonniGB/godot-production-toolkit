import re
import unittest
from pathlib import Path
import verify_tool_manifests


ROOT = Path(__file__).resolve().parents[1]

EXISTING_TOOLS = {
    "gdscript-api-comment-coverage",
    "godot-asset-pipeline-doctor",
    "godot-content-graph-doctor",
    "godot-export-preset-doctor",
    "godot-gdscript-architecture-guard",
    "godot-input-map-auditor",
    "godot-localization-qa-guard",
    "godot-mobile-perf-doctor",
    "godot-pack-mod-doctor",
    "godot-release-dashboard-kit",
    "godot-runtime-telemetry-lab",
    "godot-save-schema-guard",
    "godot-scenario-report-kit",
    "godot-scene-signal-auditor",
    "godot-visual-smoke-test-kit",
    "pixel-space-asset-toolkit",
}

NEW_PROJECTS = {
    "godot-project-doctor",
    "godot-ci-doctor-action",
    "godot-release-dashboard-action",
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
        ("jo", "hn", "tur", "be", "field"),
        ("turbe", "field"),
        ("g", "mail", ".", "com"),
    )
)

SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{16,}"),
)


class RepositoryStructureTests(unittest.TestCase):
    def test_expected_projects_exist(self) -> None:
        missing = sorted(name for name in EXISTING_TOOLS | NEW_PROJECTS if not (ROOT / name).is_dir())
        self.assertEqual([], missing)

    def test_existing_tools_keep_standalone_package_layout(self) -> None:
        required = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "pyproject.toml",
            "tool-manifest.json",
            "docs/AUTOMATION.md",
        }

        missing: list[str] = []
        for tool in sorted(EXISTING_TOOLS):
            for rel_path in sorted(required):
                if not (ROOT / tool / rel_path).exists():
                    missing.append(f"{tool}/{rel_path}")

        self.assertEqual([], missing)

    def test_umbrella_cli_package_files_exist(self) -> None:
        required = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "pyproject.toml",
            "tool-manifest.json",
            "docs/AUTOMATION.md",
            "examples/godot-project-doctor.toml",
            "src/godot_project_doctor/cli.py",
            "src/godot_project_doctor/runner.py",
            "src/godot_project_doctor/reports.py",
            "tests/test_cli.py",
        }

        missing = sorted(rel_path for rel_path in required if not (ROOT / "godot-project-doctor" / rel_path).exists())
        self.assertEqual([], missing)

    def test_github_action_files_exist(self) -> None:
        required = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "tool-manifest.json",
            "action.yml",
            "tests/test_action_metadata.py",
        }

        missing = sorted(rel_path for rel_path in required if not (ROOT / "godot-ci-doctor-action" / rel_path).exists())
        self.assertEqual([], missing)

    def test_release_dashboard_action_files_exist(self) -> None:
        required = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "tool-manifest.json",
            "action.yml",
            "tests/test_action_metadata.py",
        }

        missing = sorted(
            rel_path for rel_path in required if not (ROOT / "godot-release-dashboard-action" / rel_path).exists()
        )
        self.assertEqual([], missing)

    def test_repository_automation_files_exist(self) -> None:
        required = {
            ".gitignore",
            "pyproject.toml",
            ".github/workflows/ci.yml",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/pull_request_template.md",
        }

        missing = sorted(rel_path for rel_path in required if not (ROOT / rel_path).exists())
        self.assertEqual([], missing)

    def test_tool_manifest_verifier_covers_all_projects(self) -> None:
        self.assertTrue((EXISTING_TOOLS | NEW_PROJECTS).issubset(set(verify_tool_manifests.TOOLS)))

    def test_public_files_do_not_reference_private_project_names(self) -> None:
        ignored_dirs = {".git", ".serena", ".pytest_cache", "__pycache__", "build", "dist", ".venv", "venv"}
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

    def test_public_files_do_not_reference_local_workspace_paths(self) -> None:
        ignored_dirs = {".git", ".serena", ".pytest_cache", "__pycache__", "build", "dist", ".venv", "venv"}
        text_suffixes = {".cfg", ".gd", ".html", ".json", ".md", ".py", ".toml", ".txt", ".yml", ".yaml"}
        path_terms = tuple(
            "".join(parts)
            for parts in (
                ("C:", "\\", "Temp"),
                ("C:", "/", "Temp"),
                ("C:", "\\", "Users"),
                ("C:", "/", "Users"),
            )
        )

        matches: list[str] = []
        for path in ROOT.rglob("*"):
            if any(part in ignored_dirs for part in path.parts):
                continue
            if not path.is_file() or path.suffix.lower() not in text_suffixes:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in path_terms:
                if term in text:
                    matches.append(f"{path.relative_to(ROOT)}: {term}")

        self.assertEqual([], matches)

    def test_public_files_do_not_contain_likely_secret_tokens(self) -> None:
        ignored_dirs = {".git", ".serena", ".pytest_cache", "__pycache__", "build", "dist", ".venv", "venv"}
        text_suffixes = {".cfg", ".json", ".md", ".py", ".toml", ".txt", ".yml", ".yaml"}

        matches: list[str] = []
        for path in ROOT.rglob("*"):
            if any(part in ignored_dirs for part in path.parts):
                continue
            if not path.is_file() or path.suffix.lower() not in text_suffixes:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    matches.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")

        self.assertEqual([], matches)

    def test_public_files_do_not_use_placeholder_repository_urls(self) -> None:
        placeholders = (
            "github.com/" + "example",
            "owner/" + "godot-production-toolkit",
            "OWNER/" + "godot-production-toolkit",
            "your-" + "user",
        )
        ignored_dirs = {".git", ".serena", ".pytest_cache", "__pycache__", "build", "dist", ".venv", "venv"}
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
