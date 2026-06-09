from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Any

from .adb_parser import parse_adb_summary
from .audit import audit_settings, texture_findings
from .models import AdbSummary, Finding
from .project_settings import parse_project_settings
from .reporting import render_json_report, render_markdown_report, render_sarif_report, render_text_report
from .textures import scan_textures

DEFAULT_CONFIG = ".godot-mobile-perf-doctor.toml"


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project)
    config = _load_config(project, Path(args.config) if args.config else None)
    profile = _configured_value(args.profile, config, "profile", "portrait-2d")
    output_format = _configured_value(args.format, config, "format", "text")
    output = _configured_value(args.output, config, "output", None)
    fail_on = _configured_value(args.fail_on, config, "fail_on", "warning")
    max_texture_dimension = _configured_int(args.max_texture_dimension, config, "max_texture_dimension", 2048)
    max_viewport_pixels = _configured_int(args.max_viewport_pixels, config, "max_viewport_pixels", 1920 * 1080)
    adb_summary = _configured_value(args.adb_summary, config, "adb_summary", None)

    project_file = project / "project.godot"
    settings = parse_project_settings(project_file.read_text(encoding="utf-8")) if project_file.exists() else {}
    textures = scan_textures(project, max_dimension=max_texture_dimension)
    findings = audit_settings(settings, profile=profile, max_viewport_pixels=max_viewport_pixels)
    if not project_file.exists():
        findings.insert(
            0,
            Finding(
                "missing_project_godot",
                "error",
                "project.godot was not found, so project settings could not be audited.",
                project_file.as_posix(),
            ),
        )
    findings.extend(texture_findings(textures, max_dimension=max_texture_dimension))
    adb = _load_adb(adb_summary)

    if output_format == "json":
        rendered = render_json_report(findings, textures, adb)
    elif output_format == "markdown":
        rendered = render_markdown_report(findings, textures, adb)
    elif output_format == "sarif":
        rendered = render_sarif_report(findings, textures, adb)
    else:
        rendered = render_text_report(findings, textures, adb)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return _exit_code(findings, fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-mobile-perf-doctor",
        description="Static mobile performance diagnostics for Godot projects.",
    )
    parser.add_argument("--version", action="version", version="godot-mobile-perf-doctor 0.1.3")
    parser.add_argument("project", help="Godot project directory.")
    parser.add_argument("--static", action="store_true", help="Run static checks. Present for CLI clarity.")
    parser.add_argument("--config", help=f"TOML config path. Defaults to {DEFAULT_CONFIG}.")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--max-texture-dimension", type=int, default=None)
    parser.add_argument("--max-viewport-pixels", type=int, default=None)
    parser.add_argument("--adb-summary", help="Optional mocked or captured adb summary text file.")
    parser.add_argument("--format", choices=["text", "json", "markdown", "sarif"], default=None)
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument("--fail-on", choices=["warning", "error", "none"], default=None)
    return parser


def _load_adb(path: str | None) -> AdbSummary | None:
    if not path:
        return None
    summary_path = Path(path)
    if not summary_path.exists():
        return None
    return parse_adb_summary(summary_path.read_text(encoding="utf-8"))


def _load_config(project: Path, explicit_config: Path | None) -> dict[str, Any]:
    config_path = explicit_config or project / DEFAULT_CONFIG
    if not config_path.exists():
        return {}
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    return data if isinstance(data, dict) else {}


def _configured_value(
    cli_value: str | None,
    config: dict[str, Any],
    key: str,
    default: str | None,
) -> str | None:
    if cli_value is not None:
        return cli_value
    value = config.get(key, default)
    return str(value) if value is not None else None


def _configured_int(cli_value: int | None, config: dict[str, Any], key: str, default: int) -> int:
    if cli_value is not None:
        return cli_value
    value = config.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _exit_code(findings: object, fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {finding.severity for finding in findings}
    if fail_on == "error":
        return 1 if "error" in severities else 0
    return 1 if ("error" in severities or "warning" in severities) else 0


if __name__ == "__main__":
    sys.exit(main())
