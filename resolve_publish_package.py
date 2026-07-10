from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib

from verify_release_alignment import PUBLISHED_PACKAGES


def resolve_publish_package(root: Path, ref_name: str, manual_package: str = "") -> tuple[str, str]:
    package = manual_package.strip()
    if package:
        if package not in PUBLISHED_PACKAGES:
            raise ValueError(f"Unknown package {package!r}.")
    else:
        matches = [candidate for candidate in PUBLISHED_PACKAGES if ref_name.startswith(f"{candidate}-v")]
        if len(matches) != 1:
            raise ValueError(f"Tag {ref_name!r} does not identify exactly one published package.")
        package = matches[0]

    data = tomllib.loads((root / package / "pyproject.toml").read_text(encoding="utf-8"))
    version = str(data["project"]["version"])
    if not manual_package and ref_name != f"{package}-v{version}":
        raise ValueError(
            f"Tag {ref_name!r} does not match {package} version {version}; expected {package}-v{version}."
        )
    return package, version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve and validate the package selected for PyPI publishing.")
    parser.add_argument("--ref-name", default="")
    parser.add_argument("--manual-package", default="")
    args = parser.parse_args(argv)
    try:
        package, version = resolve_publish_package(
            Path(__file__).resolve().parent, args.ref_name, args.manual_package
        )
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(exc, file=sys.stderr)
        return 2
    print(f"{package}|{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
