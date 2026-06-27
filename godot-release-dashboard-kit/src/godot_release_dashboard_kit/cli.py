from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .dashboard import build_dashboard, render_html, render_json

VERSION_LABEL = "godot-release-dashboard 0.1.13"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a static dashboard from Godot toolkit reports.")
    parser.add_argument("--version", action="version", version=VERSION_LABEL)
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser("build", help="Build a dashboard from a reports directory.")
    build_parser.add_argument("reports_dir")
    build_parser.add_argument("--title", default="Godot Release Dashboard")
    build_parser.add_argument("--description", default="")
    build_parser.add_argument("--project", default="")
    build_parser.add_argument("--previous-reports-dir", "--baseline", dest="previous_reports_dir", default="")
    build_parser.add_argument("--format", choices=["html", "json"], default="html")
    build_parser.add_argument("--output", default="release-dashboard.html")
    build_parser.add_argument(
        "--require-reports",
        action="store_true",
        help="Fail when the reports directory has no supported report or image files.",
    )

    args = parser.parse_args(argv)
    if args.command != "build":
        parser.print_help()
        return 2
    output = Path(args.output)
    previous_reports_dir = Path(args.previous_reports_dir) if args.previous_reports_dir else None
    dashboard = build_dashboard(
        Path(args.reports_dir),
        args.title,
        output.parent,
        baseline_dir=previous_reports_dir,
        description=args.description or None,
        project=args.project or None,
    )
    if _is_empty_dashboard(dashboard):
        print(
            "No supported reports or images found in "
            f"{Path(args.reports_dir)}. Expected .json, .md, .png, .jpg, .jpeg, .svg, or .webp files. "
            "Check the reports directory path or rerun with generated toolkit artifacts. "
            "Use --require-reports to make this condition fail in CI.",
            file=sys.stderr,
        )
        if args.require_reports:
            print(
                "Example: godot-release-dashboard build reports\\release-evidence "
                "--require-reports --output reports\\release-dashboard\\index.html",
                file=sys.stderr,
            )
            return 1
    rendered = render_json(dashboard) if args.format == "json" else render_html(dashboard)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered + "\n", encoding="utf-8")
    return 0


def _is_empty_dashboard(dashboard: dict[str, object]) -> bool:
    summary = dashboard.get("summary", {})
    if not isinstance(summary, dict):
        return False
    return int(summary.get("reports", 0)) == 0 and int(summary.get("images", 0)) == 0


def entrypoint() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    sys.exit(main())
