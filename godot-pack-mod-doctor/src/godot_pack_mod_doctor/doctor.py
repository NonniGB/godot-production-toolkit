from __future__ import annotations

import hashlib
import json
from pathlib import Path, PureWindowsPath
from typing import Any

from . import __version__

DEFAULT_UNSAFE_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".cs",
    ".dll",
    ".dylib",
    ".exe",
    ".gd",
    ".pck",
    ".ps1",
    ".so",
    ".zip",
}
DEV_PATH_PARTS = {".git", ".godot", ".import", "debug", "tests", "tmp"}
DEV_FILE_NAMES = {".env"}
DEV_FILE_EXTENSIONS = {".bak", ".key", ".log", ".pem", ".pfx"}
SKIPPED_SCAN_DIRS = {".git", ".godot", "__pycache__"}


def check_manifest(
    path: Path,
    base: Path | None = None,
    allow_overrides: bool = False,
    unsafe_extensions: set[str] | None = None,
) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    base_ids = _base_ids(base) if base else set()
    files = [item for item in data.get("files", []) if isinstance(item, dict)]
    findings: list[dict[str, str]] = []

    _require_string(data, "id", "missing_pack_id", findings)
    _require_string(data, "version", "missing_pack_version", findings)
    _dependency_policy(data, findings)
    _duplicate_paths(files, findings)
    _override_policy(files, allow_overrides, findings)
    _reference_policy(files, base_ids, findings)
    _path_policy(files, findings)
    configured_unsafe_extensions = set(DEFAULT_UNSAFE_EXTENSIONS)
    if unsafe_extensions:
        configured_unsafe_extensions.update(unsafe_extensions)
    _unsafe_file_policy(files, configured_unsafe_extensions, findings)

    summary = {
        "packs": 1,
        "files": len(files),
        "dependencies": len(data.get("dependencies", []) if isinstance(data.get("dependencies"), list) else []),
        "errors": sum(1 for finding in findings if finding["severity"] == "error"),
        "warnings": sum(1 for finding in findings if finding["severity"] == "warning"),
    }
    return {
        "tool": "godot-pack-mod-doctor",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "pack_manifest_check",
        "summary": summary,
        "pack": {
            "id": str(data.get("id", "")),
            "version": str(data.get("version", "")),
        },
        "findings": findings,
    }


def manifest_from_folder(root: Path, pack_id: str, version: str) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    root = root.resolve()
    for file_path in _iter_pack_files(root):
        try:
            relative = file_path.resolve().relative_to(root)
        except ValueError:
            continue
        manifest_path = "res://" + relative.as_posix()
        files.append(
            {
                "path": manifest_path,
                "overrides": False,
                "size": file_path.stat().st_size,
                "sha256": _sha256(file_path),
            }
        )
    files.sort(key=lambda item: item["path"].lower())
    return {
        "id": pack_id,
        "version": version,
        "dependencies": [],
        "files": files,
    }


def diff_manifests(baseline: Path, current: Path) -> dict[str, Any]:
    baseline_data = _load_manifest(baseline)
    current_data = _load_manifest(current)
    baseline_files = _files_by_path(baseline_data)
    current_files = _files_by_path(current_data)
    added = sorted(set(current_files) - set(baseline_files))
    removed = sorted(set(baseline_files) - set(current_files))
    changed = [
        path
        for path in sorted(set(baseline_files) & set(current_files))
        if _stable_file_payload(baseline_files[path]) != _stable_file_payload(current_files[path])
    ]
    findings: list[dict[str, str]] = []
    for path in removed:
        findings.append(
            {
                "rule_id": "pack_file_removed",
                "severity": "warning",
                "message": f"{path!r} is present in the baseline pack but missing from the current pack.",
                "rule_help": "Check whether the removal is intended before publishing the pack update.",
            }
        )
    summary = {
        "packs": 2,
        "files": len(current_files),
        "dependencies": len(current_data.get("dependencies", []) if isinstance(current_data.get("dependencies"), list) else []),
        "added": len(added),
        "removed": len(removed),
        "changed": len(changed),
        "errors": 0,
        "warnings": len(findings),
    }
    return {
        "tool": "godot-pack-mod-doctor",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "pack_manifest_diff",
        "summary": summary,
        "baseline": str(baseline),
        "current": str(current),
        "diff": {"added": added, "removed": removed, "changed": changed},
        "findings": findings,
    }


