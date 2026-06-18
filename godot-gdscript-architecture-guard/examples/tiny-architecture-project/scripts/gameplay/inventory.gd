extends RefCounted

const ITEM_DATA = "res://data/items.json"

func add_item(id: String) -> void:
    GameState.add_item(id)
