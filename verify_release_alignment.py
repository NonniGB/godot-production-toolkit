from __future__ import annotations

import argparse
import json
from pathlib import Path
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
    action_ref = f"@{tag}"
    errors: list[str] = []

    _expect_text(root / "CHANGELOG.md", f"## {version}", errors)

    for rel_path in ACTION_REF_FILES:
        _expect_text(root / rel_path, action_ref, errors)

    for package in PUBLISHED_PACKAGES:
        package_root = root / package
        package_version = _project_version(package_root / "pyproject.toml")
        _expect_text(package_root / "CHANGELOG.md", f"## {package_version}", errors)
        _expect_text(package_root / str(PACKAGE_VERSION_FILES[package]["init"]), f'__version__ = "{package_version}"', errors)
        _expect_text(
            package_root / str(PACKAGE_VERSION_FILES[package]["cli"]),
            f'{PACKAGE_VERSION_FILES[package]["cli_name"]} {package_version}',
            errors,
        )

    return errors


def _project_version(path: Path) -> str:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def _expect_text(path: Path, expected: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if expected not in text:
        errors.append(f"{path.as_posix()} does not contain {expected!r}")


if __name__ == "__main__":
    raise SystemExit(main())
