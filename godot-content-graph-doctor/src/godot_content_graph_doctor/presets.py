from __future__ import annotations

from .models import CollectionSpec, ReferenceSpec


BUILTIN_PRESETS: dict[str, tuple[CollectionSpec, ...]] = {
    "items": (
        CollectionSpec(
            name="items",
            path="data/items.json",
            id_field="id",
            numeric_fields=("value", "price", "weight"),
        ),
    ),
    "recipes": (
        CollectionSpec(
            name="items",
            path="data/items.json",
            id_field="id",
            roots=("copper_ore", "iron_ore", "wood"),
            warn_unused=True,
            numeric_fields=("value", "price", "weight"),
        ),
        CollectionSpec(
            name="recipes",
            path="data/recipes.json",
            id_field="id",
            references=(
                ReferenceSpec(field="inputs[].item", collection="items"),
                ReferenceSpec(field="outputs[].item", collection="items"),
            ),
            numeric_fields=("craft_time", "duration", "cost"),
        ),
    ),
    "quests": (
        CollectionSpec(name="items", path="data/items.json", id_field="id"),
        CollectionSpec(
            name="quests",
            path="data/quests.json",
            id_field="id",
            references=(
                ReferenceSpec(field="prerequisites[]", collection="quests", required=False),
                ReferenceSpec(field="rewards[].item", collection="items", required=False),
            ),
        ),
    ),
    "dialogue": (
        CollectionSpec(name="characters", path="data/characters.json", id_field="id"),
        CollectionSpec(
            name="dialogue",
            path="data/dialogue.json",
            id_field="id",
            references=(
                ReferenceSpec(field="speaker", collection="characters", required=False),
                ReferenceSpec(field="next[].id", collection="dialogue", required=False),
            ),
        ),
    ),
    "levels": (
        CollectionSpec(name="items", path="data/items.json", id_field="id"),
        CollectionSpec(name="enemies", path="data/enemies.json", id_field="id"),
        CollectionSpec(
            name="levels",
            path="data/levels.json",
            id_field="id",
            references=(
                ReferenceSpec(field="items[].id", collection="items", required=False),
                ReferenceSpec(field="enemies[].id", collection="enemies", required=False),
            ),
        ),
    ),
    "content-pack": (
        CollectionSpec(name="items", path="data/items.json", id_field="id"),
        CollectionSpec(
            name="content_pack_items",
            path="mods/content_pack/items.json",
            id_field="id",
            references=(ReferenceSpec(field="replaces", collection="items", required=False),),
            numeric_fields=("value", "price", "weight"),
        ),
    ),
}


PRESET_DESCRIPTIONS: dict[str, str] = {
    "items": "Single item catalog with common numeric balance fields.",
    "recipes": "Item and recipe graph with input/output references.",
    "quests": "Quest prerequisites and optional item rewards.",
    "dialogue": "Dialogue nodes with character speakers and next-node links.",
    "levels": "Level files that reference item and enemy catalogs.",
    "content-pack": "Overlay content pack items that can replace base item ids.",
}


def load_presets(names: list[str]) -> tuple[CollectionSpec, ...]:
    specs: list[CollectionSpec] = []
    for name in names:
        try:
            specs.extend(BUILTIN_PRESETS[name])
        except KeyError as exc:
            known = ", ".join(sorted(BUILTIN_PRESETS))
            raise ValueError(f"unknown preset {name!r}; known presets: {known}") from exc
    return tuple(specs)


def merge_specs(*groups: tuple[CollectionSpec, ...]) -> tuple[CollectionSpec, ...]:
    merged: dict[str, CollectionSpec] = {}
    for specs in groups:
        for spec in specs:
            merged[spec.name] = spec
    return tuple(merged[name] for name in sorted(merged))


def render_preset_list() -> str:
    lines = ["Godot Content Graph Presets"]
    for name in sorted(BUILTIN_PRESETS):
        lines.append(f"- {name}: {PRESET_DESCRIPTIONS[name]}")
    return "\n".join(lines)
