from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .audit import audit_mobile_ui, build_readiness_matrix
from .loader import load_metadata
from .overlays import OverlayOptions, render_overlays
from .readiness import build_combined_readiness, render_combined_readiness
from .reporting import render_report
from .visual_smoke import load_visual_smoke_viewports, merge_viewports

VERSION_LABEL = "godot-mobile-ui-doctor 0.1.8"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "matrix":
        return _matrix(argv[1:])
    if argv and argv[0] == "overlays":
        return _overlays(argv[1:])
    if argv and argv[0] == "readiness":
        return _readiness(argv[1:])
    parser = _build_parser()
    args = parser.parse_args(argv)

    viewports, screens, thresholds = _load_inputs(args, parser)

    report = audit_mobile_ui(viewports, screens, thresholds)
    _emit(render_report(report, args.format), args.output)
    return _exit_code(report, args.fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-mobile-ui-doctor",
        description="Check exported Godot mobile UI metadata for touch and layout risks.",
    )
    parser.add_argument("--version", action="version", version=VERSION_LABEL)
    parser.add_argument("metadata", help="JSON file containing exported UI viewport and node metadata.")
    parser.add_argument(
        "--visual-smoke-plan",
        help="Optional JSON output from `godot-visual-smoke plan --format json` used to supply viewport metadata.",
    )
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")
    return parser


def _matrix(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="godot-mobile-ui-doctor matrix",
        description="Build a screen-by-screen mobile UI readiness matrix.",
    )
    parser.add_argument("metadata", help="JSON file containing exported UI viewport and node metadata.")
    parser.add_argument(
        "--visual-smoke-plan",
        help="Optional JSON output from `godot-visual-smoke plan --format json` used to supply viewport metadata.",
    )
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="markdown")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")
    args = parser.parse_args(argv)

    viewports, screens, thresholds = _load_inputs(args, parser)

    report = build_readiness_matrix(viewports, screens, thresholds)
    _emit(render_report(report, args.format), args.output)
    return _exit_code(report, args.fail_on)


def _overlays(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="godot-mobile-ui-doctor overlays",
        description="Render PNG mobile UI review overlays from exported layout metadata.",
    )
    parser.add_argument("metadata", help="JSON file containing exported UI viewport and node metadata.")
    parser.add_argument(
        "--visual-smoke-plan",
        help="Optional JSON output from `godot-visual-smoke plan --format json` used to supply viewport metadata.",
    )
    parser.add_argument(
        "--output-dir",
        default="mobile-ui-overlays",
        help="Directory where PNG overlays are written. Defaults to mobile-ui-overlays.",
    )
    parser.add_argument(
        "--scale",
        type=_positive_float,
        default=0.5,
        help="Scale factor for output images. Defaults to 0.5.",
    )
    parser.add_argument(
        "--screenshot-dir",
        help="Optional directory of captured PNG screenshots to use as overlay backgrounds.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", help="Write the overlay summary to this file instead of stdout.")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")
    args = parser.parse_args(argv)

    viewports, screens, thresholds = _load_inputs(args, parser)
    report = render_overlays(
        viewports,
        screens,
        thresholds,
        OverlayOptions(
            output_dir=Path(args.output_dir),
            scale=args.scale,
            screenshot_dir=Path(args.screenshot_dir) if args.screenshot_dir else None,
        ),
    )
    _emit(_render_overlay_summary(report, args.format), args.output)
    return _exit_code(report, args.fail_on)


def _readiness(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="godot-mobile-ui-doctor readiness",
        description="Combine mobile UI metadata with related toolkit reports.",
    )
    parser.add_argument("metadata", help="JSON file containing exported UI viewport and node metadata.")
    parser.add_argument(
        "--visual-smoke-plan",
        help="Optional JSON output from `godot-visual-smoke plan --format json` used to supply viewport metadata.",
    )
    parser.add_argument("--input-report", help="JSON report from godot-input-audit.")
    parser.add_argument("--export-report", help="JSON report from godot-export-doctor.")
    parser.add_argument("--localization-report", help="JSON report from godot-l10n-guard.")
    parser.add_argument("--mobile-perf-report", help="JSON report from godot-mobile-perf-doctor.")
    parser.add_argument("--visual-smoke-report", help="JSON report or plan from godot-visual-smoke.")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="markdown")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")
    args = parser.parse_args(argv)

    viewports, screens, thresholds = _load_inputs(args, parser)
    linked = _linked_report_paths(args)
    report = build_combined_readiness(viewports, screens, thresholds, linked)
    _emit(render_combined_readiness(report, args.format), args.output)
    return _exit_code(report, args.fail_on)


def _emit(rendered: str, output: str | None) -> None:
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


def _load_inputs(args: argparse.Namespace, parser: argparse.ArgumentParser):
    try:
        visual_smoke_viewports = (
            load_visual_smoke_viewports(Path(args.visual_smoke_plan)) if args.visual_smoke_plan else {}
        )
        viewports, screens, thresholds = load_metadata(
            Path(args.metadata),
            require_viewports=not bool(visual_smoke_viewports),
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return merge_viewports(visual_smoke_viewports, viewports), screens, thresholds


def _linked_report_paths(args: argparse.Namespace) -> dict[str, Path]:
    pairs = {
        "input": args.input_report,
        "export": args.export_report,
        "localization": args.localization_report,
        "mobile_perf": args.mobile_perf_report,
        "visual_smoke": args.visual_smoke_report,
    }
    return {key: Path(value) for key, value in pairs.items() if value}


def _exit_code(report: dict[str, object], fail_on: str) -> int:
    summary = report["summary"]
    if fail_on == "none":
        return 0
    if fail_on == "warning":
        return 1 if int(summary["errors"]) + int(summary["warnings"]) > 0 else 0
    return 1 if int(summary["errors"]) > 0 else 0


def _positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--scale must be a number greater than zero.") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("--scale must be greater than zero.")
    return number


def _render_overlay_summary(report: dict[str, object], fmt: str) -> str:
    if fmt == "json":
        import json

        return json.dumps(report, indent=2, sort_keys=True)
    summary = report["summary"]
    lines = [
        "Godot Mobile UI Overlay Previews",
        (
            f"Screens: {summary['screens']} | Viewports: {summary['viewports']} | "
            f"Files: {summary['files']} | Screenshots: {summary['screenshots']}"
        ),
        f"Errors: {summary['errors']} | Warnings: {summary['warnings']}",
        "",
    ]
    for item in report["files"]:
        lines.append(
            f"- {item['screen']} / {item['viewport']}: {item['path']} "
            f"({item['width']}x{item['height']})"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
