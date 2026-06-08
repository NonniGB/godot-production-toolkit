from pathlib import Path
import unittest

from verify_release_alignment import check_release_alignment


ROOT = Path(__file__).resolve().parents[1]


class ReleaseAlignmentTests(unittest.TestCase):
    def test_release_facing_versions_are_aligned(self) -> None:
        self.assertEqual([], check_release_alignment(ROOT))


if __name__ == "__main__":
    unittest.main()
