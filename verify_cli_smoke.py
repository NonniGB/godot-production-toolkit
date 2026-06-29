from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tomllib

from verify_release_alignment import PACKAGE_VERSION_FILES, PUBLISHED_PACKAGES


SMOKE_ARGS = ("--help", "--version")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test published CLI entry points from the checkout.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable smoke results.")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent
    results = run_cli_smoke(root)
    failures = [result for result in results if result.error]

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "ok": not failures,
                    "checked": len(results),
                    "failures": [result.as_dict() for result in failures],
                },
                indent=2,
                sort_keys=True,
            )
        )
    elif failures:
        for failure in failures:
            print(failure.format_error())
    else:
        cli_count = len({result.cli_name for result in results})
        print(f"Smoke tested {cli_count} CLI entry points ({len(results)} invocations).")

    return 1 if failures else 0


def run_cli_smoke(root: Path) -> list["SmokeResult"]:
    env = _checkout_env(root)
    results: list[SmokeResult] = []
    for package in PUBLISHED_PACKAGES:
        target = _script_target(root / package / "pyproject.toml", PACKAGE_VERSION_FILES[package]["cli_name"])
        if target is None:
            results.append(
                SmokeResult(
                    package=package,
                    cli_name=PACKAGE_VERSION_FILES[package]["cli_name"],
                    argument="<entrypoint>",
                    returncode=1,
                    stdout="",
                    stderr="missing [project.scripts] entry",
                    error="missing console script entry",
                )
            )
            continue
        module, function = target
        for smoke_arg in SMOKE_ARGS:
            results.append(
                _run_entrypoint(package, PACKAGE_VERSION_FILES[package]["cli_name"], module, function, smoke_arg, env)
            )
    return results


def _checkout_env(root: Path) -> dict[str, str]:
    src_paths = [str(root / package / "src") for package in PUBLISHED_PACKAGES]
    existing = os.environ.get("PYTHONPATH")
    if existing:
        src_paths.append(existing)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(src_paths)
    return env


def _script_target(pyproject_path: Path, cli_name: str) -> tuple[str, str] | None:
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    raw_target = data.get("project", {}).get("scripts", {}).get(cli_name)
    if not isinstance(raw_target, str) or ":" not in raw_target:
        return None
    module, function = raw_target.split(":", 1)
    if not module or not function:
        return None
    return module, function


def _run_entrypoint(
    package: str,
    cli_name: str,
    module: str,
    function: str,
    argument: str,
    env: dict[str, str],
) -> "SmokeResult":
    command = [
        sys.executable,
        "-c",
        (
            "import importlib, sys; "
            "module = importlib.import_module(sys.argv[1]); "
            "function = getattr(module, sys.argv[2]); "
            "sys.argv = [sys.argv[3], *sys.argv[4:]]; "
            "raise SystemExit(function())"
        ),
        module,
        function,
        cli_name,
        argument,
    ]
    completed = subprocess.run(command, check=False, capture_output=True, env=env, text=True, timeout=15)
    output = f"{completed.stdout}\n{completed.stderr}".strip()
    error = None
    if completed.returncode != 0:
        error = f"expected exit 0, got {completed.returncode}"
    elif argument == "--version" and cli_name not in output:
        error = f"--version output did not contain {cli_name!r}"
    elif argument == "--help" and "usage:" not in output.lower():
        error = "--help output did not contain usage text"

    return SmokeResult(
        package=package,
        cli_name=cli_name,
        argument=argument,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        error=error,
    )


class SmokeResult:
    def __init__(
        self,
        *,
        package: str,
        cli_name: str,
        argument: str,
        returncode: int,
        stdout: str,
        stderr: str,
        error: str | None,
    ) -> None:
        self.package = package
        self.cli_name = cli_name
        self.argument = argument
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.error = error

    def as_dict(self) -> dict[str, object]:
        return {
            "package": self.package,
            "cli_name": self.cli_name,
            "argument": self.argument,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
        }

    def format_error(self) -> str:
        output = f"{self.stdout}\n{self.stderr}".strip()
        if len(output) > 800:
            output = f"{output[:800]}..."
        return f"{self.package} {self.cli_name} {self.argument}: {self.error}\n{output}"


if __name__ == "__main__":
    raise SystemExit(main())
