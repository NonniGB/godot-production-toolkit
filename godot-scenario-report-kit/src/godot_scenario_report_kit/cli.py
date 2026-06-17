from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .reports import compare, render, summarize
from .suite import bundle, coverage, flake_compare, manifest_check

VERSION_LABEL = "godot-scenario-report 0.1.7"


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "summarize":
        report = summarize(Path(args.path))
    elif args.command == "compare":
        report = compare(Path(args.baseline), Path(args.current), args.duration_ratio)
    elif args.command == "manifest" and args.manifest_command == "check":
        report = manifest_check(Path(args.manifest), Path(args.results) if args.results else None)
    elif args.command == "manifest" and args.manifest_command == "coverage":
        report = coverage(Path(args.manifest), Path(args.results) if args.results else None)
    elif args.command == "flake" and args.flake_command == "compare":
        report = flake_compare([Path(path) for path in args.paths])
    elif args.command == "bundle":
        report = bundle(
            Path(args.results),
            manifest_path=Path(args.manifest) if args.manifest else None,
            telemetry_path=Path(args.telemetry) if args.telemetry else None,
            visual_path=Path(args.visual) if args.visual else None,
            evidence_links=args.evidence,
        )
    else:
        parser.print_help()
        return 2
    _emit(render(report, args.format), args.output)
    return _exit_code(report, getattr(args, "fail_on", "error"))


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-scenario-report",
        description="Validate, summarize, and compare Godot scenario run evidence.",
    )
    parser.add_argument("--version", action="version", version=VERSION_LABEL)
    subparsers = parser.add_subparsers(dest="command")

    summarize_parser = subparsers.add_parser("summarize", help="Summarize a scenario result file or directory.")
    summarize_parser.add_argument("path")
    _add_output_args(summarize_parser)

    compare_parser = subparsers.add_parser("compare", help="Compare baseline and current scenario results.")
    compare_parser.add_argument("baseline")
    compare_parser.add_argument("current")
    compare_parser.add_argument("--duration-ratio", type=float, default=1.5)
    _add_output_args(compare_parser)

    manifest_parser = subparsers.add_parser("manifest", help="Validate scenario manifests and coverage policy.")
    manifest_subparsers = manifest_parser.add_subparsers(dest="manifest_command")
    manifest_check_parser = manifest_subparsers.add_parser("check", help="Check a scenario manifest against optional results.")
    manifest_check_parser.add_argument("manifest")
    manifest_check_parser.add_argument("--results")
    _add_output_args(manifest_check_parser)

    coverage_parser = manifest_subparsers.add_parser("coverage", help="Report scenario tag, flow, and platform coverage.")
    coverage_parser.add_argument("manifest")
    coverage_parser.add_argument("--results")
    _add_output_args(coverage_parser)

    flake_parser = subparsers.add_parser("flake", help="Compare repeated scenario runs for unstable status changes.")
    flake_subparsers = flake_parser.add_subparsers(dest="flake_command")
    flake_compare_parser = flake_subparsers.add_parser("compare", help="Compare two or more result folders.")
    flake_compare_parser.add_argument("paths", nargs="+")
    _add_output_args(flake_compare_parser)

    bundle_parser = subparsers.add_parser("bundle", help="Create a portable scenario evidence bundle manifest.")
    bundle_parser.add_argument("results")
    bundle_parser.add_argument("--manifest", help="Optional scenario manifest used for coverage context.")
    bundle_parser.add_argument("--telemetry", help="Optional runtime telemetry report or directory to link.")
    bundle_parser.add_argument("--visual", help="Optional visual smoke report or screenshot directory to link.")
    bundle_parser.add_argument(
        "--evidence",
        action="append",
        default=[],
        type=_evidence_arg,
        metavar="KIND=PATH",
        help="Additional evidence to link, such as log=reports/run.log or junit=reports/junit.xml.",
    )
    _add_output_args(bundle_parser)
    return parser


def _add_output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=["text", "json", "markdown", "html"], default="text")
    parser.add_argument("--output")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")


def _emit(rendered: str, output: str | None) -> None:
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


def _evidence_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("evidence links must use KIND=PATH.")
    kind, raw_path = value.split("=", 1)
    kind = kind.strip()
    raw_path = raw_path.strip()
    if not kind:
        raise argparse.ArgumentTypeError("evidence kind must not be empty.")
    if not raw_path:
        raise argparse.ArgumentTypeError("evidence path must not be empty.")
    return kind, Path(raw_path)


def _exit_code(report: dict[str, object], fail_on: str) -> int:
    summary = report["summary"]
    if fail_on == "none":
        return 0
    if fail_on == "warning":
        return 1 if int(summary["errors"]) + int(summary["warnings"]) > 0 else 0
    return 1 if int(summary["errors"]) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
