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
DEFAULT_RESTRICTED_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".cs",
    ".dll",
    ".dylib",
    ".exe",
    ".gd",
    ".gdc",
    ".pck",
    ".ps1",
    ".so",
    ".zip",
}
DEV_PATH_PARTS = {".git", ".godot", ".import", "debug", "tests", "tmp"}
DEV_FILE_NAMES = {".env"}
DEV_FILE_EXTENSIONS = {".bak", ".key", ".log", ".pem", ".pfx"}
SKIPPED_SCAN_DIRS = {".git", ".godot", "__pycache__"}

RULE_CATALOG: dict[str, dict[str, str]] = {
    "content_id_conflict": {
        "title": "Content id conflict",
        "help": "Use a unique content id, mark the file as an intentional override, or adjust the pack order.",
    },
    "duplicate_content_id": {
        "title": "Duplicate content id",
        "help": "Keep content ids unique across pack entries so content replacement is explicit.",
    },
    "duplicate_file_path": {
        "title": "Duplicate file path",
        "help": "Keep one manifest entry per shipped path so overrides are explicit.",
    },
    "duplicate_pack_id": {
        "title": "Duplicate pack id",
        "help": "Give each pack a stable unique id so dependencies and overrides can be reviewed.",
    },
    "load_order_conflict": {
        "title": "Load order conflict",
        "help": "Declare intentional overrides or change pack order so resource ownership is clear.",
    },
    "missing_file_path": {
        "title": "Missing file path",
        "help": "Every shipped resource entry needs a stable path for review and diffing.",
    },
    "missing_pack_id": {
        "title": "Missing pack id",
        "help": "Add stable pack identity fields before publishing or comparing pack versions.",
    },
    "missing_pack_version": {
        "title": "Missing pack version",
        "help": "Add stable pack identity fields before publishing or comparing pack versions.",
    },
    "override_not_allowed": {
        "title": "Override not allowed",
        "help": "Pass --allow-overrides for expected patch packs, or remove the override declaration.",
    },
    "pack_absolute_path": {
        "title": "Absolute path",
        "help": "Use Godot project paths so pack reviews are portable across machines.",
    },
    "pack_dependencies_not_list": {
        "title": "Dependencies are not a list",
        "help": "Use a list of dependency objects such as {'id': 'base_pack'} or simple id strings.",
    },
    "pack_dependency_duplicate_id": {
        "title": "Duplicate dependency id",
        "help": "Keep each dependency id once so release review is easier to read.",
    },
    "pack_dependency_missing": {
        "title": "Missing dependency pack",
        "help": "Add the dependency pack to the load-order command or remove the stale dependency.",
    },
    "pack_dependency_missing_id": {
        "title": "Dependency missing id",
        "help": "Give every dependency a stable id so load order checks can match it to another pack.",
    },
    "pack_dependency_order": {
        "title": "Dependency loaded too late",
        "help": "Load dependency packs before packs that extend or override them.",
    },
    "pack_dev_or_private_file": {
        "title": "Development or private file",
        "help": "Review whether editor caches, logs, backups, tests, or key material should be shipped in the pack.",
    },
    "pack_duplicate_path_case_insensitive": {
        "title": "Case-insensitive path collision",
        "help": "Avoid case-only path differences because Windows and macOS users may see collisions.",
    },
    "pack_file_removed": {
        "title": "Pack file removed",
        "help": "Check whether the removal is intended before publishing the pack update.",
    },
    "pack_non_res_path": {
        "title": "Non-res path",
        "help": "Use stable project paths such as res://addons/example/file.tres in pack manifests.",
    },
    "pack_path_traversal": {
        "title": "Path traversal",
        "help": "Pack manifests should not contain paths that can escape the intended project tree.",
    },
    "pack_self_dependency": {
        "title": "Self dependency",
        "help": "Remove self-dependencies so load-order checks describe real pack relationships.",
    },
    "pack_unsafe_file_type": {
        "title": "Unsafe file type",
        "help": "Script, native binary, archive, and packed-project files can be legitimate, but review them before distribution.",
    },
    "restricted_pack_executable_file": {
        "title": "Restricted pack executable file",
        "help": "Remove executable, script, archive, or native-library files, or allow the extension explicitly for a reviewed scripted-pack workflow.",
    },
    "unknown_base_reference": {
        "title": "Unknown base reference",
        "help": "Check the base manifest or update the content pack dependency.",
    },
}


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
    _content_id_policy(files, findings)
    _duplicate_paths(files, findings)
    _override_policy(files, allow_overrides, findings)
    _reference_policy(files, base_ids, findings)
    _path_policy(files, findings)
    configured_unsafe_extensions = set(DEFAULT_UNSAFE_EXTENSIONS)
    if unsafe_extensions:
        configured_unsafe_extensions.update(unsafe_extensions)
    _unsafe_file_policy(files, configured_unsafe_extensions, findings)

    findings = _enrich_findings(findings)
    risk = _risk_summary(findings)
    summary = {
        "packs": 1,
        "files": len(files),
        "dependencies": len(data.get("dependencies", []) if isinstance(data.get("dependencies"), list) else []),
        "content_ids": _content_id_count(files),
        "errors": sum(1 for finding in findings if finding["severity"] == "error"),
        "warnings": sum(1 for finding in findings if finding["severity"] == "warning"),
        "risk_score": risk["score"],
        "risk_level": risk["level"],
    }
    return {
        "tool": "godot-pack-mod-doctor",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "pack_manifest_check",
        "metadata": _metadata(),
        "summary": summary,
        "pack": {
            "id": str(data.get("id", "")),
            "version": str(data.get("version", "")),
        },
        "risk": risk,
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
    added_candidates = sorted(set(current_files) - set(baseline_files))
    removed_candidates = sorted(set(baseline_files) - set(current_files))
    moved = _moved_files(removed_candidates, added_candidates, baseline_files, current_files)
    moved_from = {item["from"] for item in moved}
    moved_to = {item["to"] for item in moved}
    added = [path for path in added_candidates if path not in moved_to]
    removed = [path for path in removed_candidates if path not in moved_from]
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
    findings = _enrich_findings(findings)
    risk = _risk_summary(findings)
    summary = {
        "packs": 2,
        "files": len(current_files),
        "dependencies": len(current_data.get("dependencies", []) if isinstance(current_data.get("dependencies"), list) else []),
        "content_ids": _content_id_count(list(current_files.values())),
        "added": len(added),
        "removed": len(removed),
        "changed": len(changed),
        "moved": len(moved),
        "errors": 0,
        "warnings": len(findings),
        "risk_score": risk["score"],
        "risk_level": risk["level"],
    }
    return {
        "tool": "godot-pack-mod-doctor",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "pack_manifest_diff",
        "metadata": _metadata(),
        "summary": summary,
        "baseline": str(baseline),
        "current": str(current),
        "diff": {"added": added, "removed": removed, "changed": changed, "moved": moved},
        "risk": risk,
        "findings": findings,
    }


def load_order(manifests: list[Path]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    owners: dict[str, str] = {}
    content_owners: dict[str, tuple[str, str]] = {}
    pack_positions: dict[str, int] = {}
    packs: list[dict[str, Any]] = []
    for index, manifest in enumerate(manifests):
        data = _load_manifest(manifest)
        pack_id = str(data.get("id") or manifest.stem)
        files = [item for item in data.get("files", []) if isinstance(item, dict)]
        _dependency_policy(data, findings)
        _content_id_policy(files, findings)
        dependencies = _dependency_ids(data.get("dependencies"))
        dependency_count = _dependency_entry_count(data.get("dependencies"))
        content_ids = [content_id for item in files for content_id in _file_content_ids(item)]
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
        packs.append(
            {
                "id": pack_id,
                "path": str(manifest),
                "files": len(files),
                "dependencies": dependencies,
                "dependency_count": dependency_count,
                "content_ids": content_ids,
                "content_id_count": len(content_ids),
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
            for content_id in _file_content_ids(item):
                previous_content_owner = content_owners.get(content_id)
                if previous_content_owner and not item.get("overrides"):
                    previous_pack, previous_path = previous_content_owner
                    if previous_pack != pack_id:
                        findings.append(
                            {
                                "rule_id": "content_id_conflict",
                                "severity": "warning",
                                "message": (
                                    f"{pack_id} ships content id {content_id!r} in {path!r} "
                                    f"after {previous_pack} already used it in {previous_path!r}."
                                ),
                                "rule_help": (
                                    "Use a unique content id, mark the file as an intentional override, "
                                    "or adjust the pack order."
                                ),
                            }
                        )
                content_owners[content_id] = (pack_id, path)
    _load_order_dependency_findings(packs, pack_positions, findings)
    findings = _enrich_findings(findings)
    errors = sum(1 for finding in findings if finding["severity"] == "error")
    warnings = sum(1 for finding in findings if finding["severity"] == "warning")
    risk = _risk_summary(findings)
    return {
        "tool": "godot-pack-mod-doctor",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "pack_load_order",
        "metadata": _metadata(),
        "summary": {
            "packs": len(packs),
            "files": len(owners),
            "dependencies": sum(int(pack["dependency_count"]) for pack in packs),
            "content_ids": sum(int(pack["content_id_count"]) for pack in packs),
            "errors": errors,
            "warnings": warnings,
            "risk_score": risk["score"],
            "risk_level": risk["level"],
        },
        "packs": packs,
        "risk": risk,
        "findings": findings,
    }


def security_check(path: Path, allowed_extensions: set[str] | None = None) -> dict[str, Any]:
    data = _load_manifest(path)
    files = [item for item in data.get("files", []) if isinstance(item, dict)]
    allowed = {_normalize_extension(extension) for extension in (allowed_extensions or set())}
    restricted_extensions = DEFAULT_RESTRICTED_EXTENSIONS - allowed
    findings: list[dict[str, str]] = []

    for item in files:
        pack_path = str(item.get("path", "")).strip().replace("\\", "/")
        if not pack_path:
            continue
        suffix = Path(pack_path).suffix.lower()
        if suffix in restricted_extensions:
            findings.append(
                {
                    "rule_id": "restricted_pack_executable_file",
                    "severity": "error",
                    "message": f"{pack_path!r} uses restricted extension {suffix!r}.",
                    "rule_help": "Remove executable, script, archive, or native-library files, or allow the extension explicitly for a reviewed scripted-pack workflow.",
                }
            )

    findings = _enrich_findings(findings)
    risk = _risk_summary(findings)
    summary = {
        "packs": 1,
        "files": len(files),
        "dependencies": _dependency_entry_count(data.get("dependencies", [])),
        "content_ids": _content_id_count(files),
        "restricted_extensions": len(restricted_extensions),
        "allowed_extensions": len(allowed),
        "errors": sum(1 for finding in findings if finding["severity"] == "error"),
        "warnings": sum(1 for finding in findings if finding["severity"] == "warning"),
        "risk_score": risk["score"],
        "risk_level": risk["level"],
    }
    return {
        "tool": "godot-pack-mod-doctor",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "pack_security_check",
        "metadata": _metadata(),
        "summary": summary,
        "pack": {
            "id": str(data.get("id", "")),
            "version": str(data.get("version", "")),
        },
        "policy": {
            "name": "restricted-pack",
            "restricted_extensions": sorted(restricted_extensions),
            "allowed_extensions": sorted(allowed),
        },
        "risk": risk,
        "findings": findings,
    }


def render(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if output_format == "markdown":
        return _markdown(report)
    return _text(report)


def _metadata() -> dict[str, Any]:
    return {"rules": {rule_id: dict(rule) for rule_id, rule in RULE_CATALOG.items()}}


def _enrich_findings(findings: list[dict[str, str]]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    for finding in findings:
        rule = RULE_CATALOG.get(finding["rule_id"], {})
        updated = dict(finding)
        if "title" in rule:
            updated.setdefault("rule_title", rule["title"])
        if "help" in rule:
            updated.setdefault("rule_help", rule["help"])
        enriched.append(updated)
    return enriched


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


def _content_id_policy(files: list[dict[str, Any]], findings: list[dict[str, str]]) -> None:
    seen: dict[str, str] = {}
    for item in files:
        path = str(item.get("path", "<missing>")).strip() or "<missing>"
        for content_id in _file_content_ids(item):
            previous_path = seen.get(content_id)
            if previous_path:
                findings.append(
                    {
                        "rule_id": "duplicate_content_id",
                        "severity": "error",
                        "message": (
                            f"Content id {content_id!r} is declared by both "
                            f"{previous_path!r} and {path!r}."
                        ),
                        "rule_help": (
                            "Keep content ids unique inside a pack so saves, references, "
                            "and patch reviews do not become ambiguous."
                        ),
                    }
                )
            seen[content_id] = path


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


def _moved_files(
    removed: list[str],
    added: list[str],
    baseline_files: dict[str, dict[str, Any]],
    current_files: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    moved: list[dict[str, str]] = []
    used_added: set[str] = set()
    for removed_path in removed:
        removed_signature = _move_signature(baseline_files[removed_path])
        if removed_signature is None:
            continue
        for added_path in added:
            if added_path in used_added:
                continue
            if removed_signature == _move_signature(current_files[added_path]):
                moved.append({"from": removed_path, "to": added_path})
                used_added.add(added_path)
                break
    return moved


def _move_signature(item: dict[str, Any]) -> tuple[Any, ...] | None:
    content_ids = tuple(_file_content_ids(item))
    sha256 = str(item.get("sha256", "")).strip()
    size = item.get("size")
    if sha256:
        return ("sha256", sha256, size)
    if content_ids and size is not None:
        return ("content", content_ids, size)
    if content_ids and _stable_file_payload(item):
        return ("content", content_ids, tuple(sorted(_stable_file_payload(item).items())))
    return None


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


def _content_id_count(files: list[dict[str, Any]]) -> int:
    return sum(len(_file_content_ids(item)) for item in files)


def _file_content_ids(item: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for key in ("id", "content_id"):
        value = str(item.get(key, "")).strip()
        if value and value not in ids:
            ids.append(value)
    content_ids = item.get("content_ids", [])
    if isinstance(content_ids, list):
        for value in content_ids:
            content_id = str(value).strip()
            if content_id and content_id not in ids:
                ids.append(content_id)
    return ids


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


def _risk_summary(findings: list[dict[str, str]]) -> dict[str, Any]:
    errors = sum(1 for finding in findings if finding["severity"] == "error")
    warnings = sum(1 for finding in findings if finding["severity"] == "warning")
    level = "blocked" if errors else "attention" if warnings else "ready"
    score = errors * 100 + warnings * 10
    reasons: list[str] = []
    for finding in findings:
        rule_id = finding["rule_id"]
        if rule_id not in reasons:
            reasons.append(rule_id)
        if len(reasons) == 5:
            break
    return {"level": level, "score": score, "reasons": reasons}


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Pack Mod Doctor",
        (
            f"Files: {summary['files']} | Dependencies: {summary['dependencies']} | "
            f"Errors: {summary['errors']} | Warnings: {summary['warnings']}"
        ),
        f"Risk: {summary.get('risk_level', 'ready')} ({summary.get('risk_score', 0)})",
    ]
    if report.get("kind") == "pack_manifest_diff":
        diff = report["diff"]
        lines.append(
            f"Added: {len(diff['added'])} | Removed: {len(diff['removed'])} | "
            f"Changed: {len(diff['changed'])} | Moved: {len(diff.get('moved', []))}"
        )
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
        f"| Content IDs | {summary.get('content_ids', 0)} |",
        f"| Errors | {summary['errors']} |",
        f"| Warnings | {summary['warnings']} |",
        f"| Risk | {summary.get('risk_level', 'ready')} ({summary.get('risk_score', 0)}) |",
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
                f"- Moved: {_moved_summary(diff.get('moved', []))}",
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


def _moved_summary(moved: object) -> str:
    if not isinstance(moved, list) or not moved:
        return "-"
    pairs = []
    for item in moved:
        if not isinstance(item, dict):
            continue
        pairs.append(f"{item.get('from', '?')} -> {item.get('to', '?')}")
    return ", ".join(pairs) or "-"
