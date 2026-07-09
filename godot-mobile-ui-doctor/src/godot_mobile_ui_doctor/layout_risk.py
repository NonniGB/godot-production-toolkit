from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from . import __version__
from .models import Screen, Thresholds, UiNode, Viewport
from .rules import enrich_finding, rule_catalog


def build_layout_risk_report(
    viewports: dict[str, Viewport],
    screens: list[Screen],
    thresholds: Thresholds,
    stress_pack: Path,
) -> dict[str, Any]:
    catalogs, stress_summary = _load_stress_pack(stress_pack)
    findings: list[dict[str, Any]] = []
    text_nodes = [node for screen in screens for node in screen.nodes if node.text or node.translation_key]
    matched_nodes = 0
    matched_keys: set[str] = set()
    unmatched_nodes: list[dict[str, Any]] = []

    for screen in screens:
        viewport = viewports.get(screen.viewport)
        if viewport is None:
            continue
        for node in screen.nodes:
            if not node.text and not node.translation_key:
                continue
            entry = _match_entry(node, catalogs)
            if entry is None:
                unmatched_nodes.append(_unmatched_node(screen.name, viewport.name, node))
                continue
            matched_nodes += 1
            matched_keys.add(str(entry["key"]))
            findings.extend(_find_node_risks(screen.name, viewport, node, entry, thresholds))

    warnings = sum(1 for finding in findings if finding["severity"] == "warning")
    capped_unmatched_nodes = unmatched_nodes[:50]
    return {
        "tool": "godot-mobile-ui-doctor",
        "version": __version__,
        "tool_version": __version__,
        "schema_version": "1.1",
        "kind": "mobile_ui_layout_risk",
        "metadata": {
            "rules": rule_catalog(),
            "stress_pack": str(stress_pack),
            "stress_pack_summary": stress_summary,
        },
        "summary": {
            "screens": len(screens),
            "viewports": len(viewports),
            "text_nodes": len(text_nodes),
            "matched_nodes": matched_nodes,
            "unmatched_text_nodes": len(text_nodes) - matched_nodes,
            "unmatched_text_nodes_reported": len(capped_unmatched_nodes),
            "unmatched_text_nodes_truncated": max(0, len(unmatched_nodes) - len(capped_unmatched_nodes)),
            "matched_translation_keys": len(matched_keys),
            "stress_entries": len(catalogs),
            "stress_variants": len(stress_summary["variants"]),
            "errors": 0,
            "warnings": warnings,
        },
        "matched_translation_keys": sorted(matched_keys)[:50],
        "unmatched_text_nodes": capped_unmatched_nodes,
        "findings": [enrich_finding(finding) for finding in findings],
    }


def render_layout_risk_report(report: dict[str, Any], format_name: str) -> str:
    if format_name == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if format_name == "markdown":
        return _render_markdown(report)
    return _render_text(report)


