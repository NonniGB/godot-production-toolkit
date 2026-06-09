from __future__ import annotations


RULE_HELP: dict[str, dict[str, str]] = {
    "alpha_border_fix_disabled": {
        "title": "Alpha border fix disabled",
        "explanation": "A transparent texture is imported without Godot's alpha border fix, which can leave visible fringes.",
    },
    "large_palette": {
        "title": "Large palette",
        "explanation": "A pixel-art profile asset uses more unique colors than the configured palette threshold.",
    },
    "missing_import_metadata": {
        "title": "Missing Godot import metadata",
        "explanation": "The PNG does not have a neighboring .import file, so import-setting checks cannot fully run.",
    },
    "pixel_mipmaps_enabled": {
        "title": "Mipmaps enabled for pixel art",
        "explanation": "Mipmaps can blur pixel-art textures unless the asset is intentionally used at many scales.",
    },
    "texture_dimension_too_large": {
        "title": "Texture dimensions too large",
        "explanation": "The PNG exceeds the configured maximum texture dimension on at least one axis.",
    },
    "texture_memory_large": {
        "title": "Large texture memory estimate",
        "explanation": "The texture may use a large amount of memory when expanded to RGBA on device.",
    },
    "transparent_edge_rgb": {
        "title": "Transparent edge RGB data",
        "explanation": "Fully transparent edge pixels carry RGB data that can bleed into visible edges after filtering.",
    },
}


def explain_issue_code(code: str) -> dict[str, str]:
    return RULE_HELP.get(
        code,
        {
            "title": code.replace("_", " ").title(),
            "explanation": "This asset rule reported a project-specific issue.",
        },
    )


def catalog_for(codes: set[str]) -> dict[str, dict[str, str]]:
    return {code: explain_issue_code(code) for code in sorted(codes)}
