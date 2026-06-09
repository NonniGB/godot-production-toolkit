from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from godot_asset_doctor import __version__
from godot_asset_doctor.rule_help import catalog_for, explain_issue_code


@dataclass(frozen=True)
class RuleSettings:
    max_texture_dimension: int = 4096
    large_texture_bytes: int = 16 * 1024 * 1024
    max_palette_colors: int = 256
    large_audio_bytes: int = 8 * 1024 * 1024
    max_audio_duration_seconds: float = 120.0


@dataclass(frozen=True)
class PngInfo:
    path: Path
    width: int
    height: int
    mode: str
    has_alpha: bool
    palette_color_count: int
    transparent_pixel_count: int
    contaminated_transparent_pixel_count: int
    contaminated_transparent_edge_pixel_count: int
    estimated_rgba_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "width": self.width,
            "height": self.height,
            "mode": self.mode,
            "has_alpha": self.has_alpha,
            "palette_color_count": self.palette_color_count,
            "transparent_pixel_count": self.transparent_pixel_count,
            "contaminated_transparent_pixel_count": self.contaminated_transparent_pixel_count,
            "contaminated_transparent_edge_pixel_count": self.contaminated_transparent_edge_pixel_count,
            "estimated_rgba_bytes": self.estimated_rgba_bytes,
        }


@dataclass(frozen=True)
class ImportMetadata:
    path: Path
    sections: dict[str, dict[str, Any]]
    params: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "sections": self.sections,
            "params": self.params,
        }


@dataclass(frozen=True)
class AudioInfo:
    path: Path
    format: str
    file_size_bytes: int
    duration_seconds: float | None = None
    sample_rate_hz: int | None = None
    channels: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "format": self.format,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "sample_rate_hz": self.sample_rate_hz,
            "channels": self.channels,
        }


@dataclass(frozen=True)
class AssetRecord:
    path: Path
    png: PngInfo
    import_metadata: ImportMetadata | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "png": self.png.to_dict(),
            "import_metadata": self.import_metadata.to_dict() if self.import_metadata else None,
        }


@dataclass(frozen=True)
class AudioRecord:
    path: Path
    audio: AudioInfo
    import_metadata: ImportMetadata | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "audio": self.audio.to_dict(),
            "import_metadata": self.import_metadata.to_dict() if self.import_metadata else None,
        }


@dataclass(frozen=True)
class Issue:
    path: Path
    severity: str
    code: str
    message: str
    suggestion: str

    def to_dict(self) -> dict[str, str]:
        help_text = explain_issue_code(self.code)
        return {
            "path": str(self.path),
            "severity": self.severity,
            "code": self.code,
            "title": help_text["title"],
            "explanation": help_text["explanation"],
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass
class ScanReport:
    root: Path
    profile: str
    assets: list[AssetRecord] = field(default_factory=list)
    audio_assets: list[AudioRecord] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    def summary(self) -> dict[str, int | str]:
        error_count = sum(1 for issue in self.issues if issue.severity == "error")
        warning_count = sum(1 for issue in self.issues if issue.severity == "warning")
        info_count = sum(1 for issue in self.issues if issue.severity == "info")
        return {
            "root": str(self.root),
            "profile": self.profile,
            "asset_count": len(self.assets) + len(self.audio_assets),
            "image_asset_count": len(self.assets),
            "audio_asset_count": len(self.audio_assets),
            "issue_count": len(self.issues),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": "godot-asset-pipeline-doctor",
            "metadata": {
                "schema_version": "1.2",
                "tool_version": __version__,
                "report_kind": "asset_pipeline_scan",
                "root": str(self.root),
                "profile": self.profile,
                "formats": ["text", "json", "sarif"],
            },
            "summary": self.summary(),
            "assets": [asset.to_dict() for asset in self.assets],
            "audio_assets": [asset.to_dict() for asset in self.audio_assets],
            "rules": catalog_for({issue.code for issue in self.issues}),
            "issues": [issue.to_dict() for issue in self.issues],
        }
