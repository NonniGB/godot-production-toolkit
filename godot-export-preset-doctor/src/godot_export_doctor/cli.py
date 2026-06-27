from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

from .models import ExportPreset, Finding
from .matrix import (
    diff_report,
    exported_file_list_report,
    exported_folder_report,
    leak_report,
    matrix_report,
    render_matrix_report,
)
from .preset_parser import parse_export_presets
from .reporting import render_json_report, render_sarif_report, render_text_report
from .rules import evaluate_presets, missing_export_presets_finding

DEFAULT_CONFIG = ".godot-export-doctor.toml"


def main(argv: list[str] | None = None) -> int:
    argv = _normalize_legacy_argv(argv)
    parser = _build_parser()
    args = parser.parse_args(argv)
    command = args.command or "check"
    project = Path(args.project)
    try:
        config = _load_config(project, Path(args.config) if args.config else None)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        parser.error(f"could not read config: {exc}")

    output_format = args.format or str(config.get("format", "text"))
    fail_on = args.fail_on or str(config.get("fail_on", "warning"))
    platform = args.platform or config.get("platform")
    report_platform = args.platform if command in {"matrix", "leaks", "diff"} else platform
    required_android_abis = _configured_list(args.required_android_abi, config, "required_android_abis")
    allowed_secret_patterns = _configured_list(args.allow_secret_pattern, config, "allowed_secret_patterns")
    allowed_formats = {"text", "json", "sarif"} if command == "check" else {"text", "json", "markdown", "html"}
    _validate_choice(parser, "format", output_format, allowed_formats)
    _validate_choice(parser, "fail_on", fail_on, {"none", "warning", "error"})

    presets_file = _resolve_presets_file(project)
    if presets_file.exists():
        presets = parse_export_presets(presets_file.read_text(encoding="utf-8"))
        report_presets = _filter_presets(presets, report_platform)
        findings = evaluate_presets(
            presets,
            platform=str(platform) if platform else None,
            required_android_abis=[str(abi) for abi in required_android_abis],
            allowed_secret_patterns=allowed_secret_patterns,
        )
    else:
        report_presets = []
        findings = [missing_export_presets_finding()]

    if command == "matrix":
        expected = _configured_list(args.expected_platform, config, "expected_platforms")
        report = matrix_report(report_presets, expected_platforms=expected or None)
        rendered = render_matrix_report(report, output_format)
        findings = _findings_from_report(report)
    elif command == "leaks":
        report = leak_report(project, report_presets)
        rendered = render_matrix_report(report, output_format)
        findings = _findings_from_report(report)
    elif command == "diff":
        if not args.baseline:
            parser.error("diff requires --baseline")
        baseline_presets_file = _resolve_presets_file(Path(args.baseline))
        baseline_presets = (
            parse_export_presets(baseline_presets_file.read_text(encoding="utf-8"))
            if baseline_presets_file.exists()
            else []
        )
        report = diff_report(baseline_presets, report_presets)
        rendered = render_matrix_report(report, output_format)
        findings = _findings_from_report(report)
    elif command == "inspect-folder":
        report = exported_folder_report(project, hash_files=args.hash_files)
        rendered = render_matrix_report(report, output_format)
        findings = _findings_from_report(report)
    elif command in {"inspect-files", "pck"}:
        try:
            report = exported_file_list_report(project)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        rendered = render_matrix_report(report, output_format)
        findings = _findings_from_report(report)
    else:
        rendered = _render(output_format, report_presets, findings)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return _exit_code(findings, fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-export-doctor",
        description="Audit Godot export_presets.cfg release readiness.",
    )
    parser.add_argument("--version", action="version", version="godot-export-doctor 0.1.12")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["check", "matrix", "leaks", "diff", "inspect-folder", "inspect-files", "pck"],
        default="check",
    )
    parser.add_argument("project", help="Godot project directory or export_presets.cfg path.")
    parser.add_argument("--baseline", help="Baseline project directory or export_presets.cfg path for diff reports.")
    parser.add_argument("--config", help=f"TOML config path. Defaults to {DEFAULT_CONFIG}.")
    parser.add_argument("--platform", help="Only evaluate presets for a platform, such as Android.")
    parser.add_argument(
        "--required-android-abi",
        action="append",
        default=None,
        help="Require an Android ABI option such as arm64-v8a. Can be repeated.",
    )
    parser.add_argument(
        "--allow-secret-pattern",
        action="append",
        default=None,
        help="Allow a deliberate credential placeholder regex such as '<.+>'. Can be repeated.",
    )
    parser.add_argument(
        "--expected-platform",
        action="append",
        default=None,
        help="Expected platform for matrix reports, such as Android or Web. Can be repeated.",
    )
    parser.add_argument(
        "--hash-files",
        action="store_true",
        help="Include SHA-256 hashes in inspect-folder file manifests.",
    )
    parser.add_argument("--format", choices=["text", "json", "sarif", "markdown", "html"], help="Report format.")
    parser.add_argument("--output", help="Write the report to this file instead of stdout.")
    parser.add_argument(
        "--fail-on",
        choices=["warning", "error", "none"],
        help="Minimum severity that returns a non-zero exit code.",
    )
    return parser


