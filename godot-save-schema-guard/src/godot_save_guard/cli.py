from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .fixtures import generate_fixture, validate_fixtures
from .migration import (
    analyze_migration_graph,
    build_chain_commands,
    build_migration_command,
    compare_migrated_fixture,
    load_migration_chain,
    run_migration_command,
)
from .models import Finding, FixtureResult
from .redaction import RedactionOptions, redact_fixtures
from .reporting import render_json_report, render_markdown_report, render_text_report


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        return _validate(args)
    if args.command == "generate-fixture":
        return _generate_fixture(args)
    if args.command == "migrate":
        return _migrate(args)
    if args.command == "migrate-chain":
        return _migrate_chain(args)
    if args.command == "migration-graph":
        return _migration_graph(args)
    if args.command == "redact":
        return _redact(args)
    parser.print_help()
    return 2


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-save-guard",
        description="Validate Godot save fixtures and migration compatibility.",
    )
    parser.add_argument("--version", action="version", version="godot-save-guard 0.1.7")
    subparsers = parser.add_subparsers(dest="command")

    validate = subparsers.add_parser("validate", help="Validate JSON save fixtures.")
    validate.add_argument("fixtures", help="JSON fixture file or directory.")
    validate.add_argument("--schema", required=True, help="JSON schema file.")
    _add_report_args(validate)

    generate = subparsers.add_parser("generate-fixture", help="Generate a deterministic JSON fixture from a schema.")
    generate.add_argument("--schema", required=True, help="JSON schema file.")
    generate.add_argument("--fixture-output", required=True, help="Fixture JSON path to write.")
    generate.add_argument(
        "--include-optional",
        action="store_true",
        help="Include optional schema properties as well as required properties.",
    )
    generate.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        help='Override a dotted object path with a JSON value, such as --set \'player.name="Ada"\'.',
    )
    generate.add_argument("--overwrite", action="store_true", help="Replace an existing generated fixture.")
    _add_report_args(generate)

    migrate = subparsers.add_parser("migrate", help="Run a migration command for fixtures.")
    migrate.add_argument("fixtures", help="JSON fixture file or directory.")
    migrate.add_argument("--command", required=True, help="Command template using {input} and {output}.")
    migrate.add_argument("--output-dir", required=True, help="Directory for migrated fixtures.")
    _add_report_args(migrate)

    migrate_chain = subparsers.add_parser("migrate-chain", help="Run an ordered migration chain for fixtures.")
    migrate_chain.add_argument("fixtures", help="JSON fixture file or directory.")
    migrate_chain.add_argument("--chain", required=True, help="TOML file containing ordered migration steps.")
    migrate_chain.add_argument("--output-dir", required=True, help="Directory for migrated fixtures.")
    migrate_chain.add_argument(
        "--schema",
        help="Validate each final migrated fixture against this JSON schema after the chain succeeds.",
    )
    migrate_chain.add_argument("--dry-run", action="store_true", help="Plan commands without executing them.")
    migrate_chain.add_argument(
        "--compare-original",
        action="store_true",
        help="Compare each original fixture with its final migrated output and add a dashboard-friendly summary.",
    )
    _add_report_args(migrate_chain)

    migration_graph = subparsers.add_parser(
        "migration-graph",
        help="Verify supported save versions can migrate to the current version.",
    )
    migration_graph.add_argument("--chain", required=True, help="TOML file containing migration steps.")
    migration_graph.add_argument("--current", required=True, help="Current save version.")
    migration_graph.add_argument(
        "--supported",
        action="append",
        default=[],
        help="Supported old save version. Repeat for each supported version. Defaults to versions found in the chain.",
    )
    _add_report_args(migration_graph)

    redact = subparsers.add_parser("redact", help="Write sanitized copies of save fixtures.")
    redact.add_argument("fixtures", help="JSON fixture file or directory.")
    redact.add_argument("--output-dir", required=True, help="Directory for sanitized fixture copies.")
    redact.add_argument(
        "--path",
        "--field",
        dest="paths",
        action="append",
        required=True,
        help="Dotted path to redact. Use * for array or object children. Repeat for each path.",
    )
    redact.add_argument("--replacement", help="Replacement value. Defaults to type-aware placeholder values.")
    redact.add_argument("--dry-run", action="store_true", help="Report planned redactions without writing files.")
    redact.add_argument("--overwrite", action="store_true", help="Replace existing sanitized fixture files.")
    _add_report_args(redact)
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


