extends SceneTree

const DEFAULT_OUTPUT_PATH: String = "user://mobile-ui.json"
const DEFAULT_VIEWPORT_NAME: String = "portrait_phone"
const DEFAULT_WIDTH: int = 720
const DEFAULT_HEIGHT: int = 1280

var _options: Dictionary = {}

func _init() -> void:
    _options = _parse_args(OS.get_cmdline_user_args())
    call_deferred("_run")


func _run() -> void:
    var output_path: String = str(_options.get("output", DEFAULT_OUTPUT_PATH))
    var scene_path: String = str(_options.get("scene", _default_scene_path()))
    if scene_path.is_empty():
        push_error("No scene was supplied and the project has no main scene.")
        quit(1)
        return

    var packed_scene: PackedScene = load(scene_path) as PackedScene
    if packed_scene == null:
        push_error("Could not load scene: %s" % scene_path)
        quit(1)
        return

    var width: int = int(_options.get("width", DEFAULT_WIDTH))
    var height: int = int(_options.get("height", DEFAULT_HEIGHT))
    root.size = Vector2i(width, height)

    var scene_root: Node = packed_scene.instantiate()
    root.add_child(scene_root)
    if scene_root is Control:
        var root_control: Control = scene_root as Control
        root_control.position = Vector2.ZERO
        root_control.size = Vector2(width, height)

    await process_frame
    await process_frame

    var payload: Dictionary = {
        "thresholds": {
            "min_touch_size": int(_options.get("min_touch_size", 44)),
            "min_touch_spacing": int(_options.get("min_touch_spacing", 8))
        },
        "viewports": [
            {
                "name": str(_options.get("viewport_name", DEFAULT_VIEWPORT_NAME)),
                "width": width,
                "height": height,
                "safe_area": {
                    "left": int(_options.get("safe_left", 0)),
                    "top": int(_options.get("safe_top", 0)),
                    "right": int(_options.get("safe_right", 0)),
                    "bottom": int(_options.get("safe_bottom", 0))
                }
            }
        ],
        "screens": [
            {
                "name": scene_path.get_file().get_basename(),
                "viewport": str(_options.get("viewport_name", DEFAULT_VIEWPORT_NAME)),
                "nodes": _collect_controls(scene_root)
            }
        ]
    }

    _write_json(output_path, payload)
    quit(0)


func _collect_controls(node: Node) -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    _collect_controls_recursive(node, rows)
    return rows


func _collect_controls_recursive(node: Node, rows: Array[Dictionary]) -> void:
    if node is Control:
        var control: Control = node as Control
        var rect: Rect2 = control.get_global_rect()
        var row: Dictionary = {
            "id": str(control.get_path()),
            "kind": _control_kind(control),
            "x": int(round(rect.position.x)),
            "y": int(round(rect.position.y)),
            "width": int(round(rect.size.x)),
            "height": int(round(rect.size.y)),
            "interactive": _is_interactive(control)
        }
        var text: String = _control_text(control)
        if not text.is_empty():
            row["text"] = text
        rows.append(row)

    for child: Node in node.get_children():
        _collect_controls_recursive(child, rows)


func _control_kind(control: Control) -> String:
    if control is Button:
        return "button"
    if control is Label:
        return "label"
    if control is LineEdit:
        return "input"
    if control is TextEdit:
        return "text"
    if control is TextureRect:
        return "image"
    return control.get_class().to_snake_case()


func _control_text(control: Control) -> String:
    if control is Button:
        var button: Button = control as Button
        return button.text
    if control is Label:
        var label: Label = control as Label
        return label.text
    if control is LineEdit:
        var line_edit: LineEdit = control as LineEdit
        return line_edit.text
    if control is TextEdit:
        var text_edit: TextEdit = control as TextEdit
        return text_edit.text
    return ""


func _is_interactive(control: Control) -> bool:
    return control is BaseButton or control is LineEdit or control is TextEdit or control.focus_mode != Control.FOCUS_NONE


func _default_scene_path() -> String:
    return str(ProjectSettings.get_setting("application/run/main_scene", ""))


func _parse_args(args: PackedStringArray) -> Dictionary:
    var parsed: Dictionary = {}
    var index: int = 0
    while index < args.size():
        var key: String = args[index]
        if key.begins_with("--") and index + 1 < args.size():
            parsed[key.trim_prefix("--").replace("-", "_")] = args[index + 1]
            index += 2
        else:
            index += 1
    return parsed


func _write_json(path: String, payload: Dictionary) -> void:
    var normalized_path: String = _normalize_output_path(path)
    var file: FileAccess = FileAccess.open(normalized_path, FileAccess.WRITE)
    if file == null:
        push_error("Could not write JSON file: %s" % path)
        return
    file.store_string(JSON.stringify(payload, "  "))


func _normalize_output_path(path: String) -> String:
    var normalized_path: String = path.replace("\\", "/")
    if normalized_path.begins_with("res://") or normalized_path.begins_with("user://") or normalized_path.is_absolute_path():
        _ensure_parent_dir(normalized_path)
        return normalized_path

    var project_path: String = ProjectSettings.globalize_path("res://").path_join(normalized_path)
    _ensure_parent_dir(project_path)
    return project_path


func _ensure_parent_dir(path: String) -> void:
    var base_dir: String = path.get_base_dir()
    if not base_dir.is_empty():
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(base_dir))
