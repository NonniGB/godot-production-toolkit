from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tomllib


PUBLISHED_PACKAGES = (
    "gdscript-api-comment-coverage",
    "godot-asset-pipeline-doctor",
    "godot-content-graph-doctor",
    "godot-export-preset-doctor",
    "godot-gdscript-architecture-guard",
    "godot-input-map-auditor",
    "godot-localization-qa-guard",
    "godot-mobile-perf-doctor",
    "godot-mobile-ui-doctor",
    "godot-pack-mod-doctor",
    "godot-production-doctor",
    "godot-release-dashboard-kit",
    "godot-runtime-telemetry-lab",
    "godot-save-schema-guard",
    "godot-scenario-report-kit",
    "godot-scene-signal-auditor",
    "godot-visual-smoke-test-kit",
    "pixel-space-asset-toolkit",
)

PACKAGE_VERSION_FILES = {
    "gdscript-api-comment-coverage": {
        "init": "src/gdscript_api_coverage/__init__.py",
        "cli": "src/gdscript_api_coverage/cli.py",
        "cli_name": "gdscript-api-coverage",
    },
    "godot-asset-pipeline-doctor": {
        "init": "src/godot_asset_doctor/__init__.py",
        "cli": "src/godot_asset_doctor/cli.py",
        "cli_name": "godot-asset-doctor",
    },
    "godot-content-graph-doctor": {
        "init": "src/godot_content_graph_doctor/__init__.py",
        "cli": "src/godot_content_graph_doctor/cli.py",
        "cli_name": "godot-content-graph",
    },
    "godot-export-preset-doctor": {
        "init": "src/godot_export_doctor/__init__.py",
        "cli": "src/godot_export_doctor/cli.py",
        "cli_name": "godot-export-doctor",
    },
    "godot-gdscript-architecture-guard": {
        "init": "src/godot_architecture_guard/__init__.py",
        "cli": "src/godot_architecture_guard/cli.py",
        "cli_name": "godot-architecture-guard",
    },
    "godot-input-map-auditor": {
        "init": "src/godot_input_auditor/__init__.py",
        "cli": "src/godot_input_auditor/cli.py",
        "cli_name": "godot-input-audit",
    },
    "godot-localization-qa-guard": {
        "init": "src/godot_l10n_guard/__init__.py",
        "cli": "src/godot_l10n_guard/cli.py",
        "cli_name": "godot-l10n-guard",
    },
    "godot-mobile-perf-doctor": {
        "init": "src/godot_mobile_perf_doctor/__init__.py",
        "cli": "src/godot_mobile_perf_doctor/cli.py",
        "cli_name": "godot-mobile-perf-doctor",
    },
    "godot-mobile-ui-doctor": {
        "init": "src/godot_mobile_ui_doctor/__init__.py",
        "cli": "src/godot_mobile_ui_doctor/cli.py",
        "cli_name": "godot-mobile-ui-doctor",
    },
    "godot-pack-mod-doctor": {
        "init": "src/godot_pack_mod_doctor/__init__.py",
        "cli": "src/godot_pack_mod_doctor/cli.py",
        "cli_name": "godot-pack-mod-doctor",
    },
    "godot-production-doctor": {
        "init": "src/godot_project_doctor/__init__.py",
        "cli": "src/godot_project_doctor/cli.py",
        "cli_name": "godot-project-doctor",
        "cli_aliases": ("godot-production-doctor",),
    },
    "godot-release-dashboard-kit": {
        "init": "src/godot_release_dashboard_kit/__init__.py",
        "cli": "src/godot_release_dashboard_kit/cli.py",
        "cli_name": "godot-release-dashboard",
    },
    "godot-runtime-telemetry-lab": {
        "init": "src/godot_runtime_telemetry_lab/__init__.py",
        "cli": "src/godot_runtime_telemetry_lab/cli.py",
        "cli_name": "godot-telemetry-lab",
    },
    "godot-save-schema-guard": {
        "init": "src/godot_save_guard/__init__.py",
        "cli": "src/godot_save_guard/cli.py",
        "cli_name": "godot-save-guard",
    },
    "godot-scenario-report-kit": {
        "init": "src/godot_scenario_report_kit/__init__.py",
        "cli": "src/godot_scenario_report_kit/cli.py",
        "cli_name": "godot-scenario-report",
    },
    "godot-scene-signal-auditor": {
        "init": "src/godot_signal_auditor/__init__.py",
        "cli": "src/godot_signal_auditor/cli.py",
        "cli_name": "godot-signal-audit",
    },
    "godot-visual-smoke-test-kit": {
        "init": "src/godot_visual_smoke/__init__.py",
        "cli": "src/godot_visual_smoke/cli.py",
        "cli_name": "godot-visual-smoke",
    },
    "pixel-space-asset-toolkit": {
        "init": "src/pixel_space_assets/__init__.py",
        "cli": "src/pixel_space_assets/cli.py",
        "cli_name": "pixel-space-assets",
    },
}

ACTION_REF_FILES = (
    "README.md",
    "godot-ci-doctor-action/README.md",
    "godot-ci-doctor-action/tool-manifest.json",
)
PUBLIC_ACTION_REVISION = "06d66f390a45743b4437d09bc63eb8778b52c0a4"

