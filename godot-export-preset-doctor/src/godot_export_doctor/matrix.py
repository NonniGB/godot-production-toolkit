from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from . import __version__
from .models import ExportPreset, Finding

DEFAULT_EXPECTED_PLATFORMS = ("Android", "Web")
DEV_FILE_MARKERS = (
    "/test/",
    "/tests/",
    "/debug/",
    "/dev/",
    "/tmp/",
    "/temp/",
    ".psd",
    ".kra",
    ".aseprite",
    ".blend",
    ".xcf",
    ".bak",
    ".log",
    ".pdb",
)


def matrix_report(
    presets: list[ExportPreset],
    expected_platforms: list[str] | None = None,
) -> dict[str, Any]:
    expected = expected_platforms or list(DEFAULT_EXPECTED_PLATFORMS)
    findings: list[Finding] = []
    by_platform: dict[str, list[ExportPreset]] = {}
    for preset in presets:
        by_platform.setdefault(preset.platform or "unknown", []).append(preset)
    for platform in expected:
        matches = by_platform.get(platform, [])
        if not matches:
            findings.append(
                Finding(
                    rule_id="export_matrix_missing_platform",
                    severity="warning",
                    preset_index=None,
                    preset_name=platform,
                    message=f"Expected platform {platform!r} has no export preset.",
                )
            )
        elif len(matches) > 1:
            findings.append(
                Finding(
                    rule_id="export_matrix_duplicate_platform",
                    severity="warning",
                    preset_index=matches[0].index,
                    preset_name=platform,
                    message=f"Platform {platform!r} has {len(matches)} presets; confirm CI selects the intended variant.",
                )
            )
    return _matrix_payload("export_matrix", presets, findings, expected)


def leak_report(project: Path, presets: list[ExportPreset]) -> dict[str, Any]:
    findings: list[Finding] = []
    project_root = project.parent if project.name == "export_presets.cfg" else project
    suspicious_files = _suspicious_project_files(project_root)
    for preset in presets:
        findings.extend(_preset_local_path_findings(preset))
        if _preset_can_include_dev_files(preset):
            for relative_path in suspicious_files[:50]:
                findings.append(
                    Finding(
                        rule_id="export_leak_dev_file",
                        severity="warning",
                        preset_index=preset.index,
                        preset_name=preset.display_name(),
                        message=f"{relative_path} may be included by preset {preset.display_name()!r}.",
                    )
                )
    payload = _matrix_payload("export_leaks", presets, findings, [])
    payload["suspicious_files_scanned"] = suspicious_files
    return payload


def diff_report(baseline: list[ExportPreset], current: list[ExportPreset]) -> dict[str, Any]:
    findings: list[Finding] = []
    baseline_by_name = {preset.display_name(): preset for preset in baseline}
    current_by_name = {preset.display_name(): preset for preset in current}
    added = sorted(set(current_by_name) - set(baseline_by_name))
    removed = sorted(set(baseline_by_name) - set(current_by_name))
    changed: list[str] = []
    for name in sorted(set(baseline_by_name) & set(current_by_name)):
        before = _preset_compare_payload(baseline_by_name[name])
        after = _preset_compare_payload(current_by_name[name])
        if before != after:
            changed.append(name)
            findings.append(
                Finding(
                    rule_id="export_preset_changed",
                    severity="warning",
                    preset_index=current_by_name[name].index,
                    preset_name=name,
                    message=f"Export preset {name!r} changed since the baseline.",
                )
            )
    for name in removed:
        findings.append(
            Finding(
                rule_id="export_preset_removed",
                severity="warning",
                preset_index=baseline_by_name[name].index,
                preset_name=name,
                message=f"Export preset {name!r} was removed since the baseline.",
            )
        )
    payload = _matrix_payload("export_diff", current, findings, [])
    payload["diff"] = {"added": added, "removed": removed, "changed": changed}
    payload["summary"]["added"] = len(added)
    payload["summary"]["removed"] = len(removed)
    payload["summary"]["changed"] = len(changed)
    return payload


