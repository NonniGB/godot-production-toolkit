from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .coverage import evaluate_thresholds
from .reporting import render_json_report, render_markdown_index, render_text_report
from .scanner import scan_project


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project)

    items = scan_project(project, excludes=args.exclude)
    thresholds = _thresholds_from_args(args)
    findings = evaluate_thresholds(items, thresholds)

    if args.write_docs:
        docs_path = Path(args.write_docs)
        docs_path.parent.mkdir(parents=True, exist_ok=True)
        docs_path.write_text(render_markdown_index(items), encoding="utf-8")

    rendered = (
        render_json_report(items, findings)
        if args.format == "json"
        else render_text_report(items, findings)
    )
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
        prog="gdscript-api-coverage",
        description="Generate GDScript API indexes and enforce comment coverage thresholds.",
    )
    parser.add_argument("--version", action="version", version="gdscript-api-coverage 0.1.0")
    parser.add_argument("project", help="Godot project directory.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument("--write-docs", help="Write generated Markdown API index.")
    parser.add_argument("--exclude", action="append", default=[], help="Project-relative path to skip.")
    parser.add_argument("--fail-on", choices=["error", "none"], default="error")
    parser.add_argument("--min-all", type=float, default=0)
    parser.add_argument("--min-class", type=float, default=0)
    parser.add_argument("--min-signal", type=float, default=0)
    parser.add_argument("--min-exported-property", type=float, default=0)
    parser.add_argument("--min-public-func", type=float, default=0)
    parser.add_argument("--min-constant", type=float, default=0)
    return parser


def _thresholds_from_args(args: argparse.Namespace) -> dict[str, float]:
    return {
        "all": args.min_all,
        "class": args.min_class,
        "signal": args.min_signal,
        "exported_property": args.min_exported_property,
        "public_func": args.min_public_func,
        "constant": args.min_constant,
    }


def _exit_code(findings: object, fail_on: str) -> int:
    if fail_on == "none":
        return 0
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
