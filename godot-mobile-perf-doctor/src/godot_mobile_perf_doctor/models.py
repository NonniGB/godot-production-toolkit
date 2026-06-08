from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "path": self.path,
        }


@dataclass(frozen=True)
class TextureInfo:
    path: Path
    width: int
    height: int

    @property
    def rgba_mb(self) -> float:
        return round((self.width * self.height * 4) / (1024 * 1024), 2)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path.as_posix(),
            "width": self.width,
            "height": self.height,
            "rgba_mb": self.rgba_mb,
        }


@dataclass(frozen=True)
class TextureSummary:
    total_textures: int = 0
    large_textures: list[TextureInfo] = field(default_factory=list)
    total_estimated_rgba_mb: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "total_textures": self.total_textures,
            "large_textures": [texture.to_dict() for texture in self.large_textures],
            "total_estimated_rgba_mb": self.total_estimated_rgba_mb,
        }


@dataclass(frozen=True)
class AdbSummary:
    device: str = ""
    android: str = ""
    total_frames: int = 0
    janky_frames: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "device": self.device,
            "android": self.android,
            "total_frames": self.total_frames,
            "janky_frames": self.janky_frames,
        }
