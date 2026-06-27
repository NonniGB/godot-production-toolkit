from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import __version__
from .audit import audit_mobile_ui
from .models import Screen, Thresholds, UiNode, Viewport
from .rules import rule_catalog


@dataclass(frozen=True)
class OverlayOptions:
    output_dir: Path
    scale: float = 0.5
    screenshot_dir: Path | None = None
    layout_risk_report: Path | None = None


def render_overlays(
    viewports: dict[str, Viewport],
    screens: list[Screen],
    thresholds: Thresholds,
    options: OverlayOptions,
) -> dict[str, Any]:
    options.output_dir.mkdir(parents=True, exist_ok=True)
    audit_report = audit_mobile_ui(viewports, screens, thresholds)
    layout_risk_findings = _load_layout_risk_findings(options.layout_risk_report)
    findings = audit_report["findings"] + layout_risk_findings
    files: list[dict[str, Any]] = []

    for screen in screens:
        viewport = viewports.get(screen.viewport)
        if viewport is None:
            continue
        finding_map = _findings_by_node(findings, screen.name, viewport.name)
        layout_risk_labels = _layout_risk_labels(finding_map)
        screenshot = _find_screenshot(options.screenshot_dir, screen, viewport)
        image = _draw_screen(screen, viewport, thresholds, finding_map, options.scale, screenshot)
        path = options.output_dir / f"{_slug(screen.name)}__{_slug(viewport.name)}.png"
        image.save(path)
        files.append(
            {
                "screen": screen.name,
                "viewport": viewport.name,
                "path": path.as_posix(),
                "screenshot": str(screenshot) if screenshot else None,
                "width": image.width,
                "height": image.height,
                "layout_risk_labels": layout_risk_labels,
            }
        )

    return {
        "tool": "godot-mobile-ui-doctor",
        "version": __version__,
        "tool_version": __version__,
        "schema_version": "1.1",
        "metadata": {
            "rules": rule_catalog(),
        },
        "kind": "mobile_ui_overlay_previews",
        "summary": {
            "screens": len(screens),
            "viewports": len(viewports),
            "files": len(files),
            "screenshots": sum(1 for item in files if item["screenshot"]),
            "layout_risk_findings": len(layout_risk_findings),
            "layout_risk_labels": sum(len(item["layout_risk_labels"]) for item in files),
            "errors": audit_report["summary"]["errors"] + _count_severity(layout_risk_findings, "error"),
            "warnings": audit_report["summary"]["warnings"] + _count_severity(
                layout_risk_findings, "warning"
            ),
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
    screenshot: Path | None,
) -> Image.Image:
    width = max(1, round(viewport.width * scale))
    height = max(1, round(viewport.height * scale))
    image = _base_image(screenshot, viewport, width, height)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    title_font = ImageFont.load_default()

    if screenshot is None:
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
        _draw_node(
            draw,
            node,
            thresholds,
            finding_map.get(node.id, []),
            scale,
            font,
            fill_nodes=screenshot is None,
        )

    header = f"{screen.name} / {viewport.name} / {viewport.width}x{viewport.height}"
    legend = "yellow=review  red=error  pink=l10n text  blue=interactive"
    legend_2 = "green=safe area"
    _label(draw, (8, max(8, height - 40)), header, "#e9eefc", title_font)
    _label(draw, (8, max(20, height - 26)), legend, "#c9d2e8", font)
    _label(draw, (8, max(32, height - 14)), legend_2, "#c9d2e8", font)
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
    *,
    fill_nodes: bool = True,
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
    elif "localized_text_overflow_risk" in rules:
        color = "#ff8bd1"
    elif rules:
        color = "#ffc857"
    elif node.interactive:
        color = "#59c2ff"
    else:
        color = "#8f9bb3"

    fill = _with_alpha_hint(color) if fill_nodes else None
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
    has_room_for_details = (rect[2] - rect[0]) >= 72 and (rect[3] - rect[1]) >= 40
    if node.text and has_room_for_details:
        _label(draw, (rect[0] + 4, rect[1] + 16), node.text[:36], "#c9d2e8", font)
    if "text_expansion_overflow_risk" in rules and has_room_for_details:
        _label(draw, (rect[0] + 4, rect[1] + 28), "expanded copy", "#ffe0a3", font)
    layout_variants = sorted(
        {
            str(finding.get("variant"))
            for finding in findings
            if finding.get("rule_id") == "localized_text_overflow_risk" and finding.get("variant")
        }
    )
    if layout_variants and has_room_for_details:
        y_offset = 40 if "text_expansion_overflow_risk" in rules else 28
        _label(
            draw,
            (rect[0] + 4, rect[1] + y_offset),
            f"l10n: {', '.join(layout_variants)[:28]}",
            "#ffb7e4",
            font,
        )
        preview = _first_stress_preview(findings)
        if preview and (rect[3] - rect[1]) >= 52:
            _label(draw, (rect[0] + 4, rect[1] + y_offset + 12), preview[:28], "#ffd6ef", font)


def _with_alpha_hint(color: str) -> str:
    palette = {
        "#ff5d73": "#35151d",
        "#ff8bd1": "#35152c",
        "#ffc857": "#352a14",
        "#59c2ff": "#112a38",
        "#8f9bb3": "#1d2434",
    }
    return palette.get(color, "#1d2434")


def _base_image(screenshot: Path | None, viewport: Viewport, width: int, height: int) -> Image.Image:
    if screenshot is None:
        return Image.new("RGB", (width, height), "#0e1118")
    with Image.open(screenshot) as raw:
        image = raw.convert("RGB")
    if image.size != (viewport.width, viewport.height):
        image = image.resize((viewport.width, viewport.height), Image.Resampling.BILINEAR)
    return image.resize((width, height), Image.Resampling.BILINEAR)


def _find_screenshot(root: Path | None, screen: Screen, viewport: Viewport) -> Path | None:
    if root is None:
        return None
    names = [
        f"{screen.name}__{viewport.name}.png",
        f"{_slug(screen.name)}__{_slug(viewport.name)}.png",
        f"{screen.name}.png",
        f"{_slug(screen.name)}.png",
    ]
    for name in names:
        path = root / name
        if path.exists():
            return path
    return None


def _findings_by_node(
    findings: list[dict[str, Any]], screen_name: str, viewport_name: str
) -> dict[str, list[dict[str, Any]]]:
    by_node: dict[str, list[dict[str, Any]]] = {}
    for finding in findings:
        if finding.get("screen") != screen_name:
            continue
        if finding.get("viewport") not in {None, viewport_name}:
            continue
        node = finding.get("node")
        if not isinstance(node, str):
            continue
        for node_id in node.split(","):
            by_node.setdefault(node_id, []).append(finding)
    return by_node


def _layout_risk_labels(findings_by_node: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    labels: list[dict[str, Any]] = []
    for node, findings in sorted(findings_by_node.items()):
        for finding in findings:
            if finding.get("rule_id") != "localized_text_overflow_risk":
                continue
            preview = finding.get("stress_text_preview")
            if not isinstance(preview, str) or not preview:
                continue
            label = {
                "node": node,
                "translation_key": finding.get("translation_key"),
                "variant": finding.get("variant"),
                "locale": finding.get("locale"),
                "stress_text_preview": preview,
            }
            labels.append({key: value for key, value in label.items() if value is not None})
    return labels


def _first_stress_preview(findings: list[dict[str, Any]]) -> str | None:
    for finding in findings:
        if finding.get("rule_id") != "localized_text_overflow_risk":
            continue
        preview = finding.get("stress_text_preview")
        if isinstance(preview, str) and preview:
            return preview
    return None


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


def _load_layout_risk_findings(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    import json

    report = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise ValueError("layout risk report must be a JSON object.")
    if report.get("kind") != "mobile_ui_layout_risk":
        raise ValueError("layout risk report kind must be mobile_ui_layout_risk.")
    findings = report.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("layout risk report findings must be a list.")
    return [finding for finding in findings if isinstance(finding, dict)]


def _count_severity(findings: list[dict[str, Any]], severity: str) -> int:
    return sum(1 for finding in findings if finding.get("severity") == severity)
