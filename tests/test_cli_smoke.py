from pathlib import Path
import unittest

import verify_cli_smoke
from verify_release_alignment import PACKAGE_VERSION_FILES, PUBLISHED_PACKAGES


ROOT = Path(__file__).resolve().parents[1]


class CliSmokeTests(unittest.TestCase):
    def test_smoke_targets_cover_every_published_package(self) -> None:
        missing: list[str] = []
        for package in PUBLISHED_PACKAGES:
            cli_name = PACKAGE_VERSION_FILES[package]["cli_name"]
            if verify_cli_smoke._script_target(ROOT / package / "pyproject.toml", cli_name) is None:
                missing.append(f"{package}: {cli_name}")

        self.assertEqual([], missing)

    def test_smoke_args_cover_help_and_version(self) -> None:
        self.assertEqual(("--help", "--version"), verify_cli_smoke.SMOKE_ARGS)


if __name__ == "__main__":
    unittest.main()
