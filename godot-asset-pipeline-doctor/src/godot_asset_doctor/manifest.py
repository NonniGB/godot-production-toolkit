from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from godot_asset_doctor.inspector import inspect_png


def check_sprite_manifest(project_root: Path, manifest_path: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    manifest_path = _resolve(project_root, manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("sprite manifest must be a JSON object.")

    sprites = data.get("sprites")
    if not isinstance(sprites, list):
        raise ValueError("sprite manifest must contain a sprites list.")

    issues: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    checked = 0
    anchors_checked = 0

    for index, sprite in enumerate(sprites):
        if not isinstance(sprite, dict):
            issues.append(_issue(manifest_path, "error", "sprite_entry_invalid", f"sprites[{index}] must be an object."))
            continue

        sprite_id = _string(sprite.get("id"))
        source_path = _string(sprite.get("source_path") or sprite.get("path"))
        label = sprite_id or f"sprites[{index}]"

        if not sprite_id:
            issues.append(_issue(manifest_path, "error", "sprite_missing_id", f"{label} is missing an id."))
        elif sprite_id in seen_ids:
            issues.append(_issue(manifest_path, "error", "sprite_duplicate_id", f"Sprite id {sprite_id!r} is repeated."))
        else:
            seen_ids.add(sprite_id)

        if not source_path:
            issues.append(_issue(manifest_path, "error", "sprite_missing_source", f"{label} is missing source_path."))
            continue

        image_path = _resolve(project_root, Path(source_path))
        if not image_path.exists():
            issues.append(_issue(image_path, "error", "sprite_source_missing", f"{label} source file does not exist."))
            continue
        if image_path.suffix.lower() != ".png":
            issues.append(_issue(image_path, "error", "sprite_source_not_png", f"{label} source file is not a PNG."))
            continue

        checked += 1
        png = inspect_png(image_path)
        expected_width = _optional_int(sprite.get("width"))
        expected_height = _optional_int(sprite.get("height"))
        if expected_width is not None and expected_width != png.width:
            issues.append(
                _issue(
                    image_path,
                    "error",
                    "sprite_width_mismatch",
                    f"{label} declares width {expected_width}, but the PNG is {png.width}px wide.",
                )
            )
        if expected_height is not None and expected_height != png.height:
            issues.append(
                _issue(
                    image_path,
                    "error",
                    "sprite_height_mismatch",
                    f"{label} declares height {expected_height}, but the PNG is {png.height}px high.",
                )
            )

        anchor_items = _anchors(sprite.get("anchors"))
        anchors_checked += len(anchor_items)
        for anchor_name, x, y in anchor_items:
            if x < 0 or y < 0 or x > png.width or y > png.height:
                issues.append(
                    _issue(
                        image_path,
                        "error",
                        "sprite_anchor_out_of_bounds",
                        f"{label} anchor {anchor_name!r} at ({x:g}, {y:g}) is outside {png.width}x{png.height}.",
                    )
                )

    return {
        "tool": "godot-asset-pipeline-doctor",
        "kind": "sprite_manifest",
        "summary": {
            "manifest": str(manifest_path),
            "sprites": len(sprites),
            "sprites_checked": checked,
            "anchors_checked": anchors_checked,
            "errors": sum(1 for issue in issues if issue["severity"] == "error"),
            "warnings": sum(1 for issue in issues if issue["severity"] == "warning"),
        },
        "issues": issues,
    }


def render_manifest_report(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    summary = report["summary"]
    lines = [
        "Godot Asset Sprite Manifest",
        f"Manifest: {summary['manifest']}",
        (
            f"Sprites: {summary['sprites']} | Checked: {summary['sprites_checked']} | "
            f"Anchors: {summary['anchors_checked']}"
        ),
        f"Errors: {summary['errors']} | Warnings: {summary['warnings']}",
    ]
    if not report["issues"]:
        lines.append("No sprite manifest issues found.")
        return "\n".join(lines)
    lines.append("")
    for issue in report["issues"]:
        lines.append(f"[{issue['severity'].upper()}] {issue['code']}: {issue['path']}")
        lines.append(f"  {issue['message']}")
    return "\n".join(lines)


def manifest_exit_code(report: dict[str, Any], fail_on: str) -> int:
    summary = report["summary"]
    if fail_on == "none":
        return 0
    if fail_on == "warning" and int(summary["errors"]) + int(summary["warnings"]) > 0:
        return 1
    if fail_on == "error" and int(summary["errors"]) > 0:
        return 1
    return 0


def _anchors(raw: object) -> list[tuple[str, float, float]]:
    if raw is None:
        return []
    items: list[tuple[str, float, float]] = []
    if isinstance(raw, dict):
        iterable = raw.items()
    elif isinstance(raw, list):
        iterable = ((str(index), item) for index, item in enumerate(raw))
    else:
        return items

    for fallback_name, value in iterable:
        if not isinstance(value, dict):
            continue
        name = _string(value.get("name")) or str(fallback_name)
        x = _number(value.get("x"))
        y = _number(value.get("y"))
        if x is not None and y is not None:
            items.append((name, x, y))
    return items


def _issue(path: Path, severity: str, code: str, message: str) -> dict[str, str]:
    return {"path": str(path), "severity": severity, "code": code, "message": message}


def _resolve(project_root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (project_root / path).resolve()


def _string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _number(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None
