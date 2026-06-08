from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    id: str
    title: str
    command: str
    output_name: str
    default_enabled: bool
    project_arg: bool = True
    required_config: tuple[str, ...] = ()
    base_args: tuple[str, ...] = ()


TOOL_REGISTRY: tuple[ToolSpec, ...] = (
    ToolSpec("assets", "Asset Pipeline Doctor", "godot-asset-doctor", "assets.json", True),
    ToolSpec("export", "Export Preset Doctor", "godot-export-doctor", "export.json", True),
    ToolSpec("api_comments", "GDScript API Comment Coverage", "gdscript-api-coverage", "api-comments.json", True),
    ToolSpec("input", "Input Map Auditor", "godot-input-audit", "input-map.json", True),
    ToolSpec("localization", "Localization QA Guard", "godot-l10n-guard", "localization.json", True),
    ToolSpec("save_schema", "Save Schema Guard", "godot-save-guard", "save-schema.json", False, required_config=("fixtures", "schema")),
    ToolSpec("signals", "Scene Signal Auditor", "godot-signal-audit", "signals.json", True),
    ToolSpec("visual_smoke", "Visual Smoke Test Kit", "godot-visual-smoke", "visual-smoke-plan.json", False, required_config=("config",)),
    ToolSpec("mobile_perf", "Mobile Perf Doctor", "godot-mobile-perf-doctor", "mobile-perf.json", True, base_args=("--static",)),
    ToolSpec("pixel_assets", "Pixel Space Asset Toolkit", "pixel-space-assets", "pixel-assets.json", False, required_config=("command",)),
)


def load_config(config_path: Path | None) -> tuple[dict[str, Any], Path]:
    if not config_path:
        return {}, Path.cwd()
    resolved = config_path.resolve()
    return tomllib.loads(resolved.read_text(encoding="utf-8")), resolved.parent


def build_plan(
    config_path: Path | None = None,
    project: Path | None = None,
    checks: list[str] | None = None,
    reports_dir: Path | None = None,
    fail_on: str | None = None,
) -> dict[str, Any]:
    config, base_dir = load_config(config_path)
    project_config = config.get("project", {})
    tool_config = config.get("tools", {})

    project_root = _resolve_path(base_dir, str(project or project_config.get("path", ".")))
    report_root = _resolve_path(base_dir, str(reports_dir or project_config.get("reports_dir", "reports/godot-project-doctor")))
    selected = _selected_checks(project_config, checks)
    fail_threshold = fail_on or str(project_config.get("fail_on", "error"))

    check_plans: list[dict[str, Any]] = []
    for spec in TOOL_REGISTRY:
        specific_config = tool_config.get(spec.id, {})
        enabled = _is_enabled(spec, selected, specific_config)
        reason = "" if enabled else _disabled_reason(spec, selected, specific_config)
        missing_config = [key for key in spec.required_config if not specific_config.get(key)]
        if enabled and missing_config:
            enabled = False
            reason = f"missing required config: {', '.join(missing_config)}"
        report_path = report_root / spec.output_name
        argv = _build_tool_argv(spec, project_root, report_path, specific_config)
        check_plans.append(
            {
                "id": spec.id,
                "title": spec.title,
                "enabled": enabled,
                "reason": reason,
                "report": str(report_path),
                "argv": argv,
            }
        )

    return {
        "tool": "godot-project-doctor",
        "project": str(project_root),
        "reports_dir": str(report_root),
        "fail_on": fail_threshold,
        "checks": check_plans,
        "commands": [
            {"id": item["id"], "argv": item["argv"], "report": item["report"]}
            for item in check_plans
            if item["enabled"]
        ],
    }


def run_plan(plan: dict[str, Any], dry_run: bool = False, timeout: int = 120) -> dict[str, Any]:
    if dry_run:
        return {"status": "planned", **plan}

    reports_dir = Path(str(plan["reports_dir"]))
    reports_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for command in plan["commands"]:
        completed = subprocess.run(command["argv"], capture_output=True, text=True, timeout=timeout, check=False)
        results.append(
            {
                "id": command["id"],
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
                "report": command["report"],
            }
        )
    summary = summarize_reports(reports_dir)
    return {"status": "completed", "plan": plan, "results": results, "summary": summary["summary"], "reports": summary["reports"]}


