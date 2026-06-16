extends SceneTree

const DEFAULT_OUTPUT_PATH: String = "user://scenario-result.json"

func _init() -> void:
    var options: Dictionary = _parse_args(OS.get_cmdline_user_args())
    var scenario: String = str(options.get("scenario", "smoke_run"))
    var status: String = str(options.get("status", "passed"))
    var output_path: String = str(options.get("output", DEFAULT_OUTPUT_PATH))
    var duration_ms: int = int(options.get("duration_ms", 0))

    var payload: Dictionary = {
        "scenario": scenario,
        "status": status,
        "duration_ms": duration_ms,
        "assertions": _parse_repeated_pairs(options.get("assertion", [])),
        "artifacts": _as_string_array(options.get("artifact", []))
    }

    _write_json(output_path, payload)
    quit(1 if status == "failed" else 0)


func _parse_args(args: PackedStringArray) -> Dictionary:
    var parsed: Dictionary = {}
    var index: int = 0
    while index < args.size():
        var key: String = args[index]
        if key.begins_with("--") and index + 1 < args.size():
            var normalized_key: String = key.trim_prefix("--").replace("-", "_")
            if parsed.has(normalized_key):
                if not (parsed[normalized_key] is Array):
                    parsed[normalized_key] = [parsed[normalized_key]]
                parsed[normalized_key].append(args[index + 1])
            else:
                parsed[normalized_key] = args[index + 1]
            index += 2
        else:
            index += 1
    return parsed


func _parse_repeated_pairs(value: Variant) -> Array[Dictionary]:
    var assertions: Array[Dictionary] = []
    for item: String in _as_string_array(value):
        var parts: PackedStringArray = item.split(":", false, 1)
        assertions.append({
            "name": parts[0],
            "status": parts[1] if parts.size() > 1 else "passed"
        })
    return assertions


func _as_string_array(value: Variant) -> Array[String]:
    var result: Array[String] = []
    if value is Array:
        for item: Variant in value:
            result.append(str(item))
    elif str(value) != "":
        result.append(str(value))
    return result


func _write_json(path: String, payload: Dictionary) -> void:
    var normalized_path: String = _normalize_output_path(path)
    var file: FileAccess = FileAccess.open(normalized_path, FileAccess.WRITE)
    if file == null:
        push_error("Could not write scenario result: %s" % path)
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
