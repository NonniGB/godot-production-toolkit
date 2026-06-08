import tempfile
import unittest
from pathlib import Path

from godot_l10n_guard.csv_parser import parse_csv_file


class CsvParserTests(unittest.TestCase):
    def test_parses_godot_csv_and_detects_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "strings.csv"
            path.write_bytes(
                b"\xef\xbb\xbfkeys,en,fr\nMENU_START,Start,Demarrer\nMENU_EXIT,Exit,\nMENU_START,Start,Demarrer\n"
            )

            table = parse_csv_file(path)

            self.assertTrue(table.had_bom)
            self.assertEqual(table.languages, ["en", "fr"])
            self.assertEqual(table.entries[0].key, "MENU_START")
            self.assertEqual(table.entries[1].translations["fr"], "")
            self.assertEqual(table.duplicate_keys, {"MENU_START"})


if __name__ == "__main__":
    unittest.main()
