from __future__ import annotations

from math import hypot
from typing import Any

from .models import Finding, Screen, Thresholds, UiNode, Viewport


def audit_mobile_ui(
    viewports: dict[str, Viewport], screens: list[Screen], thresholds: Thresholds
) -> dict[str, Any]:
    findings: list[Finding] = []
    for screen in screens:
        viewport = viewports.get(screen.viewport)
        if viewport is None:
            findings.append(
                Finding(
                    rule_id="missing_viewport",
                    severity="error",
                    screen=screen.name,
                    viewport=screen.viewport,
                    message=f"Screen {screen.name!r} references unknown viewport {screen.viewport!r}.",
                    help="Add the viewport to metadata.viewports or update the screen viewport name.",
                )
            )
            continue
        findings.extend(_audit_screen(screen, viewport, thresholds))

    summary = {
        "screens": len(screens),
        "viewports": len(viewports),
        "nodes": sum(len(screen.nodes) for screen in screens),
        "interactive_nodes": sum(
            1 for screen in screens for node in screen.nodes if node.interactive
        ),
        "errors": sum(1 for finding in findings if finding.severity == "error"),
        "warnings": sum(1 for finding in findings if finding.severity == "warning"),
    }
    return {
        "tool": "godot-mobile-ui-doctor",
        "version": "0.1.7",
        "summary": summary,
        "findings": [finding.as_dict() for finding in findings],
    }


def build_readiness_matrix(
    viewports: dict[str, Viewport], screens: list[Screen], thresholds: Thresholds
) -> dict[str, Any]:
    report = audit_mobile_ui(viewports, screens, thresholds)
    findings = report["findings"]
    rows: list[dict[str, Any]] = []

    for screen in screens:
        screen_findings = [finding for finding in findings if finding.get("screen") == screen.name]
        viewport = viewports.get(screen.viewport)
        rows.append(
            {
                "screen": screen.name,
                "viewport": screen.viewport,
                "viewport_size": f"{viewport.width}x{viewport.height}" if viewport else "missing",
                "nodes": len(screen.nodes),
                "interactive_nodes": sum(1 for node in screen.nodes if node.interactive),
                "status": _screen_status(screen_findings),
                "errors": sum(1 for finding in screen_findings if finding["severity"] == "error"),
                "warnings": sum(1 for finding in screen_findings if finding["severity"] == "warning"),
                "safe_area": _rule_status(screen_findings, "safe_area_overlap"),
                "touch_targets": _rule_status(screen_findings, "touch_target_too_small"),
                "spacing": _rule_status(screen_findings, "touch_targets_too_close"),
                "text_fit": _rule_status(screen_findings, "text_overflow_risk"),
                "viewport_bounds": _rule_status(screen_findings, "node_outside_viewport"),
            }
        )

    return {
        "tool": "godot-mobile-ui-doctor",
        "version": "0.1.7",
        "kind": "mobile_readiness_matrix",
        "summary": {
            "screens": len(rows),
            "ready": sum(1 for row in rows if row["status"] == "pass"),
            "review": sum(1 for row in rows if row["status"] == "review"),
            "action": sum(1 for row in rows if row["status"] == "action"),
            "errors": report["summary"]["errors"],
            "warnings": report["summary"]["warnings"],
        },
        "matrix": rows,
        "findings": findings,
    }


def _audit_screen(screen: Screen, viewport: Viewport, thresholds: Thresholds) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    interactive_nodes = [node for node in screen.nodes if node.interactive]

    if not interactive_nodes:
        findings.append(
            Finding(
                rule_id="no_interactive_controls",
                severity="warning",
                screen=screen.name,
                viewport=viewport.name,
                message=f"Screen {screen.name!r} has no interactive controls in the metadata.",
                help="Export buttons, menus, sliders, or touch zones so the screen can be checked.",
            )
        )

    for node in screen.nodes:
        if node.id in seen:
            findings.append(
                Finding(
                    rule_id="duplicate_node_id",
                    severity="error",
                    screen=screen.name,
                    node=node.id,
                    viewport=viewport.name,
                    message=f"Node id {node.id!r} is repeated on screen {screen.name!r}.",
                    help="Use stable unique ids so reports can track the same control across runs.",
                )
            )
        seen.add(node.id)
        findings.extend(_audit_bounds(screen, viewport, node))
        findings.extend(_audit_text(screen, viewport, node, thresholds))
        if node.interactive:
            findings.extend(_audit_touch_target(screen, viewport, node, thresholds))

    findings.extend(_audit_spacing(screen, viewport, interactive_nodes, thresholds))
    return findings


