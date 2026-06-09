from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .reports import render_json, render_summary
from .runner import (
    build_plan,
    collect_evidence,
    exit_code_for_summary,
    explain_check,
    inspect_project,
    render_github_action_example,
    render_starter_config,
    run_plan,
    summarize_reports,
)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "plan":
        return _plan(args)
    if args.command == "inspect":
        return _inspect(args)
    if args.command == "recommend":
        return _recommend(args)
    if args.command == "init":
        return _init(args)
    if args.command == "explain":
        return _explain(args)
    if args.command == "run":
        return _run(args)
    if args.command == "collect":
        return _collect(args)
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
    parser.add_argument("--version", action="version", version="godot-project-doctor 0.1.3")
    subparsers = parser.add_subparsers(dest="command")

    plan = subparsers.add_parser("plan", help="Show the tool commands that would run.")
    plan.add_argument("config", nargs="?", help="Optional godot-project-doctor.toml path.")
    plan.add_argument("--project", help="Override project path.")
    plan.add_argument("--checks", help="Comma-separated check ids to include.")
    plan.add_argument("--reports-dir", help="Override report directory.")
    plan.add_argument("--fail-on", choices=["none", "warning", "error"])
    plan.add_argument("--format", choices=["text", "json"], default="text")
    plan.add_argument("--output", help="Write output to a file.")

    inspect = subparsers.add_parser("inspect", help="Inspect a project and show detected production-check signals.")
    inspect.add_argument("project", help="Godot project directory.")
    inspect.add_argument("--format", choices=["text", "json"], default="text")
    inspect.add_argument("--output", help="Write output to a file.")

    recommend = subparsers.add_parser("recommend", help="Recommend a short check set for a project.")
    recommend.add_argument("project", help="Godot project directory.")
    recommend.add_argument("--format", choices=["text", "json"], default="text")
    recommend.add_argument("--output", help="Write output to a file.")

    init = subparsers.add_parser("init", help="Create or preview a starter godot-project-doctor config.")
    init.add_argument("project", nargs="?", default=".", help="Godot project directory.")
    init.add_argument("--config", default="godot-project-doctor.toml", help="Config path to write inside the project.")
    init.add_argument("--reports-dir", default="reports/godot-project-doctor", help="Default report directory.")
    init.add_argument("--dry-run", action="store_true", help="Print files that would be written without writing them.")
    init.add_argument("--include-workflow", action="store_true", help="Also preview/write a GitHub Actions workflow.")
    init.add_argument("--output", help="Write dry-run preview to a file.")

    explain = subparsers.add_parser("explain", help="Explain a check id such as assets, export, or content_graph.")
    explain.add_argument("check_id", help="Check id to explain.")
    explain.add_argument("--format", choices=["text", "json"], default="text")
    explain.add_argument("--output", help="Write output to a file.")

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

    collect = subparsers.add_parser("collect", help="Create an evidence folder from configured checks and reports.")
    collect.add_argument("config", nargs="?", help="Optional godot-project-doctor.toml path.")
    collect.add_argument("--project", help="Override project path.")
    collect.add_argument("--checks", help="Comma-separated check ids to include.")
    collect.add_argument("--reports-dir", help="Override report directory.")
    collect.add_argument("--evidence-dir", default="reports/godot-project-doctor/evidence", help="Folder for manifest and summary files.")
    collect.add_argument("--fail-on", choices=["none", "warning", "error"])
    collect.add_argument("--skip-run", action="store_true", help="Collect existing reports without running tools first.")
    collect.add_argument("--timeout", type=int, default=120, help="Per-tool timeout in seconds.")
    collect.add_argument("--format", choices=["text", "json"], default="text")
    collect.add_argument("--output", help="Write command output to a file.")

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


def _inspect(args: argparse.Namespace) -> int:
    inspected = inspect_project(Path(args.project))
    rendered = render_json(inspected) if args.format == "json" else _render_inspect_text(inspected)
    _emit(rendered, args.output)
    return 0


def _recommend(args: argparse.Namespace) -> int:
    inspected = inspect_project(Path(args.project))
    payload = {
        "tool": "godot-project-doctor",
        "project": inspected["project"],
        "recommendations": inspected["recommendations"],
    }
    rendered = render_json(payload) if args.format == "json" else _render_recommend_text(payload)
    _emit(rendered, args.output)
    return 0


