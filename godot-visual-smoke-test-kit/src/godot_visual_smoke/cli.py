from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .approve import approve_baseline
from .config import load_config
from .diff import compare_images
from .reporting import render_json_result, render_text_result, report_metadata
from .runner import build_godot_command


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "compare":
        return _compare(args)
    if args.command == "approve":
        return _approve(args)
    if args.command == "plan":
        return _plan(args)
    parser.print_help()
    return 2


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-visual-smoke",
        description="Compare and approve Godot visual smoke screenshots.",
    )
    parser.add_argument("--version", action="version", version="godot-visual-smoke 0.1.3")
    subparsers = parser.add_subparsers(dest="command")

    compare = subparsers.add_parser("compare", help="Compare baseline and current screenshots.")
    compare.add_argument("baseline")
    compare.add_argument("current")
    compare.add_argument("--diff", help="Optional diff image path.")
    compare.add_argument("--pixel-tolerance", type=int, default=0)
    compare.add_argument("--max-changed-percent", type=float, default=0.0)
    compare.add_argument("--format", choices=["text", "json"], default="text")
    compare.add_argument("--output")
    compare.add_argument("--fail-on", choices=["diff", "none"], default="diff")

    approve = subparsers.add_parser("approve", help="Copy current screenshot to baseline.")
    approve.add_argument("current")
    approve.add_argument("baseline")
    approve.add_argument("--format", choices=["text", "json"], default="text")
    approve.add_argument("--output", help="Write approval status to a file instead of stdout.")

    plan = subparsers.add_parser("plan", help="Print Godot capture commands from visual-smoke.toml.")
    plan.add_argument("config")
    plan.add_argument("--project", required=True)
    plan.add_argument("--viewport-manifest", help="Optional TOML file with reusable viewport definitions.")
    plan.add_argument("--godot", default="godot")
    plan.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def _compare(args: argparse.Namespace) -> int:
    result = compare_images(
        Path(args.baseline),
        Path(args.current),
        diff_path=Path(args.diff) if args.diff else None,
        pixel_tolerance=args.pixel_tolerance,
        max_changed_percent=args.max_changed_percent,
    )
    rendered = render_json_result(result) if args.format == "json" else render_text_result(result)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 1 if args.fail_on == "diff" and not result.passed else 0


def _approve(args: argparse.Namespace) -> int:
    current = Path(args.current)
    baseline = Path(args.baseline)
    approve_baseline(current, baseline)
    payload = {
        "metadata": report_metadata("visual_smoke_approval", ["text", "json"]),
        "status": "ok",
        "command": "approve",
        "current": str(current),
        "baseline": str(baseline),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) if args.format == "json" else f"Approved {current} -> {baseline}"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


def _plan(args: argparse.Namespace) -> int:
    viewport_manifest = Path(args.viewport_manifest) if args.viewport_manifest else None
    config = load_config(Path(args.config), viewport_manifest=viewport_manifest)
    planned_commands = []
    for scene in config.scenes:
        viewport = config.viewports[scene.viewport]
        output = Path(config.output_dir) / f"{scene.name}.png"
        command = build_godot_command(
            godot=Path(args.godot),
            project=Path(args.project),
            scene=scene.path,
            width=viewport.width,
            height=viewport.height,
            output=output,
        )
        planned_commands.append(
            {
                "name": scene.name,
                "scene": scene.path,
                "viewport": {
                    "name": viewport.name,
                    "width": viewport.width,
                    "height": viewport.height,
                    "safe_area": viewport.safe_area.to_dict(),
                },
                "output": str(output),
                "command": command,
                "shell": " ".join(command),
            }
        )
    if args.format == "json":
        print(
            json.dumps(
                {
                    "metadata": report_metadata("visual_smoke_capture_plan", ["text", "json"]),
                    "commands": planned_commands,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        for planned in planned_commands:
            print(planned["shell"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