def _audit_bounds(screen: Screen, viewport: Viewport, node: UiNode) -> list[Finding]:
    findings: list[Finding] = []
    outside_viewport = (
        node.x < 0
        or node.y < 0
        or node.x + node.width > viewport.width
        or node.y + node.height > viewport.height
    )
    if outside_viewport:
        findings.append(
            Finding(
                rule_id="node_outside_viewport",
                severity="error",
                screen=screen.name,
                node=node.id,
                viewport=viewport.name,
                message=f"Node {node.id!r} is partly outside the {viewport.width}x{viewport.height} viewport.",
                help="Keep UI rectangles inside the exported viewport bounds.",
            )
        )

    safe_left = viewport.safe_area.left
    safe_top = viewport.safe_area.top
    safe_right = viewport.width - viewport.safe_area.right
    safe_bottom = viewport.height - viewport.safe_area.bottom
    overlaps_safe_area = (
        node.x < safe_left
        or node.y < safe_top
        or node.x + node.width > safe_right
        or node.y + node.height > safe_bottom
    )
    if overlaps_safe_area:
        findings.append(
            Finding(
                rule_id="safe_area_overlap",
                severity="warning",
                screen=screen.name,
                node=node.id,
                viewport=viewport.name,
                message=f"Node {node.id!r} overlaps the safe-area inset for viewport {viewport.name!r}.",
                help="Move important controls and labels inside the safe-area rectangle.",
            )
        )
    return findings


def _audit_touch_target(
    screen: Screen, viewport: Viewport, node: UiNode, thresholds: Thresholds
) -> list[Finding]:
    if node.width >= thresholds.min_touch_size and node.height >= thresholds.min_touch_size:
        return []
    return [
        Finding(
            rule_id="touch_target_too_small",
            severity="warning",
            screen=screen.name,
            node=node.id,
            viewport=viewport.name,
            message=(
                f"Interactive node {node.id!r} is {node.width:g}x{node.height:g}; "
                f"target size is {thresholds.min_touch_size}px."
            ),
            help="Increase the clickable area or wrap the control in a larger touch zone.",
        )
    ]


def _audit_spacing(
    screen: Screen, viewport: Viewport, nodes: list[UiNode], thresholds: Thresholds
) -> list[Finding]:
    findings: list[Finding] = []
    for index, left in enumerate(nodes):
        for right in nodes[index + 1 :]:
            gap = _rect_gap(left, right)
            if gap < thresholds.min_touch_spacing:
                findings.append(
                    Finding(
                        rule_id="touch_targets_too_close",
                        severity="warning",
                        screen=screen.name,
                        node=f"{left.id},{right.id}",
                        viewport=viewport.name,
                        message=(
                            f"Interactive nodes {left.id!r} and {right.id!r} are "
                            f"{gap:.1f}px apart; target spacing is {thresholds.min_touch_spacing}px."
                        ),
                        help="Add spacing or make only one of the overlapping rectangles interactive.",
                    )
                )
    return findings


def _audit_text(
    screen: Screen, viewport: Viewport, node: UiNode, thresholds: Thresholds
) -> list[Finding]:
    if not node.text:
        return []
    estimated_width = len(node.text) * node.font_size * 0.55
    estimated_height = node.font_size * 1.2
    if estimated_width <= node.width * thresholds.max_text_width_ratio and estimated_height <= node.height:
        return []
    return [
        Finding(
            rule_id="text_overflow_risk",
            severity="warning",
            screen=screen.name,
            node=node.id,
            viewport=viewport.name,
            message=f"Text on node {node.id!r} may not fit inside its exported rectangle.",
            help="Allow wrapping, shorten the label, resize the control, or check localized strings.",
        )
    ]


def _rect_gap(left: UiNode, right: UiNode) -> float:
    left_x2 = left.x + left.width
    left_y2 = left.y + left.height
    right_x2 = right.x + right.width
    right_y2 = right.y + right.height

    dx = max(right.x - left_x2, left.x - right_x2, 0)
    dy = max(right.y - left_y2, left.y - right_y2, 0)
    return hypot(dx, dy)


def _screen_status(findings: list[dict[str, Any]]) -> str:
    if any(finding["severity"] == "error" for finding in findings):
        return "action"
    if any(finding["severity"] == "warning" for finding in findings):
        return "review"
    return "pass"


def _rule_status(findings: list[dict[str, Any]], rule_id: str) -> str:
    count = sum(1 for finding in findings if finding["rule_id"] == rule_id)
    return "pass" if count == 0 else f"review ({count})"
