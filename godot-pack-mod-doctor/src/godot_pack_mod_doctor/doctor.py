from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import __version__


def check_manifest(path: Path, base: Path | None = None, allow_overrides: bool = False) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    base_ids = _base_ids(base) if base else set()
    files = [item for item in data.get("files", []) if isinstance(item, dict)]
    findings: list[dict[str, str]] = []

    _require_string(data, "id", "missing_pack_id", findings)
    _require_string(data, "version", "missing_pack_version", findings)
    _duplicate_paths(files, findings)
    _override_policy(files, allow_overrides, findings)
    _reference_policy(files, base_ids, findings)

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
    packs: list[dict[str, Any]] = []
    for index, manifest in enumerate(manifests):
        data = _load_manifest(manifest)
        pack_id = str(data.get("id") or manifest.stem)
        files = [item for item in data.get("files", []) if isinstance(item, dict)]
        packs.append({"id": pack_id, "path": str(manifest), "files": len(files), "order": index})
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
    return {
        "tool": "godot-pack-mod-doctor",
        "tool_version": __version__,
        "schema_version": "1.0",
        "kind": "pack_load_order",
        "summary": {
            "packs": len(packs),
            "files": len(owners),
            "dependencies": 0,
            "errors": 0,
            "warnings": len(findings),
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


def _files_by_path(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = [item for item in data.get("files", []) if isinstance(item, dict)]
    return {str(item.get("path", "")).strip(): item for item in files if str(item.get("path", "")).strip()}


def _stable_file_payload(item: dict[str, Any]) -> dict[str, Any]:
    return {key: item.get(key) for key in sorted(item) if key != "path"}


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Pack Mod Doctor",
        f"Files: {summary['files']} | Errors: {summary['errors']} | Warnings: {summary['warnings']}",
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
        lines.extend(["## Load Order", "", "| Order | Pack | Files |", "|---:|---|---:|"])
        for pack in report["packs"]:
            lines.append(f"| {pack['order']} | {pack['id']} | {pack['files']} |")
        lines.append("")
    lines.extend(["## Findings", ""])
    if not report["findings"]:
        lines.append("No pack manifest findings.")
    else:
        lines.extend(["| Severity | Rule | Message |", "|---|---|---|"])
        for finding in report["findings"]:
            lines.append(f"| {finding['severity']} | `{finding['rule_id']}` | {finding['message']} |")
    return "\n".join(lines)
