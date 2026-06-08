extends Control

func _ready() -> void:
    $StartButton.text = tr("MENU_START")
    $ExitButton.text = TranslationServer.translate("MENU_EXIT")
