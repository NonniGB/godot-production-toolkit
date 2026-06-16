from __future__ import annotations

from dataclasses import dataclass
import subprocess
from pathlib import Path
from typing import Any
import tomllib

from .models import Finding


@dataclass(frozen=True)
class MigrationStep:
    from_version: str
    to_version: str
    command: str

    @property
    def label(self) -> str:
        return f"{self.from_version}->{self.to_version}"


def build_migration_command(template: str, input_path: Path, output_path: Path) -> str:
    return template.replace("{input}", str(input_path)).replace("{output}", str(output_path))


def load_migration_chain(path: Path) -> list[MigrationStep]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return parse_migration_chain(data)


def parse_migration_chain(data: dict[str, Any]) -> list[MigrationStep]:
    steps: list[MigrationStep] = []
    for item in data.get("steps", []):
        if not isinstance(item, dict):
            continue
        from_version = str(item.get("from", "")).strip()
        to_version = str(item.get("to", "")).strip()
        command = str(item.get("command", "")).strip()
        if from_version and to_version and command:
            steps.append(MigrationStep(from_version=from_version, to_version=to_version, command=command))
    return steps


def analyze_migration_graph(
    steps: list[MigrationStep],
    current_version: str,
    supported_versions: list[str],
) -> list[Finding]:
    current = str(current_version).strip()
    supported = [str(version).strip() for version in supported_versions if str(version).strip()]
    if not supported:
        supported = sorted({step.from_version for step in steps} | {current}, key=_version_sort_key)

    findings: list[Finding] = []
    if not steps:
        findings.append(
            Finding(
                "migration_chain_empty",
                "error",
                "$",
                "No valid migration steps were found.",
            )
        )

    graph: dict[str, set[str]] = {}
    for step in steps:
        graph.setdefault(step.from_version, set()).add(step.to_version)
        graph.setdefault(step.to_version, set())

    for version in supported:
        if version == current:
            continue
        if not _has_path(graph, version, current):
            findings.append(
                Finding(
                    "migration_path_missing",
                    "error",
                    "$",
                    f"Supported save version {version} has no migration path to current version {current}.",
                )
            )
    return findings


def build_chain_commands(
    steps: list[MigrationStep],
    input_path: Path,
    output_dir: Path,
) -> list[tuple[MigrationStep, Path, Path, str]]:
    commands: list[tuple[MigrationStep, Path, Path, str]] = []
    current_input = input_path
    for step in steps:
        output_path = output_dir / f"{input_path.stem}.v{step.to_version}{input_path.suffix}"
        command = build_migration_command(step.command, current_input, output_path)
        commands.append((step, current_input, output_path, command))
        current_input = output_path
    return commands


def _has_path(graph: dict[str, set[str]], start: str, target: str) -> bool:
    queue = [start]
    seen: set[str] = set()
    while queue:
        version = queue.pop(0)
        if version == target:
            return True
        if version in seen:
            continue
        seen.add(version)
        queue.extend(sorted(graph.get(version, set()) - seen, key=_version_sort_key))
    return False


def _version_sort_key(value: str) -> tuple[int, str]:
    return (0, f"{int(value):08d}") if value.isdigit() else (1, value)


def run_migration_command(command: str) -> Finding | None:
    completed = subprocess.run(command, shell=True, check=False)
    if completed.returncode != 0:
        return Finding(
            "migration_command_failed",
            "error",
            "$",
            f"Migration command failed with exit code {completed.returncode}.",
        )
    return None
