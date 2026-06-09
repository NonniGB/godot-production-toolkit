extends Control

const Inventory = preload("res://scripts/gameplay/inventory.gd")

func _ready() -> void:
    Settings.apply()
    Inventory.new()

