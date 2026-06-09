from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .audit import audit_mobile_ui
from .loader import load_metadata
from .reporting import render_report


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        viewports, screens, thresholds = load_metadata(Path(args.metadata))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

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
    parser.add_argument("--version", action="version", version="godot-mobile-ui-doctor 0.1.0")
    parser.add_argument("metadata", help="JSON file containing exported UI viewport and node metadata.")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")
    return parser


def _emit(rendered: str, output: str | None) -> None:
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


def _exit_code(report: dict[str, object], fail_on: str) -> int:
    summary = report["summary"]
    if fail_on == "none":
        return 0
    if fail_on == "warning":
        return 1 if int(summary["errors"]) + int(summary["warnings"]) > 0 else 0
    return 1 if int(summary["errors"]) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
