from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .telemetry import BUDGET_PROFILES, adapt, budget_profile, compare, load_budget, render, summarize, timeline

VERSION_LABEL = "godot-telemetry-lab 0.1.2"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize and compare Godot runtime telemetry.")
    parser.add_argument("--version", action="version", version=VERSION_LABEL)
    subparsers = parser.add_subparsers(dest="command")

    summarize_parser = subparsers.add_parser("summarize", help="Summarize JSON or CSV telemetry samples.")
    summarize_parser.add_argument("path")
    _add_common_args(summarize_parser)

    compare_parser = subparsers.add_parser("compare", help="Compare current telemetry with a baseline.")
    compare_parser.add_argument("baseline")
    compare_parser.add_argument("current")
    compare_parser.add_argument("--regression-ratio", type=float, default=1.25)
    _add_common_args(compare_parser)

    timeline_parser = subparsers.add_parser("timeline", help="Render a frame and memory timeline from telemetry samples.")
    timeline_parser.add_argument("path")
    timeline_parser.add_argument("--memory-budget-mb", type=float)
    _add_common_args(timeline_parser, formats=["text", "json", "markdown", "html", "svg"], default_format="html")

    adapt_parser = subparsers.add_parser("adapt", help="Normalize common Godot telemetry field names.")
    adapt_parser.add_argument("path")
    adapt_parser.add_argument("--source-format", choices=["auto", "godot-monitor"], default="auto")
    adapt_parser.add_argument("--format", choices=["text", "json", "markdown"], default="json")
    adapt_parser.add_argument("--output")
    adapt_parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="none")

    budget_parser = subparsers.add_parser("budget", help="Create or inspect starter runtime budgets.")
    budget_subparsers = budget_parser.add_subparsers(dest="budget_command")
    init_parser = budget_subparsers.add_parser("init", help="Write a starter budget profile as JSON.")
    init_parser.add_argument("--profile", choices=sorted(BUDGET_PROFILES), default="desktop-dev")
    init_parser.add_argument("--format", choices=["text", "json", "markdown"], default="json")
    init_parser.add_argument("--output")

    args = parser.parse_args(argv)
    if args.command == "summarize":
        budget = _budget_from_args(args)
        report = summarize(Path(args.path), budget["frame_budget_ms"])
    elif args.command == "compare":
        budget = _budget_from_args(args)
        report = compare(Path(args.baseline), Path(args.current), budget["frame_budget_ms"], args.regression_ratio)
    elif args.command == "timeline":
        budget = _budget_from_args(args)
        memory_budget_mb = args.memory_budget_mb
        if memory_budget_mb is None:
            memory_budget_mb = budget.get("memory_budget_mb")
        report = timeline(Path(args.path), budget["frame_budget_ms"], memory_budget_mb)
    elif args.command == "adapt":
        report = adapt(Path(args.path), args.source_format)
    elif args.command == "budget" and args.budget_command == "init":
        report = budget_profile(args.profile)
    else:
        parser.print_help()
        return 2

    _emit(render(report, args.format), args.output)
    return _exit_code(report, getattr(args, "fail_on", "none"))


def entrypoint() -> None:
    raise SystemExit(main())


def _add_common_args(
    parser: argparse.ArgumentParser,
    formats: list[str] | None = None,
    default_format: str = "text",
) -> None:
    parser.add_argument("--frame-budget-ms", type=float, default=16.67)
    parser.add_argument("--budget-profile", choices=sorted(BUDGET_PROFILES))
    parser.add_argument("--budget-file")
    parser.add_argument("--format", choices=formats or ["text", "json", "markdown"], default=default_format)
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
    if "summary" not in report:
        return 0
    summary = report["summary"]
    if fail_on == "none":
        return 0
    if fail_on == "warning":
        return 1 if int(summary["errors"]) + int(summary["warnings"]) > 0 else 0
    return 1 if int(summary["errors"]) > 0 else 0


def _budget_from_args(args: argparse.Namespace) -> dict[str, float]:
    budget: dict[str, float] = {"frame_budget_ms": float(args.frame_budget_ms)}
    if args.budget_profile:
        profile = budget_profile(args.budget_profile)
        budget["frame_budget_ms"] = float(profile["frame_budget_ms"])
        budget["memory_budget_mb"] = float(profile["memory_budget_mb"])
    if args.budget_file:
        loaded = load_budget(Path(args.budget_file))
        if "frame_budget_ms" in loaded:
            budget["frame_budget_ms"] = float(loaded["frame_budget_ms"])
        if "memory_budget_mb" in loaded:
            budget["memory_budget_mb"] = float(loaded["memory_budget_mb"])
    return budget


if __name__ == "__main__":
    sys.exit(main())
