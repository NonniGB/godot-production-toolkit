extends Node

@export var output_path: String = "user://runtime-telemetry.json"
@export var scenario: String = "smoke_run"
@export var phase: String = "runtime"
@export_range(0.05, 10.0, 0.05) var sample_interval_s: float = 1.0
@export var write_on_every_sample: bool = false

var _elapsed_s: float = 0.0
var _sample_timer_s: float = 0.0
var _samples: Array[Dictionary] = []

func _ready() -> void:
    set_process(true)


func _process(delta: float) -> void:
    _elapsed_s += delta
    _sample_timer_s += delta
    if _sample_timer_s < sample_interval_s:
        return

    _sample_timer_s = 0.0
    _samples.append(_sample(delta))
    if write_on_every_sample:
        write_snapshot()


func _exit_tree() -> void:
    write_snapshot()


func write_snapshot() -> void:
    var payload: Dictionary = {"samples": _samples}
    var normalized_path: String = _normalize_output_path(output_path)
    var file: FileAccess = FileAccess.open(normalized_path, FileAccess.WRITE)
    if file == null:
        push_warning("Could not write telemetry snapshot: %s" % output_path)
        return
    file.store_string(JSON.stringify(payload, "  "))


func mark_phase(next_phase: String) -> void:
    phase = next_phase


func _sample(delta: float) -> Dictionary:
    return {
        "scenario": scenario,
        "phase": phase,
        "time_s": snappedf(_elapsed_s, 0.001),
        "frame_ms": snappedf(delta * 1000.0, 0.001),
        "physics_ms": snappedf(float(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)) * 1000.0, 0.001),
        "memory_mb": snappedf(float(Performance.get_monitor(Performance.MEMORY_STATIC)) / 1048576.0, 0.001),
        "nodes": int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
        "draw_calls": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
    }


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