def _resolve_presets_file(project: Path) -> Path:
    if project.name == "export_presets.cfg":
        return project
    return project / "export_presets.cfg"


def _load_config(project: Path, explicit_config: Path | None) -> dict[str, Any]:
    config_path = explicit_config
    if config_path is None:
        root = project.parent if project.name == "export_presets.cfg" else project
        config_path = root / DEFAULT_CONFIG
    if not config_path.exists():
        if explicit_config is not None:
            raise FileNotFoundError(
                f"config file not found: {config_path}. Omit --config to use defaults, "
                f"or create {DEFAULT_CONFIG} in the project folder."
            )
        return {}
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        return {}
    return data


def _configured_list(cli_values: list[str] | None, config: dict[str, Any], key: str) -> list[str]:
    values: list[str] = []
    value = config.get(key, [])
    if isinstance(value, list):
        values.extend(str(item) for item in value)
    elif isinstance(value, str):
        values.append(value)
    if cli_values:
        values.extend(cli_values)
    return values


def _filter_presets(presets: list[ExportPreset], platform: object) -> list[ExportPreset]:
    if not platform:
        return presets
    platform_text = str(platform).lower()
    return [preset for preset in presets if preset.platform.lower() == platform_text]


def _render(output_format: str, presets: list[ExportPreset], findings: list[Finding]) -> str:
    if output_format == "json":
        return render_json_report(presets, findings)
    if output_format == "sarif":
        return render_sarif_report(findings)
    return render_text_report(presets, findings)


def _validate_choice(parser: argparse.ArgumentParser, name: str, value: str, choices: set[str]) -> None:
    if value not in choices:
        parser.error(f"invalid {name} value {value!r}; choose one of {sorted(choices)}")


def _exit_code(findings: list[Finding], fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {finding.severity for finding in findings}
    if fail_on == "error":
        return 1 if "error" in severities else 0
    return 1 if ("error" in severities or "warning" in severities) else 0


def _findings_from_report(report: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for item in report.get("findings", []):
        if not isinstance(item, dict):
            continue
        findings.append(
            Finding(
                rule_id=str(item.get("rule_id", "")),
                severity=str(item.get("severity", "")),
                preset_index=item.get("preset_index") if isinstance(item.get("preset_index"), int) else None,
                preset_name=str(item.get("preset_name", "")),
                message=str(item.get("message", "")),
                option=str(item.get("option")) if item.get("option") is not None else None,
            )
        )
    return findings


def _normalize_legacy_argv(argv: list[str] | None) -> list[str] | None:
    if argv is None:
        argv = sys.argv[1:]
        if not argv or argv[0] in {"check", "matrix", "leaks", "diff", "inspect-folder", "inspect-files", "pck"} or argv[0] in {"--version", "-h", "--help"}:
            return None
        return _insert_default_command(argv)
    if not argv or argv[0] in {"check", "matrix", "leaks", "diff", "inspect-folder", "inspect-files", "pck"} or argv[0] in {"--version", "-h", "--help"}:
        return argv
    return _insert_default_command(argv)


def _insert_default_command(argv: list[str]) -> list[str]:
    options_with_values = {
        "--config",
        "--platform",
        "--required-android-abi",
        "--allow-secret-pattern",
        "--expected-platform",
        "--baseline",
        "--format",
        "--output",
        "--fail-on",
    }
    skip_next = False
    for index, item in enumerate(argv):
        if skip_next:
            skip_next = False
            continue
        if item in {"check", "matrix", "leaks", "diff", "inspect-folder", "inspect-files", "pck"}:
            return argv
        if item in options_with_values:
            skip_next = True
            continue
        if item.startswith("-"):
            continue
        return [*argv[:index], "check", *argv[index:]]
    return argv


if __name__ == "__main__":
    sys.exit(main())
