from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RuleSettings:
    max_texture_dimension: int = 4096
    large_texture_bytes: int = 16 * 1024 * 1024
    max_palette_colors: int = 256


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
class Issue:
    path: Path
    severity: str
    code: str
    message: str
    suggestion: str

    def to_dict(self) -> dict[str, str]:
        return {
            "path": str(self.path),
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass
class ScanReport:
    root: Path
    profile: str
    assets: list[AssetRecord] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    def summary(self) -> dict[str, int | str]:
        error_count = sum(1 for issue in self.issues if issue.severity == "error")
        warning_count = sum(1 for issue in self.issues if issue.severity == "warning")
        info_count = sum(1 for issue in self.issues if issue.severity == "info")
        return {
            "root": str(self.root),
            "profile": self.profile,
            "asset_count": len(self.assets),
            "issue_count": len(self.issues),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "assets": [asset.to_dict() for asset in self.assets],
            "issues": [issue.to_dict() for issue in self.issues],
        }
