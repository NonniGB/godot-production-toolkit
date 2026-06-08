import unittest
from pathlib import Path

from godot_signal_auditor.gdscript_parser import parse_gdscript_signals


SCRIPT = """
signal confirmed(id: String)

func _ready() -> void:
    EventBus.game_started.connect(_on_game_started)

func _on_confirmed(id: String) -> void:
    pass
"""


class GdscriptParserTests(unittest.TestCase):
    def test_parses_signals_methods_and_connect_calls(self) -> None:
        parsed = parse_gdscript_signals(Path("scripts/menu.gd"), SCRIPT, autoloads={"EventBus"})

        self.assertEqual(parsed.signals, {"confirmed"})
        self.assertIn("_on_confirmed", parsed.methods)
        self.assertEqual(len(parsed.connect_calls), 1)
        self.assertEqual(parsed.connect_calls[0].autoload, "EventBus")
        self.assertEqual(parsed.connect_calls[0].signal, "game_started")


if __name__ == "__main__":
    unittest.main()