def load_order(manifests: list[Path]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    owners: dict[str, str] = {}
    pack_positions: dict[str, int] = {}
    packs: list[dict[str, Any]] = []
    for index, manifest in enumerate(manifests):
        data = _load_manifest(manifest)
        pack_id = str(data.get("id") or manifest.stem)
        _dependency_policy(data, findings)
        dependencies = _dependency_ids(data.get("dependencies"))
        dependency_count = _dependency_entry_count(data.get("dependencies"))
        previous_index = pack_positions.get(pack_id)
        if previous_index is not None:
            findings.append(
                {
                    "rule_id": "duplicate_pack_id",
                    "severity": "error",
                    "message": (
                        f"{manifest} uses pack id {pack_id!r}, which was already used "
                        f"by pack at load order {previous_index}."
                    ),
                    "rule_help": "Give each pack a stable unique id so dependencies and overrides can be reviewed.",
                }
            )
        pack_positions.setdefault(pack_id, index)
        files = [item for item in data.get("files", []) if isinstance(item, dict)]
        packs.append(
            {
                "id": pack_id,
                "path": str(manifest),
                "files": len(files),
                "dependencies": dependencies,
                "dependency_count": dependency_count,
                "order": index,
            }
        )
        for item in files:
            path = str(item.get("path", "")).strip()
            if not path:
                continue
            previous_owner = owners.get(path)
            if previous_owner and not item.get("overrides"):
                findings.append(
                    {
                        "rule_id": "load_order_conflict",
                        "severity": "warning",
                        "message": f"{pack_id} ships {path!r} after {previous_owner} without declaring an override.",
                        "rule_help": "Declare intentional overrides or change pack order so resource ownership is clear.",
                    }
                )
            owners[path] = pack_id
    _load_order_dependency_findings(packs, pack_positions, findings)
    errors = sum(1 for finding in findings if finding["severity"] == "error")
    warnings = sum(1 for finding in findings if finding["severity"] == "warning")
    return {
        "tool": "godot-pack-mod-doctor",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "pack_load_order",
        "summary": {
            "packs": len(packs),
            "files": len(owners),
            "dependencies": sum(int(pack["dependency_count"]) for pack in packs),
            "errors": errors,
            "warnings": warnings,
        },
        "packs": packs,
        "findings": findings,
    }


def render(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if output_format == "markdown":
        return _markdown(report)
    return _text(report)


def _require_string(data: dict[str, Any], key: str, rule_id: str, findings: list[dict[str, str]]) -> None:
    if not str(data.get(key, "")).strip():
        findings.append(
            {
                "rule_id": rule_id,
                "severity": "error",
                "message": f"Pack manifest is missing a non-empty {key!r} field.",
                "rule_help": "Add stable pack identity fields before publishing or comparing pack versions.",
            }
        )


def _dependency_policy(data: dict[str, Any], findings: list[dict[str, str]]) -> None:
    dependencies = data.get("dependencies", [])
    if dependencies in (None, ""):
        return
    if not isinstance(dependencies, list):
        findings.append(
            {
                "rule_id": "pack_dependencies_not_list",
                "severity": "error",
                "message": "Pack dependencies must be a list.",
                "rule_help": "Use a list of dependency objects such as {'id': 'base_pack'} or simple id strings.",
            }
        )
        return
    seen: set[str] = set()
    for index, item in enumerate(dependencies):
        dependency_id = _dependency_id(item)
        if not dependency_id:
            findings.append(
                {
                    "rule_id": "pack_dependency_missing_id",
                    "severity": "error",
                    "message": f"Dependency entry {index} is missing a non-empty id.",
                    "rule_help": "Give every dependency a stable id so load order checks can match it to another pack.",
                }
            )
            continue
        if dependency_id == str(data.get("id") or "").strip():
            findings.append(
                {
                    "rule_id": "pack_self_dependency",
                    "severity": "error",
                    "message": f"Pack {dependency_id!r} lists itself as a dependency.",
                    "rule_help": "Remove self-dependencies so load-order checks describe real pack relationships.",
                }
            )
        if dependency_id in seen:
            findings.append(
                {
                    "rule_id": "pack_dependency_duplicate_id",
                    "severity": "warning",
                    "message": f"Dependency id {dependency_id!r} is listed more than once.",
                    "rule_help": "Keep each dependency id once so release review is easier to read.",
                }
            )
        seen.add(dependency_id)


def _load_order_dependency_findings(
    packs: list[dict[str, Any]],
    pack_positions: dict[str, int],
    findings: list[dict[str, str]],
) -> None:
    for pack in packs:
        pack_id = str(pack["id"])
        pack_index = int(pack["order"])
        for dependency in pack["dependencies"]:
            dependency_index = pack_positions.get(dependency)
            if dependency_index is None:
                findings.append(
                    {
                        "rule_id": "pack_dependency_missing",
                        "severity": "error",
                        "message": f"{pack_id} depends on missing pack {dependency!r}.",
                        "rule_help": "Add the dependency pack to the load-order command or remove the stale dependency.",
                    }
                )
            elif dependency_index > pack_index:
                findings.append(
                    {
                        "rule_id": "pack_dependency_order",
                        "severity": "warning",
                        "message": (
                            f"{pack_id} depends on {dependency!r}, but that pack appears later "
                            f"in the supplied load order."
                        ),
                        "rule_help": "Load dependency packs before packs that extend or override them.",
                    }
                )


def _duplicate_paths(files: list[dict[str, Any]], findings: list[dict[str, str]]) -> None:
    seen: set[str] = set()
    for item in files:
        path = str(item.get("path", "")).strip()
        if not path:
            findings.append(
                {
                    "rule_id": "missing_file_path",
                    "severity": "error",
                    "message": "A file entry is missing a path.",
                    "rule_help": "Every shipped resource entry needs a stable path for review and diffing.",
                }
            )
            continue
        if path in seen:
            findings.append(
                {
                    "rule_id": "duplicate_file_path",
                    "severity": "error",
                    "message": f"Pack manifest lists {path!r} more than once.",
                    "rule_help": "Keep one manifest entry per shipped path so overrides are explicit.",
                }
            )
        seen.add(path)


def _override_policy(files: list[dict[str, Any]], allow_overrides: bool, findings: list[dict[str, str]]) -> None:
    if allow_overrides:
        return
    for item in files:
        if item.get("overrides"):
            findings.append(
                {
                    "rule_id": "override_not_allowed",
                    "severity": "warning",
                    "message": f"{item.get('path', '<missing>')!r} declares an override while overrides are disabled.",
                    "rule_help": "Pass --allow-overrides for expected patch packs, or remove the override declaration.",
                }
            )


def _reference_policy(files: list[dict[str, Any]], base_ids: set[str], findings: list[dict[str, str]]) -> None:
    if not base_ids:
        return
    for item in files:
        for reference in item.get("references", []):
            ref = str(reference)
            if ref not in base_ids:
                findings.append(
                    {
                        "rule_id": "unknown_base_reference",
                        "severity": "error",
                        "message": f"{item.get('path', '<missing>')!r} references unknown base id {ref!r}.",
                        "rule_help": "Check the base manifest or update the content pack dependency.",
                    }
                )


def _path_policy(files: list[dict[str, Any]], findings: list[dict[str, str]]) -> None:
    seen_lower: dict[str, str] = {}
    for item in files:
        path = str(item.get("path", "")).strip().replace("\\", "/")
        if not path:
            continue
        if _looks_absolute_path(path):
            findings.append(
                {
                    "rule_id": "pack_absolute_path",
                    "severity": "warning",
                    "message": f"{path!r} looks like a local filesystem path.",
                    "rule_help": "Use stable project paths such as res://addons/example/file.tres in pack manifests.",
                }
            )
        if ".." in path.split("/"):
            findings.append(
                {
                    "rule_id": "pack_path_traversal",
                    "severity": "warning",
                    "message": f"{path!r} contains a parent-directory segment.",
                    "rule_help": "Pack manifests should not contain paths that can escape the intended project tree.",
                }
            )
        if not path.startswith("res://"):
            findings.append(
                {
                    "rule_id": "pack_non_res_path",
                    "severity": "warning",
                    "message": f"{path!r} is not under res://.",
                    "rule_help": "Use Godot project paths so pack reviews are portable across machines.",
                }
            )
        lower_path = path.lower()
        previous = seen_lower.get(lower_path)
        if previous and previous != path:
            findings.append(
                {
                    "rule_id": "pack_duplicate_path_case_insensitive",
                    "severity": "warning",
                    "message": f"{path!r} differs only by case from {previous!r}.",
                    "rule_help": "Avoid case-only path differences because Windows and macOS users may see collisions.",
                }
            )
        seen_lower[lower_path] = path


def _unsafe_file_policy(
    files: list[dict[str, Any]], unsafe_extensions: set[str], findings: list[dict[str, str]]
) -> None:
    normalized_extensions = {_normalize_extension(extension) for extension in unsafe_extensions}
    for item in files:
        path = str(item.get("path", "")).strip().replace("\\", "/")
        if not path:
            continue
        parts = [part for part in path.replace("res://", "", 1).split("/") if part]
        name = parts[-1].lower() if parts else ""
        suffix = Path(name).suffix.lower()
        if suffix in normalized_extensions:
            findings.append(
                {
                    "rule_id": "pack_unsafe_file_type",
                    "severity": "warning",
                    "message": f"{path!r} uses extension {suffix!r}, which often needs manual review in public packs.",
                    "rule_help": "Script, native binary, archive, and packed-project files can be legitimate, but review them before distribution.",
                }
            )
        if (
            any(part.lower() in DEV_PATH_PARTS for part in parts[:-1])
            or name in DEV_FILE_NAMES
            or suffix in DEV_FILE_EXTENSIONS
        ):
            findings.append(
                {
                    "rule_id": "pack_dev_or_private_file",
                    "severity": "warning",
                    "message": f"{path!r} looks like a development, debug, or private file.",
                    "rule_help": "Review whether editor caches, logs, backups, tests, or key material should be shipped in the pack.",
                }
            )


def _base_ids(path: Path | None) -> set[str]:
    if path is None:
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = set()
    for item in data.get("content", []):
        if isinstance(item, dict) and item.get("id"):
            ids.add(str(item["id"]))
    return ids


def _load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _dependency_ids(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    ids: list[str] = []
    for item in value:
        dependency_id = _dependency_id(item)
        if dependency_id:
            ids.append(dependency_id)
    return ids


def _dependency_entry_count(value: object) -> int:
    return len(value) if isinstance(value, list) else 0


def _dependency_id(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return str(value.get("id") or "").strip()
    return ""


def _files_by_path(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = [item for item in data.get("files", []) if isinstance(item, dict)]
    return {str(item.get("path", "")).strip(): item for item in files if str(item.get("path", "")).strip()}


def _stable_file_payload(item: dict[str, Any]) -> dict[str, Any]:
    return {key: item.get(key) for key in sorted(item) if key != "path"}


def _iter_pack_files(root: Path) -> list[Path]:
    if not root.exists() or not root.is_dir():
        raise ValueError(f"{root} is not a directory")
    files: list[Path] = []
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        relative_parts = file_path.relative_to(root).parts
        if any(part in SKIPPED_SCAN_DIRS for part in relative_parts[:-1]):
            continue
        try:
            resolved = file_path.resolve()
        except OSError:
            continue
        if not resolved.is_relative_to(root):
            continue
        files.append(file_path)
    return files


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_extension(extension: str) -> str:
    value = extension.strip().lower()
    return value if value.startswith(".") else f".{value}"


def _looks_absolute_path(path: str) -> bool:
    if path.startswith("res://"):
        return False
    return Path(path).is_absolute() or PureWindowsPath(path).is_absolute()


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Pack Mod Doctor",
        (
            f"Files: {summary['files']} | Dependencies: {summary['dependencies']} | "
            f"Errors: {summary['errors']} | Warnings: {summary['warnings']}"
        ),
    ]
    if report.get("kind") == "pack_manifest_diff":
        diff = report["diff"]
        lines.append(f"Added: {len(diff['added'])} | Removed: {len(diff['removed'])} | Changed: {len(diff['changed'])}")
    if report.get("kind") == "pack_load_order":
        lines.append(f"Packs: {summary['packs']}")
    for finding in report["findings"]:
        lines.append(f"- {finding['severity'].upper()} {finding['rule_id']}: {finding['message']}")
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Pack Mod Doctor",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Files | {summary['files']} |",
        f"| Dependencies | {summary['dependencies']} |",
        f"| Errors | {summary['errors']} |",
        f"| Warnings | {summary['warnings']} |",
        "",
    ]
    if report.get("kind") == "pack_manifest_diff":
        diff = report["diff"]
        lines.extend(
            [
                "## Diff",
                "",
                f"- Added: {', '.join(diff['added']) or '-'}",
                f"- Removed: {', '.join(diff['removed']) or '-'}",
                f"- Changed: {', '.join(diff['changed']) or '-'}",
                "",
            ]
        )
    if report.get("kind") == "pack_load_order":
        lines.extend(["## Load Order", "", "| Order | Pack | Files | Dependencies |", "|---:|---|---:|---|"])
        for pack in report["packs"]:
            dependencies = ", ".join(pack.get("dependencies", [])) or "-"
            lines.append(f"| {pack['order']} | {pack['id']} | {pack['files']} | {dependencies} |")
        lines.append("")
    lines.extend(["## Findings", ""])
    if not report["findings"]:
        lines.append("No pack manifest findings.")
    else:
        lines.extend(["| Severity | Rule | Message |", "|---|---|---|"])
        for finding in report["findings"]:
            lines.append(f"| {finding['severity']} | `{finding['rule_id']}` | {finding['message']} |")
    return "\n".join(lines)
