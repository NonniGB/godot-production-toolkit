from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .dashboard import build_dashboard, render_html, render_json

VERSION_LABEL = "godot-release-dashboard 0.1.8"


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
    rendered = render_json(dashboard) if args.format == "json" else render_html(dashboard)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered + "\n", encoding="utf-8")
    return 0


def entrypoint() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    sys.exit(main())
