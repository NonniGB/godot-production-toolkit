from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReferenceSpec:
    field: str
    collection: str
    required: bool = True


@dataclass(frozen=True)
class CollectionSpec:
    name: str
    path: str
    id_field: str = "id"
    references: tuple[ReferenceSpec, ...] = ()
    roots: tuple[str, ...] = ()
    warn_unused: bool = False
    numeric_fields: tuple[str, ...] = ()


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    collection: str | None = None
    path: str | None = None
    item_id: str | None = None
    field: str | None = None
    target_collection: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if value is not None}


@dataclass
class CollectionData:
    spec: CollectionSpec
    records: list[dict[str, Any]]
    source_path: str
    ids: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

