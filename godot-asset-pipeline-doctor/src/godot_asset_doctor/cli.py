from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib

from godot_asset_doctor.config import load_config
from godot_asset_doctor.models import RuleSettings
from godot_asset_doctor.reporting import report_to_json, report_to_sarif, report_to_text
from godot_asset_doctor.scanner import scan_project


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project_root = Path(args.path)
    try:
        config = load_config(project_root, args.config)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        parser.error(f"could not read config: {exc}")

    profile = _configured_value(args.profile, config, "profile", "default")
    output_format = _configured_value(args.format, config, "format", "text")
    fail_on = _configured_value(args.fail_on, config, "fail_on", "error")
    output = _configured_value(args.output, config, "output", None)
    exclude_globs = _configured_list(args.exclude, config, "exclude")
    rule_settings = RuleSettings(
        max_texture_dimension=_configured_int(args.max_texture_dimension, config, "max_texture_dimension", 4096),
        large_texture_bytes=_configured_mib(args.large_texture_mb, config, "large_texture_mb", 16),
        max_palette_colors=_configured_int(args.max_palette_colors, config, "max_palette_colors", 256),
    )

    _validate_choice(parser, "profile", profile, {"default", "pixel-2d", "android-mobile"})
    _validate_choice(parser, "format", output_format, {"text", "json", "sarif"})
    _validate_choice(parser, "fail_on", fail_on, {"none", "warning", "error"})
    _validate_positive(parser, "max-texture-dimension", rule_settings.max_texture_dimension)
    _validate_positive(parser, "large-texture-mb", rule_settings.large_texture_bytes)
    _validate_positive(parser, "max-palette-colors", rule_settings.max_palette_colors)

    report = scan_project(project_root, profile=profile, exclude_globs=exclude_globs, rule_settings=rule_settings)
    if output_format == "json":
        rendered = report_to_json(report)
    elif output_format == "sarif":
        rendered = report_to_sarif(report)
    else:
        rendered = report_to_text(report)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return _exit_code(report.summary(), fail_on)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-asset-doctor",
        description="Scan Godot PNG assets and .import metadata for pixel-art and mobile release risks.",
    )
    parser.add_argument("--version", action="version", version="godot-asset-doctor 0.1.4")
    parser.add_argument("path", nargs="?", default=".", help="Godot project directory to scan.")
    parser.add_argument(
        "--profile",
        choices=["default", "pixel-2d", "android-mobile"],
        default=None,
        help="Rule profile to apply.",
    )
    parser.add_argument("--format", choices=["text", "json", "sarif"], default=None, help="Report output format.")
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument(
        "--fail-on",
        choices=["none", "warning", "error"],
        default=None,
        help="Smallest severity that should return exit code 1.",
    )
    parser.add_argument(
        "--config",
        help="Optional TOML config path. Defaults to .godot-asset-doctor.toml in the scanned project.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        help="Exclude a project-relative glob such as 'addons/vendor/**'. Can be repeated.",
    )
    parser.add_argument(
        "--max-texture-dimension",
        type=int,
        default=None,
        help="Maximum allowed PNG width or height before a dimension error is reported.",
    )
    parser.add_argument(
        "--large-texture-mb",
        type=float,
        default=None,
        help="Estimated RGBA MiB threshold before a mobile texture memory warning is reported.",
    )
    parser.add_argument(
        "--max-palette-colors",
        type=int,
        default=None,
        help="Maximum unique RGBA color count before a pixel-art palette warning is reported.",
    )
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Accepted for compatibility; suggestions are included in all current reports.",
    )
    return parser


def _configured_value(cli_value: str | None, config: dict[str, object], key: str, default: str | None) -> str | None:
    if cli_value is not None:
        return cli_value
    value = config.get(key, default)
    return str(value) if value is not None else None


def _configured_list(cli_values: list[str] | None, config: dict[str, object], key: str) -> list[str]:
    values: list[str] = []
    config_value = config.get(key, [])
    if isinstance(config_value, list):
        values.extend(str(item) for item in config_value)
    elif isinstance(config_value, str):
        values.append(config_value)
    if cli_values:
        values.extend(cli_values)
    return values


def _configured_int(cli_value: int | None, config: dict[str, object], key: str, default: int) -> int:
    if cli_value is not None:
        return cli_value
    value = config.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _configured_mib(cli_value: float | None, config: dict[str, object], key: str, default: float) -> int:
    if cli_value is not None:
        value = cli_value
    else:
        value = config.get(key, default)
    try:
        mib = float(value)
    except (TypeError, ValueError):
        mib = default
    return int(mib * 1024 * 1024)


def _validate_choice(parser: argparse.ArgumentParser, name: str, value: str | None, choices: set[str]) -> None:
    if value not in choices:
        parser.error(f"invalid {name} value {value!r}; choose one of {sorted(choices)}")


def _validate_positive(parser: argparse.ArgumentParser, name: str, value: int) -> None:
    if value <= 0:
        parser.error(f"--{name} must be greater than zero")


def _exit_code(summary: dict[str, int | str], fail_on: str) -> int:
    if fail_on == "none":
        return 0
    if fail_on == "warning" and int(summary["warning_count"]) + int(summary["error_count"]) > 0:
        return 1
    if fail_on == "error" and int(summary["error_count"]) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
