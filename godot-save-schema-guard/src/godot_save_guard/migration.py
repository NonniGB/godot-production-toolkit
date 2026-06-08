from __future__ import annotations

import subprocess
from pathlib import Path

from .models import Finding


def build_migration_command(template: str, input_path: Path, output_path: Path) -> str:
    return template.replace("{input}", str(input_path)).replace("{output}", str(output_path))


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
