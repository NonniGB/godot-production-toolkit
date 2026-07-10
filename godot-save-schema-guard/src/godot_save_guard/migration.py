from __future__ import annotations

from dataclasses import dataclass
import json
import shlex
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


def build_migration_command(template: str, input_path: Path, output_path: Path) -> list[str]:
    """Build an argv without allowing fixture paths or templates through a shell."""
    parts = shlex.split(template, posix=True)
    if not parts:
        raise ValueError("migration command must name an executable")
    return [part.replace("{input}", str(input_path)).replace("{output}", str(output_path)) for part in parts]


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
    relative_path: Path | None = None,
) -> list[tuple[MigrationStep, Path, Path, list[str]]]:
    commands: list[tuple[MigrationStep, Path, Path, list[str]]] = []
    current_input = input_path
    relative = relative_path or Path(input_path.name)
    for step in steps:
        output_path = output_dir / relative.parent / f"{relative.stem}.v{step.to_version}{relative.suffix}"
        command = build_migration_command(step.command, current_input, output_path)
        commands.append((step, current_input, output_path, command))
        current_input = output_path
    return commands


def compare_migrated_fixture(original_path: Path, migrated_path: Path) -> Finding:
    try:
        original = json.loads(original_path.read_text(encoding="utf-8"))
        migrated = json.loads(migrated_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return Finding(
            "migration_compare_unavailable",
            "warning",
            "$",
            f"Could not compare original and migrated fixture: {exc}.",
        )

    original_values = _flatten_json(original)
    migrated_values = _flatten_json(migrated)
    original_paths = set(original_values)
    migrated_paths = set(migrated_values)
    added = sorted(migrated_paths - original_paths)
    removed = sorted(original_paths - migrated_paths)
    changed = sorted(
        path
        for path in original_paths & migrated_paths
        if original_values[path] != migrated_values[path]
    )
    version_note = _version_note(original, migrated)
    samples = (
        _sample_paths("added", added)
        + _sample_paths("removed", removed)
        + _sample_paths("changed", changed)
    )
    sample_note = f" Examples: {'; '.join(samples)}." if samples else ""
    return Finding(
        "migration_compare_summary",
        "info",
        "$",
        (
            f"Compared original save to {migrated_path.name}: "
            f"added {len(added)}, removed {len(removed)}, changed {len(changed)} path(s)"
            f"{version_note}.{sample_note}"
        ),
    )


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


def _flatten_json(value: object, prefix: str = "$") -> dict[str, object]:
    if isinstance(value, dict):
        rows: dict[str, object] = {}
        if not value:
            rows[prefix] = {}
        for key, child in value.items():
            rows.update(_flatten_json(child, f"{prefix}.{key}"))
        return rows
    if isinstance(value, list):
        rows = {}
        if not value:
            rows[prefix] = []
        for index, child in enumerate(value):
            rows.update(_flatten_json(child, f"{prefix}[{index}]"))
        return rows
    return {prefix: value}


def _version_note(original: object, migrated: object) -> str:
    if not isinstance(original, dict) or not isinstance(migrated, dict):
        return ""
    if "version" not in original and "version" not in migrated:
        return ""
    original_version = original.get("version", "missing")
    migrated_version = migrated.get("version", "missing")
    return f"; version {original_version} -> {migrated_version}"


def _sample_paths(label: str, paths: list[str], limit: int = 3) -> list[str]:
    if not paths:
        return []
    shown = ", ".join(paths[:limit])
    suffix = "" if len(paths) <= limit else ", ..."
    return [f"{label}: {shown}{suffix}"]


def run_migration_command(
    command: list[str], *, capture_output: bool = False, timeout: int = 120
) -> Finding | None:
    try:
        completed = subprocess.run(
            command,
            shell=False,
            check=False,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output_note = _exception_output_note(exc) if capture_output else ""
        return Finding(
            "migration_command_timed_out",
            "error",
            "$",
            f"Migration command exceeded the {timeout}-second timeout.{output_note}",
        )
    except OSError as exc:
        return Finding(
            "migration_command_unavailable",
            "error",
            "$",
            f"Migration command could not be started: {exc}.",
        )
    if completed.returncode != 0:
        output_note = _command_output_note(completed) if capture_output else ""
        return Finding(
            "migration_command_failed",
            "error",
            "$",
            f"Migration command failed with exit code {completed.returncode}.{output_note}",
        )
    return None


def _exception_output_note(exc: subprocess.TimeoutExpired) -> str:
    class Output:
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr

    return _command_output_note(Output())


def _command_output_note(completed: subprocess.CompletedProcess[str]) -> str:
    notes = []
    stdout = _compact_output(completed.stdout)
    stderr = _compact_output(completed.stderr)
    if stdout:
        notes.append(f"stdout: {stdout}")
    if stderr:
        notes.append(f"stderr: {stderr}")
    if not notes:
        return ""
    return " " + " ".join(f"{note}." for note in notes)


def _compact_output(value: str | None, limit: int = 300) -> str:
    if not value:
        return ""
    compacted = " ".join(value.strip().split())
    if len(compacted) <= limit:
        return compacted
    return compacted[: limit - 3].rstrip() + "..."
