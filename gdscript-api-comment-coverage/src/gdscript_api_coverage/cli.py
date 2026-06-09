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
    _validate_thresholds(parser, args)

    items = scan_project(project, excludes=args.exclude)
    thresholds = _thresholds_from_args(args)
    findings = evaluate_thresholds(items, thresholds)

    if args.write_docs:
        docs_path = Path(args.write_docs)
        docs_path.parent.mkdir(parents=True, exist_ok=True)
        docs_path.write_text(_with_trailing_newline(render_markdown_index(items)), encoding="utf-8")

    if args.format == "json":
        rendered = render_json_report(items, findings)
    elif args.format == "markdown":
        rendered = render_markdown_index(items)
    else:
        rendered = render_text_report(items, findings)
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
    parser.add_argument("--version", action="version", version="gdscript-api-coverage 0.1.2")
    parser.add_argument("project", help="Godot project directory.")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
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


def _validate_thresholds(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    for name in (
        "min_all",
        "min_class",
        "min_signal",
        "min_exported_property",
        "min_public_func",
        "min_constant",
    ):
        value = getattr(args, name)
        if value < 0 or value > 100:
            parser.error(f"--{name.replace('_', '-')} must be between 0 and 100")


def _with_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def _exit_code(findings: object, fail_on: str) -> int:
    if fail_on == "none":
        return 0
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
