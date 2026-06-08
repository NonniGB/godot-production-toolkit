from __future__ import annotations

from pathlib import Path
from typing import Any
import tomllib


DEFAULT_CONFIG_NAME = ".godot-asset-doctor.toml"


def load_config(project_root: Path, explicit_path: str | None = None) -> dict[str, Any]:
    config_path = Path(explicit_path) if explicit_path else project_root / DEFAULT_CONFIG_NAME
    if not config_path.exists():
        return {}

    with config_path.open("rb") as handle:
        data = tomllib.load(handle)

    if not isinstance(data, dict):
        return {}
    return data

