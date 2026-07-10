from pathlib import Path
import unittest

from verify_release_alignment import PUBLISHED_PACKAGES


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CHECKOUT_REVISION = "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
SETUP_REVISION = "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"
PUBLISH_REVISION = "pypa/gh-action-pypi-publish@cef221092ed1bacb1cc03d23a2d87d1d172e277b"


class PublishWorkflowTests(unittest.TestCase):
    def test_every_package_tag_is_owned_by_exactly_one_workflow(self) -> None:
        texts = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(WORKFLOWS.glob("publish*.yml"))
        }
        self.assertEqual(len(texts), 17)

        for package in PUBLISHED_PACKAGES:
            owners = [name for name, text in texts.items() if f'"{package}-v*"' in text]
            with self.subTest(package=package):
                self.assertEqual(len(owners), 1, msg=f"owners={owners}")

    def test_publishers_share_security_and_validation_gates(self) -> None:
        for path in sorted(WORKFLOWS.glob("publish*.yml")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(workflow=path.name):
                self.assertIn(CHECKOUT_REVISION, text)
                self.assertIn(SETUP_REVISION, text)
                self.assertIn(PUBLISH_REVISION, text)
                self.assertIn("resolve_publish_package.py", text)
                self.assertIn("verify_release_alignment.py", text)
                self.assertIn("verify_cli_smoke.py", text)
                self.assertIn("for tests_dir in */tests", text)
                self.assertNotIn("@release/", text)


if __name__ == "__main__":
    unittest.main()
