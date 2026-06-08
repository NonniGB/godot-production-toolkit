import tempfile
import unittest
from pathlib import Path

from godot_l10n_guard.usage_scanner import scan_project_keys


class UsageScannerTests(unittest.TestCase):
    def test_scans_scripts_and_scenes_for_translation_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ui.gd").write_text(
                'func _ready():\n    label.text = tr("MENU_START")\n    TranslationServer.translate("MENU_EXIT")\n',
                encoding="utf-8",
            )
            (root / "menu.tscn").write_text('text = "MENU_TITLE"\ntext = "ordinary sentence"\n', encoding="utf-8")

            keys = scan_project_keys(root, scan_scripts=True, scan_scenes=True)

            self.assertEqual(keys, {"MENU_START", "MENU_EXIT", "MENU_TITLE"})


if __name__ == "__main__":
    unittest.main()
