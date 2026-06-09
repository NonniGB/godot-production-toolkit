from __future__ import annotations

from pathlib import Path
import tomllib
from typing import Any

from .models import CollectionSpec, ReferenceSpec


def load_config(path: Path) -> tuple[CollectionSpec, ...]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    raw_collections = data.get("collections")
    if not isinstance(raw_collections, dict) or not raw_collections:
        raise ValueError("config must contain at least one [collections.<name>] table")

    specs: list[CollectionSpec] = []
    for name, raw_spec in sorted(raw_collections.items()):
        if not isinstance(raw_spec, dict):
            raise ValueError(f"collection {name!r} must be a table")
        if not raw_spec.get("path"):
            raise ValueError(f"collection {name!r} is missing path")
        references = tuple(_reference_spec(item, name) for item in raw_spec.get("references", []))
        specs.append(
            CollectionSpec(
                name=str(name),
                path=str(raw_spec["path"]),
                id_field=str(raw_spec.get("id", "id")),
                references=references,
                roots=tuple(str(item) for item in _list(raw_spec.get("roots", []))),
                warn_unused=bool(raw_spec.get("warn_unused", False)),
                numeric_fields=tuple(str(item) for item in _list(raw_spec.get("numeric_fields", []))),
            )
        )
    return tuple(specs)


def _reference_spec(raw: Any, owner: str) -> ReferenceSpec:
    if not isinstance(raw, dict):
        raise ValueError(f"reference in collection {owner!r} must be a table")
    if not raw.get("field") or not raw.get("collection"):
        raise ValueError(f"reference in collection {owner!r} needs field and collection")
    return ReferenceSpec(
        field=str(raw["field"]),
        collection=str(raw["collection"]),
        required=bool(raw.get("required", True)),
    )


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