def _init(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    config_text = render_starter_config(project, args.reports_dir)
    inspected = inspect_project(project)
    checks = [item["id"] for item in inspected["recommendations"][:6]]
    workflow_text = render_github_action_example(checks)
    config_path = project / args.config
    workflow_path = project / ".github" / "workflows" / "godot-production-checks.yml"

    if args.dry_run:
        rendered = _render_init_preview(config_path, config_text, workflow_path if args.include_workflow else None, workflow_text)
        _emit(rendered, args.output)
        return 0

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config_text + "\n", encoding="utf-8")
    (project / args.reports_dir).mkdir(parents=True, exist_ok=True)
    if args.include_workflow:
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        workflow_path.write_text(workflow_text + "\n", encoding="utf-8")
    return 0


def _explain(args: argparse.Namespace) -> int:
    try:
        payload = explain_check(args.check_id)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    rendered = render_json(payload) if args.format == "json" else _render_explain_text(payload)
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


def _collect(args: argparse.Namespace) -> int:
    plan = _build_plan_from_args(args)
    manifest = collect_evidence(
        plan,
        evidence_dir=Path(args.evidence_dir),
        skip_run=args.skip_run,
        timeout=args.timeout,
    )
    rendered = render_json(manifest) if args.format == "json" else _render_collect_text(manifest)
    _emit(rendered, args.output)
    return exit_code_for_summary(manifest, plan["fail_on"])


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


def _render_inspect_text(inspected: dict[str, object]) -> str:
    details = inspected.get("details", {})
    lines = [
        "Godot Project Doctor Inspect",
        f"Project: {inspected['project']}",
    ]
    if isinstance(details, dict) and details.get("project_name"):
        lines.append(f"Name: {details['project_name']}")
    if isinstance(details, dict):
        lines.extend(
            [
                "",
                "Project shape:",
                f"- files: {details.get('file_count', 0)}",
                f"- GDScript files: {details.get('gdscript_count', 0)}",
                f"- PNG assets: {details.get('png_count', 0)}",
                f"- localization files: {details.get('localization_count', 0)}",
                f"- content data files: {details.get('content_file_count', 0)}",
                f"- scenario result files: {details.get('scenario_result_count', 0)}",
            ]
        )
        frameworks = details.get("test_frameworks", [])
        if frameworks:
            lines.append(f"- test frameworks: {', '.join(str(item) for item in frameworks)}")
    lines.extend(["", "Detected signals:"])
    features = inspected["features"]
    for key, value in sorted(features.items()):
        label = "yes" if value else "no"
        lines.append(f"- {key.replace('_', ' ')}: {label}")
    if isinstance(details, dict):
        sample_paths = details.get("sample_paths", {})
        if isinstance(sample_paths, dict):
            visible_samples = [
                f"{group}: {', '.join(paths)}"
                for group, paths in sample_paths.items()
                if isinstance(paths, list) and paths
            ]
            if visible_samples:
                lines.extend(["", "Sample files:"])
                lines.extend(f"- {sample}" for sample in visible_samples)
    lines.extend(["", "Recommended checks:"])
    for item in inspected["recommendations"]:
        lines.append(f"- {item['id']}: {item['reason']} ({item.get('priority', 'normal')}; {item.get('config', 'ready')})")
    return "\n".join(lines)


def _render_recommend_text(payload: dict[str, object]) -> str:
    lines = [
        "Godot Project Doctor Recommendations",
        f"Project: {payload['project']}",
    ]
    for item in payload["recommendations"]:
        lines.extend(
            [
                "",
                f"- {item['id']} ({item['title']})",
                f"  Reason: {item['reason']}",
                f"  Why it helps: {item['why']}",
                f"  Use it: {item['when']}",
                f"  Setup: {item.get('config', 'ready from project path')}",
                f"  Try: {item.get('command', 'godot-project-doctor run --project <project> --checks ' + item['id'] + ' --dry-run')}",
            ]
        )
    return "\n".join(lines)


def _render_init_preview(config_path: Path, config_text: str, workflow_path: Path | None, workflow_text: str) -> str:
    lines = [
        f"Would write {config_path}:",
        "",
        config_text,
    ]
    if workflow_path:
        lines.extend(["", f"Would write {workflow_path}:", "", workflow_text])
    return "\n".join(lines)


def _render_explain_text(payload: dict[str, str]) -> str:
    return "\n".join(
        [
            f"{payload['id']} - {payload['title']}",
            f"Why it helps: {payload['why']}",
            f"Use it: {payload['when']}",
        ]
    )


def _render_collect_text(manifest: dict[str, object]) -> str:
    summary = manifest["summary"]
    lines = [
        "Godot Project Doctor Evidence",
        f"Evidence: {manifest['evidence_dir']}",
        f"Reports: {manifest['reports_dir']}",
        f"Tools: {summary['tools']}",
        f"Errors: {summary['errors']}",
        f"Warnings: {summary['warnings']}",
        "",
        "Files:",
        "- manifest.json",
        "- summary.json",
        "- summary.md",
        "- summary.html",
        "- artifacts.json",
    ]
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
