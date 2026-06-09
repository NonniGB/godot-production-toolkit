from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tomllib

import verify_tool_manifests
from verify_release_alignment import PUBLISHED_PACKAGES, check_release_alignment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print a local maintenance snapshot for the toolkit.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent
    snapshot = build_snapshot(root)

    if args.json:
        print(json.dumps(snapshot, indent=2, sort_keys=True))
    else:
        _print_text(snapshot)

    return 0 if snapshot["ok"] else 1


def build_snapshot(root: Path) -> dict[str, object]:
    root_metadata = _project_metadata(root / "pyproject.toml")
    project_metadata = json.loads((root / "project-metadata.json").read_text(encoding="utf-8"))
    release_errors = check_release_alignment(root)
    branch, commit = _git_identity(root)

    package_versions = {
        package: _project_metadata(root / package / "pyproject.toml")["version"] for package in PUBLISHED_PACKAGES
    }

    manifest_tools = list(verify_tool_manifests.TOOLS)
    metadata_tools = [tool["name"] for tool in project_metadata["tools"]]
    tool_count = int(root_metadata["tooling"].get("tool_count", 0))
    errors: list[str] = list(release_errors)

    if tool_count != len(manifest_tools):
        errors.append(f"pyproject tool_count is {tool_count}, expected {len(manifest_tools)}")
    if set(metadata_tools) != set(manifest_tools):
        errors.append("project-metadata.json tool list does not match tool manifests")

    return {
        "ok": not errors,
        "project": root_metadata["name"],
        "version": root_metadata["version"],
        "branch": branch,
        "commit": commit,
        "tool_count": len(manifest_tools),
        "published_packages": package_versions,
        "release_alignment": "ok" if not release_errors else "needs_attention",
        "errors": errors,
    }


def _project_metadata(path: Path) -> dict[str, object]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return {
        "name": str(data["project"]["name"]),
        "version": str(data["project"]["version"]),
        "tooling": data.get("tool", {}).get("godot-production-toolkit", {}),
    }


def _git_identity(root: Path) -> tuple[str, str]:
    branch = _git(root, "branch", "--show-current")
    commit = _git(root, "rev-parse", "--short", "HEAD")
    return branch or "unknown", commit or "unknown"


def _git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return completed.stdout.strip()


def _print_text(snapshot: dict[str, object]) -> None:
    print("Godot Production Toolkit maintenance snapshot")
    print(f"Version: {snapshot['version']}")
    print(f"Branch: {snapshot['branch']} ({snapshot['commit']})")
    print(f"Tools: {snapshot['tool_count']}")
    print(f"Release alignment: {snapshot['release_alignment']}")
    print("Published package versions:")
    for package, version in dict(snapshot["published_packages"]).items():
        print(f"- {package}: {version}")
    errors = list(snapshot["errors"])
    if errors:
        print("Issues:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Issues: none")


if __name__ == "__main__":
    raise SystemExit(main())
