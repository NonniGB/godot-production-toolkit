extends Control

signal menu_confirmed

@export var menu_title: String = "Main Menu"

func _ready() -> void:
    pass

func _on_start_pressed() -> void:
    menu_confirmed.emit()
