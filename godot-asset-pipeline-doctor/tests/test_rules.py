from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_asset_doctor.models import AssetRecord, ImportMetadata, PngInfo, RuleSettings
from godot_asset_doctor.rules import evaluate_asset


class RuleTests(unittest.TestCase):
    def test_pixel_profile_flags_mipmaps_alpha_border_and_transparent_rgb(self) -> None:
        asset = AssetRecord(
            path=Path("assets/player.png"),
            png=PngInfo(
                path=Path("assets/player.png"),
                width=64,
                height=64,
                mode="RGBA",
                has_alpha=True,
                palette_color_count=24,
                transparent_pixel_count=10,
                contaminated_transparent_pixel_count=2,
                contaminated_transparent_edge_pixel_count=1,
                estimated_rgba_bytes=16384,
            ),
            import_metadata=ImportMetadata(
                path=Path("assets/player.png.import"),
                sections={"params": {}},
                params={
                    "mipmaps/generate": True,
                    "process/fix_alpha_border": False,
                },
            ),
        )

        issues = evaluate_asset(asset, profile="pixel-2d")
        issue_codes = {issue.code for issue in issues}

        self.assertIn("pixel_mipmaps_enabled", issue_codes)
        self.assertIn("alpha_border_fix_disabled", issue_codes)
        self.assertIn("transparent_edge_rgb", issue_codes)

    def test_android_profile_flags_large_texture_memory(self) -> None:
        asset = AssetRecord(
            path=Path("assets/background.png"),
            png=PngInfo(
                path=Path("assets/background.png"),
                width=4096,
                height=4096,
                mode="RGBA",
                has_alpha=False,
                palette_color_count=512,
                transparent_pixel_count=0,
                contaminated_transparent_pixel_count=0,
                contaminated_transparent_edge_pixel_count=0,
                estimated_rgba_bytes=4096 * 4096 * 4,
            ),
            import_metadata=None,
        )

        issues = evaluate_asset(asset, profile="android-mobile")

        self.assertIn("missing_import_metadata", {issue.code for issue in issues})
        self.assertIn("texture_memory_large", {issue.code for issue in issues})

    def test_custom_rule_settings_adjust_thresholds(self) -> None:
        asset = AssetRecord(
            path=Path("assets/ui_panel.png"),
            png=PngInfo(
                path=Path("assets/ui_panel.png"),
                width=128,
                height=64,
                mode="RGBA",
                has_alpha=False,
                palette_color_count=4,
                transparent_pixel_count=0,
                contaminated_transparent_pixel_count=0,
                contaminated_transparent_edge_pixel_count=0,
                estimated_rgba_bytes=128 * 64 * 4,
            ),
            import_metadata=None,
        )

        issues = evaluate_asset(
            asset,
            profile="default",
            settings=RuleSettings(
                max_texture_dimension=64,
                large_texture_bytes=1,
                max_palette_colors=2,
            ),
        )
        issue_codes = {issue.code for issue in issues}

        self.assertIn("texture_dimension_too_large", issue_codes)
        self.assertIn("texture_memory_large", issue_codes)
        self.assertIn("large_palette", issue_codes)


if __name__ == "__main__":
    unittest.main()
