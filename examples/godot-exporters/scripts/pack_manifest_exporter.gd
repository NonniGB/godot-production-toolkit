extends SceneTree

const DEFAULT_OUTPUT_PATH: String = "user://pack-manifest.json"
const DEFAULT_INCLUDE_EXTENSIONS: PackedStringArray = [".tscn", ".tres", ".gd", ".png", ".jpg", ".webp", ".ogg", ".wav", ".json"]

func _init() -> void:
    var options: Dictionary = _parse_args(OS.get_cmdline_user_args())
    var output_path: String = str(options.get("output", DEFAULT_OUTPUT_PATH))
    var include_extensions: PackedStringArray = _parse_extensions(str(options.get("include", ",".join(DEFAULT_INCLUDE_EXTENSIONS))))
    var payload: Dictionary = {
        "id": str(options.get("id", "project_content")),
        "version": str(options.get("version", "0.1.0")),
        "dependencies": [],
        "files": _scan_files("res://", include_extensions)
    }

    _write_json(output_path, payload)
    quit(0)


func _scan_files(root_path: String, include_extensions: PackedStringArray) -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    var dir: DirAccess = DirAccess.open(root_path)
    if dir == null:
        return rows

    dir.list_dir_begin()
    var entry_name: String = dir.get_next()
    while not entry_name.is_empty():
        if entry_name.begins_with("."):
            entry_name = dir.get_next()
            continue

        var entry_path: String = root_path.path_join(entry_name)
        if dir.current_is_dir():
            rows.append_array(_scan_files(entry_path, include_extensions))
        elif _matches_extension(entry_path, include_extensions):
            rows.append({
                "path": entry_path,
                "references": [],
                "overrides": false
            })
        entry_name = dir.get_next()

    dir.list_dir_end()
    rows.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return str(a["path"]) < str(b["path"]))
    return rows


func _matches_extension(path: String, include_extensions: PackedStringArray) -> bool:
    for extension: String in include_extensions:
        if path.ends_with(extension):
            return true
    return false


func _parse_extensions(value: String) -> PackedStringArray:
    var result: PackedStringArray = []
    for item: String in value.split(",", false):
        var extension: String = item.strip_edges()
        if extension.is_empty():
            continue
        result.append(extension if extension.begins_with(".") else ".%s" % extension)
    return result


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
        push_error("Could not write pack manifest: %s" % path)
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
