from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adb_parser import parse_adb_summary
from .audit import audit_settings, texture_findings
from .models import AdbSummary
from .project_settings import parse_project_settings
from .reporting import render_json_report, render_markdown_report, render_sarif_report, render_text_report
from .textures import scan_textures


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project)
    project_file = project / "project.godot"
    settings = parse_project_settings(project_file.read_text(encoding="utf-8")) if project_file.exists() else {}
    textures = scan_textures(project, max_dimension=args.max_texture_dimension)
    findings = audit_settings(settings, profile=args.profile)
    findings.extend(texture_findings(textures, max_dimension=args.max_texture_dimension))
    adb = _load_adb(args.adb_summary)

    if args.format == "json":
        rendered = render_json_report(findings, textures, adb)
    elif args.format == "markdown":
        rendered = render_markdown_report(findings, textures, adb)
    elif args.format == "sarif":
        rendered = render_sarif_report(findings, textures, adb)
    else:
        rendered = render_text_report(findings, textures, adb)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return _exit_code(findings, args.fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-mobile-perf-doctor",
        description="Static mobile performance diagnostics for Godot projects.",
    )
    parser.add_argument("--version", action="version", version="godot-mobile-perf-doctor 0.1.0")
    parser.add_argument("project", help="Godot project directory.")
    parser.add_argument("--static", action="store_true", help="Run static checks. Present for CLI clarity.")
    parser.add_argument("--profile", default="portrait-2d")
    parser.add_argument("--max-texture-dimension", type=int, default=2048)
    parser.add_argument("--adb-summary", help="Optional mocked or captured adb summary text file.")
    parser.add_argument("--format", choices=["text", "json", "markdown", "sarif"], default="text")
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument("--fail-on", choices=["warning", "error", "none"], default="warning")
    return parser


def _load_adb(path: str | None) -> AdbSummary | None:
    if not path:
        return None
    summary_path = Path(path)
    if not summary_path.exists():
        return None
    return parse_adb_summary(summary_path.read_text(encoding="utf-8"))


def _exit_code(findings: object, fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {finding.severity for finding in findings}
    if fail_on == "error":
        return 1 if "error" in severities else 0
    return 1 if ("error" in severities or "warning" in severities) else 0


if __name__ == "__main__":
    sys.exit(main())
