from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import audit_catalogs
from .csv_parser import parse_csv_file
from .models import CsvTable, PoCatalog
from .po_parser import parse_po_file
from .pseudo import write_pseudo_csv
from .reporting import render_json_report, render_markdown_report, render_sarif_report, render_text_report
from .usage_scanner import scan_project_keys

Catalog = CsvTable | PoCatalog


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project)
    scan_scripts = args.scan_scripts or args.scan_all
    scan_scenes = args.scan_scenes or args.scan_all
    catalogs = _load_catalogs(parser, args)
    used_keys = (
        scan_project_keys(project, scan_scripts=scan_scripts, scan_scenes=scan_scenes)
        if scan_scripts or scan_scenes
        else None
    )
    findings = audit_catalogs(
        catalogs,
        required_languages=_parse_languages(args.require),
        source_language=args.source_lang,
        used_keys=used_keys,
        max_expansion=args.max_expansion,
        allowed_glyphs=_load_allowed_glyphs(parser, args),
    )

    rendered = _render(args.format, catalogs, findings)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.pseudo_output:
        write_pseudo_csv(
            catalogs,
            Path(args.pseudo_output),
            source_language=args.source_lang,
            pseudo_language=args.pseudo_locale,
            expansion=args.pseudo_expansion,
        )

    return _exit_code(findings, args.fail_on)


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-l10n-guard",
        description="Audit Godot CSV and PO localization files.",
    )
    parser.add_argument("--version", action="version", version="godot-l10n-guard 0.1.3")
    parser.add_argument("project", help="Godot project directory.")
    parser.add_argument("--translations", help="Directory containing CSV and PO translation files.")
    parser.add_argument("--csv", action="append", default=[], help="Godot CSV translation file.")
    parser.add_argument("--po", action="append", default=[], help="PO file or directory.")
    parser.add_argument("--require", default="", help="Comma-separated target languages required.")
    parser.add_argument("--source-lang", default="en", help="Source language column. Default: en.")
    parser.add_argument("--scan-scripts", action="store_true", help="Scan .gd files for tr(\"KEY\").")
    parser.add_argument("--scan-scenes", action="store_true", help="Scan .tscn/.scn text values for key-like strings.")
    parser.add_argument("--scan-all", action="store_true", help="Scan both scripts and scenes for translation keys.")
    parser.add_argument("--max-expansion", type=float, help="Warn when a target string exceeds this source-length ratio.")
    parser.add_argument("--allowed-glyphs", help="Characters expected to be available in the project's UI font.")
    parser.add_argument("--allowed-glyphs-file", help="Text file containing glyphs expected to be available in the UI font.")
    parser.add_argument("--pseudo-output", help="Write a pseudo-localized CSV preview catalog.")
    parser.add_argument("--pseudo-locale", default="qps-ploc", help="Locale column name for --pseudo-output.")
    parser.add_argument("--pseudo-expansion", type=float, default=0.3, help="Extra padding ratio for pseudo-localized strings.")
    parser.add_argument("--format", choices=["text", "json", "markdown", "sarif"], default="text")
    parser.add_argument("--output", help="Write report to a file instead of stdout.")
    parser.add_argument("--fail-on", choices=["warning", "error", "none"], default="warning")
    return parser


def _load_catalogs(parser: argparse.ArgumentParser, args: argparse.Namespace) -> list[Catalog]:
    catalogs: list[Catalog] = []
    paths: list[Path] = []
    for raw in args.csv:
        path = Path(raw)
        if not path.exists():
            parser.error(f"CSV catalog was not found: {path}")
        paths.append(path)
    if args.translations:
        root = Path(args.translations)
        if not root.exists():
            parser.error(f"translations directory was not found: {root}")
        paths.extend(sorted(root.glob("*.csv")))
        paths.extend(sorted(root.glob("*.po")))
    for raw in args.po:
        path = Path(raw)
        if not path.exists():
            parser.error(f"PO catalog was not found: {path}")
        if path.is_dir():
            paths.extend(sorted(path.glob("*.po")))
        else:
            paths.append(path)

    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved in seen or not path.exists():
            continue
        seen.add(resolved)
        if path.suffix.lower() == ".csv":
            catalogs.append(parse_csv_file(path))
        elif path.suffix.lower() == ".po":
            catalogs.append(parse_po_file(path))
    return catalogs


def _parse_languages(raw: str) -> set[str]:
    return {part.strip() for part in raw.split(",") if part.strip()}


def _load_allowed_glyphs(parser: argparse.ArgumentParser, args: argparse.Namespace) -> set[str] | None:
    if not args.allowed_glyphs and not args.allowed_glyphs_file:
        return None
    glyphs = set(args.allowed_glyphs or "")
    glyphs.update({" ", "\t", "\r", "\n"})
    if args.allowed_glyphs_file:
        glyph_path = Path(args.allowed_glyphs_file)
        if not glyph_path.exists():
            parser.error(f"allowed glyphs file was not found: {glyph_path}")
        glyphs.update(glyph_path.read_text(encoding="utf-8"))
    return glyphs


def _render(format_name: str, catalogs: list[Catalog], findings: object) -> str:
    if format_name == "json":
        return render_json_report(catalogs, findings)
    if format_name == "markdown":
        return render_markdown_report(catalogs, findings)
    if format_name == "sarif":
        return render_sarif_report(catalogs, findings)
    return render_text_report(catalogs, findings)


def _exit_code(findings: object, fail_on: str) -> int:
    if fail_on == "none":
        return 0
    severities = {finding.severity for finding in findings}
    if fail_on == "error":
        return 1 if "error" in severities else 0
    return 1 if ("error" in severities or "warning" in severities) else 0


if __name__ == "__main__":
    sys.exit(main())
