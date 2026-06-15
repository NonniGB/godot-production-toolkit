from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .reports import compare, render, summarize

VERSION_LABEL = "godot-scenario-report 0.1.1"


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "summarize":
        report = summarize(Path(args.path))
    elif args.command == "compare":
        report = compare(Path(args.baseline), Path(args.current), args.duration_ratio)
    else:
        parser.print_help()
        return 2
    _emit(render(report, args.format), args.output)
    return _exit_code(report, args.fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-scenario-report",
        description="Validate, summarize, and compare Godot scenario run evidence.",
    )
    parser.add_argument("--version", action="version", version=VERSION_LABEL)
    subparsers = parser.add_subparsers(dest="command")

    summarize_parser = subparsers.add_parser("summarize", help="Summarize a scenario result file or directory.")
    summarize_parser.add_argument("path")
    _add_output_args(summarize_parser)

    compare_parser = subparsers.add_parser("compare", help="Compare baseline and current scenario results.")
    compare_parser.add_argument("baseline")
    compare_parser.add_argument("current")
    compare_parser.add_argument("--duration-ratio", type=float, default=1.5)
    _add_output_args(compare_parser)
    return parser


def _add_output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=["text", "json", "markdown", "html"], default="text")
    parser.add_argument("--output")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")


def _emit(rendered: str, output: str | None) -> None:
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


def _exit_code(report: dict[str, object], fail_on: str) -> int:
    summary = report["summary"]
    if fail_on == "none":
        return 0
    if fail_on == "warning":
        return 1 if int(summary["errors"]) + int(summary["warnings"]) > 0 else 0
    return 1 if int(summary["errors"]) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