def exported_folder_report(path: Path) -> dict[str, Any]:
    findings: list[Finding] = []
    files = sorted(item.relative_to(path).as_posix() for item in path.rglob("*") if item.is_file()) if path.exists() else []
    for relative in files:
        lowered = f"/{relative.lower()}"
        if any(marker in lowered for marker in DEV_FILE_MARKERS):
            findings.append(
                Finding(
                    rule_id="exported_folder_dev_file",
                    severity="warning",
                    preset_index=None,
                    preset_name=path.name,
                    message=f"Exported folder contains development-looking file {relative!r}.",
                )
            )
    payload = _matrix_payload("exported_folder_inspection", [], findings, [])
    payload["folder"] = str(path)
    payload["files"] = files
    payload["summary"]["files"] = len(files)
    return payload


def render_matrix_report(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, sort_keys=True)
    if output_format == "html":
        return _html(report)
    if output_format == "markdown":
        return _markdown(report)
    return _text(report)


def _matrix_payload(
    kind: str,
    presets: list[ExportPreset],
    findings: list[Finding],
    expected_platforms: list[str],
) -> dict[str, Any]:
    return {
        "tool": "godot-export-preset-doctor",
        "metadata": {
            "schema_version": "1.2",
            "tool_version": __version__,
            "report_kind": kind,
            "formats": ["text", "json", "markdown", "html"],
        },
        "summary": {
            "presets": len(presets),
            "platforms": len({preset.platform for preset in presets if preset.platform}),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "expected_platforms": expected_platforms,
        "matrix": [_preset_row(preset) for preset in presets],
        "findings": [finding.to_dict() for finding in findings],
    }


def _preset_row(preset: ExportPreset) -> dict[str, Any]:
    return {
        "index": preset.index,
        "name": preset.display_name(),
        "platform": preset.platform,
        "runnable": preset.runnable,
        "export_filter": preset.export_filter,
        "include_filter": preset.include_filter,
        "exclude_filter": preset.exclude_filter,
        "custom_features": preset.custom_features,
        "export_path": preset.export_path,
        "option_count": len(preset.options),
    }


def _preset_compare_payload(preset: ExportPreset) -> dict[str, Any]:
    return {
        "platform": preset.platform,
        "runnable": preset.runnable,
        "export_filter": preset.export_filter,
        "include_filter": preset.include_filter,
        "exclude_filter": preset.exclude_filter,
        "custom_features": preset.custom_features,
        "export_path": preset.export_path,
        "options": preset.options,
    }


def _preset_local_path_findings(preset: ExportPreset) -> list[Finding]:
    findings: list[Finding] = []
    for field, value in (
        ("export_path", preset.export_path),
        ("include_filter", preset.include_filter),
        ("exclude_filter", preset.exclude_filter),
    ):
        if ":" in value or "\\" in value:
            findings.append(
                Finding(
                    rule_id="export_leak_local_path",
                    severity="warning",
                    preset_index=preset.index,
                    preset_name=preset.display_name(),
                    message=f"{field} contains a local-looking path.",
                    option=field,
                )
            )
    return findings


def _preset_can_include_dev_files(preset: ExportPreset) -> bool:
    text = f"{preset.export_filter} {preset.include_filter}".lower()
    return not text.strip() or "all" in text or "*" in text or "resources" in text


def _suspicious_project_files(project_root: Path) -> list[str]:
    if not project_root.exists() or not project_root.is_dir():
        return []
    paths: list[str] = []
    for file_path in project_root.rglob("*"):
        if not file_path.is_file():
            continue
        relative = file_path.relative_to(project_root).as_posix()
        lowered = f"/{relative.lower()}"
        if any(marker in lowered for marker in DEV_FILE_MARKERS):
            paths.append(relative)
    return sorted(paths)


def _text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        _report_title(report),
        f"Presets: {summary['presets']} | Platforms: {summary['platforms']} | Findings: {summary['findings']}",
    ]
    if report.get("diff"):
        diff = report["diff"]
        lines.append(f"Added: {len(diff['added'])} | Removed: {len(diff['removed'])} | Changed: {len(diff['changed'])}")
    if report.get("files") is not None:
        lines.append(f"Files inspected: {summary.get('files', 0)}")
    for row in report["matrix"]:
        lines.append(
            f"- preset.{row['index']} {row['name']} ({row['platform']}): {row['export_path'] or '<no export path>'}"
        )
    for finding in report["findings"]:
        lines.append(f"[{finding['severity'].upper()}] {finding['rule_id']}: {finding['message']}")
    return "\n".join(lines)


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# {_report_title(report)}",
        "",
        f"- Presets: {summary['presets']}",
        f"- Platforms: {summary['platforms']}",
        f"- Warnings: {summary['warnings']}",
        f"- Errors: {summary['errors']}",
        "",
    ]
    if report.get("diff"):
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
    if report.get("files") is not None:
        lines.extend(["## Exported Folder", "", f"- Files inspected: {summary.get('files', 0)}", ""])
    if report["matrix"]:
        lines.extend(
            [
                "| Preset | Platform | Runnable | Filter | Include | Exclude | Export path |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for row in report["matrix"]:
            lines.append(
                f"| {row['name']} | {row['platform']} | {row['runnable']} | {row['export_filter']} | "
                f"{row['include_filter']} | {row['exclude_filter']} | {row['export_path']} |"
            )
    if report["findings"]:
        lines.extend(["", "## Findings", "", "| Severity | Rule | Preset | Message |", "|---|---|---|---|"])
        for finding in report["findings"]:
            lines.append(
                f"| {finding['severity']} | `{finding['rule_id']}` | {finding['preset_name']} | {finding['message']} |"
            )
    return "\n".join(lines)


def _html(report: dict[str, Any]) -> str:
    summary = report["summary"]
    finding_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(finding['severity']))}</td>"
        f"<td><code>{escape(str(finding['rule_id']))}</code></td>"
        f"<td>{escape(str(finding['preset_name']))}</td>"
        f"<td>{escape(str(finding['message']))}</td>"
        "</tr>"
        for finding in report["findings"]
    )
    if not finding_rows:
        finding_rows = '<tr><td colspan="4">No findings at the selected threshold.</td></tr>'
    preset_rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(row['name']))}</td>"
        f"<td>{escape(str(row['platform']))}</td>"
        f"<td>{escape(str(row['runnable']))}</td>"
        f"<td>{escape(str(row['export_filter']))}</td>"
        f"<td>{escape(str(row['include_filter']))}</td>"
        f"<td>{escape(str(row['exclude_filter']))}</td>"
        f"<td>{escape(str(row['export_path']))}</td>"
        "</tr>"
        for row in report["matrix"]
    )
    if not preset_rows:
        preset_rows = '<tr><td colspan="7">No export presets were found.</td></tr>'
    title = _report_title(report)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      font-family: Inter, Segoe UI, system-ui, sans-serif;
      background: #111827;
      color: #e5e7eb;
    }}
    body {{
      margin: 0;
      padding: 32px;
      background: linear-gradient(180deg, #111827 0%, #172033 100%);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
    }}
    h1, h2 {{
      margin: 0 0 16px;
      letter-spacing: 0;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .metric {{
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 14px 16px;
      background: #1f2937;
    }}
    .metric span {{
      display: block;
      color: #94a3b8;
      font-size: 13px;
    }}
    .metric strong {{
      display: block;
      margin-top: 6px;
      font-size: 24px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 28px;
      background: #111827;
      border: 1px solid #334155;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid #253044;
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{
      color: #cbd5e1;
      background: #1f2937;
    }}
    code {{
      color: #bfdbfe;
    }}
    @media (max-width: 780px) {{
      body {{ padding: 18px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>{escape(title)}</h1>
    <p>Static export preset report for release review and CI artifacts.</p>
    <section class="summary" aria-label="Summary">
      <div class="metric"><span>Presets</span><strong>{summary['presets']}</strong></div>
      <div class="metric"><span>Platforms</span><strong>{summary['platforms']}</strong></div>
      <div class="metric"><span>Warnings</span><strong>{summary['warnings']}</strong></div>
      <div class="metric"><span>Errors</span><strong>{summary['errors']}</strong></div>
    </section>
    <h2>Presets</h2>
    <table>
      <thead><tr><th>Preset</th><th>Platform</th><th>Runnable</th><th>Filter</th><th>Include</th><th>Exclude</th><th>Export path</th></tr></thead>
      <tbody>{preset_rows}</tbody>
    </table>
    <h2>Findings</h2>
    <table>
      <thead><tr><th>Severity</th><th>Rule</th><th>Preset</th><th>Message</th></tr></thead>
      <tbody>{finding_rows}</tbody>
    </table>
  </main>
</body>
</html>"""


def _report_title(report: dict[str, Any]) -> str:
    kind = report["metadata"]["report_kind"]
    if kind == "export_leaks":
        return "Godot Export Leak Report"
    if kind == "export_diff":
        return "Godot Export Diff"
    if kind == "exported_folder_inspection":
        return "Godot Exported Folder Inspection"
    return "Godot Export Matrix"