def _load_stress_pack(manifest_path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    outputs = manifest.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("stress-pack manifest must contain a non-empty outputs list.")
    base = manifest_path.parent
    entries: dict[str, dict[str, Any]] = {}
    variants: list[dict[str, Any]] = []
    for output in outputs:
        if not isinstance(output, dict):
            continue
        csv_path = Path(str(output.get("path", "")).replace("\\", "/"))
        if not csv_path.is_absolute() and not csv_path.exists():
            csv_path = base / csv_path
        variant = str(output.get("variant", csv_path.stem))
        locale = str(output.get("locale", variant))
        _merge_stress_csv(entries, csv_path, variant, locale)
        variants.append(
            {
                "variant": variant,
                "locale": locale,
                "path": str(csv_path),
                "strings": int(output.get("strings", 0) or 0),
            }
        )
    return entries, {
        "source_language": manifest.get("source_language"),
        "catalogs": manifest.get("catalogs", []),
        "manifest_path": str(manifest_path),
        "variants": variants,
    }


def _merge_stress_csv(
    entries: dict[str, dict[str, Any]], csv_path: Path, variant: str, locale: str
) -> None:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "keys" not in reader.fieldnames:
            raise ValueError(f"stress CSV must include a keys column: {csv_path}")
        source_columns = [name for name in reader.fieldnames if name not in {"keys", locale}]
        source_column = source_columns[0] if source_columns else None
        for row in reader:
            key = str(row.get("keys", "")).strip()
            if not key:
                continue
            entry = entries.setdefault(
                key,
                {
                    "key": key,
                    "source": str(row.get(source_column, "")) if source_column else "",
                    "variants": {},
                },
            )
            if not entry.get("source") and source_column:
                entry["source"] = str(row.get(source_column, ""))
            entry["variants"][variant] = {
                "locale": locale,
                "text": str(row.get(locale, "")),
                "path": str(csv_path),
            }


def _match_entry(node: UiNode, entries: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    if node.translation_key and node.translation_key in entries:
        return entries[node.translation_key]
    for entry in entries.values():
        if node.text and node.text == entry.get("source"):
            return entry
    return None


def _unmatched_node(screen_name: str, viewport_name: str, node: UiNode) -> dict[str, Any]:
    row = {
        "screen": screen_name,
        "viewport": viewport_name,
        "node": node.id,
        "translation_key": node.translation_key,
        "text_preview": _preview_text(node.text),
        "match_hint": "translation_key" if node.translation_key else "source_text",
    }
    return {key: value for key, value in row.items() if value}


def _find_node_risks(
    screen_name: str,
    viewport: Viewport,
    node: UiNode,
    entry: dict[str, Any],
    thresholds: Thresholds,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    usable_width = node.width * thresholds.max_text_width_ratio
    usable_height = node.height
    for variant, payload in sorted(entry["variants"].items()):
        text = str(payload.get("text", ""))
        if not text:
            continue
        estimated_width = len(text) * node.font_size * 0.55
        estimated_height = node.font_size * 1.2
        if estimated_width <= usable_width and estimated_height <= usable_height:
            continue
        findings.append(
            {
                "rule_id": "localized_text_overflow_risk",
                "severity": "warning",
                "screen": screen_name,
                "viewport": viewport.name,
                "node": node.id,
                "message": (
                    f"Node {node.id!r} may overflow with {variant} stress text "
                    f"from key {entry['key']!r}."
                ),
                "help": "Review this control with stress-pack strings, wrapping, or a wider layout.",
                "translation_key": entry["key"],
                "variant": variant,
                "locale": payload.get("locale"),
                "estimated_width": round(estimated_width, 1),
                "available_width": round(usable_width, 1),
                "stress_text_length": len(text),
                "stress_text_preview": _preview_text(text),
            }
        )
    return findings


def _preview_text(text: str, limit: int = 64) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)].rstrip() + "..."


def _render_text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Godot Mobile UI Layout Risk",
        (
            f"Text nodes: {summary['text_nodes']} | Matched: {summary['matched_nodes']} | "
            f"Unmatched: {summary['unmatched_text_nodes']}"
        ),
        f"Stress variants: {summary['stress_variants']} | Matched keys: {summary['matched_translation_keys']}",
        f"Warnings: {summary['warnings']}",
    ]
    if report.get("unmatched_text_nodes"):
        lines.append("Unmatched text nodes:")
        for row in report["unmatched_text_nodes"][:5]:
            key = f" key {row['translation_key']}" if row.get("translation_key") else ""
            lines.append(f"- {row['screen']} / {row['node']}{key}")
    if not report["findings"]:
        lines.append("No stress-pack layout risks found.")
        return "\n".join(lines)
    lines.append("")
    for finding in report["findings"]:
        lines.append(
            f"- {finding['severity'].upper()} {finding['screen']} / {finding['node']} "
            f"{finding['variant']}: {finding['message']}"
        )
    return "\n".join(lines)


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Godot Mobile UI Layout Risk",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Text nodes | {summary['text_nodes']} |",
        f"| Matched nodes | {summary['matched_nodes']} |",
        f"| Unmatched text nodes | {summary['unmatched_text_nodes']} |",
        f"| Unmatched text nodes reported | {summary['unmatched_text_nodes_reported']} |",
        f"| Matched translation keys | {summary['matched_translation_keys']} |",
        f"| Stress entries | {summary['stress_entries']} |",
        f"| Stress variants | {summary['stress_variants']} |",
        f"| Warnings | {summary['warnings']} |",
        "",
        "## Stress Pack",
        "",
        "| Variant | Locale | Strings | File |",
        "|---|---|---:|---|",
    ]
    for variant in report.get("metadata", {}).get("stress_pack_summary", {}).get("variants", []):
        lines.append(
            f"| {variant['variant']} | {variant['locale']} | {variant['strings']} | `{variant['path']}` |"
        )
    lines.extend(
        [
            "",
            "## Unmatched Text Nodes",
            "",
        ]
    )
    unmatched_nodes = report.get("unmatched_text_nodes", [])
    if unmatched_nodes:
        lines.extend(
            [
                "| Screen | Viewport | Node | Translation Key | Text Preview | Match Hint |",
                "|---|---|---|---|---|---|",
            ]
        )
        for row in unmatched_nodes:
            lines.append(
                f"| {row['screen']} | {row['viewport']} | {row['node']} | "
                f"{row.get('translation_key', '-')} | {row.get('text_preview', '-')} | {row['match_hint']} |"
            )
    else:
        lines.append("All exported UI text nodes matched the stress pack.")
    if summary["unmatched_text_nodes_truncated"]:
        lines.append("")
        lines.append(f"Additional unmatched nodes omitted: {summary['unmatched_text_nodes_truncated']}.")
    lines.extend(
        [
            "",
            "## Findings",
            "",
        ]
    )
    if not report["findings"]:
        lines.append("No stress-pack layout risks found.")
        return "\n".join(lines)
    lines.extend(
        [
            "| Severity | Screen | Node | Key | Variant | Estimated / Available Width | Message |",
            "|---|---|---|---|---|---:|---|",
        ]
    )
    for finding in report["findings"]:
        lines.append(
            f"| {finding['severity']} | {finding['screen']} | {finding['node']} | "
            f"`{finding['translation_key']}` | {finding['variant']} | "
            f"{finding['estimated_width']} / {finding['available_width']} | "
            f"{finding['message']} |"
        )
    return "\n".join(lines)
