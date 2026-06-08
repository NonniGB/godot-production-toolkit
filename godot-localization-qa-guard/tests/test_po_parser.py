import tempfile
import unittest
from pathlib import Path

from godot_l10n_guard.po_parser import parse_po_file


class PoParserTests(unittest.TestCase):
    def test_parses_po_entries_flags_and_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fr.po"
            path.write_text(
                """
#, fuzzy
msgid "MENU_START"
msgstr "Demarrer"

msgid "MENU_EXIT"
msgstr ""

msgid "MENU_START"
msgstr "Commencer"
""",
                encoding="utf-8",
            )

            catalog = parse_po_file(path)

            self.assertEqual(catalog.language, "fr")
            self.assertEqual(catalog.entries[0].key, "MENU_START")
            self.assertTrue(catalog.entries[0].fuzzy)
            self.assertEqual(catalog.duplicate_keys, {"MENU_START"})


if __name__ == "__main__":
    unittest.main()
