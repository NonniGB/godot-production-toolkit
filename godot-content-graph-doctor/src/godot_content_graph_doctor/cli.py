from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import load_config
from .presets import BUILTIN_PRESETS, load_presets, merge_specs, render_preset_list
from .reporting import render_report
from .scanner import render_mermaid, validate_content_graph


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project)
    try:
        if args.list_presets:
            _emit(render_preset_list(), args.output)
            return 0
        if not args.config and not args.preset:
            parser.error("provide --config, --preset, or --list-presets")
        preset_specs = load_presets(args.preset or [])
        config_specs = load_config(_resolve_config(project, Path(args.config))) if args.config else ()
        specs = merge_specs(preset_specs, config_specs)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    if args.format == "mermaid":
        rendered = render_mermaid(specs)
        _emit(rendered, args.output)
        return 0

    report = validate_content_graph(project, specs)
    rendered = render_report(report, args.format)
    _emit(rendered, args.output)
    return _exit_code(report, args.fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-content-graph",
        description="Validate data-driven Godot content ids, references, and numeric outliers.",
    )
    parser.add_argument("--version", action="version", version="godot-content-graph 0.1.1")
    parser.add_argument("project", help="Godot project/content root.")
    parser.add_argument("--config", help="Content graph TOML config. Overrides preset collections with the same names.")
    parser.add_argument(
        "--preset",
        action="append",
        choices=sorted(BUILTIN_PRESETS),
        help="Use a built-in preset. Repeat to combine presets.",
    )
    parser.add_argument("--list-presets", action="store_true", help="List built-in presets and exit.")
    parser.add_argument("--format", choices=["text", "json", "markdown", "mermaid"], default="text")
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


def _resolve_config(project: Path, config: Path) -> Path:
    if config.is_absolute() or config.exists():
        return config
    return project / config


def _exit_code(report: dict[str, object], fail_on: str) -> int:
    summary = report["summary"]
    if fail_on == "none":
        return 0
    if fail_on == "warning":
        return 1 if int(summary["errors"]) + int(summary["warnings"]) > 0 else 0
    return 1 if int(summary["errors"]) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
