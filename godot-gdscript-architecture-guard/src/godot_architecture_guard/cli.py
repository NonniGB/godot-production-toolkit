from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import load_policy
from .reporting import render_report
from .scanner import audit_project, render_mermaid

VERSION_LABEL = "godot-architecture-guard 0.1.5"


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project)
    try:
        config_path = _resolve_config(project, Path(args.config))
        modules, autoloads = load_policy(config_path)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    report = audit_project(project, modules, autoloads, config_path)
    rendered = render_mermaid(report) if args.format == "mermaid" else render_report(report, args.format)
    _emit(rendered, args.output)
    return _exit_code(report, args.fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-architecture-guard",
        description="Check GDScript module boundaries and autoload access policy.",
    )
    parser.add_argument("--version", action="version", version=VERSION_LABEL)
    parser.add_argument("project", help="Godot project directory.")
    parser.add_argument("--config", required=True, help="Architecture policy TOML file.")
    parser.add_argument("--format", choices=["text", "json", "markdown", "sarif", "mermaid"], default="text")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    parser.add_argument("--fail-on", choices=["none", "warning", "error"], default="error")
    return parser


def _resolve_config(project: Path, config: Path) -> Path:
    if config.is_absolute() or config.exists():
        return config
    return project / config


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
