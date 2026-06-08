## Public controller for the sample actor.
class_name SampleActor
extends Node

## Emitted when the actor changes state.
signal state_changed(state: String)

## Speed in pixels per second.
@export var speed: float = 120.0

## Applies a new state.
func apply_state(state: String) -> void:
    state_changed.emit(state)

func reset_state() -> void:
    pass
