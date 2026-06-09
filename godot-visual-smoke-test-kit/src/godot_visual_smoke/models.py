from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SafeArea:
    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom,
        }


@dataclass(frozen=True)
class Viewport:
    name: str
    width: int
    height: int
    safe_area: SafeArea = field(default_factory=SafeArea)


@dataclass(frozen=True)
class SceneSpec:
    name: str
    path: str
    viewport: str


@dataclass(frozen=True)
class SmokeConfig:
    pixel_tolerance: int = 0
    max_changed_percent: float = 0.0
    output_dir: str = "visual-smoke-output"
    viewports: dict[str, Viewport] = field(default_factory=dict)
    scenes: list[SceneSpec] = field(default_factory=list)


@dataclass(frozen=True)
class DiffResult:
    baseline: str
    current: str
    width: int
    height: int
    changed_pixels: int
    total_pixels: int
    changed_percent: float
    max_delta: int
    passed: bool
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "baseline": self.baseline,
            "current": self.current,
            "width": self.width,
            "height": self.height,
            "changed_pixels": self.changed_pixels,
            "total_pixels": self.total_pixels,
            "changed_percent": self.changed_percent,
            "max_delta": self.max_delta,
            "passed": self.passed,
            "reason": self.reason,
        }
