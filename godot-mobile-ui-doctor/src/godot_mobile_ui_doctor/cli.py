from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .audit import audit_mobile_ui, build_readiness_matrix
from .loader import load_metadata
from .overlays import OverlayOptions, render_overlays
from .reporting import render_report
from .visual_smoke import load_visual_smoke_viewports, merge_viewports


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "matrix":
        return _matrix(argv[1:])
    if argv and argv[0] == "overlays":
        return _overlays(argv[1:])
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
    parser.add_argument("--version", action="version", version="godot-mobile-ui-doctor 0.1.3")
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
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", help="Write the overlay summary to this file instead of stdout.")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")
    args = parser.parse_args(argv)

    viewports, screens, thresholds = _load_inputs(args, parser)
    report = render_overlays(
        viewports,
        screens,
        thresholds,
        OverlayOptions(output_dir=Path(args.output_dir), scale=args.scale),
    )
    _emit(_render_overlay_summary(report, args.format), args.output)
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
            f"Files: {summary['files']}"
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
