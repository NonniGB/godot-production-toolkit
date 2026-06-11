from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from .asteroids import generate_asteroid_tiles
from .compare import compare_images
from .preview import build_contact_sheet
from .starfield import generate_starfield
from .strip_background import strip_background


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    _validate_args(parser, args)
    if args.command == "starfield":
        return _starfield(args)
    if args.command == "asteroid-hex":
        manifest = generate_asteroid_tiles(
            Path(args.output),
            material=args.material,
            count=args.count,
            size=args.size,
            seed=args.seed,
        )
        _emit_status(
            args,
            {
                "status": "ok",
                "command": "asteroid-hex",
                "outputs": {
                    "directory": str(Path(args.output)),
                    "manifest": str(Path(args.output) / "manifest.json"),
                },
                "manifest": manifest,
            },
        )
        return 0
    if args.command == "strip-background":
        return _strip_background(args)
    if args.command == "preview":
        return _preview(args)
    if args.command == "compare":
        return _compare(args)
    parser.print_help()
    return 2


def entrypoint() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pixel-space-assets", description="Deterministic pixel-space asset tools.")
    parser.add_argument("--version", action="version", version="pixel-space-assets 0.1.2")
    subparsers = parser.add_subparsers(dest="command")

    starfield = subparsers.add_parser("starfield")
    starfield.add_argument("--width", type=int, required=True)
    starfield.add_argument("--height", type=int, required=True)
    starfield.add_argument("--seed", type=int, required=True)
    starfield.add_argument("--stars", type=int, default=200)
    starfield.add_argument("--output", required=True)
    starfield.add_argument("--manifest")
    starfield.add_argument("--format", choices=["text", "json"], default="text")

    asteroid = subparsers.add_parser("asteroid-hex")
    asteroid.add_argument("--material", default="carbon", choices=["carbon", "ferric", "ice"])
    asteroid.add_argument("--count", type=int, default=16)
    asteroid.add_argument("--size", type=int, default=64)
    asteroid.add_argument("--seed", type=int, default=1)
    asteroid.add_argument("--output", required=True)
    asteroid.add_argument("--format", choices=["text", "json"], default="text")

    strip = subparsers.add_parser("strip-background")
    strip.add_argument("input")
    strip.add_argument("--output", required=True)
    strip.add_argument("--tolerance", type=int, default=0)
    strip.add_argument("--format", choices=["text", "json"], default="text")

    preview = subparsers.add_parser("preview")
    preview.add_argument("input")
    preview.add_argument("--output", required=True)
    preview.add_argument("--columns", type=int, default=4)
    preview.add_argument("--cell-size", type=int, default=64)
    preview.add_argument("--format", choices=["text", "json"], default="text")

    compare = subparsers.add_parser("compare")
    compare.add_argument("baseline")
    compare.add_argument("current")
    compare.add_argument("--diff-output", required=True)
    compare.add_argument("--tolerance", type=int, default=0)
    compare.add_argument("--fail-on-diff", action="store_true")
    compare.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    for field in ("width", "height", "stars", "count", "size", "columns", "cell_size"):
        value = getattr(args, field, None)
        if value is not None and value <= 0:
            parser.error(f"--{field.replace('_', '-')} must be greater than zero")
    if getattr(args, "tolerance", 0) < 0:
        parser.error("--tolerance must be zero or greater")


def _starfield(args: argparse.Namespace) -> int:
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    image = generate_starfield(width=args.width, height=args.height, seed=args.seed, stars=args.stars)
    image.save(output)
    if args.manifest:
        manifest = {
            "type": "starfield",
            "width": args.width,
            "height": args.height,
            "seed": args.seed,
            "stars": args.stars,
            "output": str(output),
        }
        manifest_path = Path(args.manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    _emit_status(
        args,
        {
            "status": "ok",
            "command": "starfield",
            "outputs": {
                "image": str(output),
                "manifest": str(Path(args.manifest)) if args.manifest else None,
            },
            "parameters": {
                "width": args.width,
                "height": args.height,
                "seed": args.seed,
                "stars": args.stars,
            },
        },
    )
    return 0


def _strip_background(args: argparse.Namespace) -> int:
    with Image.open(args.input) as image:
        stripped = strip_background(image, tolerance=args.tolerance)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    stripped.save(output)
    _emit_status(
        args,
        {
            "status": "ok",
            "command": "strip-background",
            "outputs": {"image": str(output)},
            "parameters": {"input": args.input, "tolerance": args.tolerance},
        },
    )
    return 0


def _preview(args: argparse.Namespace) -> int:
    root = Path(args.input)
    paths = sorted(root.glob("*.png")) if root.is_dir() else [root]
    sheet = build_contact_sheet(paths, columns=args.columns, cell_size=args.cell_size)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    _emit_status(
        args,
        {
            "status": "ok",
            "command": "preview",
            "outputs": {"image": str(output)},
            "parameters": {
                "input": args.input,
                "columns": args.columns,
                "cell_size": args.cell_size,
                "source_count": len(paths),
            },
        },
    )
    return 0


def _compare(args: argparse.Namespace) -> int:
    result = compare_images(
        Path(args.baseline),
        Path(args.current),
        Path(args.diff_output),
        tolerance=args.tolerance,
    )
    payload = {
        "status": "ok",
        "command": "compare",
        "outputs": {"diff": str(Path(args.diff_output))},
        "parameters": {
            "baseline": args.baseline,
            "current": args.current,
            "tolerance": args.tolerance,
        },
        "comparison": result.as_dict(),
    }
    _emit_status(args, payload)
    if getattr(args, "format", "text") == "text":
        print(
            "Pixel asset comparison: "
            f"{result.different_pixels}/{result.total_pixels} pixels changed "
            f"({result.percent_different:.2f}%). Diff: {args.diff_output}"
        )
    return 1 if args.fail_on_diff and result.different_pixels > 0 else 0


def _emit_status(args: argparse.Namespace, payload: dict[str, object]) -> None:
    if getattr(args, "format", "text") == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
