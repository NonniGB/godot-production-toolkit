from __future__ import annotations

import json

from . import __version__
from .models import DiffResult
from .rule_help import catalog_for, explain_rule


def render_text_result(result: DiffResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    lines = [f"Visual smoke diff: {status}"]
    if result.total_pixels:
        lines.extend(
            [
                f"Changed pixels: {result.changed_pixels}/{result.total_pixels} ({result.changed_percent:.4f}%).",
                f"Max delta: {result.max_delta}.",
            ]
        )
    if result.reason:
        lines.append(result.reason)
    if not result.passed:
        rule_id = _rule_id_for_result(result)
        help_text = explain_rule(rule_id)
        lines.append(f"Why it matters: {help_text['explanation']}")
    return "\n".join(lines)


def render_json_result(result: DiffResult) -> str:
    rule_ids = set()
    findings = []
    if not result.passed:
        rule_id = _rule_id_for_result(result)
        rule_ids.add(rule_id)
        help_text = explain_rule(rule_id)
        findings.append(
            {
                "rule_id": rule_id,
                "severity": "error",
                "title": help_text["title"],
                "explanation": help_text["explanation"],
                "message": result.reason or f"{result.changed_percent:.4f}% of pixels changed.",
            }
        )
    payload = {
        **result.to_dict(),
        "metadata": report_metadata("visual_smoke_compare", ["text", "json"]),
        "rules": catalog_for(rule_ids),
        "findings": findings,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def report_metadata(report_kind: str, formats: list[str]) -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "tool_version": __version__,
        "report_kind": report_kind,
        "formats": formats,
    }


def _rule_id_for_result(result: DiffResult) -> str:
    if result.reason.startswith(("Missing baseline screenshot", "Missing current screenshot")):
        return "visual_screenshot_missing"
    if result.reason.startswith("Image size differs"):
        return "visual_image_size_mismatch"
    return "visual_diff_threshold_exceeded"
