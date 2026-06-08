import unittest
from pathlib import Path

from gdscript_api_coverage.parser import parse_gdscript


SCRIPT = """
## Public class entry point.
class_name PlayerController

## Fired when interaction starts.
signal interaction_started(target_id: String)

## Maximum movement speed.
@export var max_speed: float = 200.0

@export
var undocumented_toggle: bool = false

## Starts movement.
func start_move(direction: Vector2) -> void:
    pass

func stop_move() -> void:
    pass

func _ready() -> void:
    pass

const DEFAULT_LAYER := 2
"""


class ParserTests(unittest.TestCase):
    def test_parses_public_api_items_and_comment_status(self) -> None:
        items = parse_gdscript(Path("scripts/player_controller.gd"), SCRIPT)

        by_name = {item.name: item for item in items}

        self.assertEqual(by_name["PlayerController"].kind, "class")
        self.assertTrue(by_name["PlayerController"].documented)
        self.assertEqual(by_name["interaction_started"].kind, "signal")
        self.assertTrue(by_name["max_speed"].documented)
        self.assertFalse(by_name["undocumented_toggle"].documented)
        self.assertTrue(by_name["start_move"].documented)
        self.assertFalse(by_name["stop_move"].documented)
        self.assertNotIn("_ready", by_name)
        self.assertEqual(by_name["DEFAULT_LAYER"].kind, "constant")


if __name__ == "__main__":
    unittest.main()