PUBLIC_ACTION_PROJECTS = {
    "godot-ci-doctor-action",
    "godot-release-dashboard-action",
}

PACKAGE_FINDER_PATH = "docs/PACKAGE_FINDER.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check release-facing version references stay aligned.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable check results.")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent
    errors = check_release_alignment(root)

    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors}, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(error)
    else:
        print("Release alignment looks good.")

    return 1 if errors else 0


def check_release_alignment(root: Path) -> list[str]:
    version = _project_version(root / "pyproject.toml")
    tag = f"v{version}"
    action_ref = f"@{PUBLIC_ACTION_REVISION}"
    errors: list[str] = []

    _expect_text(root / "CHANGELOG.md", f"## {version}", errors)

    for rel_path in ACTION_REF_FILES:
        _expect_text(root / rel_path, action_ref, errors)

    for package in PUBLISHED_PACKAGES:
        package_root = root / package
        package_version = _project_version(package_root / "pyproject.toml")
        pyproject_data = _pyproject_data(package_root / "pyproject.toml")
        tool_manifest = json.loads((package_root / "tool-manifest.json").read_text(encoding="utf-8"))
        cli_name = PACKAGE_VERSION_FILES[package]["cli_name"]

        if pyproject_data.get("project", {}).get("name") != package:
            errors.append(f"{package}/pyproject.toml project.name does not match package directory")
        if cli_name not in pyproject_data.get("project", {}).get("scripts", {}):
            errors.append(f"{package}/pyproject.toml does not define console script {cli_name!r}")
        for alias in PACKAGE_VERSION_FILES[package].get("cli_aliases", ()):
            if alias not in pyproject_data.get("project", {}).get("scripts", {}):
                errors.append(f"{package}/pyproject.toml does not define console script alias {alias!r}")
        if tool_manifest.get("name") != package:
            errors.append(f"{package}/tool-manifest.json name does not match package directory")
        if tool_manifest.get("entrypoint") != cli_name:
            errors.append(f"{package}/tool-manifest.json entrypoint does not match {cli_name!r}")
        if tool_manifest.get("interfaces", {}).get("cli") is not True:
            errors.append(f"{package}/tool-manifest.json does not mark the CLI interface as true")

        _expect_text(package_root / "CHANGELOG.md", f"## {package_version}", errors)
        _expect_text(package_root / str(PACKAGE_VERSION_FILES[package]["init"]), f'__version__ = "{package_version}"', errors)
        _expect_text(
            package_root / str(PACKAGE_VERSION_FILES[package]["cli"]),
            f"{cli_name} {package_version}",
            errors,
        )

    errors.extend(_check_public_package_references(root))
    return errors


def _project_version(path: Path) -> str:
    return str(_pyproject_data(path)["project"]["version"])


def _pyproject_data(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _expect_text(path: Path, expected: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if expected not in text:
        errors.append(f"{path.as_posix()} does not contain {expected!r}")


def _check_public_package_references(root: Path) -> list[str]:
    errors: list[str] = []
    metadata_path = root / "project-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata_tools = {tool.get("name") for tool in metadata.get("tools", [])}
    expected_tools = set(PUBLISHED_PACKAGES) | PUBLIC_ACTION_PROJECTS
    missing_metadata = expected_tools - metadata_tools
    extra_metadata = metadata_tools - expected_tools
    if missing_metadata:
        errors.append(f"project-metadata.json is missing tools {sorted(missing_metadata)}")
    if extra_metadata:
        errors.append(f"project-metadata.json lists unknown tools {sorted(extra_metadata)}")

    for package in PUBLISHED_PACKAGES:
        metadata_entry = next((tool for tool in metadata.get("tools", []) if tool.get("name") == package), None)
        if metadata_entry and "cli" not in metadata_entry.get("interfaces", []):
            errors.append(f"project-metadata.json entry for {package} does not list the cli interface")

    package_finder_text = (root / PACKAGE_FINDER_PATH).read_text(encoding="utf-8")
    known_packages = set(PUBLISHED_PACKAGES)
    for package in PUBLISHED_PACKAGES:
        cli_name = PACKAGE_VERSION_FILES[package]["cli_name"]
        package_version = _project_version(root / package / "pyproject.toml")
        _expect_text(root / "README.md", f"python -m pip install {package}", errors)
        _expect_text(root / "README.md", f"https://pypi.org/project/{package}/", errors)
        _expect_text(root / "README.md", f"| `{package_version}` |", errors)
        _expect_text(root / PACKAGE_FINDER_PATH, f"python -m pip install {package}", errors)
        _expect_text(root / PACKAGE_FINDER_PATH, cli_name, errors)

    for package in sorted(_pip_install_packages(package_finder_text) - known_packages):
        errors.append(f"{PACKAGE_FINDER_PATH} references unknown install package {package!r}")

    return errors


def _pip_install_packages(text: str) -> set[str]:
    packages: set[str] = set()
    for match in re.finditer(r"python -m pip install ([^`|]+)", text):
        for token in match.group(1).split():
            if token.startswith("-") or "\\" in token or "/" in token or token == ".":
                continue
            packages.add(token)
    return packages


if __name__ == "__main__":
    raise SystemExit(main())
