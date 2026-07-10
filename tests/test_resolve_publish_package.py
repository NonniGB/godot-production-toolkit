from pathlib import Path
import unittest

from resolve_publish_package import resolve_publish_package


ROOT = Path(__file__).resolve().parents[1]


class ResolvePublishPackageTests(unittest.TestCase):
    def test_resolves_exact_versioned_tag(self) -> None:
        package, version = resolve_publish_package(
            ROOT, "godot-production-doctor-v0.2.4"
        )

        self.assertEqual((package, version), ("godot-production-doctor", "0.2.4"))

    def test_rejects_tag_with_wrong_version(self) -> None:
        with self.assertRaises(ValueError):
            resolve_publish_package(ROOT, "godot-production-doctor-v999")

    def test_manual_package_must_be_known(self) -> None:
        with self.assertRaises(ValueError):
            resolve_publish_package(ROOT, "", "unknown-package")
