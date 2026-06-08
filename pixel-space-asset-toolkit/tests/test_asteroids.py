import json
import tempfile
import unittest
from pathlib import Path

from pixel_space_assets.asteroids import generate_asteroid_tiles


class AsteroidTests(unittest.TestCase):
    def test_generates_tiles_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)

            manifest = generate_asteroid_tiles(output, material="ferric", count=3, size=32, seed=7)

            self.assertEqual(len(list(output.glob("*.png"))), 3)
            self.assertEqual(manifest["material"], "ferric")
            self.assertEqual(len(manifest["tiles"]), 3)
            self.assertEqual(json.loads((output / "manifest.json").read_text(encoding="utf-8"))["seed"], 7)


if __name__ == "__main__":
    unittest.main()
