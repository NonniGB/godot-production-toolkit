from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import audit_project_model
from .reporting import render_json_report, render_mermaid_graph, render_text_report
from .scanner import scan_project


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    autoloads = _parse_csv(args.autoload)
    scenes, scripts = scan_project(Path(args.project), autoloads=autoloads)
    findings = audit_project_model(
        scenes,
        scripts,
        strict_stale_connections=args.strict_stale_connections,
    )

    if args.format == "json":
        rendered = render_json_report(scenes, scripts, findings)
    elif args.format == "mermaid":
        rendered = render_mermaid_graph(scenes)
    else:
        rendered = render_text_report(scenes, scripts, findings)

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
        prog="godot-signal-audit",
        description="Audit Godot scene signal connections and autoload signal usage.",
    )
    parser.add_argument("--version", action="version", version="godot-signal-audit 0.1.1")
    parser.add_argument("project", help="Godot project directory.")
    parser.add_argument("--autoload", default="", help="Comma-separated autoload names to flag.")
    parser.add_argument("--strict-stale-connections", action="store_true")
    parser.add_argument("--format", choices=["text", "json", "mermaid"], default="text")
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument("--fail-on", choices=["warning", "error", "none"], default="warning")
    return parser


def _parse_csv(raw: str) -> set[str]:
    return {part.strip() for part in raw.split(",") if part.strip()}


def _exit_code(findings: object, fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {finding.severity for finding in findings}
    if fail_on == "error":
        return 1 if "error" in severities else 0
    return 1 if ("error" in severities or "warning" in severities) else 0


if __name__ == "__main__":
    sys.exit(main())
