from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .reports import render_json, render_summary
from .runner import build_plan, exit_code_for_summary, run_plan, summarize_reports


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "plan":
        return _plan(args)
    if args.command == "run":
        return _run(args)
    if args.command == "summarize":
        return _summarize(args)
    parser.print_help()
    return 2


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-project-doctor",
        description="Plan, run, and summarize the Godot production toolkit.",
    )
    parser.add_argument("--version", action="version", version="godot-project-doctor 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    plan = subparsers.add_parser("plan", help="Show the tool commands that would run.")
    plan.add_argument("config", nargs="?", help="Optional godot-project-doctor.toml path.")
    plan.add_argument("--project", help="Override project path.")
    plan.add_argument("--checks", help="Comma-separated check ids to include.")
    plan.add_argument("--reports-dir", help="Override report directory.")
    plan.add_argument("--fail-on", choices=["none", "warning", "error"])
    plan.add_argument("--format", choices=["text", "json"], default="text")
    plan.add_argument("--output", help="Write output to a file.")

    run = subparsers.add_parser("run", help="Run enabled checks and summarize their JSON reports.")
    run.add_argument("config", nargs="?", help="Optional godot-project-doctor.toml path.")
    run.add_argument("--project", help="Override project path.")
    run.add_argument("--checks", help="Comma-separated check ids to include.")
    run.add_argument("--reports-dir", help="Override report directory.")
    run.add_argument("--fail-on", choices=["none", "warning", "error"])
    run.add_argument("--dry-run", action="store_true", help="Print the plan without creating reports or running tools.")
    run.add_argument("--timeout", type=int, default=120, help="Per-tool timeout in seconds.")
    run.add_argument("--format", choices=["text", "json", "markdown", "html"], default="text")
    run.add_argument("--output", help="Write output to a file.")

    summarize = subparsers.add_parser("summarize", help="Summarize a directory of JSON reports.")
    summarize.add_argument("reports_dir", help="Directory containing per-tool JSON reports.")
    summarize.add_argument("--format", choices=["text", "json", "markdown", "html"], default="text")
    summarize.add_argument("--output", help="Write output to a file.")
    summarize.add_argument("--fail-on", choices=["none", "warning", "error"], default="none")
    return parser


def _plan(args: argparse.Namespace) -> int:
    plan = _build_plan_from_args(args)
    rendered = render_json(plan) if args.format == "json" else _render_plan_text(plan)
    _emit(rendered, args.output)
    return 0


def _run(args: argparse.Namespace) -> int:
    plan = _build_plan_from_args(args)
    result = run_plan(plan, dry_run=args.dry_run, timeout=args.timeout)
    if args.dry_run:
        rendered = json.dumps(result, indent=2, sort_keys=True) if args.format == "json" else _render_plan_text(result)
        _emit(rendered, args.output)
        return 0

    rendered = render_summary(result, args.format)
    _emit(rendered, args.output)
    return exit_code_for_summary(result, plan["fail_on"])


def _summarize(args: argparse.Namespace) -> int:
    summary = summarize_reports(Path(args.reports_dir))
    _emit(render_summary(summary, args.format), args.output)
    return exit_code_for_summary(summary, args.fail_on)


def _build_plan_from_args(args: argparse.Namespace) -> dict[str, object]:
    return build_plan(
        config_path=Path(args.config) if args.config else None,
        project=Path(args.project) if args.project else None,
        checks=_split_checks(args.checks) if args.checks else None,
        reports_dir=Path(args.reports_dir) if args.reports_dir else None,
        fail_on=args.fail_on,
    )


def _split_checks(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _render_plan_text(plan: dict[str, object]) -> str:
    lines = [
        "Godot Project Doctor Plan",
        f"Project: {plan['project']}",
        f"Reports: {plan['reports_dir']}",
    ]
    for check in plan["checks"]:
        if check["enabled"]:
            lines.append(f"- {check['id']}: {' '.join(check['argv'])}")
        else:
            lines.append(f"- {check['id']}: disabled ({check['reason']})")
    return "\n".join(lines)


def _emit(rendered: str, output: str | None) -> None:
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    sys.exit(main())
