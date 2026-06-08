import hashlib
import unittest

from pixel_space_assets.starfield import generate_starfield


class StarfieldTests(unittest.TestCase):
    def test_starfield_is_deterministic_for_seed(self) -> None:
        first = generate_starfield(width=32, height=32, seed=42, stars=20)
        second = generate_starfield(width=32, height=32, seed=42, stars=20)

        self.assertEqual(first.size, (32, 32))
        self.assertEqual(
            hashlib.sha256(first.tobytes()).hexdigest(),
            hashlib.sha256(second.tobytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