def _generate_fixture(args: argparse.Namespace) -> int:
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    result = generate_fixture(
        schema,
        Path(args.fixture_output),
        include_optional=args.include_optional,
        overwrite=args.overwrite,
        overrides=args.overrides,
    )
    _write_report(args, [result])
    return _exit_code([result], args.fail_on)


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


def _migrate_chain(args: argparse.Namespace) -> int:
    fixtures_path = Path(args.fixtures)
    files = [fixtures_path] if fixtures_path.is_file() else sorted(fixtures_path.rglob("*.json"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    steps = load_migration_chain(Path(args.chain))
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8")) if args.schema and not args.dry_run else None
    results: list[FixtureResult] = []
    if not files:
        results.append(
            FixtureResult(
                fixtures_path,
                [Finding("no_fixtures", "error", "$", "No JSON save fixtures were found.")],
            )
        )
    if not steps:
        results.append(
            FixtureResult(
                Path(args.chain),
                [Finding("migration_chain_empty", "error", "$", "No valid migration steps were found.")],
            )
        )
    for fixture in files:
        findings: list[Finding] = []
        commands = build_chain_commands(steps, fixture, output_dir)
        if args.dry_run:
            labels = ", ".join(step.label for step, _, _, _ in commands) or "none"
            findings.append(
                Finding(
                    "migration_chain_planned",
                    "info",
                    "$",
                    f"Planned {len(commands)} migration step(s): {labels}.",
                )
            )
        else:
            for step, _, output_path, command in commands:
                finding = run_migration_command(command, capture_output=True)
                if finding:
                    findings.append(
                        Finding(
                            finding.rule_id,
                            finding.severity,
                            finding.json_path,
                            (
                                f"Migration step {step.label} failed for {fixture.name}. "
                                f"Expected output: {output_path}. {finding.message} "
                                "Review this step's migration script before continuing the chain."
                            ),
                        )
                    )
                    break
            if schema is not None and commands and not any(finding.severity == "error" for finding in findings):
                final_output = commands[-1][2]
                if final_output.exists():
                    validated = validate_fixtures(final_output, schema)
                    results.extend(validated)
                else:
                    findings.append(
                        Finding(
                            "migration_output_missing",
                            "error",
                            "$",
                            f"Final migrated fixture was not written: {final_output}.",
                        )
                    )
            if (
                args.compare_original
                and commands
                and not any(finding.severity == "error" for finding in findings)
            ):
                final_output = commands[-1][2]
                if final_output.exists():
                    findings.append(compare_migrated_fixture(fixture, final_output))
                else:
                    findings.append(
                        Finding(
                            "migration_output_missing",
                            "error",
                            "$",
                            f"Final migrated fixture was not written: {final_output}.",
                        )
                    )
        results.append(FixtureResult(fixture, findings))
    _write_report(args, results)
    return _exit_code(results, args.fail_on)


def _migration_graph(args: argparse.Namespace) -> int:
    chain_path = Path(args.chain)
    steps = load_migration_chain(chain_path)
    findings = analyze_migration_graph(steps, args.current, args.supported)
    results = [FixtureResult(chain_path, findings)]
    _write_report(args, results)
    return _exit_code(results, args.fail_on)


def _redact(args: argparse.Namespace) -> int:
    fixtures_path = Path(args.fixtures)
    results = redact_fixtures(
        fixtures_path,
        RedactionOptions(
            paths=args.paths,
            output_dir=Path(args.output_dir),
            replacement=args.replacement,
            dry_run=args.dry_run,
            overwrite=args.overwrite,
        ),
    )
    if not results:
        results = [
            FixtureResult(
                fixtures_path,
                [Finding("no_fixtures", "error", "$", "No JSON save fixtures were found.")],
            )
        ]
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
