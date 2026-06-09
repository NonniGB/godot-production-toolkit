from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .fixtures import validate_fixtures
from .migration import build_migration_command, run_migration_command
from .models import Finding, FixtureResult
from .reporting import render_json_report, render_markdown_report, render_text_report


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        return _validate(args)
    if args.command == "migrate":
        return _migrate(args)
    parser.print_help()
    return 2


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-save-guard",
        description="Validate Godot save fixtures and migration compatibility.",
    )
    parser.add_argument("--version", action="version", version="godot-save-guard 0.1.1")
    subparsers = parser.add_subparsers(dest="command")

    validate = subparsers.add_parser("validate", help="Validate JSON save fixtures.")
    validate.add_argument("fixtures", help="JSON fixture file or directory.")
    validate.add_argument("--schema", required=True, help="JSON schema file.")
    _add_report_args(validate)

    migrate = subparsers.add_parser("migrate", help="Run a migration command for fixtures.")
    migrate.add_argument("fixtures", help="JSON fixture file or directory.")
    migrate.add_argument("--command", required=True, help="Command template using {input} and {output}.")
    migrate.add_argument("--output-dir", required=True, help="Directory for migrated fixtures.")
    _add_report_args(migrate)
    return parser


def _add_report_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument("--fail-on", choices=["warning", "error", "none"], default="error")


def _validate(args: argparse.Namespace) -> int:
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    fixtures_path = Path(args.fixtures)
    results = validate_fixtures(fixtures_path, schema)
    if not results:
        results = [
            FixtureResult(
                fixtures_path,
                [Finding("no_fixtures", "error", "$", "No JSON save fixtures were found.")],
            )
        ]
    _write_report(args, results)
    return _exit_code(results, args.fail_on)


def _migrate(args: argparse.Namespace) -> int:
    fixtures_path = Path(args.fixtures)
    files = [fixtures_path] if fixtures_path.is_file() else sorted(fixtures_path.rglob("*.json"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[FixtureResult] = []
    if not files:
        results.append(
            FixtureResult(
                fixtures_path,
                [Finding("no_fixtures", "error", "$", "No JSON save fixtures were found.")],
            )
        )
    for fixture in files:
        output = output_dir / fixture.name
        command = build_migration_command(args.command, fixture, output)
        finding = run_migration_command(command)
        results.append(FixtureResult(fixture, [finding] if finding else []))
    _write_report(args, results)
    return _exit_code(results, args.fail_on)


def _write_report(args: argparse.Namespace, results: list[FixtureResult]) -> None:
    if args.format == "json":
        rendered = render_json_report(results)
    elif args.format == "markdown":
        rendered = render_markdown_report(results)
    else:
        rendered = render_text_report(results)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


def _exit_code(results: list[FixtureResult], fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {finding.severity for result in results for finding in result.findings}
    if fail_on == "warning":
        return 1 if ("error" in severities or "warning" in severities) else 0
    return 1 if "error" in severities else 0


if __name__ == "__main__":
    sys.exit(main())
