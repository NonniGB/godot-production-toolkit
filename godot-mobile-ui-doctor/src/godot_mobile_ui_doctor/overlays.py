from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .audit import audit_mobile_ui
from .models import Screen, Thresholds, UiNode, Viewport


@dataclass(frozen=True)
class OverlayOptions:
    output_dir: Path
    scale: float = 0.5


def render_overlays(
    viewports: dict[str, Viewport],
    screens: list[Screen],
    thresholds: Thresholds,
    options: OverlayOptions,
) -> dict[str, Any]:
    options.output_dir.mkdir(parents=True, exist_ok=True)
    audit_report = audit_mobile_ui(viewports, screens, thresholds)
    findings = audit_report["findings"]
    files: list[dict[str, Any]] = []

    for screen in screens:
        viewport = viewports.get(screen.viewport)
        if viewport is None:
            continue
        finding_map = _findings_by_node(findings, screen.name)
        image = _draw_screen(screen, viewport, thresholds, finding_map, options.scale)
        path = options.output_dir / f"{_slug(screen.name)}__{_slug(viewport.name)}.png"
        image.save(path)
        files.append(
            {
                "screen": screen.name,
                "viewport": viewport.name,
                "path": path.as_posix(),
                "width": image.width,
                "height": image.height,
            }
        )

    return {
        "tool": "godot-mobile-ui-doctor",
        "version": "0.1.5",
        "kind": "mobile_ui_overlay_previews",
        "summary": {
            "screens": len(screens),
            "viewports": len(viewports),
            "files": len(files),
            "errors": audit_report["summary"]["errors"],
            "warnings": audit_report["summary"]["warnings"],
        },
        "files": files,
        "findings": findings,
    }


def _draw_screen(
    screen: Screen,
    viewport: Viewport,
    thresholds: Thresholds,
    finding_map: dict[str, list[dict[str, Any]]],
    scale: float,
) -> Image.Image:
    width = max(1, round(viewport.width * scale))
    height = max(1, round(viewport.height * scale))
    image = Image.new("RGB", (width, height), "#0e1118")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    title_font = ImageFont.load_default()

    _draw_grid(draw, width, height)
    safe_rect = (
        viewport.safe_area.left * scale,
        viewport.safe_area.top * scale,
        (viewport.width - viewport.safe_area.right) * scale,
        (viewport.height - viewport.safe_area.bottom) * scale,
    )
    draw.rectangle(safe_rect, outline="#45d483", width=2)
    _label(draw, (safe_rect[0] + 6, safe_rect[1] + 6), "safe area", "#45d483", font)

    for node in screen.nodes:
        _draw_node(draw, node, thresholds, finding_map.get(node.id, []), scale, font)

    header = f"{screen.name} / {viewport.name} / {viewport.width}x{viewport.height}"
    legend = "yellow=review  red=error  blue=interactive  green=safe area"
    _label(draw, (8, max(8, height - 40)), header, "#e9eefc", title_font)
    _label(draw, (8, max(20, height - 26)), legend, "#c9d2e8", font)
    return image


def _draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for x in range(0, width, 40):
        draw.line((x, 0, x, height), fill="#202638")
    for y in range(0, height, 40):
        draw.line((0, y, width, y), fill="#202638")


def _draw_node(
    draw: ImageDraw.ImageDraw,
    node: UiNode,
    thresholds: Thresholds,
    findings: list[dict[str, Any]],
    scale: float,
    font: ImageFont.ImageFont,
) -> None:
    rect = (
        node.x * scale,
        node.y * scale,
        (node.x + node.width) * scale,
        (node.y + node.height) * scale,
    )
    rules = {str(finding["rule_id"]) for finding in findings}
    if "node_outside_viewport" in rules:
        color = "#ff5d73"
    elif rules:
        color = "#ffc857"
    elif node.interactive:
        color = "#59c2ff"
    else:
        color = "#8f9bb3"

    fill = _with_alpha_hint(color)
    draw.rectangle(rect, outline=color, fill=fill, width=2)
    if node.interactive:
        target = (
            node.x * scale,
            node.y * scale,
            (node.x + max(node.width, thresholds.min_touch_size)) * scale,
            (node.y + max(node.height, thresholds.min_touch_size)) * scale,
        )
        draw.rectangle(target, outline="#59c2ff", width=1)

    label = node.id if not rules else f"{node.id} ({len(rules)})"
    _label(draw, (rect[0] + 4, rect[1] + 4), label, "#ffffff", font)
    if node.text:
        _label(draw, (rect[0] + 4, rect[1] + 16), node.text[:36], "#c9d2e8", font)


def _with_alpha_hint(color: str) -> str:
    palette = {
        "#ff5d73": "#35151d",
        "#ffc857": "#352a14",
        "#59c2ff": "#112a38",
        "#8f9bb3": "#1d2434",
    }
    return palette.get(color, "#1d2434")


def _findings_by_node(
    findings: list[dict[str, Any]], screen_name: str
) -> dict[str, list[dict[str, Any]]]:
    by_node: dict[str, list[dict[str, Any]]] = {}
    for finding in findings:
        if finding.get("screen") != screen_name:
            continue
        node = finding.get("node")
        if not isinstance(node, str):
            continue
        for node_id in node.split(","):
            by_node.setdefault(node_id, []).append(finding)
    return by_node


def _label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    color: str,
    font: ImageFont.ImageFont,
) -> None:
    x, y = xy
    draw.text((x + 1, y + 1), text, fill="#05070d", font=font)
    draw.text((x, y), text, fill=color, font=font)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._")
    return slug or "screen"