def summarize_reports(reports_dir: Path) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    for path in sorted(reports_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        errors, warnings = _severity_counts(data)
        reports.append(
            {
                "tool": _tool_name(data, path),
                "path": str(path),
                "summary": {"errors": errors, "warnings": warnings},
                "finding_count": _finding_count(data),
                "findings": _findings(data),
            }
        )
    return {
        "tool": "godot-project-doctor",
        "reports_dir": str(reports_dir),
        "summary": {
            "tools": len(reports),
            "errors": sum(int(report["summary"]["errors"]) for report in reports),
            "warnings": sum(int(report["summary"]["warnings"]) for report in reports),
        },
        "reports": reports,
    }


def exit_code_for_summary(summary: dict[str, Any], fail_on: str) -> int:
    totals = summary["summary"] if "summary" in summary else summary
    if fail_on == "none":
        return 0
    if fail_on == "warning" and int(totals["errors"]) + int(totals["warnings"]) > 0:
        return 1
    if fail_on == "error" and int(totals["errors"]) > 0:
        return 1
    return 0


def _selected_checks(project_config: dict[str, Any], cli_checks: list[str] | None) -> set[str] | None:
    raw_checks = cli_checks if cli_checks is not None else project_config.get("checks")
    if not raw_checks:
        return None
    if isinstance(raw_checks, str):
        raw_checks = [item.strip() for item in raw_checks.split(",")]
    return {str(item).strip() for item in raw_checks if str(item).strip()}


def _is_enabled(spec: ToolSpec, selected: set[str] | None, config: dict[str, Any]) -> bool:
    if "enabled" in config:
        return bool(config["enabled"])
    if selected is not None:
        return spec.id in selected
    return spec.default_enabled


def _disabled_reason(spec: ToolSpec, selected: set[str] | None, config: dict[str, Any]) -> str:
    if config.get("enabled") is False:
        return "disabled by config"
    if selected is not None and spec.id not in selected:
        return "not selected"
    if not spec.default_enabled:
        return "specialized tool; enable with required config"
    return ""


def _build_tool_argv(spec: ToolSpec, project: Path, report_path: Path, config: dict[str, Any]) -> list[str]:
    args = [str(item) for item in config.get("args", [])]
    if spec.id == "save_schema":
        return [
            spec.command,
            "validate",
            str(_resolve_path(project, str(config.get("fixtures", ".")))),
            "--schema",
            str(_resolve_path(project, str(config.get("schema", "schema.json")))),
            "--format",
            "json",
            "--output",
            str(report_path),
            *args,
        ]
    if spec.id == "visual_smoke":
        return [
            spec.command,
            "plan",
            str(_resolve_path(project, str(config.get("config", "visual-smoke.toml")))),
            "--project",
            str(project),
            "--format",
            "json",
            *args,
        ]
    if spec.id == "pixel_assets":
        command = str(config.get("command", "preview"))
        return [spec.command, command, *args, "--format", "json"]

    return [
        spec.command,
        str(project),
        *spec.base_args,
        "--format",
        "json",
        "--output",
        str(report_path),
        *args,
    ]


def _resolve_path(base: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (base / path).resolve()


def _tool_name(data: dict[str, Any], path: Path) -> str:
    return str(data.get("tool") or data.get("name") or path.stem)


def _severity_counts(data: dict[str, Any]) -> tuple[int, int]:
    summary = data.get("summary", {})
    errors = int(summary.get("errors", summary.get("error_count", 0)))
    warnings = int(summary.get("warnings", summary.get("warning_count", 0)))
    if errors or warnings:
        return errors, warnings

    errors = 0
    warnings = 0
    for finding in _findings(data):
        severity = str(finding.get("severity", "")).lower()
        if severity == "error":
            errors += 1
        elif severity == "warning":
            warnings += 1
    return errors, warnings


def _finding_count(data: dict[str, Any]) -> int:
    return len(_findings(data))


def _findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("findings", "issues"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []
