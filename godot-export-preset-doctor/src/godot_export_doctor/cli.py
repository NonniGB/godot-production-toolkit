from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Any

from .models import ExportPreset, Finding
from .preset_parser import parse_export_presets
from .reporting import render_json_report, render_sarif_report, render_text_report
from .rules import evaluate_presets, missing_export_presets_finding

DEFAULT_CONFIG = ".godot-export-doctor.toml"


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project)
    config = _load_config(project, Path(args.config) if args.config else None)

    output_format = args.format or str(config.get("format", "text"))
    fail_on = args.fail_on or str(config.get("fail_on", "warning"))
    platform = args.platform or config.get("platform")
    required_android_abis = config.get("required_android_abis", [])

    presets_file = _resolve_presets_file(project)
    if presets_file.exists():
        presets = parse_export_presets(presets_file.read_text(encoding="utf-8"))
        report_presets = _filter_presets(presets, platform)
        findings = evaluate_presets(
            presets,
            platform=str(platform) if platform else None,
            required_android_abis=[str(abi) for abi in required_android_abis],
        )
    else:
        report_presets = []
        findings = [missing_export_presets_finding()]

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
    parser.add_argument("--version", action="version", version="godot-export-doctor 0.1.0")
    parser.add_argument("project", help="Godot project directory or export_presets.cfg path.")
    parser.add_argument("--config", help=f"TOML config path. Defaults to {DEFAULT_CONFIG}.")
    parser.add_argument("--platform", help="Only evaluate presets for a platform, such as Android.")
    parser.add_argument("--format", choices=["text", "json", "sarif"], help="Report format.")
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
        return {}
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        return {}
    return data


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


def _exit_code(findings: list[Finding], fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {finding.severity for finding in findings}
    if fail_on == "error":
        return 1 if "error" in severities else 0
    return 1 if ("error" in severities or "warning" in severities) else 0


if __name__ == "__main__":
    sys.exit(main())
