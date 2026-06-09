import csv
import tempfile
import unittest
from pathlib import Path

from godot_l10n_guard.models import CsvTable, TranslationEntry
from godot_l10n_guard.pseudo import pseudo_localize, write_pseudo_csv


class PseudoLocalizationTests(unittest.TestCase):
    def test_pseudo_localize_preserves_placeholders(self) -> None:
        text = pseudo_localize("Hello {name}, score %d")

        self.assertIn("{name}", text)
        self.assertIn("%d", text)
        self.assertTrue(text.startswith("[!! "))
        self.assertTrue(text.endswith("!!]"))

    def test_write_pseudo_csv_uses_source_text(self) -> None:
        table = CsvTable(
            path="strings.csv",
            languages=["en"],
            entries=[TranslationEntry("MENU_START", "Start Game", {"en": "Start Game"}, "strings.csv", 2)],
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "pseudo.csv"
            write_pseudo_csv([table], output, source_language="en", pseudo_language="qps-ploc")

            with output.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))

        self.assertEqual(rows[0], ["keys", "en", "qps-ploc"])
        self.assertEqual(rows[1][0], "MENU_START")
        self.assertEqual(rows[1][1], "Start Game")
        self.assertIn("[!!", rows[1][2])


if __name__ == "__main__":
    unittest.main()
