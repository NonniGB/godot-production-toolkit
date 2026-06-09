from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib


PUBLISHED_PACKAGES = (
    "godot-asset-pipeline-doctor",
    "godot-export-preset-doctor",
    "godot-mobile-perf-doctor",
)

PACKAGE_VERSION_FILES = {
    "godot-asset-pipeline-doctor": {
        "init": "src/godot_asset_doctor/__init__.py",
        "cli": "src/godot_asset_doctor/cli.py",
        "cli_name": "godot-asset-doctor",
    },
    "godot-export-preset-doctor": {
        "init": "src/godot_export_doctor/__init__.py",
        "cli": "src/godot_export_doctor/cli.py",
        "cli_name": "godot-export-doctor",
    },
    "godot-mobile-perf-doctor": {
        "init": "src/godot_mobile_perf_doctor/__init__.py",
        "cli": "src/godot_mobile_perf_doctor/cli.py",
        "cli_name": "godot-mobile-perf-doctor",
    },
}

ACTION_REF_FILES = (
    "README.md",
    "godot-ci-doctor-action/README.md",
    "godot-ci-doctor-action/tool-manifest.json",
    "docs/PUBLICATION_GUIDE.md",
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
    _expect_text(root / "docs" / "RELEASE_CHECKLIST.md", f"git tag {tag}", errors)

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
