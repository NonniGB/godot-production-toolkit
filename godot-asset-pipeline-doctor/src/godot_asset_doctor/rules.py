from __future__ import annotations

from godot_asset_doctor.models import AssetRecord, Issue


LARGE_TEXTURE_BYTES = 16 * 1024 * 1024
MAX_TEXTURE_DIMENSION = 4096


def evaluate_asset(asset: AssetRecord, profile: str) -> list[Issue]:
    issues: list[Issue] = []
    issues.extend(_common_rules(asset))

    if profile == "pixel-2d":
        issues.extend(_pixel_2d_rules(asset))
    elif profile == "android-mobile":
        issues.extend(_android_mobile_rules(asset))
    elif profile == "default":
        issues.extend(_pixel_2d_rules(asset))
        issues.extend(_android_mobile_rules(asset))
    else:
        raise ValueError(f"Unknown profile: {profile}")

    return issues


def _common_rules(asset: AssetRecord) -> list[Issue]:
    issues: list[Issue] = []
    png = asset.png

    if asset.import_metadata is None:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="missing_import_metadata",
                message="PNG has no adjacent Godot .import metadata file.",
                suggestion="Open the project in Godot or reimport assets before relying on import-setting checks.",
            )
        )

    if png.width > MAX_TEXTURE_DIMENSION or png.height > MAX_TEXTURE_DIMENSION:
        issues.append(
            Issue(
                path=asset.path,
                severity="error",
                code="texture_dimension_too_large",
                message=f"Texture is {png.width}x{png.height}, which exceeds {MAX_TEXTURE_DIMENSION}px on one axis.",
                suggestion="Split the image, lower source resolution, or verify target devices support this texture size.",
            )
        )

    return issues


def _pixel_2d_rules(asset: AssetRecord) -> list[Issue]:
    issues: list[Issue] = []
    png = asset.png
    params = asset.import_metadata.params if asset.import_metadata else {}

    if png.palette_color_count > 256:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="large_palette",
                message=f"Image uses {png.palette_color_count} unique RGBA colors, which may not be intentional pixel art.",
                suggestion="Check whether this asset should be palette-reduced or excluded from the pixel-2d profile.",
            )
        )

    if params.get("mipmaps/generate") is True:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="pixel_mipmaps_enabled",
                message="Mipmaps are enabled for a pixel-art profile asset.",
                suggestion="Disable mipmap generation unless the asset is intentionally scaled in 3D or at many sizes.",
            )
        )

    if png.has_alpha and params.get("process/fix_alpha_border") is False:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="alpha_border_fix_disabled",
                message="Alpha border fixing is disabled on an image with transparency.",
                suggestion="Enable alpha border fixing or ensure transparent pixels are decontaminated in source art.",
            )
        )

    if png.contaminated_transparent_edge_pixel_count > 0:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="transparent_edge_rgb",
                message=(
                    f"{png.contaminated_transparent_edge_pixel_count} fully transparent edge pixel(s) "
                    "carry non-black RGB values."
                ),
                suggestion="Clean transparent RGB data or enable alpha-border fixing to reduce fringe artifacts.",
            )
        )

    return issues


def _android_mobile_rules(asset: AssetRecord) -> list[Issue]:
    issues: list[Issue] = []
    png = asset.png

    if png.estimated_rgba_bytes >= LARGE_TEXTURE_BYTES:
        mib = png.estimated_rgba_bytes / (1024 * 1024)
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="texture_memory_large",
                message=f"Texture would occupy about {mib:.1f} MiB as RGBA in memory.",
                suggestion="Reduce dimensions, use atlases carefully, or review compression/import settings for mobile builds.",
            )
        )

    return issues

