from __future__ import annotations

from godot_asset_doctor.models import AssetRecord, AudioRecord, Issue, RuleSettings


def evaluate_asset(asset: AssetRecord, profile: str, settings: RuleSettings | None = None) -> list[Issue]:
    rule_settings = settings or RuleSettings()
    issues: list[Issue] = []
    issues.extend(_common_rules(asset, rule_settings))

    if profile == "pixel-2d":
        issues.extend(_pixel_2d_rules(asset, rule_settings))
    elif profile == "android-mobile":
        issues.extend(_android_mobile_rules(asset, rule_settings))
    elif profile == "audio-mobile":
        return []
    elif profile == "default":
        issues.extend(_pixel_2d_rules(asset, rule_settings))
        issues.extend(_android_mobile_rules(asset, rule_settings))
    else:
        raise ValueError(f"Unknown profile: {profile}")

    return issues


def evaluate_audio_asset(asset: AudioRecord, profile: str, settings: RuleSettings | None = None) -> list[Issue]:
    rule_settings = settings or RuleSettings()
    if profile not in {"default", "android-mobile", "audio-mobile"}:
        return []
    return _audio_mobile_rules(asset, rule_settings)


def _common_rules(asset: AssetRecord, settings: RuleSettings) -> list[Issue]:
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

    if png.width > settings.max_texture_dimension or png.height > settings.max_texture_dimension:
        issues.append(
            Issue(
                path=asset.path,
                severity="error",
                code="texture_dimension_too_large",
                message=(
                    f"Texture is {png.width}x{png.height}, which exceeds "
                    f"{settings.max_texture_dimension}px on one axis."
                ),
                suggestion="Split the image, lower source resolution, or verify target devices support this texture size.",
            )
        )

    return issues


def _pixel_2d_rules(asset: AssetRecord, settings: RuleSettings) -> list[Issue]:
    issues: list[Issue] = []
    png = asset.png
    params = asset.import_metadata.params if asset.import_metadata else {}

    if png.palette_color_count > settings.max_palette_colors:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="large_palette",
                message=(
                    f"Image uses {png.palette_color_count} unique RGBA colors, "
                    f"above the configured {settings.max_palette_colors} color pixel-art threshold."
                ),
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


def _android_mobile_rules(asset: AssetRecord, settings: RuleSettings) -> list[Issue]:
    issues: list[Issue] = []
    png = asset.png

    if png.estimated_rgba_bytes >= settings.large_texture_bytes:
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


def _audio_mobile_rules(asset: AudioRecord, settings: RuleSettings) -> list[Issue]:
    issues: list[Issue] = []
    audio = asset.audio

    if asset.import_metadata is None:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="missing_audio_import_metadata",
                message="Audio file has no adjacent Godot .import metadata file.",
                suggestion="Open the project in Godot or reimport audio before relying on import-setting checks.",
            )
        )

    if audio.file_size_bytes >= settings.large_audio_bytes:
        mib = audio.file_size_bytes / (1024 * 1024)
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="audio_file_large",
                message=f"Audio source file is {mib:.1f} MiB, above the configured mobile budget.",
                suggestion="Review compression, streaming settings, or whether this clip belongs in a lower-memory build.",
            )
        )

    if audio.duration_seconds is not None and audio.duration_seconds > settings.max_audio_duration_seconds:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="audio_duration_long",
                message=(
                    f"Audio duration is {audio.duration_seconds:.1f}s, above the configured "
                    f"{settings.max_audio_duration_seconds:.1f}s budget."
                ),
                suggestion="Use streaming/compressed import settings for long music, ambience, or narration tracks.",
            )
        )

    if audio.format == "wav" and audio.file_size_bytes >= settings.large_audio_bytes:
        issues.append(
            Issue(
                path=asset.path,
                severity="warning",
                code="large_uncompressed_audio",
                message="Large WAV files can create avoidable package size and memory pressure.",
                suggestion="Keep WAV for short effects; consider OGG/MP3 or streaming import settings for longer clips.",
            )
        )

    return issues
