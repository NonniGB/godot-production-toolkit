from __future__ import annotations

from fnmatch import fnmatch
import os
from pathlib import Path

from godot_asset_doctor.import_parser import parse_import_file
from godot_asset_doctor.inspector import inspect_audio, inspect_png
from godot_asset_doctor.models import AssetRecord, AudioRecord, ImportMetadata, RuleSettings, ScanReport
from godot_asset_doctor.rules import evaluate_asset, evaluate_audio_asset


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

    if profile != "audio-mobile":
        for png_path in _iter_png_files(root, exclude_globs or []):
            import_metadata = _read_import_metadata(png_path)
            asset = AssetRecord(path=png_path, png=inspect_png(png_path), import_metadata=import_metadata)
            report.assets.append(asset)
            report.issues.extend(evaluate_asset(asset, profile=profile, settings=rule_settings))

    if profile in {"default", "android-mobile", "audio-mobile"}:
        for audio_path in _iter_audio_files(root, exclude_globs or []):
            import_metadata = _read_import_metadata(audio_path)
            asset = AudioRecord(path=audio_path, audio=inspect_audio(audio_path), import_metadata=import_metadata)
            report.audio_assets.append(asset)
            report.issues.extend(evaluate_audio_asset(asset, profile=profile, settings=rule_settings))

    report.issues.sort(key=lambda issue: (str(issue.path), issue.severity, issue.code))
    return report


def _iter_png_files(root: Path, exclude_globs: list[str]) -> list[Path]:
    return _iter_files(root, exclude_globs, {".png"})


def _iter_audio_files(root: Path, exclude_globs: list[str]) -> list[Path]:
    return _iter_files(root, exclude_globs, {".wav", ".ogg", ".mp3"})


def _iter_files(root: Path, exclude_globs: list[str], suffixes: set[str]) -> list[Path]:
    files: list[Path] = []

    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = [name for name in dir_names if name not in EXCLUDED_DIRS]
        current_path = Path(current_root)

        for file_name in file_names:
            path = current_path / file_name
            if path.suffix.lower() not in suffixes:
                continue
            relative_path = path.relative_to(root).as_posix()
            if any(fnmatch(relative_path, pattern) for pattern in exclude_globs):
                continue
            files.append(path)

    return sorted(files)


def _read_import_metadata(asset_path: Path) -> ImportMetadata | None:
    import_path = asset_path.with_name(f"{asset_path.name}.import")
    if not import_path.exists():
        return None
    return parse_import_file(import_path)
