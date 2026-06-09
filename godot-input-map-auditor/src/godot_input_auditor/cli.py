from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import evaluate_actions
from .input_parser import parse_input_map
from .models import Finding
from .reporting import (
    render_gdscript_constants,
    render_json_report,
    render_markdown_reference,
    render_sarif_report,
    render_text_report,
)

KNOWN_DEVICE_FAMILIES = {"keyboard", "mouse", "controller", "touch"}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project)
    project_file = project if project.name == "project.godot" else project / "project.godot"

    if not project_file.exists():
        actions = []
        findings = [
            Finding(
                rule_id="missing_project_godot",
                severity="error",
                action=None,
                message="project.godot was not found.",
            )
        ]
    else:
        actions = parse_input_map(project_file.read_text(encoding="utf-8"))
        required_devices = _parse_required(args.require)
        unknown_devices = sorted(required_devices - KNOWN_DEVICE_FAMILIES)
        if unknown_devices:
            parser.error(f"unknown required device family: {', '.join(unknown_devices)}")
        findings = evaluate_actions(actions, required_devices=required_devices)

    if args.write_docs:
        path = Path(args.write_docs)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_markdown_reference(actions), encoding="utf-8")

    if args.generate_gd:
        path = Path(args.generate_gd)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_gdscript_constants(actions), encoding="utf-8")

    if args.format == "json":
        rendered = render_json_report(actions, findings)
    elif args.format == "sarif":
        rendered = render_sarif_report(actions, findings)
    else:
        rendered = render_text_report(actions, findings)
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
        prog="godot-input-audit",
        description="Audit Godot input actions for device coverage and duplicate bindings.",
    )
    parser.add_argument("--version", action="version", version="godot-input-audit 0.1.1")
    parser.add_argument("project", help="Godot project directory or project.godot file.")
    parser.add_argument(
        "--require",
        default="",
        help="Comma-separated device families every action should support, e.g. keyboard,touch.",
    )
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text")
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument("--write-docs", help="Write Markdown input reference.")
    parser.add_argument("--generate-gd", help="Write GDScript constants file.")
    parser.add_argument("--fail-on", choices=["warning", "error", "none"], default="warning")
    return parser


def _parse_required(raw: str) -> set[str]:
    return {part.strip() for part in raw.split(",") if part.strip()}


def _exit_code(findings: list[Finding], fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {finding.severity for finding in findings}
    if fail_on == "error":
        return 1 if "error" in severities else 0
    return 1 if ("error" in severities or "warning" in severities) else 0


if __name__ == "__main__":
    sys.exit(main())
