extends Control

signal start_requested

func _ready() -> void:
    $StartButton.text = tr("MENU_START") if has_node("StartButton") else tr("MENU_START")

func start_game() -> void:
    start_requested.emit()
