from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MobileProfile:
    name: str
    description: str
    max_texture_dimension: int
    max_viewport_pixels: int


PROFILES: dict[str, MobileProfile] = {
    "portrait-2d": MobileProfile(
        name="portrait-2d",
        description="Phone-first 2D projects with a portrait-oriented base viewport.",
        max_texture_dimension=2048,
        max_viewport_pixels=720 * 1280,
    ),
    "balanced-mobile": MobileProfile(
        name="balanced-mobile",
        description="General mobile projects that can tolerate a 1080p-style base viewport.",
        max_texture_dimension=2048,
        max_viewport_pixels=1920 * 1080,
    ),
    "low-end-mobile": MobileProfile(
        name="low-end-mobile",
        description="Stricter budgets for older Android devices or battery-sensitive builds.",
        max_texture_dimension=1024,
        max_viewport_pixels=720 * 1280,
    ),
    "tablet-2d": MobileProfile(
        name="tablet-2d",
        description="Larger-screen 2D projects where a bigger base viewport is intentional.",
        max_texture_dimension=2048,
        max_viewport_pixels=2048 * 1536,
    ),
}

DEFAULT_PROFILE = "portrait-2d"


def get_profile(name: str) -> MobileProfile:
    return PROFILES[name]


def profile_rows() -> list[MobileProfile]:
    return [PROFILES[name] for name in sorted(PROFILES)]
