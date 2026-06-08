extends Control

signal menu_confirmed

func _ready() -> void:
    pass

func _on_start_pressed() -> void:
    menu_confirmed.emit()
