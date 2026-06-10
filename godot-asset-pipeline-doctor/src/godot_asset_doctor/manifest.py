from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

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


def render_contact_sheet(
    project_root: Path,
    manifest_path: Path,
    output_path: Path,
    *,
    thumb_size: int = 96,
    columns: int = 4,
    show_anchor_labels: bool = False,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    manifest_path = _resolve(project_root, manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("sprite manifest must be a JSON object.")
    sprites = data.get("sprites")
    if not isinstance(sprites, list):
        raise ValueError("sprite manifest must contain a sprites list.")
    if thumb_size <= 0:
        raise ValueError("thumb_size must be greater than zero.")
    if columns <= 0:
        raise ValueError("columns must be greater than zero.")

    entries: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    anchors_rendered = 0

    for index, sprite in enumerate(sprites):
        if not isinstance(sprite, dict):
            issues.append(_issue(manifest_path, "warning", "sprite_entry_invalid", f"sprites[{index}] must be an object."))
            continue
        sprite_id = _string(sprite.get("id")) or f"sprites[{index}]"
        source_path = _string(sprite.get("source_path") or sprite.get("path"))
        if not source_path:
            issues.append(_issue(manifest_path, "warning", "sprite_missing_source", f"{sprite_id} is missing source_path."))
            continue
        image_path = _resolve(project_root, Path(source_path))
        if not image_path.exists() or image_path.suffix.lower() != ".png":
            issues.append(_issue(image_path, "warning", "sprite_source_unavailable", f"{sprite_id} source PNG is unavailable."))
            continue
        entries.append({"id": sprite_id, "image_path": image_path, "anchors": _anchors(sprite.get("anchors"))})

    if not entries:
        raise ValueError("sprite manifest did not contain any renderable PNG sprites.")

    padding = 12
    label_height = 22
    cell_width = thumb_size + padding * 2
    cell_height = thumb_size + padding * 2 + label_height
    rows = math.ceil(len(entries) / columns)
    sheet = Image.new("RGBA", (columns * cell_width, rows * cell_height), (28, 31, 38, 255))
    draw = ImageDraw.Draw(sheet)

    for entry_index, entry in enumerate(entries):
        col = entry_index % columns
        row = entry_index // columns
        cell_x = col * cell_width
        cell_y = row * cell_height
        image = Image.open(entry["image_path"]).convert("RGBA")
        original_width, original_height = image.size
        preview = image.copy()
        preview.thumbnail((thumb_size, thumb_size), Image.Resampling.NEAREST)
        image_x = cell_x + padding + (thumb_size - preview.width) // 2
        image_y = cell_y + padding + (thumb_size - preview.height) // 2

        draw.rectangle(
            [cell_x + 6, cell_y + 6, cell_x + cell_width - 7, cell_y + cell_height - 7],
            outline=(78, 86, 104, 255),
        )
        sheet.alpha_composite(_checkerboard(preview.width, preview.height), (image_x, image_y))
        sheet.alpha_composite(preview, (image_x, image_y))

        scale_x = preview.width / original_width if original_width else 1.0
        scale_y = preview.height / original_height if original_height else 1.0
        for anchor_name, anchor_x, anchor_y in entry["anchors"]:
            marker_x = image_x + int(round(anchor_x * scale_x))
            marker_y = image_y + int(round(anchor_y * scale_y))
            _draw_anchor_marker(draw, marker_x, marker_y, anchor_name if show_anchor_labels else "")
            anchors_rendered += 1

        label = str(entry["id"])[: max(8, (cell_width - padding * 2) // 6)]
        draw.text((cell_x + padding, cell_y + padding + thumb_size + 4), label, fill=(230, 235, 245, 255))

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
    return {
        "tool": "godot-asset-pipeline-doctor",
        "kind": "sprite_manifest_contact_sheet",
        "summary": {
            "manifest": str(manifest_path),
            "output": str(output_path),
            "sprites": len(sprites),
            "sprites_rendered": len(entries),
            "anchors_rendered": anchors_rendered,
            "warnings": len(issues),
        },
        "issues": issues,
    }


def manifest_exit_code(report: dict[str, Any], fail_on: str) -> int:
    summary = report["summary"]
    if fail_on == "none":
        return 0
    if fail_on == "warning" and int(summary["errors"]) + int(summary["warnings"]) > 0:
        return 1
    if fail_on == "error" and int(summary["errors"]) > 0:
        return 1
    return 0


def _checkerboard(width: int, height: int, size: int = 8) -> Image.Image:
    image = Image.new("RGBA", (width, height), (214, 219, 229, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, height, size):
        for x in range(0, width, size):
            if ((x // size) + (y // size)) % 2:
                draw.rectangle([x, y, min(x + size - 1, width - 1), min(y + size - 1, height - 1)], fill=(172, 180, 195, 255))
    return image


def _draw_anchor_marker(draw: ImageDraw.ImageDraw, x: int, y: int, name: str) -> None:
    color = (255, 77, 109, 255)
    outline = (20, 22, 28, 255)
    draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=color, outline=outline)
    draw.line([x - 7, y, x + 7, y], fill=outline)
    draw.line([x, y - 7, x, y + 7], fill=outline)
    if name:
        draw.text((x + 6, y - 9), name[:18], fill=color)


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
