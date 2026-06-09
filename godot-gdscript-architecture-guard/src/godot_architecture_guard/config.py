from __future__ import annotations

from pathlib import Path
import tomllib
from typing import Any

from .models import ModulePolicy


def load_policy(path: Path) -> tuple[tuple[ModulePolicy, ...], tuple[str, ...]]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    raw_modules = data.get("modules")
    if not isinstance(raw_modules, dict) or not raw_modules:
        raise ValueError("policy must contain at least one [modules.<name>] table")
    modules: list[ModulePolicy] = []
    for name, raw in sorted(raw_modules.items()):
        if not isinstance(raw, dict):
            raise ValueError(f"module {name!r} must be a table")
        modules.append(
            ModulePolicy(
                name=str(name),
                paths=tuple(str(item) for item in _list(raw.get("paths", []))),
                may_depend_on=tuple(str(item) for item in _list(raw.get("may_depend_on", []))),
                allowed_autoloads=tuple(str(item) for item in _list(raw.get("allowed_autoloads", []))),
            )
        )
    autoloads_raw = data.get("autoloads", {})
    autoloads = tuple(str(item) for item in _list(autoloads_raw.get("names", []) if isinstance(autoloads_raw, dict) else []))
    return tuple(modules), autoloads


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

