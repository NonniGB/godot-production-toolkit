import csv
import json
import tempfile
import unittest
from pathlib import Path

from godot_l10n_guard.cli import main
from godot_l10n_guard.models import CsvTable, TranslationEntry
from godot_l10n_guard.stress import write_stress_pack


class StressPackTests(unittest.TestCase):
    def test_write_stress_pack_creates_variants_and_manifest(self) -> None:
        table = CsvTable(
            path="strings.csv",
            languages=["en"],
            entries=[
                TranslationEntry(
                    "MENU_START",
                    "Start {name} %d",
                    {"en": "Start {name} %d"},
                    "strings.csv",
                    2,
                )
            ],
        )

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "stress"
            manifest = write_stress_pack(
                [table],
                output_dir,
                source_language="en",
                variants=["pseudo", "long", "compact", "rtl"],
            )

            self.assertEqual(manifest["summary"]["variants"], 4)
            self.assertTrue((output_dir / "stress-pack-manifest.json").exists())
            for filename in ("pseudo.csv", "long.csv", "compact.csv", "rtl.csv"):
                with (output_dir / filename).open("r", encoding="utf-8", newline="") as handle:
                    rows = list(csv.reader(handle))
                self.assertEqual(rows[0][0:2], ["keys", "en"])
                self.assertEqual(rows[1][0], "MENU_START")
                self.assertIn("{name}", rows[1][2])
                self.assertIn("%d", rows[1][2])

    def test_stress_pack_cli_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            csv_path = project / "strings.csv"
            csv_path.write_text("keys,en\nMENU_START,Start Game\n", encoding="utf-8")
            output_dir = project / "stress"
            report_path = project / "stress-report.json"

            exit_code = main(
                [
                    "stress-pack",
                    str(project),
                    "--csv",
                    str(csv_path),
                    "--variants",
                    "pseudo,long",
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                    "--output",
                    str(report_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metadata"]["report_kind"], "localization_stress_pack")
            self.assertEqual(report["summary"]["variants"], 2)
            self.assertTrue((output_dir / "pseudo.csv").exists())
            self.assertTrue((output_dir / "long.csv").exists())


if __name__ == "__main__":
    unittest.main()
