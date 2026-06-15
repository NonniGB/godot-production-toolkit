from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tomllib

from godot_asset_doctor.config import load_config
from godot_asset_doctor.manifest import (
    check_sprite_manifest,
    manifest_exit_code,
    render_contact_sheet,
    render_manifest_report,
    render_overlay_images,
)
from godot_asset_doctor.models import RuleSettings
from godot_asset_doctor.reporting import report_to_json, report_to_sarif, report_to_text
from godot_asset_doctor.scanner import scan_project


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:2] == ["manifest", "check"]:
        return _manifest_check(argv[2:])
    if argv[:2] == ["manifest", "contact-sheet"]:
        return _manifest_contact_sheet(argv[2:])
    if argv[:2] == ["manifest", "overlays"]:
        return _manifest_overlays(argv[2:])
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
        large_audio_bytes=_configured_mib(args.large_audio_mb, config, "large_audio_mb", 8),
        max_audio_duration_seconds=_configured_float(
            args.max_audio_duration_seconds,
            config,
            "max_audio_duration_seconds",
            120.0,
        ),
    )

    _validate_choice(parser, "profile", profile, {"default", "pixel-2d", "android-mobile", "audio-mobile"})
    _validate_choice(parser, "format", output_format, {"text", "json", "sarif"})
    _validate_choice(parser, "fail_on", fail_on, {"none", "warning", "error"})
    _validate_positive(parser, "max-texture-dimension", rule_settings.max_texture_dimension)
    _validate_positive(parser, "large-texture-mb", rule_settings.large_texture_bytes)
    _validate_positive(parser, "max-palette-colors", rule_settings.max_palette_colors)
    _validate_positive(parser, "large-audio-mb", rule_settings.large_audio_bytes)
    _validate_float_positive(parser, "max-audio-duration-seconds", rule_settings.max_audio_duration_seconds)

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
        description="Scan Godot image/audio assets and .import metadata for release risks.",
    )
    parser.add_argument("--version", action="version", version="godot-asset-doctor 0.1.10")
    parser.add_argument("path", nargs="?", default=".", help="Godot project directory to scan.")
    parser.add_argument(
        "--profile",
        choices=["default", "pixel-2d", "android-mobile", "audio-mobile"],
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
        "--large-audio-mb",
        type=float,
        default=None,
        help="Source audio MiB threshold before a mobile audio-size warning is reported.",
    )
    parser.add_argument(
        "--max-audio-duration-seconds",
        type=float,
        default=None,
        help="WAV duration threshold before a long-audio warning is reported.",
    )
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Accepted for compatibility; suggestions are included in all current reports.",
    )
    return parser


def _manifest_check(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="godot-asset-doctor manifest check",
        description="Validate a sprite manifest against PNG dimensions and anchor bounds.",
    )
    parser.add_argument("manifest", help="Sprite manifest JSON file.")
    parser.add_argument("--project", default=".", help="Project root used to resolve manifest paths.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")
    args = parser.parse_args(argv)

    try:
        report = check_sprite_manifest(Path(args.project), Path(args.manifest))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    rendered = render_manifest_report(report, args.format)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return manifest_exit_code(report, args.fail_on)


def _manifest_contact_sheet(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="godot-asset-doctor manifest contact-sheet",
        description="Render a PNG contact sheet from a sprite manifest, including anchor markers.",
    )
    parser.add_argument("manifest", help="Sprite manifest JSON file.")
    parser.add_argument("--project", default=".", help="Project root used to resolve manifest paths.")
    parser.add_argument("--output", required=True, help="PNG file to write.")
    parser.add_argument("--thumb-size", type=int, default=96, help="Maximum thumbnail size in pixels.")
    parser.add_argument("--columns", type=int, default=4, help="Number of sprite columns in the sheet.")
    parser.add_argument("--show-anchor-labels", action="store_true", help="Draw anchor names next to marker dots.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Summary output format.")
    args = parser.parse_args(argv)

    try:
        report = render_contact_sheet(
            Path(args.project),
            Path(args.manifest),
            Path(args.output),
            thumb_size=args.thumb_size,
            columns=args.columns,
            show_anchor_labels=args.show_anchor_labels,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    if args.format == "json":
        print(_render_json(report))
    else:
        summary = report["summary"]
        print("Godot Asset Sprite Contact Sheet")
        print(f"Manifest: {summary['manifest']}")
        print(f"Output: {summary['output']}")
        print(
            f"Sprites rendered: {summary['sprites_rendered']} / {summary['sprites']} | "
            f"Anchors: {summary['anchors_rendered']} | Warnings: {summary['warnings']}"
        )
    return 0


def _manifest_overlays(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="godot-asset-doctor manifest overlays",
        description="Render one PNG overlay per sprite, including anchor markers.",
    )
    parser.add_argument("manifest", help="Sprite manifest JSON file.")
    parser.add_argument("--project", default=".", help="Project root used to resolve manifest paths.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated PNG overlays.")
    parser.add_argument("--scale", type=int, default=4, help="Nearest-neighbor scale factor for small pixel sprites.")
    parser.add_argument("--show-anchor-labels", action="store_true", help="Draw anchor names next to marker dots.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Summary output format.")
    args = parser.parse_args(argv)

    try:
        report = render_overlay_images(
            Path(args.project),
            Path(args.manifest),
            Path(args.output_dir),
            scale=args.scale,
            show_anchor_labels=args.show_anchor_labels,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    if args.format == "json":
        print(_render_json(report))
    else:
        summary = report["summary"]
        print("Godot Asset Sprite Overlays")
        print(f"Manifest: {summary['manifest']}")
        print(f"Output directory: {summary['output_dir']}")
        print(
            f"Sprites rendered: {summary['sprites_rendered']} / {summary['sprites']} | "
            f"Anchors: {summary['anchors_rendered']} | Warnings: {summary['warnings']}"
        )
    return 0


def _render_json(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


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


def _configured_float(cli_value: float | None, config: dict[str, object], key: str, default: float) -> float:
    if cli_value is not None:
        return cli_value
    value = config.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _validate_choice(parser: argparse.ArgumentParser, name: str, value: str | None, choices: set[str]) -> None:
    if value not in choices:
        parser.error(f"invalid {name} value {value!r}; choose one of {sorted(choices)}")


def _validate_positive(parser: argparse.ArgumentParser, name: str, value: int) -> None:
    if value <= 0:
        parser.error(f"--{name} must be greater than zero")


def _validate_float_positive(parser: argparse.ArgumentParser, name: str, value: float) -> None:
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
