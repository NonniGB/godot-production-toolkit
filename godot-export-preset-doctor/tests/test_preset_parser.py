import unittest

from godot_export_doctor.preset_parser import parse_export_presets


SAMPLE_PRESETS = """
[preset.0]
name="Android Release"
platform="Android"
runnable=false
export_filter="all_resources"
export_path="build/android/game.apk"

[preset.0.options]
package/unique_name="com.example.game"
version/code=12
version/name="1.2.0"
architectures/arm64-v8a=true
architectures/armeabi-v7a=false

[preset.1]
name="Windows Debug"
platform="Windows Desktop"
runnable=true
export_path="build/windows/game.exe"
"""


class PresetParserTests(unittest.TestCase):
    def test_parses_presets_and_options(self) -> None:
        presets = parse_export_presets(SAMPLE_PRESETS)

        self.assertEqual(len(presets), 2)
        android = presets[0]
        self.assertEqual(android.index, 0)
        self.assertEqual(android.name, "Android Release")
        self.assertEqual(android.platform, "Android")
        self.assertFalse(android.runnable)
        self.assertEqual(android.export_filter, "all_resources")
        self.assertEqual(android.include_filter, "")
        self.assertEqual(android.exclude_filter, "")
        self.assertEqual(android.export_path, "build/android/game.apk")
        self.assertEqual(android.options["package/unique_name"], "com.example.game")
        self.assertEqual(android.options["version/code"], 12)
        self.assertTrue(android.options["architectures/arm64-v8a"])

    def test_ignores_unrelated_sections(self) -> None:
        content = """
[configuration]
entry_symbol="main"

[preset.2]
name="HTML5"
platform="Web"
export_path="build/web/index.html"
"""

        presets = parse_export_presets(content)

        self.assertEqual([preset.index for preset in presets], [2])
        self.assertEqual(presets[0].platform, "Web")

    def test_parses_matrix_fields(self) -> None:
        content = """
[preset.0]
name="Web Demo"
platform="Web"
runnable=true
export_filter="all_resources"
include_filter="*.pck,*.json"
exclude_filter="tests/*"
custom_features="web,demo"
export_path="build/web/index.html"
"""

        preset = parse_export_presets(content)[0]

        self.assertEqual(preset.export_filter, "all_resources")
        self.assertEqual(preset.include_filter, "*.pck,*.json")
        self.assertEqual(preset.exclude_filter, "tests/*")
        self.assertEqual(preset.custom_features, "web,demo")


if __name__ == "__main__":
    unittest.main()
