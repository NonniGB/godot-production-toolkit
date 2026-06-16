from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .doctor import check_manifest, diff_manifests, load_order, render

VERSION_LABEL = "godot-pack-mod-doctor 0.1.1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Godot pack, DLC, and mod manifests.")
    parser.add_argument("--version", action="version", version=VERSION_LABEL)
    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser("check", help="Check a pack manifest.")
    check_parser.add_argument("manifest")
    check_parser.add_argument("--base", help="Optional base game content manifest.")
    check_parser.add_argument("--allow-overrides", action="store_true")
    check_parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    check_parser.add_argument("--output")
    check_parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")

    diff_parser = subparsers.add_parser("diff", help="Compare two pack manifests.")
    diff_parser.add_argument("baseline")
    diff_parser.add_argument("current")
    diff_parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    diff_parser.add_argument("--output")
    diff_parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="none")

    load_order_parser = subparsers.add_parser("load-order", help="Check override conflicts across ordered packs.")
    load_order_parser.add_argument("manifests", nargs="+")
    load_order_parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    load_order_parser.add_argument("--output")
    load_order_parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="warning")

    args = parser.parse_args(argv)
    if args.command == "check":
        report = check_manifest(Path(args.manifest), Path(args.base) if args.base else None, args.allow_overrides)
    elif args.command == "diff":
        report = diff_manifests(Path(args.baseline), Path(args.current))
    elif args.command == "load-order":
        report = load_order([Path(path) for path in args.manifests])
    else:
        parser.print_help()
        return 2
    _emit(render(report, args.format), args.output)
    return _exit_code(report, args.fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


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
