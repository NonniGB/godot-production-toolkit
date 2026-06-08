from __future__ import annotations

from fnmatch import fnmatch
import os
from pathlib import Path

from godot_asset_doctor.import_parser import parse_import_file
from godot_asset_doctor.inspector import inspect_png
from godot_asset_doctor.models import AssetRecord, ImportMetadata, RuleSettings, ScanReport
from godot_asset_doctor.rules import evaluate_asset


EXCLUDED_DIRS = {
    ".git",
    ".godot",
    ".playwright-cli",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "docs",
    "logs",
    "node_modules",
    "test-results",
    "venv",
}


def scan_project(
    root: Path,
    profile: str = "default",
    exclude_globs: list[str] | None = None,
    rule_settings: RuleSettings | None = None,
) -> ScanReport:
    root = root.resolve()
    report = ScanReport(root=root, profile=profile)

    for png_path in _iter_png_files(root, exclude_globs or []):
        import_metadata = _read_import_metadata(png_path)
        asset = AssetRecord(path=png_path, png=inspect_png(png_path), import_metadata=import_metadata)
        report.assets.append(asset)
        report.issues.extend(evaluate_asset(asset, profile=profile, settings=rule_settings))

    report.issues.sort(key=lambda issue: (str(issue.path), issue.severity, issue.code))
    return report


def _iter_png_files(root: Path, exclude_globs: list[str]) -> list[Path]:
    files: list[Path] = []

    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = [name for name in dir_names if name not in EXCLUDED_DIRS]
        current_path = Path(current_root)

        for file_name in file_names:
            if not file_name.lower().endswith(".png"):
                continue
            path = current_path / file_name
            relative_path = path.relative_to(root).as_posix()
            if any(fnmatch(relative_path, pattern) for pattern in exclude_globs):
                continue
            files.append(path)

    return sorted(files)


def _read_import_metadata(png_path: Path) -> ImportMetadata | None:
    import_path = png_path.with_name(f"{png_path.name}.import")
    if not import_path.exists():
        return None
    return parse_import_file(import_path)
