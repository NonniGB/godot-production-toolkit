from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from godot_asset_doctor.import_parser import parse_import_file


class ImportParserTests(unittest.TestCase):
    def test_parse_import_file_reads_params_and_coerces_common_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            import_path = Path(tmp_dir) / "sprite.png.import"
            import_path.write_text(
                "\n".join(
                    [
                        "[remap]",
                        'importer="texture"',
                        "",
                        "[params]",
                        "compress/mode=0",
                        "mipmaps/generate=true",
                        "process/fix_alpha_border=false",
                        'detect_3d/compress_to="Disabled"',
                    ]
                ),
                encoding="utf-8",
            )

            metadata = parse_import_file(import_path)

            self.assertEqual(metadata.path, import_path)
            self.assertEqual(metadata.params["compress/mode"], 0)
            self.assertTrue(metadata.params["mipmaps/generate"])
            self.assertFalse(metadata.params["process/fix_alpha_border"])
            self.assertEqual(metadata.params["detect_3d/compress_to"], "Disabled")


if __name__ == "__main__":
    unittest.main()

